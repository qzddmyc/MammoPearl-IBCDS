# Doc: https://docs.siliconflow.cn/cn/api-reference/chat-completions/chat-completions

import os
import json
import atexit
import aiohttp
import asyncio
from filelock import FileLock
from typing import Tuple, Union
from concurrent.futures import ThreadPoolExecutor

from config.configs import AI_CONFIG
from src.utils import read_json, save_json
from src.logger_config import Logger

"""BEGIN CONSTS"""


class __F:
    """
    预定义flags类型
    需要与以下语句同步种类：
    [1] ... or item["flag"] not in (Flags.finish, Flags.wrong, Flags.unresolved),
            in func check_if_match_format_of_history_json
    [2] const Flags in /static/assets/data/qa_doc.js
    """

    def __init__(self):
        self.finish = 0  # AI已返回回答
        self.unresolved = 1  # AI正在回答，尚且未返回值
        self.wrong = 2  # 发生错误，"reply"记录值为错误信息


Flags = __F()

_thread_pool = ThreadPoolExecutor(max_workers=5)


def _shutdown_thread_pool():
    """
    Before shutdown the service, this function will run, to make sure all requests are answered by AI.
    If something goes wrong, an unresolved message may be kept in history.json file.
    And if this happens, next time starts the service, all unresolved messages will be deleted automatically.
    """
    print("正在关闭线程池，等待所有询问被AI回复完成...")
    _thread_pool.shutdown(wait=True)
    print("线程池已关闭")
    Logger.info("+" * 20 + " Service stop " + "+" * 20)


atexit.register(_shutdown_thread_pool)

# 文件锁对象，在初始化时被赋值
__LOCK = None
# 文件锁对象的后缀名，使用配置确保与utils.py文件统一
__lock_suffix = AI_CONFIG['LOCK_SUFFIX']

"""END CONSTS"""


def check_if_environ_created():
    """
    Do not use it for checking, function get_reply_from_ai_and_save_json already did that.
    """
    silicon_cloud_api = get_silicon_cloud_api()
    return False if silicon_cloud_api == '' else True


def INIT_check_if_json_available(path: str) -> bool:
    """
    前端页面被初始化时（开启Flask时）调用一次，检测json文件是否存在，并验证其合法性。
    若不存在，将文件新建并初始化内容为空列表。
    若存在，检测其中是否包含unresolved项，若包含，将其删除。
    注意，该函数返回False时表示遇到了不能修复的问题，请终止app.py的继续执行。
    需要传入的是.json结尾的文件路径
    * This func can be used in v1.py called by app.py, generate path in v1.py
    :param path: the path of the history.json
    :return: [bool] is initial ok
    """
    global __LOCK
    if __LOCK is None:
        __LOCK = FileLock(path + __lock_suffix)
    else:
        Logger.debug(f'Init for json, for AI: __LOCK had an init val: {__LOCK}')  # occur only in test env
        return False
    folder_path = os.path.dirname(path)
    if folder_path and not os.path.exists(folder_path):
        try:
            os.makedirs(folder_path, exist_ok=True)
            Logger.info(f"Init for json, for AI: folder '{folder_path}' created successfully")
        except Exception as e:
            Logger.error(f"Init for json, for AI: folder '{folder_path}' created failure: {e}")
            return False
    if not os.path.isfile(path):
        # Init as an empty list if the file do not exist.
        IsOkInit, msg = save_json([], path, __LOCK)
        if not IsOkInit:
            Logger.error(f"Init for json, for AI: file '{path}' created error: {msg}")
            return False
        Logger.info(f"Init for json, for AI: file '{path}' created as an empty list successfully")
        return True
    isFormatOK, msg = check_if_match_format_of_history_json(path)
    if not isFormatOK:
        print(f"严重警告: 初始化时json格式异常: {msg}\n\t请撤销修改，或直接删除文件: {path}")
        Logger.critical(f"Init for json, for AI: json format error: {msg}, in file '{path}', "
                        f"initiating and program running will stop before user restore the file")
        return False
    isOkInCheck, msgOrNum, _ = check_number_of_unresolved_msg(path)
    if not isOkInCheck:
        Logger.error(f"Init for json, for AI: Unexpected Error in Func check_number_of_unresolved_msg: {msgOrNum}, "
                     f"from Func 'INIT_check_if_json_available', in File 'utils_ai.py'")
        return False
    if msgOrNum != 0:
        # Error: while initiating, there should not exist any unresolved message.
        Logger.warning(f"Init for json, for AI: detected {msgOrNum} unresolved messages, but it should be zero, "
                       f"it may be caused by the unexpected interruption during the last run.")
        Logger.info("Trying to read json for deleting all unresolved messages.")
        isReadOk, data = read_json(path, __LOCK)
        if not isReadOk or not isinstance(data, list):
            Logger.error(f"Init for json, for AI: Unexpected Error in reading json file: {data}, "
                         f"from Func 'INIT_check_if_json_available', in File 'utils_ai.py'")
            return False
        new_data = [i for i in data if i['flag'] != Flags.unresolved]
        isSaveOK, msg = save_json(new_data, path, __LOCK)
        if not isSaveOK:
            Logger.error(f"Init for json, for AI: Unexpected Error in saving json file: {msg}, "
                         f"from Func 'INIT_check_if_json_available', in File 'utils_ai.py'")
            return False
        Logger.info(f"Init for json, for AI: deleted {msgOrNum} unresolved dialogues with AI")
    return True


