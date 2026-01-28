import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from config import Config
# ✨✨✨ 1. 引入 mail (确保 extensions.py 里已经写了 mail = Mail())
from extensions import db, mail 
from routes import api_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # ========================================================
    # 🖼️ 图片上传配置
    # ========================================================
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # ========================================================
    # 📧 邮件服务配置 (163邮箱稳过版)
    # ⚠️ 请把下面这三行换成你自己刚才测试成功的真实信息！
    # ========================================================
    app.config['MAIL_SERVER'] = 'smtp.163.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USE_TLS'] = False
    
    # 👇👇👇 修改这里 👇👇👇
    app.config['MAIL_USERNAME'] = 'ui144ud851@163.com'       # 你的真实邮箱
    app.config['MAIL_PASSWORD'] = 'MSeaSXbt4W6RFyQH'             # 你的授权码
    app.config['MAIL_DEFAULT_SENDER'] = ('AI心理顾问', 'ui144ud851@163.com') # (昵称, 邮箱)
    # 👆👆👆 修改这里 👆👆👆

    # ========================================================
    # 🔌 插件初始化
    # ========================================================
    CORS(app)
    db.init_app(app)
    mail.init_app(app) # ✨✨✨ 2. 这一行必须加！
    
    # 注册路由
    app.register_blueprint(api_bp)
    
    # 图片访问路由
    @app.route('/uploads/<filename>')
    def serve_uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    return app

if __name__ == "__main__":
    app = create_app()
    
    with app.app_context():
        try:
            db.create_all()
            print("✅ 数据库连接成功")
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")

    print("🚀 服务启动: http://127.0.0.1:8080")
    app.run(host="127.0.0.1", port=8080, debug=True)