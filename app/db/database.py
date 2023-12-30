from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config.settings import settings

# 您的异步MySQL数据库URL，通常以 "mysql+aiomysql://" 开头
ASYNC_SQLALCHEMY_DATABASE_URL = settings.database_url

engine = create_async_engine(ASYNC_SQLALCHEMY_DATABASE_URL, echo=True)

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

ASYNC_SQLALCHEMY_DATABASE_URL2 = settings.database_url2
engine2 = create_async_engine(ASYNC_SQLALCHEMY_DATABASE_URL2, echo=True)
AsyncSessionLocal2 = sessionmaker(engine2, class_=AsyncSession, expire_on_commit=False)
