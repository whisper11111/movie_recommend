# 后端主程序入口，启动后端服务，定义接口
from flask import Flask, request, jsonify
from flask_cors import CORS  # 解决跨域问题（前端和后端端口不同导致的访问限制）
from config import Config  # 导入配置文件
from models import db  # 导入数据库对象
from models.user import User
from models.movie import Movie
from models.history import UserHistory
from models.rating import UserRating
from services import user_service, movie_service, recommend_service
from utils.auth import admin_required

import traceback  # 新增：打印详细错误日志
import base64  # 重新添加：用于Base64解码

# 1. 初始化Flask应用
app = Flask(__name__)
# 2. 加载配置（数据库连接等）
app.config.from_object(Config)
# 3. 初始化数据库（将db与app关联）
db.init_app(app)
# 4. 解决跨域问题（允许前端访问后端接口）
# 关键修改1：精细化跨域配置，适配前端5173端口+管理员接口权限
CORS(app, resources={
    r"/api/*": {
        "origins": "http://localhost:5173",  # 仅允许前端5173端口访问
        "methods": ["GET", "POST", "PUT", "DELETE"],  # 支持前端所有请求方式
        "allow_headers": ["Authorization", "Content-Type"],  # 允许前端传的请求头
        "supports_credentials": True  # 允许携带凭证（如token）
    }
})

# 5. 创建数据库表（首次启动时执行，确保表存在）
with app.app_context():
    db.create_all()  # 如果表不存在，自动创建（已通过SQL脚本创建，这里是双重保障）

# ---------------------- 1. 用户相关接口 ----------------------
# 接口1：用户注册（前端通过POST请求调用）
@app.route("/api/user/register", methods=["POST"])
def api_user_register():
    # 获取前端传入的JSON数据
    data = request.get_json()
    # 调用user_service中的register函数处理业务
    result = user_service.register(db, data)
    # 返回结果给前端
    return jsonify(result)

# 接口2：用户登录（前端通过POST请求调用）
@app.route("/api/user/login", methods=["POST"])
def api_user_login():
    data = request.get_json()
    result = user_service.login(db, data)
    return jsonify(result)

# 接口3：添加浏览记录（用户看电影后调用）
@app.route("/api/user/history/add", methods=["POST"])
def api_add_history():
    data = request.get_json()
    result = user_service.add_history(db, data)
    return jsonify(result)

# 接口4：添加评分（用户评分电影后调用）
@app.route("/api/user/rating/add", methods=["POST"])
def api_add_rating():
    data = request.get_json()
    result = user_service.add_rating(db, data)
    return jsonify(result)

# 【新增】接口：验证用户是否为管理员（给前端路由守卫用）
@app.route("/api/user/is-admin", methods=["GET"])
def api_check_admin():
    try:
        # 获取前端传入的用户ID参数
        user_id = request.args.get("uid")
        if not user_id:
            return jsonify({"code": 0, "msg": "缺少用户ID", "data": {}})
        
        # 查询用户信息
        user = User.query.get(int(user_id))
        if not user:
            return jsonify({"code": 0, "msg": "用户不存在", "data": {}})
        
        # 返回是否为管理员的结果
        return jsonify({
            "code": 1,
            "msg": "验证管理员权限成功",
            "data": {"is_admin": user.is_admin}
        })
    except Exception as e:
        # 捕获异常并返回错误信息
        return jsonify({"code": 0, "msg": f"验证失败：{str(e)}", "data": {}})

# ---------------------- 2. 电影相关接口 ----------------------
# 接口5：获取电影列表（支持分页）
@app.route("/api/movie/list", methods=["GET"])
def api_get_movie_list():
    # 获取前端传入的分页参数（page=当前页，page_size=每页数量）
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 10, type=int)
    result = movie_service.get_movie_list(db, page, page_size)
    return jsonify(result)

# 接口6：获取电影详情（根据电影ID）
@app.route("/api/movie/detail/<int:movie_id>", methods=["GET"])
def api_get_movie_detail(movie_id):
    result = movie_service.get_movie_detail(db, movie_id)
    return jsonify(result)

# 接口7：获取热门电影
@app.route("/api/movie/hot", methods=["GET"])
def api_get_hot_movies():
    limit = request.args.get("limit", 10, type=int)
    hot_movies = movie_service.get_hot_movies(db, limit)
    return jsonify({"code": 1, "msg": "获取热门电影成功", "data": hot_movies})

# ---------------------- 3. 推荐相关接口 ----------------------
# 接口8：获取个性化推荐（根据用户ID）
@app.route("/api/recommend/<int:user_id>", methods=["GET"])
def api_get_recommend(user_id):
    result = recommend_service.get_recommend_movies(db, user_id)
    return jsonify(result)

