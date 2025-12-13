# app/utils.py

from imports import datetime, timezone, HTTPException, Session



# -------------------------- 时间中间件 --------------------------
def get_current_utc_time():
    """获取当前UTC时间，兼容不同Python版本"""
    try:
        # Python 3.11+ 推荐方式
        return datetime.now(timezone.utc)
    except AttributeError:
        # 回退到旧方法（Python 3.9+ 应该不需要这个）
        return datetime.utcnow().replace(tzinfo=timezone.utc)
    


# -------------------------- category 中间件 --------------------------
def check_category_exists(db: Session, category_id: int):
    from .models import Category, Article
    """检查分类是否存在，不存在则抛出404异常"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail=f"Category {category_id} not found")
    return category

def check_category_name_unique(db: Session, name: str):
    """检查分类名称是否已存在，存在则抛出400异常"""
    from .models import Category, Article
    if db.query(Category).filter(Category.name == name).first():
        raise HTTPException(status_code=400, detail=f"Category '{name}' already exists")

def check_article_owner(db: Session, article_id: int, user_id: int):
    """检查文章是否存在且当前用户为作者"""
    from .models import Category, Article
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail=f"Article {article_id} not found")
    if article.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this article")
    return article