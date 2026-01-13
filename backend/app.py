import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from config import Config
from extensions import db
from routes import api_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # ✨✨✨ 修复：显式设置图片上传路径 ✨✨✨
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    # 存入 app 配置，这样其他地方用 app.config['UPLOAD_FOLDER'] 就能找到了
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # 初始化插件
    CORS(app)
    db.init_app(app)
    
    # 注册路由
    app.register_blueprint(api_bp)
    
    # 图片访问路由
    @app.route('/uploads/<filename>')
    def serve_uploaded_file(filename):
        # 现在 app.config 里肯定有这个 key 了
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