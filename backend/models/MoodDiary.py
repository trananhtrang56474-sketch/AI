
# backend/models/MoodDiary.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime
from database import Base

class MoodDiary(Base):
    __tablename__ = 'mood_diary' 

   
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    mood = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'mood': self.mood,
            'content': self.content,
            # 做个安全保护，防止 created_at 为空时报错
            'created_at': self.created_at.isoformat() if self.created_at else None
        }