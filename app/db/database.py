from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# 您的异步MySQL数据库URL，通常以 "mysql+aiomysql://" 开头
ASYNC_SQLALCHEMY_DATABASE_URL = "mysql+aiomysql://root:303816@localhost:3306/test"

engine = create_async_engine(ASYNC_SQLALCHEMY_DATABASE_URL, echo=True)

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)