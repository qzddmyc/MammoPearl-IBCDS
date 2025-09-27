# Doc: https://docs.siliconflow.cn/cn/api-reference/chat-completions/chat-completions

import os
import json
import atexit
# import requests
import aiohttp
import asyncio
from typing import Tuple, Union
# import threading
from concurrent.futures import ThreadPoolExecutor

from config.configs import AI_CONFIG
from src.utils import read_json, save_json


# BEGIN CONSTS

# 预定义flags类型
# 需要与check_if_match_format_of_history_json函数的以下语句同步种类：
# ... or item["flag"] not in (Flags.finish, Flags.wrong, Flags.unresolved)
# const Flags in /static/assets/data/qa_doc.js
class __F:
    def __init__(self):
        self.finish = 0  # AI已返回回答
        self.unresolved = 1  # AI正在回答，尚且未返回值
        self.wrong = 2  # 发生错误，"reply"记录值为错误信息


Flags = __F()

_thread_pool = ThreadPoolExecutor(max_workers=5)


def _shutdown_thread_pool():
    print("正在关闭线程池，等待所有任务完成...")
    _thread_pool.shutdown(wait=True)
    print("线程池已关闭")


atexit.register(_shutdown_thread_pool)


# END CONSTS


# Do not use it for checking, function get_reply_from_ai_and_save_json already did that.
def check_if_environ_created():
    silicon_cloud_api = os.environ.get(AI_CONFIG['ENV_NAME'])
    return False if silicon_cloud_api is None else True


# 前端页面被初始化时（开启Flask时）调用一次，检测json文件是否存在，并验证其合法性。
# 若不存在，将文件新建并初始化内容为空列表。
# 若存在，检测其中是否包含unresolved项，若包含，将其删除。
# 注意，该函数返回False时表示遇到了不能修复的问题，请终止app.py的继续执行。
# 需要传入的是.json结尾的文件路径
# This func can be used in v1.py in app.py, generate path in v1.py
def INIT_check_if_json_available(path):
    folder_path = os.path.dirname(path)
    if folder_path and not os.path.exists(folder_path):
        try:
            os.makedirs(folder_path, exist_ok=True)
            print(f"INIT: 文件夹创建成功：{folder_path}")
        except Exception as e:
            print(f"INIT: 文件夹创建时失败：{e}")
            return False
    if not os.path.isfile(path):
        # 文件不存在，则初始化为空列表
        save_json([], path)
        print(f'INIT: 初始化 {path} 文件成功')
        return True
    isFormatOK, msg = check_if_match_format_of_history_json(path)
    if not isFormatOK:
        print(f"INIT: json格式异常: {msg}\n\t请撤销修改，或直接删除文件: {path}")
        return False
    isOkInCheck, msgOrNum, _ = check_number_of_unresolved_msg(path)
    if not isOkInCheck:
        print(f"INIT: Unexpected Error in check_number_of_unresolved_msg: {msgOrNum}")
        return False
    if msgOrNum != 0:
        # 异常，初始时不应该存在unresolved信息
        isReadOk, data = read_json(path)
        if not isReadOk or not isinstance(data, list):
            print(f"INIT: Unexpected Error in reading json file: {data}")
            return False
        new_data = [i for i in data if i['flag'] != Flags.unresolved]
        isSaveOK, msg = save_json(new_data, path)
        if not isSaveOK:
            print(f"INIT: Unexpected Error in saving json file: {msg}")
        print(f"INIT: Warning: 存在{msgOrNum}条unresolved的AI对话信息，已删除。")
    return True


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


# 检查Flags.unresolved问答的数量，并探测是第一项是未完成项，包含原先json文件格式是否正确的检查
# 返回值：[是否发生异常, unresolved数量/异常信息, 第一项数据是否为unresolved数据]
def check_number_of_unresolved_msg(path: str) -> Tuple[bool, Union[int, str], bool]:
    isJsonOk, infoForIsJsonOk = check_if_match_format_of_history_json(path)
    if not isJsonOk:
        return False, infoForIsJsonOk, False  # 返回False表示原先的json文件已经被修改
    openJsonOk, data = read_json(path)
    if not openJsonOk:
        return False, data, False
    if not isinstance(data, list):
        return False, 'this message is untouchable', False
    cnt = 0
    IsFirstDataUnresolved = False
    if len(data) >= 1:
        IsFirstDataUnresolved = data[0]["flag"] == Flags.unresolved
    for item in data:
        if item["flag"] == Flags.unresolved:
            cnt += 1
    return True, cnt, IsFirstDataUnresolved


