# imports.py

"""项目统一导入管理文件 - 第三方与内置模块集中导出"""


# ==================== 内置模块 ====================
import re
import os
import sys
import time
import json
import signal
import asyncio
import logging
from typing import (
    Optional,
    Union
)
from contextlib import asynccontextmanager
from datetime import (
    datetime, 
    timedelta, 
    timezone
)


# ==================== FastAPI 相关 ====================
from fastapi import (
    FastAPI,
    Request,
    HTTPException,
    APIRouter,
    Depends,
    status,
    Response
)
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import (
    HTTPBearer, 
    HTTPAuthorizationCredentials
)


# ==================== SQLAlchemy 相关 ====================
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    UniqueConstraint, 
    desc,
    func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    sessionmaker, 
    Session, 
    relationship
)


# ==================== Pydantic 相关 ====================
from pydantic import (
    BaseModel, 
    EmailStr, 
    Field, 
    field_validator
)


# ==================== 认证相关 ====================
import uuid
from passlib.context import CryptContext
from jose import (
    JWTError, 
    jwt
)


# ==================== uvicorn 相关 ====================
import uvicorn