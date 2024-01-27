import redis

from config.settings import settings

print(settings.redis_host)


def listen_to_channel(channel_name):
    # 创建 Redis 连接
    redis_client = redis.Redis(
        host=settings.redis_host, port=6379, db=0, password=settings.redis_password
    )
    print("redis连接成功")
    # 创建 pubsub 对象
    pubsub = redis_client.pubsub()

    # 订阅指定的频道
    pubsub.subscribe(channel_name)
    pubsub.subscribe("DB0:sendmsg")

    print(f"开始监听频道：{channel_name}")

    # 监听订阅的消息
    for message in pubsub.listen():
        print(message)
        if message["type"] == "message":
            print(f"收到消息：{message['data'].decode('utf-8')}")


if __name__ == "__main__":
    channel_name = "DB0:Moment"
    listen_to_channel(channel_name)
