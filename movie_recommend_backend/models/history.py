# 用户历史记录表模型，对应数据库中的user_history表
from . import db  # 导入models/__init__.py中的db对象

class UserHistory(db.Model):
    __tablename__ = "user_history"
    
    id = db.Column(db.Integer, primary_key=True, comment="记录编号")
    uid = db.Column(db.Integer, nullable=False, comment="用户编号")
    mid = db.Column(db.Integer, nullable=False, comment="电影编号")
    time = db.Column(db.DateTime, default=db.func.current_timestamp(), comment="浏览时间")