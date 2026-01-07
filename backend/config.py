import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 数据库配置 
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:ZJQzxcvbnm123.@127.0.0.1:3306/mental_health_bot?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 安全密钥
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_secret_key')
    
    # 🔥 通义千问配置 (填入您提供的 Key)
    DASHSCOPE_API_KEY = "sk-56307adfa2e44424a95148cab9830edc" 
    API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    MODEL_NAME = "qwen-plus" # 指定模型