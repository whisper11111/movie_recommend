# 电影表模型，对应数据库中的movie表
# models/movie.py
from . import db  # 导入models/__init__.py中的db对象

class Movie(db.Model):
    __tablename__ = "movie"
    
    id = db.Column(db.Integer, primary_key=True, comment="电影编号")
    name = db.Column(db.String(50), nullable=False, comment="电影名称")
    release_date = db.Column(db.Date, comment="发行日期")
    picture = db.Column(db.LargeBinary, comment="电影图片（暂不使用）")  # 已有字段，无需改
    director = db.Column(db.String(100), comment="导演")
    actors = db.Column(db.Text, comment="主要演员")
    language = db.Column(db.String(50), comment="语言类别")
    company = db.Column(db.String(50), comment="制片公司")
    style = db.Column(db.Text, comment="电影类别")
    duration = db.Column(db.Text, comment="电影时长")
    description = db.Column(db.Text, comment="电影介绍")

    # 新增：序列化方法（处理海报+兼容原有字段）
    def to_dict(self, with_picture=True, trunc_desc=True):
        """
        模型转字典
        :param with_picture: 是否返回picture字段（二进制转Base64）
        :param trunc_desc: 是否截取简介（前端列表用）
        :return: 格式化后的字典
        """
        # 基础字段
        data = {
            "id": self.id,
            "name": self.name,
            "release_date": self.release_date.strftime("%Y-%m-%d") if self.release_date else "",
            "director": self.director or "",
            "actors": self.actors or "",
            "language": self.language or "",
            "company": self.company or "",
            "style": self.style or "",
            "duration": self.duration or "",
            # 简介处理（保留你的截取逻辑）
            "description": (self.description[:100] + "...") if (trunc_desc and self.description and len(self.description) > 100) else (self.description or "")
        }
        
        # 海报处理：二进制转Base64（仅当需要时返回）
        if with_picture and self.picture:
            import base64
            data["picture"] = base64.b64encode(self.picture).decode("utf-8")
        else:
            data["picture"] = ""
        
        return data