def get_silicon_cloud_api() -> str:
    """
    Get the environment variable (secret key) used for AI function.
    If user did not provide it, an empty string is returned.
    """
    return os.environ.get(AI_CONFIG['ENV_NAME']) or ''


def check_if_match_format_of_history_json(path) -> Tuple[bool, str]:
    """
    检测是否满足预设的history.json格式。
    format of history.json:
    [
       {
          "ask": "something by user",
          "reply": "something by AI",
          "flag": int
       },
       { ... }
    ]
    No extra logger here, except __LOCK.

    :param path: path of history.json
    :return: [isFileOk, message]
    """
    global __LOCK
    if __LOCK is None:
        Logger.error('__LOCK is None in check_if_match_format_of_history_json')
        return False, 'ERROR: __LOCK is None in check_if_match_format_of_history_json'
    if __LOCK and __LOCK.lock_file != path + __lock_suffix:
        __LOCK = FileLock(path + __lock_suffix)
        Logger.warning('__LOCK target is not the same in check_if_match_format_of_history_json')
    try:
        Logger.info('Trying to read json for checking the format of data.')
        is_ok, data = read_json(path, __LOCK)
        if not is_ok:
            Logger.error(f'Reading file error happened while verifying history.json: {data}')
            return is_ok, data
        if not isinstance(data, list):
            Logger.critical("Found history.json format error: The outermost layer should be a list.")
            return False, "最外层应为列表"
        required_keys = ["ask", "reply", "flag"]
        required_keys_set = set(required_keys)
        for index, item in enumerate(data):
            if not isinstance(item, dict):
                Logger.critical(f"Found history.json format error: The {index + 1} element should be a dict.")
                return False, f"列表中第{index + 1}个元素不是字典"
            item_keys_set = set(item.keys())
            if item_keys_set != required_keys_set:
                extra_keys = item_keys_set - required_keys_set
                missing_keys = required_keys_set - item_keys_set
                error_msg = f"列表中第{index + 1}个元素包含无效的键组合"
                _log_msg = f"The {index + 1} element contains invalid key-value combinations: "
                if extra_keys:
                    error_msg += f"，额外的键: {', '.join(extra_keys)}"
                    _log_msg += f"extra keys: {', '.join(extra_keys)}"
                if missing_keys:
                    error_msg += f"，缺失的键: {', '.join(missing_keys)}"
                    _log_msg += f"missing keys: {', '.join(missing_keys)}"
                Logger.critical(f"Found history.json format error: {_log_msg}")
                return False, error_msg
            if not isinstance(item["ask"], str):
                Logger.critical(f"Found history.json format error: The {index + 1} element's 'ask' is not a string")
                return False, f"列表中第{index + 1}个元素的 'ask' 不是字符串类型"
            if not isinstance(item["reply"], str):
                Logger.critical(f"Found history.json format error: The {index + 1} element's 'reply' is not a string")
                return False, f"列表中第{index + 1}个元素的 'reply' 不是字符串类型"
            if not isinstance(item["flag"], int) or item["flag"] not in (Flags.finish, Flags.wrong, Flags.unresolved):
                Logger.critical(f"Found history.json format error: "
                                f"The {index + 1} element's 'flag' is not a valid integer.")
                return False, f"列表中第{index + 1}个元素的 'flag' 不是整数类型, 或不是符合要求的整数类型"
        Logger.info('Verify history.json ok, good file')
        return True, 'good file'
    except json.JSONDecodeError:
        Logger.critical(f"Found history.json format error: The content in this file is not a valid json")
        return False, "文件不是有效的JSON格式"
    except Exception as e:
        Logger.error(f'Unexpected error happened while verifying history.json: {e}')
        return False, f"验证过程中发生错误: {str(e)}"


