# Doc: https://docs.siliconflow.cn/cn/api-reference/chat-completions/chat-completions

import os
import requests
from typing import Tuple

from config.configs import AI_CONFIG


# Do not use it for checking, function get_reply_from_ai already did that.
def check_if_environ_created():
    silicon_cloud_api = os.environ.get(AI_CONFIG['ENV_NAME'])
    return False if silicon_cloud_api is None else True


def get_silicon_cloud_api():
    return os.environ.get(AI_CONFIG['ENV_NAME']) or ''


# return [status, message]
# if status is False, message is the reason for failure.
# if status is True, message is the reply for the question.
def get_reply_from_ai(ipt: str) -> Tuple[bool, str]:
    if not check_if_environ_created():
        return False, f'You should create your private api key first. Check if "{AI_CONFIG['ENV_NAME']}" exits in environment variables.'

    payload = {
        "model": AI_CONFIG['MODEL'],
        "messages": [
            {
                "role": "system",
                "content": AI_CONFIG['SYS_PROMPT']
            },
            {
                "role": "user",
                "content": ipt
            }
        ]
    }
    headers = {
        "Authorization": f"Bearer {get_silicon_cloud_api()}",
        "Content-Type": "application/json"
    }

    response = requests.post(AI_CONFIG['URL'], json=payload, headers=headers)
    data = response.json()

    if response.status_code in (401, 404, 504):
        return False, data
    if response.status_code in (400, 429, 503):
        return False, data.get('message')
    if response.status_code == 200:
        return True, data["choices"][0]["message"]["content"].strip()
    return False, f'Unknown response code: {response.status_code}.'


if __name__ == '__main__':
    # To test, run: python -m src.utils_ai
    a, b = get_reply_from_ai(input('>'))
    print(a)
    print(b)
