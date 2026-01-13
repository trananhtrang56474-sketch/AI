import os
from datetime import datetime
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# 引入配置
from extensions import db
from models import User, ChatLog, ChatSession

# ✨✨✨ 引入核心智能模块 ✨✨✨
from llm.qwen_client import QwenClient
from rag.retriever import rag_engine
from rag.prompt_builder import prompt_engine
from agent.emotion import analyze_emotion, analyze_trend  # 感知
from agent.policy import PolicyRouter                   # 决策

# 创建蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')
llm_client = QwenClient()

# ===========================
# 辅助函数
# ===========================
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# ===========================
# 1. 基础接口 (注册/登录/会话)
# ===========================
@api_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    if User.query.filter_by(username=data.get("username")).first():
        return jsonify({"error": "用户名已存在"}), 400
    new_user = User(username=data.get("username"), password_hash=generate_password_hash(data.get("password")))
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "注册成功", "user_id": new_user.id}), 201

@api_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get("username")).first()
    if user and check_password_hash(user.password_hash, data.get("password")):
        return jsonify({"message": "登录成功", "user_id": user.id, "username": user.username})
    return jsonify({"error": "用户名或密码错误"}), 401

@api_bp.route("/sessions", methods=["GET"])
def get_sessions():
    uid = request.args.get("user_id")
    if not uid: return jsonify([])
    sessions = ChatSession.query.filter_by(user_id=uid).order_by(ChatSession.created_at.desc()).all()
    return jsonify([{"id": s.id, "title": s.title, "created_at": s.created_at.strftime("%m-%d %H:%M")} for s in sessions])

# ==================================================================
# 🔥 核心修改：升级版历史记录接口 (支持状态回溯)
# ==================================================================
@api_bp.route("/history", methods=["GET"])
def get_history():
    sid = request.args.get("session_id")
    if not sid: return jsonify([])

    # 1. 获取消息记录 (按时间正序)
    logs = ChatLog.query.filter_by(session_id=sid).order_by(ChatLog.created_at.asc()).all()
    
    # 2. ✨✨✨ 状态回溯逻辑 ✨✨✨
    # 目的：当用户点开历史记录时，右侧面板要恢复到那次对话最后的状态，而不是显示默认值。
    
    # A. 回溯情绪 (找最后一条用户的消息，读取当时的 emotion_tag)
    last_user_log = ChatLog.query.filter_by(session_id=sid, role='user').order_by(ChatLog.created_at.desc()).first()
    restored_emotion = last_user_log.emotion_tag if (last_user_log and last_user_log.emotion_tag) else "平静"
    
    # B. 回溯策略 (找最后一条 AI 的消息，因为我们在 chat 接口里把策略存进去了)
    last_ai_log = ChatLog.query.filter_by(session_id=sid, role='assistant').order_by(ChatLog.created_at.desc()).first()
    restored_strategy = last_ai_log.emotion_tag if (last_ai_log and last_ai_log.emotion_tag) else "GENERAL_SUPPORT"
    
    # C. 回溯趋势 (调用 agent 重新计算一遍)
    restored_trend = analyze_trend(sid)

    # 3. 返回组合数据
    # 注意：这里的数据结构变了！以前是直接返回数组，现在是返回一个字典对象
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
# 3. 🔥 核心聊天接口 (智能 Agent + 防御门控版)
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

    # B. 🧠 智能体感知与决策
    current_emotion = "neutral"
    emotion_trend = "FIRST_CONTACT"
    policy = {"stage": "VISUAL", "instruction": "多模态回复"}
    
    if user_msg and user_msg != '[发送了图片]':
        # 1. 感知
        current_emotion = analyze_emotion(user_msg)
        emotion_trend = analyze_trend(session_id) 
        print(f"📊 [Agent] 情绪: {current_emotion} | 趋势: {emotion_trend}")
        
        # 2. 决策
        policy = PolicyRouter.route(current_emotion, emotion_trend, user_msg)
        print(f"🧭 [Agent] 策略: {policy['stage']}")
    else:
        policy = {
            "search_intent": "", "stage": "VISUAL_ANALYSIS", 
            "instruction": "用户发送了图片。调用视觉能力分析图片内容和氛围，结合语境回复。"
        }

    # C. 📚 RAG 检索
    query_text = user_msg if (user_msg and user_msg != '[发送了图片]') else "用户发送了图片"
    search_query = f"{query_text} {policy.get('search_intent', '')}"
    knowledge = rag_engine.search(search_query)
    
    if not knowledge and image_url:
        knowledge = {"type": "MULTIMODAL", "stage": "视觉分析", "content": "用户上传了图片..."}

    # ==================================================================
    # 🛡️ Step 3.5: 心理测评防御门控 (中文硬拦截版)
    # ==================================================================
    if knowledge and ("量表" in str(knowledge) or "PHQ-9" in str(knowledge) or "GAD-7" in str(knowledge)):
        
        # 定义负面情绪集合 (中文)
        negative_emotions = ["抑郁", "焦虑", "危机", "痛苦", "愤怒", "悲伤", "愧疚", "迷茫"]
        # 如果当前情绪不在负面列表中 (比如是 平静)
        if current_emotion not in negative_emotions:
            print(f"🛡️ [Gate] 硬拦截触发！用户情绪 [{current_emotion}] 不需要量表，已丢弃 RAG 结果。")
            knowledge = None 
            
            policy['instruction'] += "\n\n【注意】用户当前状态良好。请聚焦于积极心理学，讨论用户的优势和快乐源泉，不要提及任何病理性的内容。"

        # 危机状态特殊处理
        elif current_emotion == "危机":
             policy['instruction'] += "\n\n【特别注意】用户处于危机状态。🚫 不要进行复杂的量表评估。✅ 直接进行危机干预。"
    # ==================================================================

    # D. ⚙️ 组装动态 Prompt
    base_prompt = prompt_engine.build(knowledge)
    final_prompt = (
        f"{base_prompt}\n\n"
        f"### 状态感知\n- 情绪: {current_emotion}\n- 趋势: {emotion_trend}\n\n"
        f"### 干预指令 ({policy['stage']})\n{policy.get('instruction', '')}"
    )

    # E. 💬 LLM 生成
    history = ChatLog.query.filter_by(session_id=session_id).order_by(ChatLog.created_at.desc()).limit(6).all()
    history.reverse()
    messages = [{"role": "system", "content": final_prompt}]
    for l in history:
        messages.append({"role": l.role, "content": l.content})
    if user_msg and user_msg != '[发送了图片]' and (not history or history[-1].content != user_msg):
         messages.append({"role": "user", "content": user_msg})

    # 图片路径处理
    local_image_path = None
    if image_url:
        try:
            fname = image_url.split('/')[-1].split('?')[0]
            local_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], fname)
        except: pass

    ai_reply = llm_client.chat(messages, image_path=local_image_path)

    # F. 📝 存入数据库
    try:
        if image_url:
            db.session.add(ChatLog(user_id=user_id, session_id=session_id, role="user", content=image_url, emotion_tag="multimodal"))
        if user_msg and user_msg != '[发送了图片]':
            db.session.add(ChatLog(
                user_id=user_id, session_id=session_id, role="user", 
                content=user_msg, emotion_tag=current_emotion
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