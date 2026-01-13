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
    
    # ✨ 建议改为 256，防止某些哈希算法生成的字符串过长
    password_hash = db.Column(db.String(256), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.now)

    # 关系：User -> ChatSession
    sessions = db.relationship(
        'ChatSession',
        backref='user',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )