import redis
from config.settings import settings


async def get_redis_client():
    redis_client = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
        db=settings.redis_db,
    )
    yield redis_client
