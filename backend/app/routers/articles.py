# app/routers/articles.py

from imports import APIRouter, Depends, HTTPException, status, Session, func, Optional


from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user
from ..utils import check_category_exists, check_article_owner



# 创建文章相关的路由
router = APIRouter()


@router.post("", response_model=schemas.Article)
def create_article(article: schemas.ArticleCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """创建新文章（需要用户登录）"""
    
    try:
        # 使用当前登录用户的ID作为文章作者，而不是依赖客户端提供
        db_article = models.Article(
            title=article.title,
            content=article.content,
            owner_id=current_user.id,  # 从认证系统获取当前用户ID
            owner_name = current_user.username
        )
        
        # 添加到数据库并提交
        db.add(db_article)
        db.commit()
        db.refresh(db_article)  # 刷新获取数据库生成的ID等字段
        
        return db_article
    except Exception as e:
        db.rollback()  # 回滚事务
        raise HTTPException(status_code=400, detail=str(e))



@router.get("/{article_id}", response_model=schemas.ArticleWithStats)
def read_article(
    article_id: int, 
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user)  # 支持未登录用户
):
    """获取文章详情（含点赞/收藏统计，仅登录用户可见评论）"""
    # 1. 查询文章主数据
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 2. 计算点赞/收藏数
    like_count = db.query(func.count(models.Like.id)).filter(
        models.Like.article_id == article_id
    ).scalar() or 0
    
    collect_count = db.query(func.count(models.Collect.id)).filter(
        models.Collect.article_id == article_id
    ).scalar() or 0
    
    # 3. 初始化状态变量
    is_liked = False
    is_collected = False
    comments_response = None  # 未登录时返回None（符合Optional定义）
    
    # 4. 仅登录用户处理：互动状态 + 评论列表
    if current_user:
        # 4.1 检查当前用户点赞/收藏状态
        is_liked = db.query(models.Like).filter(
            models.Like.user_id == current_user.id,
            models.Like.article_id == article_id
        ).first() is not None
        
        is_collected = db.query(models.Collect).filter(
            models.Collect.user_id == current_user.id,
            models.Collect.article_id == article_id
        ).first() is not None

        # 4.2 查询文章评论（按创建时间倒序）
        comments = db.query(models.Comment).filter(
            models.Comment.article_id == article_id
        ).order_by(models.Comment.created_at.desc()).all()
        
        # 4.3 转换为CommentMinimal模型（推荐用from_orm，避免手动映射错误）
        # 核心：from_orm会自动匹配字段（id/content/user_name/user_id/article_id/parent_id/created_at）
        comments_response = [schemas.CommentMinimal.from_orm(comment) for comment in comments]
    
    # 5. 构建最终响应
    return {
        **article.__dict__,  # 原始文章字段（id/owner_id/owner_name/created_at/category_id等）
        "like_count": like_count,
        "collect_count": collect_count,
        "is_liked": is_liked,
        "is_collected": is_collected,
        "comments": comments_response  # 登录=评论列表，未登录=None
    }



@router.put("/{article_id}", response_model=schemas.Article)
def update_article(article_id: int, article: schemas.ArticleUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """更新文章内容（需要登录且只能更新自己的文章）"""
    
    try:
        # 查询指定ID的文章
        db_article = db.query(models.Article).filter(models.Article.id == article_id).first()
        
        # 如果文章不存在，返回404错误
        if db_article is None:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # 检查当前用户是否是文章的作者
        if db_article.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this article"
            )
        
        # 更新文章内容
        db_article.title = article.title
        db_article.content = article.content
        
        # 提交更改
        db.commit()
        db.refresh(db_article)
        
        return db_article
    except Exception as e:
        db.rollback()  # 回滚事务
        raise HTTPException(status_code=400, detail=f"更新文章失败：{str(e)}")



@router.delete("/{article_id}")
def delete_article(article_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """删除文章（需要登录且只能删除自己的文章）"""
    
    try:
        # 查询指定ID的文章
        db_article = db.query(models.Article).filter(models.Article.id == article_id).first()
        
        # 如果文章不存在，返回404错误
        if db_article is None:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # 检查当前用户是否是文章的作者
        if db_article.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this article"
            )
        
        # 删除文章（如果设置了级联删除，相关评论也会被自动删除）
        db.delete(db_article)
        db.commit()
        
        return {"message": "Article deleted successfully"}
    except Exception as e:
        db.rollback()  # 回滚事务
        raise HTTPException(status_code=400, detail=f"删除文章失败：{str(e)}")



# -------------------------- 为文章添加 / 删除分类 --------------------------
@router.put("/{article_id}/category/id/{category_id}", response_model=schemas.Article)
def set_article_category_by_id(
    article_id: int,
    category_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """为文章绑定分类（仅作者可操作）"""
    try:
        category = check_category_exists(db, category_id)  # 调用辅助函数
        article = check_article_owner(db, article_id, current_user.id)  # 调用辅助函数
        article.category_id = category_id
        db.commit()
        db.refresh(article)
        return article
    except Exception as e:
        db.rollback()  # 回滚事务
        raise HTTPException(status_code=400, detail=f"为文章绑定分类失败：{str(e)}")



@router.put("/{article_id}/category/name/{category_name}", response_model=schemas.Article)
def set_article_category_by_name(
    article_id: int,
    category_name: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """为文章绑定分类（仅作者可操作）"""
    try:
        category = db.query(models.Category).filter(models.Category.name == category_name).first()
        if not category:
            raise HTTPException(status_code=404, detail=f"分类 '{category_name}' 不存在")
        category_id = category.id
        category = check_category_exists(db, category_id)  # 调用辅助函数
        article = check_article_owner(db, article_id, current_user.id)  # 调用辅助函数
        article.category_id = category_id
        db.commit()
        db.refresh(article)
        return article
    except Exception as e:
        db.rollback()  # 回滚事务
        raise HTTPException(status_code=400, detail=f"为文章绑定分类失败：{str(e)}")



@router.delete("/{article_id}/category", response_model=schemas.Article)
def remove_article_category(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """移除文章的分类（仅作者可操作）"""
    try:
        article = check_article_owner(db, article_id, current_user.id)  # 调用辅助函数
        article.category_id = None
        db.commit()
        db.refresh(article)
        return article
    except Exception as e:
        db.rollback()  # 回滚事务
        raise HTTPException(status_code=400, detail=f"移除文章的分类失败：{str(e)}")