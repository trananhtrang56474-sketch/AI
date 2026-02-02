# backend/routes.py
import os
import random
import string
from datetime import datetime
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Message

# 引入配置
from extensions import db, mail
from models import User, ChatLog, ChatSession

# 引入核心智能模块
from llm.qwen_client import QwenClient
from rag.retriever import rag_engine
from rag.prompt_builder import prompt_engine
from agent.emotion import analyze_emotion, analyze_trend
from agent.policy import PolicyRouter

# 创建蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')
llm_client = QwenClient()

# 全局变量：临时存储验证码
verification_codes = {}

# ===========================
# 辅助函数
# ===========================
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# ===========================
# 1. 基础接口 (注册/登录/验证码)
# ===========================

@api_bp.route("/send-code", methods=["POST"])
def send_code():
    email = request.json.get("email")
    if not email:
        return jsonify({"error": "请输入邮箱地址"}), 400

    code = ''.join(random.choices(string.digits, k=6))
    verification_codes[email] = code

    try:
        msg = Message(subject="【AI Counselor】注册验证码", recipients=[email])
        msg.body = f"欢迎注册 AI Counselor 心理咨询平台。\n您的验证码是：{code}\n有效期 5 分钟，请勿泄露给他人。"
        
        mail.send(msg)
        print(f"✅ [Mail] 验证码已发送至 {email}")
        return jsonify({"message": "验证码发送成功"})

    except Exception as e:
        print(f"❌ [Mail Error] 发送失败: {e}")
        # 模拟模式
        print(f"👉 [模拟模式] 请手动输入验证码: {code}")
        return jsonify({"message": "验证码已发送(模拟)"})