def check_number_of_unresolved_msg(path: str) -> Tuple[bool, Union[int, str], bool]:
    """
    检查Flags.unresolved问答的数量，并探测是第一项是未完成项，包含原先json文件格式是否正确的检查
    No extra logger here, except __LOCK.
    :return: [是否发生异常, unresolved数量/异常信息, 第一项数据是否为unresolved数据]
    """
    global __LOCK
    if __LOCK is None:
        Logger.error('__LOCK is None in check_number_of_unresolved_msg')
        return False, 'ERROR: __LOCK is None in check_number_of_unresolved_msg', False
    if __LOCK and __LOCK.lock_file != path + __lock_suffix:
        __LOCK = FileLock(path + __lock_suffix)
        Logger.warning('__LOCK target is not the same in check_number_of_unresolved_msg')
    isJsonOk, infoForIsJsonOk = check_if_match_format_of_history_json(path)
    if not isJsonOk:
        return False, infoForIsJsonOk, False
    Logger.info('Trying to read json for checking the number of unresolved message.')
    openJsonOk, data = read_json(path, __LOCK)
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


def add_msg_to_json(path: str, ask: str, reply: str, flag: int) -> Tuple[bool, str]:
    """
    将一个问题添加至json文件。该问题状态必须为Flags.unresolved
    :param path: json file path
    :param ask: the question raised by user
    :param reply: the placeholder
    :param flag: the flag (Flags.unresolved)
    :return: [is added success, message]
    """
    global __LOCK
    if __LOCK is None:
        Logger.error('__LOCK is None in add_msg_to_json')
        return False, 'ERROR: __LOCK is None in add_msg_to_json'
    if __LOCK and __LOCK.lock_file != path + __lock_suffix:
        __LOCK = FileLock(path + __lock_suffix)
        Logger.warning('__LOCK target is not the same in add_msg_to_json')
    if not flag == Flags.unresolved:
        return False, 'You can only insert unresolved message directly'
    isCheckOK, msg, IsFirstDataUnresolved = check_number_of_unresolved_msg(path)
    if not isCheckOK:
        return False, msg
    if msg != 0:
        return False, 'Contains unresolved message, you can not insert a new one'
    Logger.info("Trying to read json for adding a new unresolved message to it.")
    isRead_ok, json_data = read_json(path, __LOCK)
    if not isRead_ok:
        return False, f'Read json error: {json_data}, in add_msg_to_json'
    new_single_json = {
        "ask": ask,
        "reply": reply,
        "flag": flag
    }
    json_data.insert(0, new_single_json)
    isSaveOk, msg = save_json(json_data, path, __LOCK)
    if not isSaveOk:
        return False, f'Save json error: {msg}, in add_msg_to_json'
    return True, 'ok'


