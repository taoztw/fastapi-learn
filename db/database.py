"""
创建数据库引擎对象和数据库会话对象
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

from config.config import get_settings

async_engine = create_async_engine(get_settings().ASYNC_DATABASE_URL, echo=False)

Base = declarative_base()

sessionLocal = sessionmaker(bind=async_engine, expire_on_commit=False, class_=AsyncSession)