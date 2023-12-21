from datetime import datetime

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine


from config.settings import settings

import asyncio

print(settings.database_url)

# 创建一个引擎实例
engine = create_async_engine(settings.database_url, echo=True)


async def main():
    # 测试连接
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT * FROM lb_chat"))
            print(list(result.scalars()))
            print("连接测试成功:", result.scalar() == 1)
            last_post_timestamp = datetime.utcnow()
            print(last_post_timestamp)
    except SQLAlchemyError as e:
        print("连接测试失败:", e)


if __name__ == "__main__":
    asyncio.run(main())
