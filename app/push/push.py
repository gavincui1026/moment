import json
import random
import threading
import time

import configparser
import asyncio
import aioredis
from pathlib import Path


class PushService:
    def __init__(self):
        self.redis_client = None
        self.subscribe_redis = None
        self.c2c = 1
        self.group = 2
        self.system = 3
        self.moment = 4
        self.chat_history = {}
        self.chat_interval = {}
        self.chat_group_history = {}
        self.chat_group_data = {}
        self.chat_group_interval = {}

    async def get_redis_client(self):
        current_file = Path(__file__).resolve()
        current_dir = current_file.parent
        current_path = current_dir.joinpath("config.ini")
        config = configparser.ConfigParser()
        config.read(current_path)
        redis_client = aioredis.from_url(
            f"redis://{config.get('redis', 'redis_host')}:{config.get('redis', 'redis_port')}",
            db=int(config.get("redis", "redis_db")),
            password=config.get("redis", "redis_password"),
            encoding="utf-8",
            decode_responses=True,
        )
        return redis_client

    async def start(self):
        self.redis_client = await self.get_redis_client()
        self.subscribe_redis = self.redis_client.pubsub()
        await self.subscribe_redis.subscribe("DB0:sendmsg")
        print("订阅 sendmsg 频道成功")
        asyncio.create_task(self.listen_to_messages())

    async def listen_to_messages(self):
        while True:
            try:
                message = await self.subscribe_redis.get_message(
                    ignore_subscribe_messages=True  # 忽略订阅消息
                )
                if message and message["type"] == "message":
                    channel = message["channel"]
                    data = message["data"]

                    # 解析 JSON
                    try:
                        message_data = json.loads(data)
                        # print(f"收到 {channel} 频道的消息：{message_data}")
                        if channel == "DB0:sendmsg":
                            result = await self.sendMessageInfo(message_data)
                            if result:
                                print("发送成功")
                                # print("发送成功")
                            else:
                                print("发送失败")
                    except json.JSONDecodeError as e:
                        print(f"解析 JSON 时发生错误：{e}")

                await asyncio.sleep(1)
            except Exception as e:
                print(f"监听消息时发生错误：{e}")

    async def sendMessageInfo(self, data):
        if data.get("is_refuse"):
            print("refuse")
            return False

        push_channel = data.get("offLinePush", {}).get("channel", "default")

        if push_channel != "default":
            return False

        session_type = data.get("session_type", "")
        is_all = False
        # C2C 单聊
        if session_type == self.c2c:
            chat_to_id = data.get("chat_to_id")
            if not chat_to_id:
                print("chatId error")
                return False

            # 检查是否设置免打扰
            disturb = await self.redis_client.hget(
                f"disturb_c2c_{chat_to_id}", data.get("chat_from_id")
            )
            if not disturb:
                # 读取收件人的离线设备ID
                device_id = await self.redis_client.hget("push_user_list", chat_to_id)
                if device_id:
                    await self.process_msg(device_id, data)
            return True

        # 群聊
        elif session_type == self.group:
            group_id = data.get("group_id")
            if not group_id:
                print("chatId error")
                return False

            # 读取群成员
            group_members = await self.redis_client.hgetall(f"group_user_{group_id}")
            for chat_id in group_members:
                # 检查是否设置免打扰
                disturb = await self.redis_client.hget(
                    f"disturb_grp_{chat_id}", group_id
                )
                if not disturb:
                    # 读取收件人的离线设备ID
                    device_id = await self.redis_client.hget("push_user_list", chat_id)
                    if device_id:
                        await self.process_msg(device_id, data)
            return True
        # 系统
        elif session_type == self.system:
            is_all = True

            # 发送给目标群体
            if data.get("chat_to_ids"):
                is_all = False
                for chat_to_id in data["chat_to_ids"]:
                    device_id = await self.redis_client.hget(
                        "push_user_list", chat_to_id
                    )
                    if device_id:
                        await self.process_msg(device_id, data)

            # 发送给指定人
            if data.get("chat_to_id"):
                is_all = False
                device_id = await self.redis_client.hget(
                    "push_user_list", data["chat_to_id"]
                )
                if device_id:
                    await self.process_msg(device_id, data)

            # 发送给指定群
            if data.get("group_id"):
                is_all = False
                group_members = await self.redis_client.hgetall(
                    f'group_user_{data["group_id"]}'
                )
                for chat_id in group_members:
                    disturb = await self.redis_client.hget(
                        f"disturb_grp_{chat_id}", data["group_id"]
                    )
                    if not disturb:
                        device_id = await self.redis_client.hget(
                            "push_user_list", chat_id
                        )
                        if device_id:
                            await self.process_msg(device_id, data)
        elif session_type == self.moment:
            is_all = False
            device_id = await self.redis_client.hget(
                "push_user_list", data["chat_to_id"]
            )

            if device_id:
                await self.process_msg(device_id, data)
                return True

        if is_all:
            self.send_msg([], data)
            return True
        return False

    async def process_msg(self, device_id, data):
        # print(f"------process_msg: {device_id}------")
        # print(data)
        keyname = device_id

        self.chat_history[keyname] = data  # 覆盖消息

        if keyname not in self.chat_interval:
            self.chat_interval[keyname] = asyncio.create_task(
                self.check_and_process(keyname)
            )

    async def check_and_process(self, keyname):
        await asyncio.sleep(0.2)
        if self.chat_history.get(keyname):
            await self.process_group_msg(keyname, self.chat_history[keyname])
            self.chat_history[keyname] = None
        else:
            self.chat_interval[keyname].cancel()
            del self.chat_interval[keyname]

    async def process_group_msg(self, device_id, data):
        # print(f"------process_group_msg: {device_id}------")
        print(data)
        keyname = data["msgid"]
        print(keyname)

        if keyname not in self.chat_group_history:
            self.chat_group_history[keyname] = []
        self.chat_group_history[keyname].append(device_id)  # 合并收件人
        self.chat_group_data[keyname] = data  # 临时存储消息

        if keyname not in self.chat_group_interval:
            self.chat_group_interval[keyname] = asyncio.create_task(
                self.schedule_send_msg(keyname)
            )

    async def schedule_send_msg(self, keyname):
        await asyncio.sleep(0.2)
        if self.chat_group_history.get(keyname):
            self.send_msg(
                self.chat_group_history[keyname], self.chat_group_data[keyname]
            )
            self.chat_group_data[keyname] = None
            self.chat_group_history[keyname] = []
        del self.chat_group_interval[keyname]

    def send_msg(self, device_ids, data):
        title = ""
        content = ""
        if data["session_type"] == self.group:
            title = data["group"]["name"]
            content = data["from_user"]["nickname"] + ":" + data["content"]
        elif data["session_type"] == self.system:
            title = "系统通知"
            if "group_id" in data and "group" in data:
                title = data["group"].get("name", "群消息")
                content = data["session_content"]
        elif data["session_type"] == self.c2c:
            title = data["from_user"]["nickname"]
            content = data["session_content"]
        elif data["session_type"] == self.moment:
            data["from_user"] = json.loads(data["from_user"])
            title = data["from_user"]["nickname"]
            content = data["session_content"]
        payload = json.dumps(data)
        self.callback(device_ids, title, content, payload)

    def callback(self, device_ids, title, content, payload):
        pass
