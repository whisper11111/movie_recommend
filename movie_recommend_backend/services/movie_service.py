# 电影相关业务逻辑：获取电影列表、获取电影详情、获取热门电影
from models.movie import Movie
from models.rating import UserRating
from models import db
from sqlalchemy import func

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
        
        # 格式化电影数据（将数据库对象转为字典，方便前端使用）
        movie_list = []
        for movie in movies:
            # 计算电影的平均评分（用于显示）
            avg_score = db.session.query(func.avg(UserRating.score)).filter_by(mid=movie.id).scalar()
            avg_score = round(avg_score, 1) if avg_score else 0.0  # 无评分时显示0.0
            
            movie_list.append({
                "id": movie.id,
                "name": movie.name,
                "release_date": movie.release_date.strftime("%Y-%m-%d") if movie.release_date else "",
                "director": movie.director,
                "style": movie.style,
                "avg_score": avg_score,  # 平均评分
                "duration": movie.duration,
                "description": movie.description[:100] + "..." if len(movie.description) > 100 else movie.description  # 简介截取前100字
            })
        
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
        
        # 格式化电影详情
        movie_detail = {
            "id": movie.id,
            "name": movie.name,
            "release_date": movie.release_date.strftime("%Y-%m-%d") if movie.release_date else "",
            "director": movie.director,
            "actors": movie.actors.split(" ") if movie.actors else [],  # 演员转为列表
            "language": movie.language,
            "company": movie.company,
            "style": movie.style.split(",") if movie.style else [],  # 类型转为列表
            "duration": movie.duration,
            "description": movie.description,
            "avg_score": avg_score,
            "rating_count": rating_count
        }
        
        return {"code": 1, "msg": "获取电影详情成功！", "data": movie_detail}
    except Exception as e:
        return {"code": 0, "msg": f"获取失败：{str(e)}", "data": {}}

def get_hot_movies(db, limit=10):
    """
    获取热门电影（按评分次数排序，取前N部）
    :param db: 数据库对象
    :param limit: 取前多少部（默认10）
    :return: 热门电影列表
    """
    try:
        # 关联查询：按电影的评分次数排序
        hot_movie_ids = db.session.query(
            UserRating.mid, func.count(UserRating.id).label("rating_count")
        ).group_by(UserRating.mid).order_by(func.desc("rating_count")).limit(limit).all()
        
        # 提取电影ID列表
        movie_ids = [mid for mid, _ in hot_movie_ids]
        
        # 查询电影详情
        hot_movies = []
        for movie_id in movie_ids:
            movie = Movie.query.get(movie_id)
            if movie:
                avg_score = db.session.query(func.avg(UserRating.score)).filter_by(mid=movie_id).scalar()
                avg_score = round(avg_score, 1) if avg_score else 0.0
                hot_movies.append({
                    "id": movie.id,
                    "name": movie.name,
                    "director": movie.director,
                    "style": movie.style,
                    "avg_score": avg_score,
                    "description": movie.description[:80] + "..." if len(movie.description) > 80 else movie.description
                })
        
        return hot_movies
    except Exception as e:
        print(f"获取热门电影失败：{str(e)}")
        return []

def get_movie_details(db, movie_ids):
    """
    根据电影ID列表获取电影详情（用于推荐功能）
    :param db: 数据库对象
    :param movie_ids: 电影ID列表
    :return: 电影详情列表
    """
    try:
        movies = Movie.query.filter(Movie.id.in_(movie_ids)).all()
        movie_details = []
        for movie in movies:
            avg_score = db.session.query(func.avg(UserRating.score)).filter_by(mid=movie.id).scalar()
            avg_score = round(avg_score, 1) if avg_score else 0.0
            movie_details.append({
                "id": movie.id,
                "name": movie.name,
                "director": movie.director,
                "actors": movie.actors.split(" ") if movie.actors else [],
                "style": movie.style.split(",") if movie.style else [],
                "avg_score": avg_score,
                "duration": movie.duration,
                "description": movie.description
            })
        return movie_details
    except Exception as e:
        print(f"获取电影详情列表失败：{str(e)}")
        return []