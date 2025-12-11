from models.movie import Movie
from models.rating import UserRating
from models import db
from sqlalchemy import func
import base64  # 新增：导入Base64编码模块

def get_movie_list(db, page=1, page_size=10):
    """
    获取电影列表（支持分页）
    :param db: 数据库对象
    :param page: 当前页码（默认1）
    :param page_size: 每页显示数量（默认10）
    :return: 电影列表和总数量
    """
    try:
        # 计算分页偏移量
        offset = (page - 1) * page_size
        
        # 查询电影列表（按发行日期倒序，最新的在前）
        movies = Movie.query.order_by(Movie.release_date.desc()).offset(offset).limit(page_size).all()
        
        # 查询电影总数量（用于分页）
        total = Movie.query.count()
        
        # 格式化电影数据（手动处理，确保海报Base64转换）
        movie_list = []
        for movie in movies:
            # 计算电影的平均评分
            avg_score = db.session.query(func.avg(UserRating.score)).filter_by(mid=movie.id).scalar()
            avg_score = round(avg_score, 1) if avg_score else 0.0  # 无评分时显示0.0
            
            # 处理海报：二进制→Base64字符串（兼容空值）
            picture_base64 = ""
            if movie.picture:
                if isinstance(movie.picture, bytes):
                    # 二进制海报转Base64
                    picture_base64 = base64.b64encode(movie.picture).decode("utf-8")
                elif isinstance(movie.picture, str):
                    # 已存储Base64字符串，直接使用
                    picture_base64 = movie.picture
            
            # 构造统一的返回格式
            movie_dict = {
                "id": movie.id,
                "name": movie.name,
                "director": movie.director,
                "actors": movie.actors,
                "language": movie.language,
                "company": movie.company,
                "style": movie.style,
                "release_date": movie.release_date.strftime("%Y-%m-%d") if movie.release_date else "",
                "duration": movie.duration,
                "description": movie.description[:80] + "..." if movie.description and len(movie.description) > 80 else movie.description or "",
                "picture": picture_base64,  # 确保返回Base64格式
                "avg_score": avg_score
            }
            movie_list.append(movie_dict)
        
        return {"code": 1, "msg": "获取电影列表成功！", "data": {"movie_list": movie_list, "total": total}}
    except Exception as e:
        return {"code": 0, "msg": f"获取失败：{str(e)}", "data": {"movie_list": [], "total": 0}}

def get_movie_detail(db, movie_id):
    """
    获取电影详情（根据电影ID）
    :param db: 数据库对象
    :param movie_id: 电影ID
    :return: 电影详情
    """
    try:
        # 根据ID查询电影
        movie = Movie.query.get(movie_id)
        if not movie:
            return {"code": 0, "msg": "未找到该电影！", "data": {}}
        
        # 计算平均评分和评分数量
        avg_score = db.session.query(func.avg(UserRating.score)).filter_by(mid=movie_id).scalar()
        avg_score = round(avg_score, 1) if avg_score else 0.0
        rating_count = db.session.query(func.count(UserRating.id)).filter_by(mid=movie_id).scalar() or 0
        
        # 处理海报：二进制→Base64字符串
        picture_base64 = ""
        if movie.picture:
            if isinstance(movie.picture, bytes):
                picture_base64 = base64.b64encode(movie.picture).decode("utf-8")
            elif isinstance(movie.picture, str):
                picture_base64 = movie.picture
        
        # 构造详情数据
        movie_detail = {
            "id": movie.id,
            "name": movie.name,
            "director": movie.director,
            "actors": movie.actors.split(" ") if movie.actors else [],
            "language": movie.language,
            "company": movie.company,
            "style": movie.style.split(",") if movie.style else [],
            "release_date": movie.release_date.strftime("%Y-%m-%d") if movie.release_date else "",
            "duration": movie.duration,
            "description": movie.description or "",
            "picture": picture_base64,  # 确保返回Base64格式
            "avg_score": avg_score,
            "rating_count": rating_count
        }
        
        return {"code": 1, "msg": "获取电影详情成功！", "data": movie_detail}
    except Exception as e:
        return {"code": 0, "msg": f"获取失败：{str(e)}", "data": {}}

def get_hot_movies(db, limit=10):
    """获取热门电影（补充海报字段）"""
    try:
        # 关联查询：按电影的评分次数排序
        hot_movie_ids = db.session.query(
            UserRating.mid, func.count(UserRating.id).label("rating_count")
        ).group_by(UserRating.mid).order_by(func.desc("rating_count")).limit(limit).all()
        
        # 提取电影ID列表
        movie_ids = [mid for mid, _ in hot_movie_ids]
        
        # 查询电影详情（带海报）
        hot_movies = []
        for movie_id in movie_ids:
            movie = Movie.query.get(movie_id)
            if movie:
                avg_score = db.session.query(func.avg(UserRating.score)).filter_by(mid=movie_id).scalar()
                avg_score = round(avg_score, 1) if avg_score else 0.0
                
                # 处理海报
                picture_base64 = ""
                if movie.picture:
                    if isinstance(movie.picture, bytes):
                        picture_base64 = base64.b64encode(movie.picture).decode("utf-8")
                    elif isinstance(movie.picture, str):
                        picture_base64 = movie.picture
                
                hot_movies.append({
                    "id": movie.id,
                    "name": movie.name,
                    "director": movie.director,
                    "style": movie.style,
                    "picture": picture_base64,  # 新增：返回海报
                    "avg_score": avg_score,
                    "description": movie.description[:80] + "..." if len(movie.description) > 80 else movie.description
                })
        
        return hot_movies
    except Exception as e:
        print(f"获取热门电影失败：{str(e)}")
        return []

