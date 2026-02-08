# backend/models/MoodDiary.py
from extensions import db
from datetime import datetime

class MoodDiary(db.Model):
    __tablename__ = 'mood_diary' # 👈 指定表名

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mood = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'mood': self.mood,
            'content': self.content,
            'created_at': self.created_at.isoformat()
        }