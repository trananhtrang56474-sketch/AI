import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from config import Config
# 引入插件
from extensions import db, mail 
# 引入路由
from routes import api_bp

# ========================================================
# 1. 初始化 Flask 应用 (改为全局变量，方便外部导入)
# ========================================================
app = Flask(__name__)
app.config.from_object(Config)

# ========================================================
# 2. 图片上传配置
# ========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ========================================================
# 3. 📧 邮件服务配置 (163邮箱)
# ========================================================
app.config['MAIL_SERVER'] = 'smtp.163.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False

# 👇👇👇 你的账号信息 👇👇👇
app.config['MAIL_USERNAME'] = 'ui144ud851@163.com'       # 你的真实邮箱
app.config['MAIL_PASSWORD'] = 'MSeaSXbt4W6RFyQH'         # 你的授权码
app.config['MAIL_DEFAULT_SENDER'] = ('AI心理顾问', 'ui144ud851@163.com') 
# 👆👆👆 你的账号信息 👆👆👆

# ========================================================
# 4. 🔌 插件初始化 & 路由注册
# ========================================================
CORS(app)
db.init_app(app)
mail.init_app(app)

# 注册蓝图
app.register_blueprint(api_bp)

# 图片访问路由
@app.route('/uploads/<filename>')
def serve_uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ========================================================
# 5. 启动入口
# ========================================================
if __name__ == "__main__":
    # 在启动时自动检查并创建数据库表
    with app.app_context():
        try:
            # 引入所有模型，确保 create_all 能识别到它们
            # 必须放在这里，防止循环导入
            from models import User, ChatLog, ChatSession, MoodDiary
            
            db.create_all()
            print("✅ 数据库表结构检查/创建成功")
        except Exception as e:
            print(f"❌ 数据库连接或创建表失败: {e}")

    print("🚀 服务启动: http://127.0.0.1:8080")
    # 注意：debug=True 修改代码会自动重启，port=8080
    app.run(host="127.0.0.1", port=8080, debug=True)