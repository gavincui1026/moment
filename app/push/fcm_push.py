import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
from app.push.push import PushService
import os
import asyncio


class FirebasePush(PushService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def callback(self, device_ids, title, content, payload):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(
            current_directory, "barddies-firebase-adminsdk-aqjd4-8a1e3509cb.json"
        )
        cred = credentials.Certificate(json_path)
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


if __name__ == "__main__":
    push = FirebasePush()
    push.callback(
        device_ids=[
            "dZlDPPY74E21j8Akkz5n-X:APA91bHJzuQttY7gbD7V_abdjWbqOtlKpSuXhyn3fQ01oGfJtcz-K-hohXRc6qHzmKH1howvewaPSt1aepKMZncK41NR-e857EFNtMFyUG7DefyxaOyQiFZqJsYYyCxfMYnq8xz8oElH"
        ],
        title="test",
        content="test",
        payload="test",
    )
