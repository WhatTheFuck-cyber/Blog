# app/routers/categories.py

from imports import APIRouter, Depends, HTTPException, Session
from .. import models, schemas
from ..database import get_db
from ..schemas import Category, CategoryCreate
from ..auth import get_current_user
from ..utils import check_category_exists, check_category_name_unique



router = APIRouter()



@router.post("", response_model=Category)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)  # 需登录
):
    """创建文章分类"""  
    try:
        check_category_name_unique(db, category.name)  # 调用辅助函数
        db_category = models.Category(**category.model_dump())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    except Exception as e:
        db.rollback()  # 回滚事务
        raise HTTPException(status_code=400, detail=f"创建分类失败: {str(e)}")



@router.get("", response_model=list[Category])
def get_all_categories(db: Session = Depends(get_db)):
    """获取所有分类"""
    try:
        return db.query(models.Category).all()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取分类失败: {str(e)}")



@router.get("/name/{name}/articles", response_model=list[schemas.ArticleMinimal])
def get_articles_by_category_name(name: str, db: Session = Depends(get_db)):
    """通过分类名称获取该分类下所有文章的摘要信息"""
    try:
        # 查询分类是否存在
        category = db.query(models.Category).filter(models.Category.name == name).first()
        if not category:
            raise HTTPException(status_code=404, detail=f"Category '{name}' not found")
        
        # 返回该分类下的所有文章（使用ArticleMinimal模型只返回摘要信息）
        return category.articles
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取分类失败: {str(e)}")
    


@router.get("/id/{id}/articles", response_model=list[schemas.ArticleMinimal])
def get_articles_by_category_id(id: int, db: Session = Depends(get_db)):
    """通过分类名称获取该分类下所有文章的摘要信息"""
    try:
        # 查询分类是否存在
        category = db.query(models.Category).filter(models.Category.id == id).first()
        if not category:
            raise HTTPException(status_code=404, detail=f"Category '{id}' not found")
        
        # 返回该分类下的所有文章（使用ArticleMinimal模型只返回摘要信息）
        return category.articles
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取分类失败: {str(e)}")



@router.get("/{category_id}", response_model=Category)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """获取单个分类详情"""
    try:
        return check_category_exists(db, category_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取分类失败: {str(e)}")
    


@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """删除单个分类"""
    try:
        category = check_category_exists(db, category_id)
        db.delete(category)
        db.commit()
        return {"message": "分类删除成功"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"删除分类失败: {str(e)}")