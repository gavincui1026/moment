from config.settings import settings
import redis


def lock():
    # 创建 Redis 连接
    redis_client = redis.Redis(
        host=settings.redis_host, port=6379, db=0, password=settings.redis_password
    )
    flag = redis_client.get("startup_flag")
    if not flag:
        # 设置标记并保留一段时间（例如 30 秒）
        redis_client.set("startup_flag", "true", ex=30)
        return True
    return False
