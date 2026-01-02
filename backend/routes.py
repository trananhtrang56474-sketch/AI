import requests
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User, ChatLog
from config import Config

api_bp = Blueprint('api', __name__, url_prefix='/api')

# ===========================
# 1. 注册接口 (保持不变)
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
        return jsonify({"error": "注册失败，请检查数据库连接"}), 500

# ===========================
# 2. 登录接口 (保持不变)
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
# 3. 聊天接口 (🔥 融合您的成功代码)
# ===========================
@api_bp.route("/chat", methods=["POST"])
def chat_handler():
    # 1. 获取前端数据
    data = request.json
    user_message = data.get("message")
    user_id = data.get("user_id")

    # 校验参数
    if not user_message:
        return jsonify({"error": "Message 字段是必须的"}), 400
    if not user_id:
        return jsonify({"error": "未登录，无法保存记录"}), 401

    # ---------------------------------------------------
    # 步骤 A: 尝试把用户的话存入数据库
    # ---------------------------------------------------
    try:
        print(f"📝 正在保存用户消息: {user_message}")
        user_log = ChatLog(user_id=user_id, role="user", content=user_message)
        db.session.add(user_log)
        db.session.commit()
    except Exception as e:
        print(f"❌ 数据库写入失败 (ChatLog): {e}")
        return jsonify({"error": "数据库故障，无法保存消息"}), 500

    # ---------------------------------------------------
    # 步骤 B: 准备发给 API 的历史记录 (Context)
    # ---------------------------------------------------
    try:
        # 取最近 6 条记录作为上下文，避免 token 消耗过多
        recent_logs = ChatLog.query.filter_by(user_id=user_id).order_by(ChatLog.created_at.desc()).limit(6).all()
        recent_logs.reverse() # 倒序变正序
        
        messages_payload = []
        for log in recent_logs:
            messages_payload.append({"role": log.role, "content": log.content})
        
        # 如果是新对话，加个系统提示词
        if not messages_payload:
            messages_payload.append({"role": "user", "content": user_message})

    except Exception as e:
        print(f"⚠️ 读取历史记录失败: {e}")
        # 如果读数据库失败，至少把当前这句话发出去，不阻断聊天
        messages_payload = [{"role": "user", "content": user_message}]

    # ---------------------------------------------------
    # 步骤 C: 调用通义千问 API (您的核心代码)
    # ---------------------------------------------------
    print("🚀 正在请求通义千问 API...")
    
    # 直接使用您提供的 Key，防止 config 读取不到
    # 注意：正式上线建议还是放 config，这里为了测试先写死
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

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status() # 如果 4xx/5xx 会直接报错跳到 except
        response_data = response.json()

        # 解析回复
        ai_reply = ""
        if "choices" in response_data:
            ai_reply = response_data["choices"][0].get("message", {}).get("content", "")
        
        if not ai_reply:
            ai_reply = "（AI 似乎思考了很久，但没有说话...）"

        print(f"✅ AI 回复: {ai_reply[:20]}...")

    except requests.exceptions.RequestException as e:
        print(f"❌ API 网络请求失败: {e}")
        return jsonify({"error": "连不上通义千问，请检查网络或Key"}), 500
    except Exception as e:
        print(f"❌ API 处理未知错误: {e}")
        return jsonify({"error": "API 解析错误"}), 500

    # ---------------------------------------------------
    # 步骤 D: 把 AI 的话存入数据库
    # ---------------------------------------------------
    try:
        ai_log = ChatLog(user_id=user_id, role="assistant", content=ai_reply)
        db.session.add(ai_log)
        db.session.commit()
    except Exception as e:
        print(f"❌ AI 回复保存失败: {e}")
        # 即使保存失败，也要把回复返给前端，不然用户看不到
    
    return jsonify({"reply": ai_reply})


# ===========================
# 4. 获取历史接口 (保持不变)
# ===========================
@api_bp.route("/history", methods=["GET"])
def get_history():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify([])
    
    try:
        logs = ChatLog.query.filter_by(user_id=user_id).order_by(ChatLog.created_at.asc()).all()
        return jsonify([{
            "sender": "user" if log.role == "user" else "ai",
            "content": log.content
        } for log in logs])
    except Exception as e:
        print(f"获取历史失败: {e}")
        return jsonify([])