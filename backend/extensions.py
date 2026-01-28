# backend/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail  # ✨ 1. 必须引入这个

db = SQLAlchemy()
mail = Mail()  # ✨ 2. 必须实例化这个，否则 routes.py 里的 mail 是空的