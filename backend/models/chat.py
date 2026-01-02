from datetime import datetime
from extensions import db

# --- 会话表 ---
class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    __table_args__ = (
        db.Index('idx_user_created', 'user_id', 'created_at'),
        {
            'mysql_charset': 'utf8mb4',
            'mysql_collate': 'utf8mb4_unicode_ci',
            'mysql_engine': 'InnoDB'
        }
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # 关系：Session -> ChatLog
    logs = db.relationship(
        'ChatLog',
        backref='session',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

# --- 消息表 ---
class ChatLog(db.Model):
    __tablename__ = 'chat_logs'
    __table_args__ = (
        db.Index('idx_session_created', 'session_id', 'created_at'),
        {
            'mysql_charset': 'utf8mb4',
            'mysql_collate': 'utf8mb4_unicode_ci',
            'mysql_engine': 'InnoDB'
        }
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    
    role = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)