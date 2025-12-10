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

# 1. 初始化Flask应用
app = Flask(__name__)
# 2. 加载配置（数据库连接等）
app.config.from_object(Config)
# 3. 初始化数据库（将db与app关联）
db.init_app(app)
# 4. 解决跨域问题（允许前端访问后端接口）
CORS(app, resources=r"/*")  # 允许所有路径的跨域请求

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

# ---------------------- 4. 启动后端服务 ----------------------
if __name__ == "__main__":
    # 启动服务：host=0.0.0.0（允许其他设备访问），port=5000（端口号），debug=True（调试模式）
    app.run(host="0.0.0.0", port=5000, debug=True)