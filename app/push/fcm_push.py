import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
from .push import PushService
import asyncio


class FirebasePush(PushService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def callback(self, device_ids, title, content, payload):
        cred = credentials.Certificate(
            "barddies-firebase-adminsdk-aqjd4-8a1e3509cb.json"
        )
        default_app = firebase_admin.initialize_app(cred)
        print(f"------callback: {device_ids}------")
        print(f"------callback: {title}------")
        print(f"------callback: {content}------")
        print(f"------callback: {payload}------")

        message = messaging.MulticastMessage(
            notification=messaging.Notification(title=title, body=content),
            data={"payload": payload},
            tokens=device_ids,
        )
        response = messaging.send_each_for_multicast(message)
        for idx, result in enumerate(response.responses):
            if result.success:
                # 成功发送消息
                print(f"Successfully sent message to {message.tokens[idx]}")
            else:
                # 发送消息失败
                print(
                    f"Failed to send message to {message.tokens[idx]}: {result.exception}"
                )
