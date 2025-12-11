# 初始化数据库，供其他模型文件使用
from flask_sqlalchemy import SQLAlchemy

# 创建数据库对象，后续所有模型都基于这个对象
db = SQLAlchemy()