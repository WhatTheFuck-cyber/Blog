# app/routers/interactions.py

from imports import APIRouter, Depends, HTTPException, Session
from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user



router = APIRouter()



# -------------------------- 点赞功能 --------------------------
@router.post("/likes", response_model=schemas.Like)
def like_article(
    like: schemas.LikeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """点赞文章"""
    try:
        # 检查文章是否存在
        article = db.query(models.Article).filter(models.Article.id == like.article_id).first()
        if not article:
            raise HTTPException(status_code=404, detail="文章不存在")
        
        # 检查是否已点赞
        existing_like = db.query(models.Like).filter(
            models.Like.user_id == current_user.id,
            models.Like.article_id == like.article_id
        ).first()
        if existing_like:
            raise HTTPException(status_code=400, detail="已点赞该文章")
        
        # 创建点赞记录
        db_like = models.Like(
            user_id=current_user.id,
            article_id=like.article_id
        )
        db.add(db_like)
        db.commit()
        db.refresh(db_like)
        return db_like
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))



@router.delete("/likes/{article_id}")
def unlike_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """取消点赞"""
    try:
        like = db.query(models.Like).filter(
            models.Like.user_id == current_user.id,
            models.Like.article_id == article_id
        ).first()
        if not like:
            raise HTTPException(status_code=404, detail="未点赞该文章")
        
        db.delete(like)
        db.commit()
        return {"message": "取消点赞成功"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))



# -------------------------- 收藏功能 --------------------------
@router.post("/collects", response_model=schemas.Collect)
def collect_article(
    collect: schemas.CollectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """收藏文章"""
    try:
        # 检查文章是否存在
        article = db.query(models.Article).filter(models.Article.id == collect.article_id).first()
        if not article:
            raise HTTPException(status_code=404, detail="文章不存在")
        
        # 检查是否已收藏
        existing_collect = db.query(models.Collect).filter(
            models.Collect.user_id == current_user.id,
            models.Collect.article_id == collect.article_id
        ).first()
        if existing_collect:
            raise HTTPException(status_code=400, detail="已收藏该文章")
        
        # 创建收藏记录
        db_collect = models.Collect(
            user_id=current_user.id,
            article_id=collect.article_id
        )
        db.add(db_collect)
        db.commit()
        db.refresh(db_collect)
        return db_collect
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))



@router.delete("/collects/{article_id}")
def uncollect_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """取消收藏"""
    try:
        collect = db.query(models.Collect).filter(
            models.Collect.user_id == current_user.id,
            models.Collect.article_id == article_id
        ).first()
        if not collect:
            raise HTTPException(status_code=404, detail="未收藏该文章")
        
        db.delete(collect)
        db.commit()
        return {"message": "取消收藏成功"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))



# -------------------------- 我的点赞/收藏列表 --------------------------
@router.get("/my/likes", response_model=list[schemas.ArticleMinimal])  # 改为ArticleMinimal列表
def get_my_liked_articles(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """获取当前用户点赞的文章（返回摘要信息）"""
    # 检查用户是否登录（避免未登录时current_user为None）
    if not current_user:
        raise HTTPException(status_code=401, detail="请先登录")
    
    try:
        # 关联查询：文章 + 作者信息（获取owner_name）
        liked_articles = db.query(
            models.Article,  # 文章表
            models.User.username.label("owner_name")  # 作者用户名（假设用户表用username存名字）
        ).join(
            models.Like,  # 关联点赞表
            models.Article.id == models.Like.article_id
        ).join(
            models.User,  # 关联用户表（获取作者信息）
            models.Article.owner_id == models.User.id  # 假设文章表用owner_id关联作者
        ).filter(
            models.Like.user_id == current_user.id  # 筛选当前用户的点赞
        ).all()
        
        # 转换为ArticleMinimal格式（提取字段）
        return [
            {
                "id": article.id,
                "title": article.title,
                "owner_id": article.owner_id,
                "owner_name": owner_name,  # 从关联查询中获取
                "created_at": article.created_at
            }
            for article, owner_name in liked_articles
        ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取点赞文章失败：{str(e)}")



@router.get("/my/collects", response_model=list[schemas.ArticleMinimal])  # 改为ArticleMinimal列表
def get_my_collected_articles(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """获取当前用户收藏的文章（返回摘要信息）"""
    # 检查用户是否登录
    if not current_user:
        raise HTTPException(status_code=401, detail="请先登录")
    
    try:
        # 关联查询：文章 + 作者信息
        collected_articles = db.query(
            models.Article,
            models.User.username.label("owner_name")  # 作者用户名
        ).join(
            models.Collect,  # 关联收藏表
            models.Article.id == models.Collect.article_id
        ).join(
            models.User,  # 关联用户表
            models.Article.owner_id == models.User.id
        ).filter(
            models.Collect.user_id == current_user.id  # 筛选当前用户的收藏
        ).all()
        
        # 转换为ArticleMinimal格式
        return [
            {
                "id": article.id,
                "title": article.title,
                "owner_id": article.owner_id,
                "owner_name": owner_name,
                "created_at": article.created_at
            }
            for article, owner_name in collected_articles
        ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取收藏文章失败：{str(e)}")