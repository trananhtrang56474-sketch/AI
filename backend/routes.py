import requests
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
# 确保导入了 ChatSession
from models import User, ChatLog, ChatSession 

api_bp = Blueprint('api', __name__, url_prefix='/api')

# ===========================
# 1. 注册接口
# ===========================
@api_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "用户名和密码不能为空"}), 400
        
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "用户名已存在"}), 400

        new_user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "注册成功", "user_id": new_user.id, "username": new_user.username}), 201
    except Exception as e:
        print(f"❌ 注册报错: {e}")
        return jsonify({"error": "注册失败"}), 500

# ===========================
# 2. 登录接口
# ===========================
@api_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password")

        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            return jsonify({
                "message": "登录成功",
                "user_id": user.id,
                "username": user.username
            })
        
        return jsonify({"error": "用户名或密码错误"}), 401
    except Exception as e:
        print(f"❌ 登录报错: {e}")
        return jsonify({"error": "数据库连接异常"}), 500

# ===========================
# 3. 获取会话列表 (侧边栏必须用这个！)
# ===========================
@api_bp.route("/sessions", methods=["GET"])
def get_sessions():
    user_id = request.args.get("user_id")
    if not user_id: return jsonify([])
    
    try:
        # 按时间倒序获取
        sessions = ChatSession.query.filter_by(user_id=user_id).order_by(ChatSession.created_at.desc()).all()
        return jsonify([{
            "id": s.id,
            "title": s.title,
            "created_at": s.created_at.strftime("%m-%d %H:%M")
        } for s in sessions])
    except Exception as e:
        print(f"❌ 获取会话列表失败: {e}")
        return jsonify([])

# ===========================
# 4. 获取聊天历史 (点击侧边栏时用)
# ===========================
@api_bp.route("/history", methods=["GET"])
def get_history():
    session_id = request.args.get("session_id")
    if not session_id: return jsonify([])
    
    try:
        logs = ChatLog.query.filter_by(session_id=session_id).order_by(ChatLog.created_at.asc()).all()
        return jsonify([{
            "sender": "user" if log.role == "user" else "ai",
            "content": log.content
        } for log in logs])
    except Exception as e:
        print(f"获取历史失败: {e}")
        return jsonify([])

# ===========================
# 5. 聊天接口 (🔥 修复了 Session ID 问题)
# ===========================
@api_bp.route("/chat", methods=["POST"])
def chat_handler():
    print("🔥 进入 Chat 接口...") # 调试哨兵

    data = request.json
    user_message = data.get("message")
    user_id = data.get("user_id")
    session_id = data.get("session_id") # 前端如果没有 session_id，这里就是 None

    if not user_message or not user_id:
        return jsonify({"error": "Message 字段是必须的"}), 400

    # ---------------------------------------------------
    # 步骤 A: 检查 Session，如果没有，先创建！(关键修复)
    # ---------------------------------------------------
    if not session_id:
        print("💡 发现是新对话，正在创建 Session...")
        try:
            # 取前10个字做标题
            title = user_message[:10] + "..." if len(user_message) > 10 else user_message
            new_session = ChatSession(user_id=user_id, title=title)
            db.session.add(new_session)
            db.session.commit()
            
            # ✅ 拿到 ID，赋值给 session_id，这样下面存消息就不会报错了
            session_id = new_session.id
            print(f"✅ 新 Session 创建成功: {session_id}")
        except Exception as e:
            print(f"❌ 创建 Session 失败: {e}")
            return jsonify({"error": "创建会话失败"}), 500

    # ---------------------------------------------------
    # 步骤 B: 存入用户消息 (必须带 session_id)
    # ---------------------------------------------------
    try:
        print(f"📝 正在保存用户消息到 Session {session_id}")
        user_log = ChatLog(user_id=user_id, session_id=session_id, role="user", content=user_message)
        db.session.add(user_log)
        db.session.commit()
    except Exception as e:
        print(f"❌ 数据库写入失败 (ChatLog): {e}")
        db.session.rollback()
        return jsonify({"error": "无法保存消息"}), 500

    # ---------------------------------------------------
    # 步骤 C: 准备上下文 (Context)
    # ---------------------------------------------------
    messages_payload = []
    try:
        # 只查当前 session 的记录
        recent_logs = ChatLog.query.filter_by(session_id=session_id).order_by(ChatLog.created_at.desc()).limit(6).all()
        recent_logs.reverse()
        
        for log in recent_logs:
            messages_payload.append({"role": log.role, "content": log.content})
    except:
        messages_payload = [{"role": "user", "content": user_message}]

    # ---------------------------------------------------
    # 步骤 D: 调用通义千问 API
    # ---------------------------------------------------
    print("🚀 请求通义千问 API...")
    REAL_API_KEY = "sk-56307adfa2e44424a95148cab9830edc" 
    API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

    payload = {
        "model": "qwen-plus",
        "messages": messages_payload,
        "max_tokens": 1000,
        "temperature": 0.7
    }
    headers = {
        "Authorization": f"Bearer {REAL_API_KEY}",
        "Content-Type": "application/json"
    }

    ai_reply = "（AI 思考中...）"
    try:
        response = requests.post(API_URL, json=payload, headers=headers, verify=False, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if "choices" in data:
                ai_reply = data["choices"][0].get("message", {}).get("content", "")
        else:
            print(f"API Error Status: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ API 请求异常: {e}")

    # ---------------------------------------------------
    # 步骤 E: 把 AI 的话存入数据库
    # ---------------------------------------------------
    try:
        ai_log = ChatLog(user_id=user_id, session_id=session_id, role="assistant", content=ai_reply)
        db.session.add(ai_log)
        db.session.commit()
    except Exception as e:
        print(f"❌ AI 回复保存失败: {e}")
    
    # 🌟 重点：一定要返回 session_id，否则前端不知道这是哪个会话
    return jsonify({"reply": ai_reply, "session_id": session_id})