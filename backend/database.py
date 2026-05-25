# backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config import Config

# 从你的 config.py 中读取 MySQL 链接
engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True, # 防止 MySQL 连接超时断开
    pool_recycle=3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 所有数据表都要继承这个 Base
Base = declarative_base()

# FastAPI 依赖注入，用于在每次请求时获取数据库连接
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()