# 用户相关业务逻辑：注册、登录、添加浏览记录、添加评分
from models.user import User
from models.history import UserHistory
from models.rating import UserRating
from models import db
from sqlalchemy.exc import IntegrityError  # 用于捕获数据库唯一约束错误

def register(db, data):
    """
    用户注册功能
    :param db: 数据库对象
    :param data: 前端传入的注册数据（包含name, password, email, sex）
    :return: 注册结果（成功/失败信息）
    """
    try:
        # 1. 提取前端传入的数据
        username = data.get("name")
        password = data.get("password")
        email = data.get("email")
        sex = data.get("sex")  # 1=男，0=女，可能为None
        
        # 2. 验证必要数据是否存在
        if not all([username, password, email]):
            return {"code": 0, "msg": "用户名、密码、邮箱不能为空！", "data": {}}
        
        # 3. 密码加密（调用User类的静态方法）
        encrypted_password = User.encrypt_password(password)
        
        # 4. 创建用户对象并保存到数据库
        new_user = User(
            name=username,
            password=encrypted_password,
            email=email,
            sex=sex
        )
        db.session.add(new_user)
        db.session.commit()  # 提交事务
        
        # 5. 返回成功结果
        return {"code": 1, "msg": "注册成功！", "data": {"user_id": new_user.id, "username": new_user.name}}
    
    except IntegrityError:
        # 捕获“邮箱已存在”的错误（因为数据库中email字段设为unique）
        db.session.rollback()  # 回滚事务
        return {"code": 0, "msg": "该邮箱已被注册，请更换邮箱！", "data": {}}
    except Exception as e:
        # 捕获其他未知错误
        db.session.rollback()
        return {"code": 0, "msg": f"注册失败：{str(e)}", "data": {}}

def login(db, data):
    """
    用户登录功能
    :param db: 数据库对象
    :param data: 前端传入的登录数据（包含email, password）
    :return: 登录结果（成功/失败信息）
    """
    try:
        # 1. 提取前端传入的数据
        email = data.get("email")
        password = data.get("password")
        
        # 2. 验证必要数据是否存在
        if not all([email, password]):
            return {"code": 0, "msg": "邮箱和密码不能为空！", "data": {}}
        
        # 3. 密码加密（与注册时的加密方式一致）
        encrypted_password = User.encrypt_password(password)
        
        # 4. 查询数据库，验证邮箱和密码是否匹配
        user = User.query.filter_by(email=email, password=encrypted_password).first()
        if not user:
            return {"code": 0, "msg": "邮箱或密码错误！", "data": {}}
        
        # 5. 返回成功结果（包含用户ID和用户名，供前端存储）
        return {"code": 1, "msg": "登录成功！", "data": {"user_id": user.id, "username": user.name}}
    
    except Exception as e:
        return {"code": 0, "msg": f"登录失败：{str(e)}", "data": {}}

def add_history(db, data):
    """
    添加用户浏览记录
    :param db: 数据库对象
    :param data: 前端传入的数据（包含uid, mid）
    :return: 添加结果
    """
    try:
        uid = data.get("uid")
        mid = data.get("mid")
        
        if not all([uid, mid]):
            return {"code": 0, "msg": "用户ID和电影ID不能为空！", "data": {}}
        
        # 创建历史记录对象
        new_history = UserHistory(uid=uid, mid=mid)
        db.session.add(new_history)
        db.session.commit()
        
        return {"code": 1, "msg": "浏览记录添加成功！", "data": {}}
    except Exception as e:
        db.session.rollback()
        return {"code": 0, "msg": f"添加失败：{str(e)}", "data": {}}

def add_rating(db, data):
    """
    添加用户评分
    :param db: 数据库对象
    :param data: 前端传入的数据（包含uid, mid, score, description）
    :return: 添加结果
    """
    try:
        uid = data.get("uid")
        mid = data.get("mid")
        score = data.get("score")
        description = data.get("description", "")  # 评论可空，默认空字符串
        
        # 验证必要数据
        if not all([uid, mid, score]):
            return {"code": 0, "msg": "用户ID、电影ID、评分不能为空！", "data": {}}
        # 验证评分范围（1.0-5.0）
        if not (1.0 <= float(score) <= 5.0):
            return {"code": 0, "msg": "评分必须在1.0-5.0之间！", "data": {}}
        
        # 检查是否已评分（避免重复评分，数据库也有unique约束）
        existing_rating = UserRating.query.filter_by(uid=uid, mid=mid).first()
        if existing_rating:
            return {"code": 0, "msg": "你已对该电影评过分，不可重复评分！", "data": {}}
        
        # 创建评分对象
        new_rating = UserRating(
            uid=uid,
            mid=mid,
            score=float(score),
            description=description
        )
        db.session.add(new_rating)
        db.session.commit()
        
        return {"code": 1, "msg": "评分成功！", "data": {}}
    except IntegrityError:
        db.session.rollback()
        return {"code": 0, "msg": "已对该电影评分，不可重复！", "data": {}}
    except Exception as e:
        db.session.rollback()
        return {"code": 0, "msg": f"评分失败：{str(e)}", "data": {}}