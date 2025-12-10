# 协同过滤推荐算法核心逻辑
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity  # 余弦相似度计算
from models.rating import UserRating
from .movie_service import get_hot_movies, get_movie_details

def get_recommend_movies(db, user_id):
    """
    基于用户的协同过滤推荐算法（核心函数）
    步骤：1. 构建用户-电影评分矩阵 → 2. 计算用户相似度 → 3. 找到最近邻居 → 4. 生成推荐
    :param db: 数据库对象
    :param user_id: 目标用户ID（给谁推荐）
    :return: 推荐电影列表
    """
    try:
        # 1. 读取数据库中的评分数据
        ratings = db.session.query(
            UserRating.uid,  # 用户ID
            UserRating.mid,  # 电影ID
            UserRating.score  # 评分
        ).all()
        
        # 如果没有评分数据，直接返回热门电影
        if not ratings:
            return {"code": 0, "msg": "暂无评分数据，为你推荐热门电影", "data": get_hot_movies(db)}
        
        # 2. 构建用户-电影评分矩阵（关键步骤）
        # 将评分数据转为DataFrame（类似Excel表格）
        rating_df = pd.DataFrame(ratings, columns=["uid", "mid", "score"])
        # 构建矩阵：行=用户ID，列=电影ID，值=评分（无评分的位置填0）
        user_movie_matrix = rating_df.pivot_table(
            index="uid",  # 行索引：用户ID
            columns="mid",  # 列索引：电影ID
            values="score",  # 单元格值：评分
            fill_value=0  # 无评分的位置填0
        )
        
        # 3. 计算用户相似度（使用余弦相似度）
        # 余弦相似度：值越接近1，两个用户兴趣越相似；越接近0，兴趣越不相似
        user_similarity = cosine_similarity(user_movie_matrix)
        # 将相似度矩阵转为DataFrame，方便查询
        user_similarity_df = pd.DataFrame(
            user_similarity,
            index=user_movie_matrix.index,  # 行=用户ID
            columns=user_movie_matrix.index  # 列=用户ID
        )
        
        # 4. 检查目标用户是否有评分记录
        if user_id not in user_similarity_df.index:
            # 目标用户无评分，返回热门电影
            return {"code": 0, "msg": "你暂无评分记录，为你推荐热门电影", "data": get_hot_movies(db)}
        
        # 5. 找到目标用户的最近邻居（取相似度最高的前5个用户，排除自己）
        # 对目标用户的相似度排序（从高到低）
        target_user_similarity = user_similarity_df[user_id].sort_values(ascending=False)
        # 取前5个邻居（iloc[1:6]：排除第一个自己）
        nearest_neighbors = target_user_similarity.iloc[1:6].index
        
        # 6. 生成推荐电影：邻居喜欢且目标用户未看过的电影
        # 第一步：获取目标用户已经评分过的电影（即已经看过的）
        target_user_rated_movies = user_movie_matrix.loc[user_id][user_movie_matrix.loc[user_id] > 0].index
        
        # 第二步：收集邻居喜欢的电影（邻居评分≥3.5的电影，认为是喜欢的）
        recommend_movie_ids = []
        for neighbor in nearest_neighbors:
            # 获取邻居评分≥3.5的电影ID
            neighbor_liked_movies = user_movie_matrix.loc[neighbor][user_movie_matrix.loc[neighbor] >= 3.5].index
            # 筛选出目标用户未看过的电影
            unrated_movies = set(neighbor_liked_movies) - set(target_user_rated_movies)
            # 添加到推荐列表
            recommend_movie_ids.extend(unrated_movies)
        
        # 7. 去重并限制推荐数量（最多推荐10部）
        recommend_movie_ids = list(set(recommend_movie_ids))[:10]  # 去重，取前10部
        
        # 8. 获取推荐电影的详情
        recommend_movies = get_movie_details(db, recommend_movie_ids)
        
        # 9. 返回推荐结果
        return {"code": 1, "msg": "为你推荐以下电影", "data": recommend_movies}
    
    except Exception as e:
        # 捕获异常，返回热门电影
        print(f"推荐算法执行失败：{str(e)}")
        return {"code": 0, "msg": "推荐服务暂时异常，为你推荐热门电影", "data": get_hot_movies(db)}