from .database import AsyncSessionLocal, AsyncSessionLocal2


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def get_db2():
    async with AsyncSessionLocal2() as session:
        yield session
