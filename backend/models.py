import requests
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User, ChatLog, ChatSession
from config import Config

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
# 3. 获取会话列表
# ===========================
@api_bp.route("/sessions", methods=["GET"])
def get_sessions():
    user_id = request.args.get("user_id")
    if not user_id: return jsonify([])
    
    try:
        sessions = ChatSession.query.filter_by(user_id=user_id).order_by(ChatSession.created_at.desc()).all()
        return jsonify([{
            "id": s.id,
            "title": s.title,
            "created_at": s.created_at.strftime("%m-%d %H:%M")
        } for s in sessions])
    except Exception as e:
        print(f"❌ 获取会话失败: {e}")
        return jsonify([])

# ===========================
# 4. 获取历史记录
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
        print(f"❌ 获取历史失败: {e}")
        return jsonify([])

# ===========================
# 5. 聊天接口 (🔥逻辑顺序已修正)
# ===========================
@api_bp.route("/chat", methods=["POST"])
def chat_handler():
    data = request.json
    user_message = data.get("message")
    user_id = data.get("user_id")
    session_id = data.get("session_id") 

    if not user_message or not user_id:
        return jsonify({"error": "缺少必要参数"}), 400

    # 🔥 第一步：绝对优先解决 session_id 问题
    # 如果没传 session_id，或者传的是 null/None，必须先创建一个！
    if not session_id:
        try:
            # 自动取标题
            title = user_message[:10] + "..." if len(user_message) > 10 else user_message
            new_session = ChatSession(user_id=user_id, title=title)
            db.session.add(new_session)
            db.session.commit() # 提交后，new_session.id 就有值了
            
            session_id = new_session.id # 拿到这个至关重要的 ID
            print(f"🆕 自动创建新会话: ID={session_id}, 标题={title}")
        except Exception as e:
            print(f"❌ 创建会话失败: {e}")
            db.session.rollback()
            return jsonify({"error": "无法建立新对话"}), 500

    # 🔥 第二步：此时 session_id 绝对有值了，才去存消息
    try:
        print(f"💾 正在存储消息到 Session {session_id}...")
        user_log = ChatLog(
            user_id=user_id, 
            session_id=session_id, # 这里的 session_id 绝对不可能是 None
            role="user", 
            content=user_message
        )
        db.session.add(user_log)
        db.session.commit()
    except Exception as e:
        print(f"❌ 存用户消息失败: {e}")
        db.session.rollback()
        return jsonify({"error": "消息保存失败"}), 500

    # 🔥 第三步：准备上下文 (去数据库查，或者直接用当前这句)
    messages_payload = []
    try:
        recent_logs = ChatLog.query.filter_by(session_id=session_id).order_by(ChatLog.created_at.desc()).limit(6).all()
        recent_logs.reverse()
        for log in recent_logs:
            messages_payload.append({"role": log.role, "content": log.content})
    except:
        messages_payload = [{"role": "user", "content": user_message}]

    # 🔥 第四步：调 API
    REAL_API_KEY = "sk-56307adfa2e44424a95148cab9830edc" 
    API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    
    payload = {
        "model": "qwen-plus",
        "messages": messages_payload,
        "max_tokens": 1000
    }
    headers = {"Authorization": f"Bearer {REAL_API_KEY}", "Content-Type": "application/json"}

    ai_reply = "（AI 似乎在思考...）"
    try:
        response = requests.post(API_URL, json=payload, headers=headers, verify=False, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if "choices" in data:
                ai_reply = data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"❌ API 调用异常: {e}")

    # 🔥 第五步：存 AI 回复
    try:
        ai_log = ChatLog(user_id=user_id, session_id=session_id, role="assistant", content=ai_reply)
        db.session.add(ai_log)
        db.session.commit()
    except Exception as e:
        print(f"❌ AI 存库失败: {e}")
        db.session.rollback()

    # 返回 session_id，让前端知道这是哪个会话
    return jsonify({"reply": ai_reply, "session_id": session_id})