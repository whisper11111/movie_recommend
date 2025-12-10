# 用户评分表模型，对应数据库中的user_rating表
from . import db  # 导入models/__init__.py中的db对象

class UserRating(db.Model):
    __tablename__ = "user_rating"
    
    id = db.Column(db.Integer, primary_key=True, comment="评分编号")
    uid = db.Column(db.Integer, nullable=False, comment="用户编号")
    mid = db.Column(db.Integer, nullable=False, comment="电影编号")
    score = db.Column(db.Float, nullable=False, comment="评分值（1.0-5.0）")
    description = db.Column(db.Text, comment="用户评论")
    time = db.Column(db.DateTime, default=db.func.current_timestamp(), comment="评论时间")