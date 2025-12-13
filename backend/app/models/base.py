# app/models/base.py

"""基础配置：共享的数据库基类、工具函数和通用导入"""
from imports import (
    Column, Integer, String, DateTime, Boolean, Text,
    ForeignKey, UniqueConstraint, relationship
)
from app.database import Base
from app.utils import get_current_utc_time



# 导出所有基础组件（方便其他模型文件导入）
__all__ = [
    "Column", "Integer", "String", "DateTime", "Boolean", "Text",
    "ForeignKey", "UniqueConstraint", "relationship",
    "Base", "get_current_utc_time"
]