def change_the_first_msg_in_json(path: str, reply: str, flag: int) -> Tuple[bool, str]:
    """
    Get the history data, then replace the first message to a resolved (or error) one, then rewrite the whole file.
    :param path: json file path
    :param reply: the AI's reply message
    :param flag: the new flag
    :return: [is there any error, message]
    """
    global __LOCK
    if __LOCK is None:
        Logger.error('__LOCK is None in change_the_first_msg_in_json')
        return False, 'ERROR: __LOCK is None in change_the_first_msg_in_json'
    if __LOCK and __LOCK.lock_file != path + __lock_suffix:
        __LOCK = FileLock(path + __lock_suffix)
        Logger.warning('__LOCK target is not the same in change_the_first_msg_in_json')
    if flag not in (Flags.finish, Flags.wrong):
        return False, 'You can only modify msg to finished or wrong'
    isCheckOK, msg, IsFirstDataUnresolved = check_number_of_unresolved_msg(path)
    if not isCheckOK:
        return False, msg
    if msg == 1 and IsFirstDataUnresolved:
        Logger.info("Trying to read json for changing the first message to resolved status.")
        isRead_ok, json_data = read_json(path, __LOCK)
        if not isRead_ok:
            return False, f'Read json error: {json_data}, in change_the_first_msg_in_json'
        if not isinstance(json_data, list) or len(json_data) == 0:
            # This part won't cause any issues, it just prevents the editor from showing errors.
            return False, 'Unexpected empty json'
        new_first_item = {
            "ask": json_data[0]["ask"],
            "reply": reply,
            "flag": flag
        }
        json_data[0] = new_first_item
        isSaveOk, msg = save_json(json_data, path, __LOCK)
        if not isSaveOk:
            return False, f'Save json error: {msg}, in change_the_first_msg_in_json'
        return True, 'ok'
    else:
        if not msg == 1:
            return False, f'Unexpected error: contains error nums of unresolved messages: {msg} unresolved.'
        if not IsFirstDataUnresolved:
            return False, f'Unexpected error: The unresolved message is not the first message.'
    return False, 'untouchable message in change_the_first_msg_in_json'


async def __async_ai(input_: str) -> Tuple[bool, str]:
    """
    You should not use this function directly, use "get_reply_from_ai_and_save_json" instead.
    [1] If returned status is False, message is the reason for failure.
    [2] If returned status is True, message is the reply for the question.
    :return: [status, message]
    """
    payload = {
        "model": AI_CONFIG['MODEL'],
        "messages": [
            {
                "role": "system",
                "content": AI_CONFIG['SYS_PROMPT']
            },
            {
                "role": "user",
                "content": input_
            }
        ]
    }
    headers = {
        "Authorization": f"Bearer {get_silicon_cloud_api()}",
        "Content-Type": "application/json"
    }

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


def get_reply_from_ai_and_save_json(ipt: str, pth: str) -> Tuple[bool, str]:
    """
    这个函数会调用__async_ai，但不会返回发出post请求后任何的内容。
    该函数返回值是非异步产生的错误。如环境变量不存在，保存json失败等信息。
    调用该函数后，会执行以下操作：
        1. 将用户发出的问题保存至json文件中，并设定该问答为“未完成”状态。
        2. 创建一个任务对象并让其异步执行，在该异步操作完成后，会将执行结果写入json文件。
    因此，在src.v1调用该函数后，需要使用一个定时器持续查询任务完成状态。

    No logger here, except func 'run_async_task'
    :param pth: .json结尾的文件路径
    :param ipt: 用户输入的问题
    """
    if not check_if_environ_created():
        return False, (f'You should create your private api key first. '
                       f'Check if "{AI_CONFIG['ENV_NAME']}" exits in environment variables.')

    def run_async_task(input_text: str, path: str) -> None:
        """
        该函数会被放进线程池中异步执行，会调用__async_ai函数并等待返回结果。
        在返回后，会将AI的返回结果写入history.json文件。
        该函数没有返回值，因为外部函数不会等待该函数执行结束。
        """
        success, reply = asyncio.run(__async_ai(input_text))
        new_flag = Flags.finish if success else Flags.wrong
        isOK, msg_change = change_the_first_msg_in_json(path, reply, new_flag)
        if isOK:
            Logger.info('AI reply got, and saved to file.')
            if not success:
                Logger.error(f'Continuing the previous log: But AI replied something wrong: {reply}')
        else:
            Logger.error(f"Error happened while saving AI's reply: {msg_change}")
        return

    try:
        isAdded, msg = add_msg_to_json(pth, ipt, AI_CONFIG['PLACEHOLDER_FOR_UNRESOLVED_QUESTION'], Flags.unresolved)
        if not isAdded:
            return False, msg
        _thread_pool.submit(run_async_task, ipt, pth)
    except Exception as e:
        return False, str(e)
    return True, 'ok'


