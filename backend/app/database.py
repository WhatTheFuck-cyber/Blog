# app/database.py

from imports import create_engine, declarative_base, sessionmaker



# -------------------------- 极简数据库设置 --------------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """数据库会话依赖注入函数：为每个请求创建独立的数据库会话，请求完成后自动关闭"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()