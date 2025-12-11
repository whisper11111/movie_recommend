# 权限验证工具：检查用户是否为管理员
from functools import wraps
from flask import jsonify, request
from models.user import User

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 从请求头获取用户ID（假设前端登录后将user_id存入Authorization头）
        user_id = request.headers.get("Authorization")
        if not user_id:
            return jsonify({"code": 0, "msg": "请先登录", "data": {}})
        
        # 验证用户是否为管理员
        user = User.query.get(int(user_id))
        if not user or not user.is_admin:
            return jsonify({"code": 0, "msg": "权限不足：仅管理员可操作", "data": {}})
        
        return f(*args, **kwargs)
    return decorated_function

