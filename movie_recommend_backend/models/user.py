# 用户表模型，对应数据库中的user表
from . import db  # 导入models/__init__.py中的db对象
import hashlib  # 用于密码MD5加密

class User(db.Model):
    # 指定对应的数据表名称
    __tablename__ = "user"
    
    # 定义表中的字段，与数据库表结构一致
    id = db.Column(db.Integer, primary_key=True, comment="用户编号")
    name = db.Column(db.String(50), nullable=False, comment="用户名")
    password = db.Column(db.String(100), nullable=False, comment="登录密码（MD5加密）")
    email = db.Column(db.String(100), unique=True, nullable=False, comment="用户邮箱")
    sex = db.Column(db.Boolean, comment="性别（1=男，0=女）")
    create_time = db.Column(db.DateTime, default=db.func.current_timestamp(), comment="创建时间")
    is_admin = db.Column(db.Boolean, default=False, comment="是否为管理员（默认普通用户）")  # 新增字段

    # 静态方法：密码加密（将明文密码转为MD5密文）
    @staticmethod
    def encrypt_password(password):
        md5 = hashlib.md5()  # 创建MD5对象
        md5.update(password.encode("utf-8"))  # 将明文密码转为字节流并更新到MD5对象
        return md5.hexdigest()  # 返回MD5加密后的字符串
    

