import sys
import os
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# 1. 引入配置和数据库
from config import Config
from extensions import db
from models import User, ChatLog, ChatSession

# 2. 引入 RAG 和 LLM 模块
try:
    from llm.qwen_client import QwenClient
    from rag.retriever import rag_engine
    from rag.prompt_builder import prompt_engine  # ✅ 修改：导入实例化后的引擎
    from rag.safety import SafetyGuard
except ImportError as e:
    print(f"❌ 模块导入失败: {e}")
    sys.exit(1)

# 初始化 Flask 应用
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
db.init_app(app)
llm_client = QwenClient()

# ==================================================================
# 🔧 图片上传配置
# ==================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==================================================================
#  API 接口区域
# ==================================================================

# 1. 注册
@app.route("/api/register", methods=["POST"])
def register():
    try:
        data = request.json
        if User.query.filter_by(username=data.get("username")).first():
            return jsonify({"error": "用户名已存在"}), 400
        new_user = User(username=data.get("username"), password_hash=generate_password_hash(data.get("password")))
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "注册成功", "user_id": new_user.id}), 201
    except: return jsonify({"error": "注册失败"}), 500

# 2. 登录
@app.route("/api/login", methods=["POST"])
def login():
    try:
        data = request.json
        user = User.query.filter_by(username=data.get("username")).first()
        if user and check_password_hash(user.password_hash, data.get("password")):
            return jsonify({"message": "登录成功", "user_id": user.id, "username": user.username})
        return jsonify({"error": "用户名或密码错误"}), 401
    except: return jsonify({"error": "系统错误"}), 500

# 3. 会话列表
@app.route("/api/sessions", methods=["GET"])
def get_sessions():
    uid = request.args.get("user_id")
    if not uid: return jsonify([])
    sessions = ChatSession.query.filter_by(user_id=uid).order_by(ChatSession.created_at.desc()).all()
    return jsonify([{"id": s.id, "title": s.title, "created_at": s.created_at.strftime("%m-%d %H:%M")} for s in sessions])

# 4. 聊天历史
@app.route("/api/history", methods=["GET"])
def get_history():
    sid = request.args.get("session_id")
    if not sid: return jsonify([])
    logs = ChatLog.query.filter_by(session_id=sid).order_by(ChatLog.created_at.asc()).all()
    return jsonify([{"sender": "user" if l.role=="user" else "ai", "content": l.content} for l in logs])

# 5. 图片上传
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files: return jsonify({'error': '无文件'}), 400
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename): return jsonify({'error': '文件无效'}), 400
    
    filename = f"{int(datetime.now().timestamp())}_{secure_filename(file.filename)}"
    try:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # 返回图片访问 URL
        file_url = f"http://127.0.0.1:8080/uploads/{filename}"
        return jsonify({'message': '上传成功', 'url': file_url})
    except: return jsonify({'error': '保存失败'}), 500