def check_and_get_full_json_by_v1(path: str) -> Tuple[bool, Union[list, str], bool]:
    """
    获取history.json的所有内容，并对这份文件中的内容做合法性检验。
    该函数仅允许：json文件的至多第一项内容为Flags.unresolved状态，其他情况会判定不合法。
    当合法性(第一个返回值)为False时，第三个返回值无意义。
    No extra logger here, except __LOCK.
    :return: [合法性(不出意外肯定为True), json数据/不合法原因, 第一条数据是否为unresolved]
    """
    global __LOCK
    if __LOCK is None:
        Logger.error('__LOCK is None in check_and_get_full_json_by_v1')
        return False, 'ERROR: __LOCK is None in check_and_get_full_json_by_v1', False
    if __LOCK and __LOCK.lock_file != path + __lock_suffix:
        __LOCK = FileLock(path + __lock_suffix)
        Logger.warning('__LOCK target is not the same in check_and_get_full_json_by_v1')
    isCheckOk, data1, isFirstUnresolved = check_number_of_unresolved_msg(path)
    if not isCheckOk:
        return False, data1, False
    if data1 not in (0, 1):
        return False, 'Error: unexpected number of unresolved datas', False
    Logger.info("Trying to read json for getting full json for initiating the web page.")
    isReadOk, data2 = read_json(path, __LOCK)
    if not isReadOk:
        return False, data2, False
    return True, data2, isFirstUnresolved


def check_if_unresolved_msg_resolves_and_get_it(path: str) -> Tuple[bool, str, bool]:
    """
    检查第一条消息是否已经被标记为finish状态(或者是wrong，这两者不进行区分)。实际上，会检查unresolved消息的数量是否为0
    当程序发生不应当存在的错误时，第三个返回值会为True，表示应当停止继续的请求。
    若已为Flags.finish，第二个返回值为AI回复的值。
    当然，如果AI返回了一个错误的状态码，这里不做处理，只将内容返回，后续会将AI触发Flags.wrong原因直接作为正常回复写在页面上。
    """
    global __LOCK
    if __LOCK is None:
        Logger.error('__LOCK is None in check_if_unresolved_msg_resolves_and_get_it')
        return False, 'ERROR: __LOCK is None in check_if_unresolved_msg_resolves_and_get_it', True
    if __LOCK and __LOCK.lock_file != path + __lock_suffix:
        __LOCK = FileLock(path + __lock_suffix)
        Logger.warning('__LOCK target is not the same in check_if_unresolved_msg_resolves_and_get_it')
    isCheckOk, data, isFirstUnresolved = check_number_of_unresolved_msg(path)
    if not isCheckOk:
        return False, data, True
    if data not in (0, 1) or (data != 0 and not isFirstUnresolved) or (data == 0 and isFirstUnresolved):
        return False, 'Error: unexpected number of unresolved', True
    if data == 0 and not isFirstUnresolved:
        Logger.info("Trying to read json for getting the first message, which is resolved.")
        isReadOK, newContent = read_json(path, __LOCK)
        if not isReadOK:
            return False, newContent, True
        reply = newContent[0].get('reply')
        return True, reply, False
    if data == 1 and isFirstUnresolved:
        return False, 'waiting', False
    return False, 'untouchable', True

# You can't test this with: python -m src.utils_ai, it needs one async environment.