# 将一个问题添加至json文件。该问题状态必须为Flags.unresolved
# 返回是否添加成功，以及对应的信息
def add_msg_to_json(path: str, ask: str, reply: str, flag: int) -> Tuple[bool, str]:
    if not flag == Flags.unresolved:
        return False, 'You can only insert unresolved message directly'
    isCheckOK, msg, IsFirstDataUnresolved = check_number_of_unresolved_msg(path)
    if not isCheckOK:
        return False, msg
    if msg != 0:
        return False, 'Contains unresolved message, you can not insert a new one'
    isRead_ok, json_data = read_json(path)
    if not isRead_ok:
        return False, f'Read json error: {json_data}, in add_msg_to_json'
    new_single_json = {
        "ask": ask,
        "reply": reply,
        "flag": flag
    }
    json_data.insert(0, new_single_json)
    isSaveOk, msg = save_json(json_data, path)
    if not isSaveOk:
        return False, f'Save json error: {msg}, in add_msg_to_json'
    return True, 'ok'


def change_the_first_msg_in_json(path: str, reply: str, flag: int) -> Tuple[bool, str]:
    if flag not in (Flags.finish, Flags.wrong):
        return False, 'You can only modify msg to finished or wrong'
    isCheckOK, msg, IsFirstDataUnresolved = check_number_of_unresolved_msg(path)
    if not isCheckOK:
        return False, msg
    if msg == 1 and IsFirstDataUnresolved:
        isRead_ok, json_data = read_json(path)
        if not isRead_ok:
            return False, f'Read json error: {json_data}, in change_the_first_msg_in_json'
        if not isinstance(json_data, list) or len(json_data) == 0:
            # isinstance 部分不会出问题，只是让编辑器不显示错误
            return False, 'Unexpected empty json'
        new_first_item = {
            "ask": json_data[0]["ask"],
            "reply": reply,
            "flag": flag
        }
        json_data[0] = new_first_item
        isSaveOk, msg = save_json(json_data, path)
        if not isSaveOk:
            return False, f'Save json error: {msg}, in change_the_first_msg_in_json'
        return True, 'ok'
    else:
        if not msg == 1:
            return False, f'Unexpected error: contains error nums of unresolved messages: {msg} unresolved.'
        if not IsFirstDataUnresolved:
            return False, f'Unexpected error: The unresolved message is not the first message.'
    return False, 'untouchable message in change_the_first_msg_in_json'


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
# 参数pth路径为.json结尾的文件路径
def get_reply_from_ai_and_save_json(ipt: str, pth: str) -> Tuple[bool, str]:
    if not check_if_environ_created():
        return False, f'You should create your private api key first. Check if "{AI_CONFIG['ENV_NAME']}" exits in environment variables.'

    def run_async_task(input_text, path):
        success, reply = asyncio.run(__async_ai(input_text))
        # 原先的json第一项应当是Flags.unresolved对象，现在应当替换relpy与flag字段
        new_flag = Flags.finish if success else Flags.wrong
        isOK, msg_change = change_the_first_msg_in_json(path, reply, new_flag)
        if isOK:
            print('AI reply got, and saved successfully.')
            if not success:
                print(f'But AI replied something wrong: {reply}')
        else:
            print(f'Warning: Error happened while saving reply: {msg_change}')
        return

    try:
        isAdded, msg = add_msg_to_json(pth, ipt, AI_CONFIG['PLACEHOLDER_FOR_UNRESOLVED_QUESTION'], Flags.unresolved)
        if not isAdded:
            return False, msg
        _thread_pool.submit(run_async_task, ipt, pth)
    except Exception as e:
        return False, str(e)
    return True, 'ok'


# 该函数仅允许：至多第一项内容为Flags.unresolved状态，其他情况会判定不合法
# 返回值: [合法性(不出意外肯定为True), json数据/不合法原因, 第一条数据是否为unresolved]
# 当合法性为False时，第三个返回值无意义
def check_and_get_full_json_by_v1(path: str) -> Tuple[bool, Union[list, str], bool]:
    isCheckOk, data1, isFirstUnresolved = check_number_of_unresolved_msg(path)
    if not isCheckOk:
        return False, data1, False
    if data1 not in (0, 1):
        return False, 'Error: unexpected number of unresolved datas', False
    isReadOk, data2 = read_json(path)
    if not isReadOk:
        return False, data2, False
    return True, data2, isFirstUnresolved

# You can't test this with: python -m src.utils_ai
