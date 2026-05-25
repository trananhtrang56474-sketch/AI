# backend/models/chat.py
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Index, Float # 确保导入了 Float
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class ChatSession(Base):
    __tablename__ = 'chat_sessions'
    __table_args__ = (
        Index('idx_user_created', 'user_id', 'created_at'),
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'mysql_engine': 'InnoDB'}
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    #  这里的 relationship 会寻找 ChatLog 里的 ForeignKey
    logs = relationship('ChatLog', backref='session', lazy='dynamic', cascade='all, delete-orphan')

class ChatLog(Base):
    __tablename__ = 'chat_logs'
    __table_args__ = (
        Index('idx_session_created', 'session_id', 'created_at'),
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'mysql_engine': 'InnoDB'}
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    #  关键点：这一行必须包含 ForeignKey('chat_sessions.id') ✨✨✨
    session_id = Column(Integer, ForeignKey('chat_sessions.id'), nullable=False)
    
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    
    # 我们刚刚修改的浮点数字段
    image_url = Column(Text, nullable=True) 
    emotion_tag = Column(String(50), nullable=True)
    emotion_score = Column(Integer, default=60)
    
    #  确认这里是 Float
    valence = Column(Float, nullable=True, default=5.0)  
    arousal = Column(Float, nullable=True, default=3.0)  
    
    created_at = Column(DateTime, default=datetime.now)