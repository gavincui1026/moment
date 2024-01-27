import random

import requests

message = f"Your Barddies verification code is: 123456. Please enter this code to verify your account."
number = "14383408868"


def test(number):
    url = "https://api.paasoo.com/json"
    code = random.randint(100000, 999999)
    params = {
        "key": "neqbtugn",
        "secret": "6b5mcRHt",
        "from": "123456",
        "to": number,
        "text": message,
    }
    response = requests.get(url, params=params)
    print(response.text)


if __name__ == "__main__":
    test(number)
