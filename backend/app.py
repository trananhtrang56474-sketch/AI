import sys
from flask import Flask
from flask_cors import CORS
from extensions import db
from config import Config

# 1. 尝试导入路由，如果 routes.py 写错，这里会直接报错提示
try:
    from routes import api_bp
except ImportError as e:
    print(f"❌ 启动失败：routes.py 文件有问题。\n详细错误: {e}")
    sys.exit(1)

def create_app():
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(Config)
    
    # 初始化插件
    CORS(app)
    db.init_app(app)

    # 2. 尝试连接数据库
    with app.app_context():
        try:
            # 必须导入模型，SQLAlchemy 才能识别表结构
            import models 
            
            # 尝试建表（这一步最容易报错）
            db.create_all()
            print("✅ 数据库连接成功，表结构已就绪。")
            
        except Exception as e:
            print("\n" + "="*50)
            print("❌ 严重错误：数据库连接失败！")
            print("请检查 backend/config.py 里的密码是否正确。")
            print("请检查 MySQL 是否已启动，且存在 'mental_health_bot' 数据库。")
            print(f"详细报错信息: {e}")
            print("="*50 + "\n")
            # 不退出程序，防止窗口闪退，方便你看报错
    
    # 注册路由
    app.register_blueprint(api_bp)
    
    return app

if __name__ == "__main__":
    app = create_app()
    # 打印一条提示，证明程序正在跑
    print("🚀 服务正在启动，监听端口 8080...")
    app.run(host="127.0.0.1", port=8080, debug=True)