def get_movie_details(db, movie_ids):
    """获取电影详情列表（补充海报字段）"""
    try:
        movies = Movie.query.filter(Movie.id.in_(movie_ids)).all()
        movie_details = []
        for movie in movies:
            avg_score = db.session.query(func.avg(UserRating.score)).filter_by(mid=movie.id).scalar()
            avg_score = round(avg_score, 1) if avg_score else 0.0
            
            # 处理海报
            picture_base64 = ""
            if movie.picture:
                if isinstance(movie.picture, bytes):
                    picture_base64 = base64.b64encode(movie.picture).decode("utf-8")
                elif isinstance(movie.picture, str):
                    picture_base64 = movie.picture
            
            movie_details.append({
                "id": movie.id,
                "name": movie.name,
                "director": movie.director,
                "actors": movie.actors.split(" ") if movie.actors else [],
                "style": movie.style.split(",") if movie.style else [],
                "picture": picture_base64,  # 新增：返回海报
                "avg_score": avg_score,
                "duration": movie.duration,
                "description": movie.description
            })
        return movie_details
    except Exception as e:
        print(f"获取电影详情列表失败：{str(e)}")
        return []

def add_movie(db, movie_data):
    """
    新增电影（优化空值处理+海报二进制存储）
    :param db: 数据库对象
    :param movie_data: 前端传的电影数据（dict）
    :return: 操作结果
    """
    try:
        # 校验必填字段（与前端表单规则一致）
        required_fields = ['name', 'director', 'style']
        for field in required_fields:
            field_value = movie_data.get(field, "").strip()
            if not field_value:
                return {"code": 0, "msg": f"字段 {field} 不能为空！", "data": {}}
        
        # 构建Movie对象（优化空值处理，海报为二进制）
        new_movie = Movie(
            name=movie_data.get('name', "").strip(),
            director=movie_data.get('director', "").strip(),
            actors=movie_data.get('actors', "").strip(),
            language=movie_data.get('language', "").strip(),
            company=movie_data.get('company', "").strip(),
            style=movie_data.get('style', "").strip(),
            release_date=movie_data.get('release_date'),  # 日期格式已由前端处理为YYYY-MM-DD
            duration=movie_data.get('duration', "").strip(),
            description=movie_data.get('description', "").strip(),
            picture=movie_data.get('picture', b"")  # 接收二进制海报数据
        )
        
        # 写入数据库
        db.session.add(new_movie)
        db.session.commit()
        
        return {"code": 1, "msg": "电影添加成功！", "data": {"movie_id": new_movie.id}}
    except Exception as e:
        db.session.rollback()  # 异常回滚
        return {"code": 0, "msg": f"添加电影失败：{str(e)}", "data": {}}

def update_movie(db, movie_id, movie_data):
    """
    编辑电影（优化空值处理+海报二进制更新）
    :param db: 数据库对象
    :param movie_id: 电影ID
    :param movie_data: 前端传的更新数据（dict）
    :return: 操作结果
    """
    try:
        # 校验电影是否存在
        movie = Movie.query.get(movie_id)
        if not movie:
            return {"code": 0, "msg": "未找到该电影！", "data": {}}
        
        # 校验必填字段（优化空值判断）
        required_fields = ['name', 'director', 'style']
        for field in required_fields:
            field_value = movie_data.get(field, "").strip()
            if not field_value:
                return {"code": 0, "msg": f"字段 {field} 不能为空！", "data": {}}
        
        # 更新字段（优化空值处理，海报为二进制）
        movie.name = movie_data.get('name', "").strip()
        movie.director = movie_data.get('director', "").strip()
        movie.actors = movie_data.get('actors', "").strip()
        movie.language = movie_data.get('language', "").strip()
        movie.company = movie_data.get('company', "").strip()
        movie.style = movie_data.get('style', "").strip()
        movie.release_date = movie_data.get('release_date')
        movie.duration = movie_data.get('duration', "").strip()
        movie.description = movie_data.get('description', "").strip()
        
        # 仅当传了新海报且非空时更新（二进制）
        new_picture = movie_data.get('picture')
        if new_picture is not None:  # 允许空二进制（清空海报）
            movie.picture = new_picture
        
        # 提交更新
        db.session.commit()
        
        return {"code": 1, "msg": "电影更新成功！", "data": {}}
    except Exception as e:
        db.session.rollback()  # 异常回滚
        return {"code": 0, "msg": f"更新电影失败：{str(e)}", "data": {}}