@api_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    code = data.get("code")

    if not email or not password or not code:
        return jsonify({"error": "信息填写不完整"}), 400

    stored_code = verification_codes.get(email)
    if not stored_code or stored_code != code:
        return jsonify({"error": "验证码错误或已过期"}), 400

    if User.query.filter_by(username=email).first():
        return jsonify({"error": "该邮箱已注册"}), 400

    try:
        new_user = User(username=email, password_hash=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        
        verification_codes.pop(email, None)
        
        return jsonify({"message": "注册成功", "user_id": new_user.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get("username")).first()
    
    if user and check_password_hash(user.password_hash, data.get("password")):
        return jsonify({"message": "登录成功", "user_id": user.id, "username": user.username})
    return jsonify({"error": "账号或密码错误"}), 401

# ==================================================================
# 📚 会话管理接口 (获取列表 & ✨✨✨ 删除会话)
# ==================================================================
@api_bp.route("/sessions", methods=["GET"])
def get_sessions():
    uid = request.args.get("user_id")
    if not uid: return jsonify([])
    sessions = ChatSession.query.filter_by(user_id=uid).order_by(ChatSession.created_at.desc()).all()
    return jsonify([{"id": s.id, "title": s.title, "created_at": s.created_at.strftime("%m-%d %H:%M")} for s in sessions])

# ✨✨✨ 新增：删除会话接口 ✨✨✨
@api_bp.route('/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    try:
        # 1. 查找会话
        session = ChatSession.query.get(session_id)
        if not session:
            return jsonify({'error': '会话不存在'}), 404
        
        # 2. 删除关联的消息
        ChatLog.query.filter_by(session_id=session_id).delete()
        
        # 3. 删除会话本身
        db.session.delete(session)
        db.session.commit()
        
        return jsonify({'message': '删除成功', 'id': session_id})
        
    except Exception as e:
        db.session.rollback()
        print(f"删除失败: {e}")
        return jsonify({'error': str(e)}), 500

# ==================================================================
# 🔥 历史记录接口
# ==================================================================
@api_bp.route("/history", methods=["GET"])
def get_history():
    sid = request.args.get("session_id")
    if not sid: return jsonify([])

    logs = ChatLog.query.filter_by(session_id=sid).order_by(ChatLog.created_at.asc()).all()
    
    last_user_log = ChatLog.query.filter_by(session_id=sid, role='user').order_by(ChatLog.created_at.desc()).first()
    restored_emotion = last_user_log.emotion_tag if (last_user_log and last_user_log.emotion_tag) else "平静"
    
    last_ai_log = ChatLog.query.filter_by(session_id=sid, role='assistant').order_by(ChatLog.created_at.desc()).first()
    restored_strategy = last_ai_log.emotion_tag if (last_ai_log and last_ai_log.emotion_tag) else "GENERAL_SUPPORT"
    
    restored_trend = analyze_trend(sid)

    return jsonify({
        "messages": [{"sender": "user" if l.role=="user" else "ai", "content": l.content} for l in logs],
        "analysis": {
            "emotion": restored_emotion,
            "strategy": restored_strategy,
            "trend": restored_trend
        }
    })

# ===========================
# 2. 文件上传
# ===========================
@api_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files: return jsonify({'error': '无文件'}), 400
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename): return jsonify({'error': '文件无效'}), 400
    
    filename = f"{int(datetime.now().timestamp())}_{secure_filename(file.filename)}"
    save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    try:
        file.save(save_path)
        file_url = f"http://127.0.0.1:8080/uploads/{filename}"
        return jsonify({'message': '上传成功', 'url': file_url})
    except: return jsonify({'error': '保存失败'}), 500

# ===========================
# 📊 图表数据接口
# ===========================
@api_bp.route("/chart-data", methods=["GET"])
def get_chart_data():
    user_id = request.args.get("user_id")
    session_id = request.args.get("session_id")
    
    if not user_id: return jsonify({"dates": [], "scores": []})

    query = ChatLog.query.filter_by(user_id=user_id, role='user')
    if session_id:
        query = query.filter_by(session_id=session_id)
        
    logs = query.order_by(ChatLog.created_at.desc()).limit(10).all()
    logs.reverse()
    
    fallback_map = {
        '危机': 10, 'crisis': 10,
        '焦虑': 30, 'anxiety': 30, '抑郁': 25, 'depression': 25,
        '痛苦': 20, 'distress': 20, '愤怒': 35, 'anger': 35,
        '悲伤': 30, 'grief': 30, '愧疚': 30, 'guilt': 30,
        '迷茫': 45, 'confusion': 45,
        '平静': 60, 'neutral': 60,
        '积极': 85, 'positive': 85
    }

    dates = []
    scores = []
    
    for log in logs:
        dates.append(log.created_at.strftime("%H:%M"))
        if log.emotion_score is not None:
            scores.append(log.emotion_score)
        else:
            tag = log.emotion_tag or '平静'
            score = 60 
            for key, val in fallback_map.items():
                if key in tag:
                    score = val
                    break
            scores.append(score)

    return jsonify({
        "dates": dates,
        "scores": scores
    })

# ===========================
# 3. 核心聊天接口
# ===========================
@api_bp.route("/chat", methods=["POST"])
def chat():
    print("\n💡 [Chat] 收到新请求...")
    data = request.json
    user_msg = data.get("message", "")   
    image_url = data.get("image_url")    
    user_id = data.get("user_id")
    session_id = data.get("session_id")

    if not user_id: return jsonify({"error": "参数缺失"}), 400

    # A. 自动创建会话
    if not session_id:
        try:
            title = "[图片分享]" if image_url else (user_msg[:10] + "..." if len(user_msg)>10 else user_msg)
            new_session = ChatSession(user_id=user_id, title=title)
            db.session.add(new_session)
            db.session.commit()
            session_id = new_session.id
        except: return jsonify({"error": "会话创建失败"}), 500

    # B. 智能体感知与决策
    current_emotion = "平静"
    current_score = 60
    emotion_trend = "FIRST_CONTACT"
    policy = {"stage": "VISUAL", "instruction": "多模态回复"}
    
    if user_msg and user_msg != '[发送了图片]':
        analysis_result = analyze_emotion(user_msg)
        current_emotion = analysis_result.get("tag", "平静")
        current_score = analysis_result.get("score", 60)
        
        emotion_trend = analyze_trend(session_id) 
        print(f"📊 [Agent] 情绪: {current_emotion} ({current_score}分) | 趋势: {emotion_trend}")
        
        policy = PolicyRouter.route(current_emotion, emotion_trend, user_msg)
        print(f"🧭 [Agent] 策略: {policy['stage']}")
    else:
        policy = {
            "search_intent": "", "stage": "VISUAL_ANALYSIS", 
            "instruction": "用户发送了图片。调用视觉能力分析图片内容和氛围，结合语境回复。"
        }

    # C. RAG 检索
    query_text = user_msg if (user_msg and user_msg != '[发送了图片]') else "用户发送了图片"
    search_query = f"{query_text} {policy.get('search_intent', '')}"
    knowledge = rag_engine.search(search_query)
    
    if not knowledge and image_url:
        knowledge = {"type": "MULTIMODAL", "stage": "视觉分析", "content": "用户上传了图片..."}

    # 🛡️ 心理测评防御门控
    if knowledge and ("量表" in str(knowledge) or "PHQ-9" in str(knowledge) or "GAD-7" in str(knowledge)):
        negative_emotions = ["抑郁", "焦虑", "危机", "痛苦", "愤怒", "悲伤", "愧疚", "迷茫"]
        if current_emotion not in negative_emotions:
            print(f"🛡️ [Gate] 硬拦截触发！用户情绪 [{current_emotion}] 不需要量表，已丢弃 RAG 结果。")
            knowledge = None 
            policy['instruction'] += "\n\n【注意】用户当前状态良好。请聚焦于积极心理学，讨论用户的优势和快乐源泉，不要提及任何病理性的内容。"
        elif current_emotion == "危机":
             policy['instruction'] += "\n\n【特别注意】用户处于危机状态。🚫 不要进行复杂的量表评估。✅ 直接进行危机干预。"

    # D. 组装动态 Prompt
    base_prompt = prompt_engine.build(knowledge)
    final_prompt = (
        f"{base_prompt}\n\n"
        f"### 状态感知\n- 情绪: {current_emotion} (强度: {current_score}/100)\n- 趋势: {emotion_trend}\n\n"
        f"### 干预指令 ({policy['stage']})\n{policy.get('instruction', '')}"
    )

    # E. LLM 生成
    history = ChatLog.query.filter_by(session_id=session_id).order_by(ChatLog.created_at.desc()).limit(6).all()
    history.reverse()
    messages = [{"role": "system", "content": final_prompt}]
    for l in history:
        messages.append({"role": l.role, "content": l.content})
    if user_msg and user_msg != '[发送了图片]' and (not history or history[-1].content != user_msg):
         messages.append({"role": "user", "content": user_msg})

    local_image_path = None
    if image_url:
        try:
            fname = image_url.split('/')[-1].split('?')[0]
            local_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], fname)
        except: pass

    ai_reply = llm_client.chat(messages, image_path=local_image_path)

    # F. 存入数据库
    try:
        if image_url:
            db.session.add(ChatLog(user_id=user_id, session_id=session_id, role="user", content=image_url, emotion_tag="multimodal"))
        if user_msg and user_msg != '[发送了图片]':
            db.session.add(ChatLog(
                user_id=user_id, session_id=session_id, role="user", 
                content=user_msg, 
                emotion_tag=current_emotion, 
                emotion_score=current_score 
            ))
        db.session.add(ChatLog(
            user_id=user_id, session_id=session_id, role="assistant", 
            content=ai_reply, emotion_tag=policy['stage']
        ))
        db.session.commit()
    except Exception as e:
        print(f"❌ DB Error: {e}")

    return jsonify({
        "reply": ai_reply, 
        "session_id": session_id,
        "emotion": current_emotion,
        "trend": emotion_trend,
        "strategy": policy['stage']
    })