# ---------------------- 4. 管理员接口 ----------------------
# 接口9：获取所有用户信息（管理员）
@app.route("/api/admin/users", methods=["GET"])
@admin_required
def api_get_all_users():
    try:
        users = User.query.all()
        user_list = [{
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "sex": "男" if user.sex else "女" if user.sex is not None else "未设置",
            "create_time": user.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "is_admin": user.is_admin
        } for user in users]
        return jsonify({"code": 1, "msg": "获取用户列表成功", "data": user_list})
    except Exception as e:
        return jsonify({"code": 0, "msg": f"获取失败：{str(e)}", "data": []})

# 接口10：获取用户行为记录（浏览+评分）
@app.route("/api/admin/user/behavior/<int:user_id>", methods=["GET"])
@admin_required
def api_get_user_behavior(user_id):
    try:
        # 浏览记录
        histories = UserHistory.query.filter_by(uid=user_id).order_by(UserHistory.time.desc()).all()
        history_list = [{
            "mid": h.mid,
            "movie_name": Movie.query.get(h.mid).name if Movie.query.get(h.mid) else "未知电影",
            "time": h.time.strftime("%Y-%m-%d %H:%M:%S"),
            "type": "浏览"
        } for h in histories]
        
        # 评分记录
        ratings = UserRating.query.filter_by(uid=user_id).order_by(UserRating.time.desc()).all()
        rating_list = [{
            "mid": r.mid,
            "movie_name": Movie.query.get(r.mid).name if Movie.query.get(r.mid) else "未知电影",
            "score": r.score,
            "time": r.time.strftime("%Y-%m-%d %H:%M:%S"),
            "type": "评分"
        } for r in ratings]
        
        # 合并并按时间排序
        behavior_list = sorted(history_list + rating_list, key=lambda x: x["time"], reverse=True)
        return jsonify({"code": 1, "msg": "获取行为记录成功", "data": behavior_list})
    except Exception as e:
        return jsonify({"code": 0, "msg": f"获取失败：{str(e)}", "data": []})

# 关键修改2：添加电影接口（处理Base64转二进制）
@app.route("/api/admin/movie/add", methods=["POST"])
@admin_required
def api_add_movie():
    try:
        # 1. 校验请求数据
        data = request.get_json()
        if not data:
            return jsonify({"code": 0, "msg": "请求数据不能为空", "data": {}})
        
        # 2. 处理海报：Base64字符串转二进制
        picture_data = b""
        if data.get("picture") and data.get("picture").strip():
            try:
                picture_data = base64.b64decode(data.get("picture").strip())
            except Exception as e:
                return jsonify({"code": 0, "msg": f"海报Base64解码失败：{str(e)}", "data": {}})
        
        # 3. 替换picture字段为二进制数据
        data["picture"] = picture_data
        
        # 4. 调用movie_service的add_movie函数
        result = movie_service.add_movie(db, data)
        
        return jsonify(result)
    except Exception as e:
        # 打印详细错误日志
        print(f"添加电影异常：{traceback.format_exc()}")
        return jsonify({"code": 0, "msg": f"添加失败：{str(e)}", "data": {}})

# 关键修改3：编辑电影接口（处理Base64转二进制）
@app.route("/api/admin/movie/update/<int:movie_id>", methods=["PUT"])
@admin_required
def api_update_movie(movie_id):
    try:
        # 1. 获取并校验请求数据
        data = request.get_json()
        if not data:
            return jsonify({"code": 0, "msg": "请求数据不能为空", "data": {}})
        
        # 2. 处理海报：Base64字符串转二进制
        if "picture" in data and data.get("picture") and data.get("picture").strip():
            try:
                data["picture"] = base64.b64decode(data.get("picture").strip())
            except Exception as e:
                return jsonify({"code": 0, "msg": f"海报Base64解码失败：{str(e)}", "data": {}})
        elif "picture" in data:
            data["picture"] = b""
        
        # 3. 调用movie_service的update_movie函数
        result = movie_service.update_movie(db, movie_id, data)
        
        return jsonify(result)
    except Exception as e:
        # 打印详细错误日志
        print(f"更新电影异常：{traceback.format_exc()}")
        return jsonify({"code": 0, "msg": f"更新失败：{str(e)}", "data": {}})

# ---------------------- 启动后端服务 ----------------------
if __name__ == "__main__":
    # 启动服务：host=0.0.0.0（允许其他设备访问），port=5000（端口号），debug=True（调试模式）
    app.run(host="0.0.0.0", port=5000, debug=True)