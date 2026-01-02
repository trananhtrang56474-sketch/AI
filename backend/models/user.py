from datetime import datetime
from extensions import db

class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_engine': 'InnoDB'
    }

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # 关系：User -> ChatSession
    # 注意：这里用字符串 'ChatSession' 引用，避免直接 import 导致循环引用
    sessions = db.relationship(
        'ChatSession',
        backref='user',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )