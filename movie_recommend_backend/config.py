# 后端配置文件，主要配置数据库连接信息
import os

class Config:
    # 数据库连接地址：格式为 "mysql+mysqlconnector://用户名:密码@localhost:端口号/数据库名"
    # 注意：这里的密码要改成你安装MySQL时设置的密码（如123456）
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://root:001128@localhost:3306/movie_recommend"
    # 关闭SQLAlchemy的修改跟踪（避免警告）
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 生成随机密钥（用于Flask会话管理）
    SECRET_KEY = os.urandom(24)