# app/routers/home.py

from imports import APIRouter, Depends, desc, Session, HTTPException, func
from .. import models
from ..database import get_db
from ..schemas import HomeResponse



router = APIRouter()



@router.get("", response_model=HomeResponse)
def get_homepage(db: Session = Depends(get_db), latest_limit: int = 10):
    """获取博客主页数据（包含文章点赞和收藏数）"""
    try:
        # 获取所有分类
        categories = db.query(models.Category).all()
        
        # 1. 查询最新文章
        latest_articles = db.query(models.Article)\
            .order_by(models.Article.created_at.desc())\
            .limit(latest_limit)\
            .all()
        
        # 提取文章ID列表
        article_ids = [article.id for article in latest_articles]
        
        if not article_ids:
            # 没有文章时直接返回
            return {
                "categories": categories,
                "latest_articles": []
            }
        
        # 2. 统计每篇文章的点赞数
        like_counts = db.query(
            models.Like.article_id,
            func.count(models.Like.id).label('count')
        ).filter(
            models.Like.article_id.in_(article_ids)
        ).group_by(
            models.Like.article_id
        ).all()
        
        # 转换为字典便于查找
        like_count_dict = {item.article_id: item.count for item in like_counts}
        
        # 3. 统计每篇文章的收藏数
        collect_counts = db.query(
            models.Collect.article_id,
            func.count(models.Collect.id).label('count')
        ).filter(
            models.Collect.article_id.in_(article_ids)
        ).group_by(
            models.Collect.article_id
        ).all()
        
        # 转换为字典便于查找
        collect_count_dict = {item.article_id: item.count for item in collect_counts}
        
        # 4. 为每篇文章添加点赞数和收藏数字段
        for article in latest_articles:
            # 动态添加属性
            article.like_count = like_count_dict.get(article.id, 0)
            article.collect_count = collect_count_dict.get(article.id, 0)
        
        return {
            "categories": categories,
            "latest_articles": latest_articles
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取主页数据失败: {str(e)}")