# app/routers/comments.py

from imports import APIRouter, Depends, HTTPException, status, Session

from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user



# 创建评论相关的路由
router = APIRouter()



@router.post("", response_model=schemas.Comment)
def create_comment(comment: schemas.CommentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """创建新评论（需要用户登录）"""
    if not current_user:
        raise HTTPException(status_code=401, detail="未登录或登录状态已过期，请重新登录")
    try:
        # 验证文章是否存在
        db_article = db.query(models.Article).filter(models.Article.id == comment.article_id).first()
        if not db_article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # 如果提供了parent_id，验证父评论是否存在且属于同一文章
        if comment.parent_id:
            db_parent_comment = db.query(models.Comment).filter(
                models.Comment.id == comment.parent_id,
                models.Comment.article_id == comment.article_id
            ).first()
            if not db_parent_comment:
                raise HTTPException(status_code=404, detail="Parent comment not found or does not belong to this article")
        
        # 创建评论对象，使用当前登录用户的ID
        db_comment = models.Comment(
            content=comment.content,
            article_id=comment.article_id,
            parent_id=comment.parent_id,
            user_id=current_user.id,  # 使用认证系统中的当前用户ID
            user_name=current_user.username  # 使用认证系统中的当前用户名
        )
        
        # 添加到数据库
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        
        return db_comment
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"发布评论失败:{str(e)}")



@router.get("/{comment_id}", response_model=schemas.Comment)
def get_comment(comment_id: int, db: Session = Depends(get_db)):
    """根据ID获取评论详情（无需登录）"""
    try:
        db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
        if not db_comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        return db_comment
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取评论失败:{str(e)}")
    


@router.get("/article/{article_id}", response_model=list[schemas.Comment])
def get_comments_by_article(article_id: int, db: Session = Depends(get_db)):
    """根据文章ID获取所有评论（无需登录）"""
    try:
        # 验证文章是否存在
        db_article = db.query(models.Article).filter(models.Article.id == article_id).first()
        if not db_article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # 获取该文章的所有评论
        comments = db.query(models.Comment).filter(models.Comment.article_id == article_id).all()
        
        return comments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取评论失败:{str(e)}")



@router.put("/{comment_id}", response_model=schemas.Comment)
def update_comment(
    comment_id: int, 
    comment: schemas.CommentUpdate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)  # 需要登录
):
    """更新评论内容（只能更新自己的评论）"""
    try:
        db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
        if not db_comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        # 检查当前用户是否是评论的作者
        if db_comment.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this comment"
            )
        
        # 更新评论内容
        db_comment.content = comment.content
        db.commit()
        db.refresh(db_comment)
        
        return db_comment
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新评论失败:{str(e)}")



@router.delete("/{comment_id}")
def delete_comment(
    comment_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)  # 需要登录
):
    """删除评论（只能删除自己的评论）"""
    try:
        delete_nested_comments(db, comment_id)
        db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
        if not db_comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        # 检查当前用户是否是评论的作者
        if db_comment.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this comment"
            )
        
        # 先删除所有回复
        db.query(models.Comment).filter(models.Comment.parent_id == comment_id).delete()
        
        # 删除评论
        db.delete(db_comment)
        db.commit()
        
        return {"message": "Comment deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除评论失败:{str(e)}")
    
def delete_nested_comments(db: Session, parent_id: int):
    """递归删除所有嵌套回复"""
    child_comments = db.query(models.Comment).filter(models.Comment.parent_id == parent_id).all()
    for child in child_comments:
        delete_nested_comments(db, child.id)  # 递归删除子回复
        db.delete(child)