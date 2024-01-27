from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

import configparser

# 您的异步MySQL数据库URL，通常以 "mysql+aiomysql://" 开头
config = configparser.ConfigParser()
database_url = f"mysql+aiomysql://{config.get('mysql', 'mysql_user')}:{config.get('mysql', 'mysql_password')}@{config.get('mysql', 'mysql_host')}:{config.get('mysql', 'mysql_port')}"
ASYNC_SQLALCHEMY_DATABASE_URL = database_url

engine = create_async_engine(ASYNC_SQLALCHEMY_DATABASE_URL, echo=True)

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# 创建基本异步会话
async_session = AsyncSessionLocal()
