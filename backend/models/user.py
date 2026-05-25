# from datetime import datetime
# from extensions import db

# class User(db.Model):
#     __tablename__ = 'users'
#     __table_args__ = {
#         'mysql_charset': 'utf8mb4',
#         'mysql_collate': 'utf8mb4_unicode_ci',
#         'mysql_engine': 'InnoDB'
#     }

#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
    
#     # ✨ 建议改为 256，防止某些哈希算法生成的字符串过长
#     password_hash = db.Column(db.String(256), nullable=False)
    
#     created_at = db.Column(db.DateTime, default=datetime.now)

#     # 关系：User -> ChatSession
#     sessions = db.relationship(
#         'ChatSession',
#         backref='user',
#         lazy='dynamic',
#         cascade='all, delete-orphan'
#     )
# backend/models/user.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base # 引入刚才建的 Base

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_engine': 'InnoDB'
    }

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    # 关系：User -> ChatSession
    sessions = relationship(
        'ChatSession',
        backref='user',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )