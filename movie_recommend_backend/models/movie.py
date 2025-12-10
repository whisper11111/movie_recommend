# 电影表模型，对应数据库中的movie表
from . import db  # 导入models/__init__.py中的db对象

class Movie(db.Model):
    __tablename__ = "movie"
    
    id = db.Column(db.Integer, primary_key=True, comment="电影编号")
    name = db.Column(db.String(50), nullable=False, comment="电影名称")
    release_date = db.Column(db.Date, comment="发行日期")
    picture = db.Column(db.LargeBinary, comment="电影图片（暂不使用）")
    director = db.Column(db.String(100), comment="导演")
    actors = db.Column(db.Text, comment="主要演员")
    language = db.Column(db.String(50), comment="语言类别")
    company = db.Column(db.String(50), comment="制片公司")
    style = db.Column(db.Text, comment="电影类别")
    duration = db.Column(db.Text, comment="电影时长")
    description = db.Column(db.Text, comment="电影介绍")