# 6. 图片访问
@app.route('/uploads/<filename>')
def serve_uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ==================================================================
# 🔥 核心聊天接口 (真正集成了视觉能力的版本)
# ==================================================================
@app.route("/api/chat", methods=["POST"])
def chat():
    print("🔥 进入 RAG 多模态聊天接口...")
    
    data = request.json
    user_msg = data.get("message", "")   
    image_url = data.get("image_url")    
    user_id = data.get("user_id")
    session_id = data.get("session_id")

    if not user_id: return jsonify({"error": "参数缺失"}), 400

    # ---------------------------------------------------
    # A. 自动创建 Session
    # ---------------------------------------------------
    if not session_id:
        try:
            if image_url and (not user_msg or user_msg == '[发送了图片]'):
                title = "[图片分享]"
            elif image_url:
                title = f"[图] {user_msg[:8]}..."
            else:
                title = user_msg[:10] + "..." if len(user_msg) > 10 else user_msg
            new_session = ChatSession(user_id=user_id, title=title)
            db.session.add(new_session)
            db.session.commit()
            session_id = new_session.id
        except: return jsonify({"error": "创建会话失败"}), 500

    # ---------------------------------------------------
    # B. 存消息 (先图后文)
    # ---------------------------------------------------
    try:
        if image_url:
            db.session.add(ChatLog(user_id=user_id, session_id=session_id, role="user", content=image_url))
        if user_msg and user_msg != '[发送了图片]':
            db.session.add(ChatLog(user_id=user_id, session_id=session_id, role="user", content=user_msg))
        db.session.commit()
    except Exception as e:
        return jsonify({"error": "数据库错误"}), 500

    # ---------------------------------------------------
    # C. RAG 检索 & 上下文准备
    # ---------------------------------------------------
    query_text = user_msg if (user_msg and user_msg != '[发送了图片]') else "用户发送了图片"
    knowledge = rag_engine.search(query_text)
    
    # 补充多模态知识上下文
    if not knowledge and image_url:
        knowledge = {
            "type": "MULTIMODAL",
            "stage": "视觉辅助分析",
            "content": "用户上传了图片。请使用你的视觉能力真正地分析图片内容（你拥有视觉模型能力）。结合用户的文字进行情感支持。",
            "response_strategy": "结合视觉内容回复"
        }

    is_crisis = SafetyGuard.check_crisis(knowledge)
    system_prompt = prompt_engine.build(knowledge) # ✅ 修改：使用实例调用 build
    
    # 准备历史记录
    history = ChatLog.query.filter_by(session_id=session_id).order_by(ChatLog.created_at.desc()).limit(6).all()
    history.reverse()
    
    messages = [{"role": "system", "content": system_prompt}]
    for l in history:
        messages.append({"role": l.role, "content": l.content})
    
    # 确保当前文字在最后
    if user_msg and user_msg != '[发送了图片]' and (not history or history[-1].content != user_msg):
         messages.append({"role": "user", "content": user_msg})

    # ---------------------------------------------------
    # D. 🔥 关键步骤：解析图片本地物理路径
    # ---------------------------------------------------
    local_image_path = None
    if image_url:
        # image_url 格式: http://127.0.0.1:8080/uploads/170000_abc.jpg
        # 我们提取文件名 170000_abc.jpg，并拼接到本地 upload 文件夹路径
        try:
            filename = image_url.split('/')[-1]
            # 确保只获取文件名部分，防止 URL 带有 query 参数
            if '?' in filename:
                filename = filename.split('?')[0]
                
            local_image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(f"📍 解析到本地图片路径: {local_image_path}")
            
            if not os.path.exists(local_image_path):
                print("❌ 警告：本地图片文件不存在！")
                local_image_path = None
        except Exception as e:
            print(f"❌ 图片路径解析异常: {e}")

    # ---------------------------------------------------
    # E. 调用 LLM (传入 image_path)
    # ---------------------------------------------------
    print("🚀 请求通义千问 (智能切换文本/视觉模型)...")
    temp = 0.3 if is_crisis else 0.7
    
    # 这里一定要传 image_path 参数，QwenClient 才能读取并转 Base64
    ai_reply = llm_client.chat(messages, temperature=temp, image_path=local_image_path)

    # ---------------------------------------------------
    # F. 存 AI 回复
    # ---------------------------------------------------
    try:
        db.session.add(ChatLog(user_id=user_id, session_id=session_id, role="assistant", content=ai_reply))
        db.session.commit()
    except: pass

    return jsonify({"reply": ai_reply, "session_id": session_id})

if __name__ == "__main__":
    with app.app_context():
        try:
            db.create_all()
            print("✅ 数据库连接成功")
        except Exception as e: # <--- 修改了这里
            print(f"❌ 数据库连接失败: {e}") # <--- 让它打印具体错误
    
    print("🚀 服务启动: http://127.0.0.1:8080")
    app.run(host="127.0.0.1", port=8080, debug=True)