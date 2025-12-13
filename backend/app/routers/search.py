# app/routers/search.py

from imports import APIRouter, Depends, HTTPException, Session
from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user



router = APIRouter()



# -------------------------- 作者搜索接口 --------------------------
@router.get("/authors/id/{author_id}", response_model=schemas.UserSearch)
def search_author_by_id(
    author_id: int, 
    db: Session = Depends(get_db),
):
    """通过作者ID搜索用户"""
    try:
        user = db.query(models.User).filter(
            models.User.id == author_id,
            models.User.is_active == True
        ).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User with ID {author_id} not found")
        return user
    except Exception as e:
        raise 


@router.get("/authors/email/{email}", response_model=schemas.UserSearch)
def search_author_by_email(
    email: str, 
    db: Session = Depends(get_db),
):
    """通过作者邮箱搜索用户"""
    try:
        user = db.query(models.User).filter(
            models.User.email == email,
            models.User.is_active == True
        ).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User with email {email} not found")
        return user
    except Exception as e:
        raise 


@router.get("/authors/name/{username}", response_model=list[schemas.UserSearch])
def search_author_by_name(
    username: str, 
    db: Session = Depends(get_db),
):
    """通过作者名字搜索用户（支持模糊搜索）"""
    try:
        users = db.query(models.User).filter(
            models.User.username.contains(username),
            models.User.is_active == True
        ).all()
        if not users:
            raise HTTPException(status_code=404, detail=f"No users found with name containing '{username}'")
        return users
    except Exception as e:
        raise 



# -------------------------- 文章搜索接口 --------------------------
@router.get("/articles/id/{article_id}", response_model=schemas.Article)
def search_article_by_id(article_id: int, db: Session = Depends(get_db)):
    """通过文章ID搜索文章（无需登录）"""
    try:
        article = db.query(models.Article).filter(models.Article.id == article_id).first()
        if not article:
            raise HTTPException(status_code=404, detail=f"Article with ID {article_id} not found")
        return article
    except Exception as e:
        raise 


# 在正式发布时，请慎用模糊搜索，因为使用简单的模糊搜索可能会影响性能
@router.get("/articles/author/{author_name}", response_model=list[schemas.Article])
def search_articles_by_author(author_name: str, db: Session = Depends(get_db)):
    """通过作者名字搜索文章（无需登录，支持模糊搜索）"""
    try:
        articles = db.query(models.Article).filter(
            models.Article.owner_name.contains(author_name)
        ).all()
        if not articles:
            raise HTTPException(status_code=404, detail=f"No articles found by author '{author_name}'")
        return articles
    except Exception as e:
        raise 


# 在正式发布时，请慎用模糊搜索，因为使用简单的模糊搜索可能会影响性能
@router.get("/articles/title/{title}", response_model=list[schemas.Article])
def search_articles_by_title(title: str, db: Session = Depends(get_db)):
    """通过文章标题搜索文章（无需登录，支持模糊搜索）"""
    try:
        articles = db.query(models.Article).filter(
            models.Article.title.contains(title)
        ).all()
        if not articles:
            raise HTTPException(status_code=404, detail=f"No articles found with title containing '{title}'")
        return articles
    except Exception as e:
        raise 


# 在正式发布时，请慎用模糊搜索，因为使用简单的模糊搜索可能会影响性能
@router.get("/articles/content/{content}", response_model=list[schemas.Article])
def search_articles_by_content(content: str, db: Session = Depends(get_db)):
    """通过文章内容搜索文章（无需登录，支持模糊搜索）"""
    try:
        articles = db.query(models.Article).filter(
            models.Article.content.contains(content)
        ).all()
        if not articles:
            raise HTTPException(status_code=404, detail=f"No articles found with content containing '{content}'")
        return articles
    except Exception as e:
        raise 