# Doc: https://docs.siliconflow.cn/cn/api-reference/chat-completions/chat-completions

import os
import json
# import requests
import aiohttp
import asyncio
from typing import Tuple

from config.configs import AI_CONFIG
from src.utils import read_json


# BEGIN CONSTS

# 预定义flags类型
# 需要与check_if_match_format_of_history_json函数的以下语句同步种类：
# ... or item["flag"] not in (Flags.finish, Flags.wrong, Flags.unresolved)
class __F:
    def __init__(self):
        self.finish = 0  # AI已返回回答
        self.unresolved = 1  # AI正在回答，尚且未返回值
        self.wrong = 2  # 发生错误，"reply"记录值为错误信息


Flags = __F()


# END CONSTS


# Do not use it for checking, function get_reply_from_ai_and_save_json already did that.
def check_if_environ_created():
    silicon_cloud_api = os.environ.get(AI_CONFIG['ENV_NAME'])
    return False if silicon_cloud_api is None else True


def get_silicon_cloud_api():
    return os.environ.get(AI_CONFIG['ENV_NAME']) or ''


# 检测是否满足预设的history.json格式。需要传入路径
# format of history.json:
# [
#    {
#       "ask": "something by user",
#       "reply": "something by AI",
#       "flag": 0
#    },
#    { ... }
# ]
def check_if_match_format_of_history_json(path):
    try:
        is_ok, data = read_json(path)
        if not is_ok:
            return is_ok, data
        if not isinstance(data, list):
            return False, "最外层应为列表"
        required_keys = ["ask", "reply", "flag"]
        required_keys_set = set(required_keys)
        for index, item in enumerate(data):
            if not isinstance(item, dict):
                return False, f"列表中第{index + 1}个元素不是字典"
            item_keys_set = set(item.keys())
            if item_keys_set != required_keys_set:
                extra_keys = item_keys_set - required_keys_set
                missing_keys = required_keys_set - item_keys_set
                error_msg = f"列表中第{index + 1}个元素包含无效的键组合"
                if extra_keys:
                    error_msg += f"，额外的键: {', '.join(extra_keys)}"
                if missing_keys:
                    error_msg += f"，缺失的键: {', '.join(missing_keys)}"
                return False, error_msg
            if not isinstance(item["ask"], str):
                return False, f"列表中第{index + 1}个元素的 'ask' 不是字符串类型"
            if not isinstance(item["reply"], str):
                return False, f"列表中第{index + 1}个元素的 'reply' 不是字符串类型"
            if not isinstance(item["flag"], int) or item["flag"] not in (Flags.finish, Flags.wrong, Flags.unresolved):
                return False, f"列表中第{index + 1}个元素的 'flag' 不是整数类型, 或不是符合要求的整数类型"
        return True, 'good file'
    except json.JSONDecodeError:
        return False, "文件不是有效的JSON格式"
    except Exception as e:
        return False, f"验证过程中发生错误: {str(e)}"


# 获取是否含有Flags.unresolved的问答
def check_if_has_unresolved_msg(path):
    isJsonOk, infoForIsJsonOk = check_if_match_format_of_history_json(path)
    if not isJsonOk:
        return False, infoForIsJsonOk
    ...


# return [status, message]
# if status is False, message is the reason for failure.
# if status is True, message is the reply for the question.
# You should not use this func, use 'get_reply_from_ai_and_save_json' instead.
async def __async_ai(ipt: str) -> Tuple[bool, str]:
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

    # response = requests.post(AI_CONFIG['URL'], json=payload, headers=headers)
    # data = response.json()
    #
    # if response.status_code in (401, 404, 504):
    #     return False, data
    # if response.status_code in (400, 429, 503):
    #     return False, data.get('message')
    # if response.status_code == 200:
    #     return True, data["choices"][0]["message"]["content"].strip()
    # return False, f'Unknown response code: {response.status_code}.'

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    AI_CONFIG['URL'],
                    json=payload,
                    headers=headers
            ) as response:
                data = await response.json()

                if response.status in (401, 404, 504):
                    return False, data
                if response.status in (400, 429, 503):
                    return False, data.get('message')
                if response.status == 200:
                    return True, data["choices"][0]["message"]["content"].strip()
                return False, f'Unknown response code: {response.status}.'
    except aiohttp.ClientError as e:
        return False, f'Network error: {str(e)}'
    except Exception as e:
        return False, f'Unexpected error: {str(e)}'


# 这个函数会调用__async_ai，但不会返回发出post请求后任何的内容。
# 该函数返回值是非异步产生的错误。如环境变量不存在，保存json失败等信息。
# 调用该函数后，会执行以下操作：
#   1. 将用户发出的问题保存至json文件中，并设定该问答为“未完成”状态。
#   2. 创建一个任务对象并让其异步执行，在该异步操作完成后，会将执行结果写入json文件。
# 因此，在src.v1调用该函数后，需要使用一个定时器持续查询任务完成状态。
async def get_reply_from_ai_and_save_json(ipt: str) -> Tuple[bool, str]:
    if not check_if_environ_created():
        return False, f'You should create your private api key first. Check if "{AI_CONFIG['ENV_NAME']}" exits in environment variables.'
    ...


if __name__ == '__main__':
    # To test, run: python -m src.utils_ai

    async def abc():
        a, b = await __async_ai(input('>'))
        print(a)
        print(b)


    asyncio.run(abc())

# async def your_function():
#     # 保存任务对象
#     task = asyncio.create_task(get_reply_from_ai("Hello AI!"))
#
#     # 注册回调函数（任务完成后触发）
#     def handle_result(future):
#         try:
#             success, reply = future.result()  # 获取任务结果
#             if not success:
#                 print(f"任务执行失败: {reply}")
#         except Exception as e:
#             print(f"任务抛出异常: {e}")
#
#     task.add_done_callback(handle_result)
#
#     # 直接返回True
#     return True
