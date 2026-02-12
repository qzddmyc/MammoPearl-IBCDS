import re
import hashlib
import time
import os
import sys
import json
import subprocess
import uuid
import socket
import base64
import binascii
from filelock import BaseFileLock
from typing import Tuple, Union, Dict, List, Optional
from datetime import datetime
from config.configs import AI_CONFIG
from src.logger_config import Logger


def generate_short_unique_time_str() -> str:
    """
    Generate a time stamp, maybe unique most of the time, uses to mark every detect record.
    :return: a string time stamp
    """
    timestamp_ns = time.time_ns()
    hex_str = hex(timestamp_ns)[2:]
    Logger.info(f"Generated unique time stamp success.")
    return hex_str


def open_file_in_system(relative_path: str) -> Tuple[bool, str]:
    """
    This function is uses to open a file in the system.
    :param relative_path: the relative path of the file to be opened
    :return: [is open success; error message or success message]
    """
    try:
        absolute_path = os.path.abspath(relative_path)

        if not os.path.exists(absolute_path):
            Logger.error(f"Trying to open a nonexistent file '{absolute_path}' in system")
            return False, f"打开失败: 文件不存在 - {absolute_path}"

        if sys.platform.startswith('win'):  # Windows
            os.startfile(absolute_path)
        elif sys.platform.startswith('darwin'):  # macOS
            subprocess.Popen(['open', absolute_path])
        elif sys.platform.startswith('linux'):  # Linux
            try:
                subprocess.Popen(['xdg-open', absolute_path],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except FileNotFoundError:
                # 处理极简Linux系统可能没有安装 xdg-open 的情况
                Logger.error("In Linux system: xdg-open command not found")
                return False, "打开失败: 系统缺少 xdg-open 命令"
        else:
            return False, f"打开失败: 不支持的操作系统 - {sys.platform}"

        Logger.info(f"Opened file '{absolute_path}' successfully in system: {sys.platform}")
        return True, "打开成功"

    except Exception as e:
        return False, f"打开失败: {str(e)}"


def write_to_file(file_path: str, content: str) -> Tuple[bool, str]:
    """
    Save the content to the file, you should ensure the directory exists.
    If the directory doesn't exist, it will be created and a warning will be written to the log.
    :param file_path: the path of the file
    :param content: the content to save
    :return: [is written success; error message or success message]
    """
    try:
        directory = os.path.dirname(file_path)

        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            Logger.warning(f"The directory '{directory}' uses in Func 'write_to_file' does not exist, "
                           f"it should be created before using this function. In File 'utils.py'")

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

        Logger.info(f"success in writing to file: {os.path.abspath(file_path)}, "
                    f"in Func 'write_to_file', in File 'utils.py'")
        return True, f"成功将内容写入文件: {os.path.abspath(file_path)}"

    except Exception as e:
        Logger.error(f"fail in writing to file: {os.path.abspath(file_path)}, info: {e}, "
                     f"in Func 'write_to_file', in File 'utils.py'")
        return False, f"写入文件失败: {str(e)}"


def get_current_time() -> str:
    """
    Get current time formatted as YYYY年MM月DD日 HH:MM:SS
    :return: time string
    """
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y年%m月%d日 %H:%M:%S")
    Logger.info("Got formatted current time.")
    return formatted_time


def generate_user_id() -> str:
    """
    Generate a VARCHAR(64) unique id for users in database. Unique most of the time.
    :return: varchar id of length 64
    """
    timestamp = str(int(time.time() * 1000))
    uuid_str = str(uuid.uuid4()).replace('-', '')
    combined = timestamp + uuid_str
    hash_obj = hashlib.sha256(combined.encode())
    Logger.info("Generated a user id.")
    return hash_obj.hexdigest()[:64]


def is_usrName_ok(name: str) -> bool:
    """
    Check whether a username is valid
    :param name: username
    :return: bool
    """
    pattern = r'^[\u4e00-\u9fa5a-zA-Z0-9_-]{1,10}$'
    Logger.info("Checking for user's name format.")
    return bool(re.match(pattern, name))


def is_usrPwd_ok(pwd: str) -> bool:
    """
    Check whether a password is valid
    :param pwd: password
    :return: bool
    """
    pattern = r'^[a-zA-Z0-9_]{6,18}$'
    Logger.info("Checking for user's password format.")
    return bool(re.match(pattern, pwd))


def save_json(data: Union[Dict, List, str], file_path: str, lock: BaseFileLock) -> Tuple[bool, str]:
    """
    Saves the data to a json file, the data should be able to transform to a json format.
    You should ensure the directory of the json file exists, otherwise it will be created and a warning will be logged.
    你不需要保证数据被json化，符合格式即可。
    :param data: dict, list, or str, which can be formatted to json
    :param file_path: the path of the json file
    :param lock: filelock instance, uses to lock the file whiling saving data
    No extra _error_ logs here, they were written by the caller.
    """
    if lock is None:
        return False, 'You need to provide a valid file lock'
    if lock.lock_file != file_path + AI_CONFIG['LOCK_SUFFIX']:
        return False, 'Lock target in not the same as parameter "file_path" in save_json'
    if not re.match(r'^.+\.json$', file_path):
        return False, f'Path does not reflect a json file.'
    try:
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            Logger.warning(f"The directory '{directory}' uses in Func 'save_json' does not exist, "
                           f"it should be created before using this function. In File 'utils.py'")
        with lock:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        Logger.info(f"Saved json to file '{file_path}' success")
        return True, 'ok'
    except Exception as e:
        return False, f"Save JSON file error: {str(e)}."


def read_json(file_path: str, lock: BaseFileLock) -> Tuple[bool, Union[Dict, List, str]]:
    """
    Read a json file and return the full data
    This func will check if the path exists and is the path a json file path
    :param file_path: json file path
    :param lock: filelock instance, uses to lock the file whiling reading data
    :return: [is read success; the data of the file, or error message]
    No extra logger here.
    """
    if lock is None:
        return False, 'You need to provide a valid file lock'
    if lock.lock_file != file_path + AI_CONFIG['LOCK_SUFFIX']:
        return False, 'Lock target in not the same as parameter "file_path" in read_json'
    if not re.match(r'^.+\.json$', file_path):
        return False, f'Path does not reflect a json file.'
    try:
        if not os.path.exists(file_path):
            return False, f'File not exist: {file_path}.'
        with lock:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        Logger.info(f"Read json file '{file_path}' success")
        return True, data
    except json.JSONDecodeError:
        return False, 'JSON decode error.'
    except Exception as e:
        return False, f'Read JSON file error: {str(e)}.'


def check_web_conn(timeout=3.0) -> bool:
    """
    Check whether the user is connected to the network
    :param timeout: time out for each trying
    :return: bool
    """
    Logger.info('Starting to check web connection...')
    targets = [
        ("8.8.8.8", 53),  # Google DNS
        ("223.5.5.5", 53)  # Alibaba DNS
        # ("1.1.1.1", 53),  # Cloudflare DNS
        # ("www.baidu.com", 80),
        # ('www.luxmeth.cn', 80)
    ]
    for host, port in targets:
        try:
            socket.create_connection((host, port), timeout=timeout)
            Logger.info(f'{host}:{port} connection ok. Web conn check success.')
            return True
        except (socket.timeout, ConnectionRefusedError, OSError, Exception):
            print(f'{host}:{port} connection failure.')
            Logger.error(f"{host}:{port} connection failure, user may not connect to the Internet.")
            continue
    return False


def save_a_picture(pic: bytes, filePath: str) -> bool:
    """
    Save a bytes picture to a path. The path must exist, otherwise will directly return a False.
    If this function returns False, the function that calls the func don't need to write log. True needs.
    :param pic: The bytes picture to save
    :param filePath: The path to save the picture
    :return: Saved success or not
    """
    if not os.path.exists(os.path.dirname(filePath)):
        Logger.error(f"Directory not exists: '{os.path.dirname(filePath)}', while trying to save a picture")
        return False
    if not re.match(r'^.*\.(?:jpg|jpeg|png|webp|bmp|raw)$', filePath, flags=re.IGNORECASE):
        _match = re.search(r'^(?:\.\\|\./|(?:\.\.\\)+|(?:\.\./)+)?.*\.([^.]+)$', filePath, flags=re.IGNORECASE)
        _suffix = _match.group(1) if _match else '_NoSuffix_'
        Logger.error(f"Picture file suffix error: '.{_suffix}' found, while trying to save a picture")
        return False
    try:
        with open(filePath, 'wb') as f:
            f.write(pic)
            Logger.info(f"Saved a picture to '{filePath}', in Func 'save_a_picture', in File 'utils.py'")
    except Exception as e:
        Logger.error(f"Save picture to '{filePath}' failure: {e}, in Func 'save_a_picture', in File 'utils.py'")
        return False
    return True


def secret_a_string(s: str) -> str:
    """
    将一个字符串加密，示例：
        1. Methry -> M***y
        2. A -> A***A
        3. ab -> a***b
    If the param s is empty, return empty string too.
    If the param s is not a string, return an empty string
    """
    if not isinstance(s, str) or len(s) == 0:
        return ''

    return f'{s}***{s}' if len(s) == 1 else f'{s[0]}***{s[-1]}'


def encode_username(text: str) -> Optional[str]:
    """
    encode a username string to a 44-len string (token)
    """
    Logger.info("Encoding username.")
    BLOCK_SIZE = 32

    if not is_usrName_ok(text):
        return None

    text_bytes = text.encode('utf-8')
    pad_len = BLOCK_SIZE - len(text_bytes)
    if pad_len < 0:
        return None

    padded_data = text_bytes + (b'\x00' * pad_len)
    seed = ord(os.urandom(1))
    xor_result = bytearray([seed])

    for i, byte in enumerate(padded_data):
        key_byte = (seed + i + 828) % 256
        xor_result.append(byte ^ key_byte)

    return base64.urlsafe_b64encode(xor_result).decode('utf-8')


def decode_username(encrypted_text: str) -> Optional[str]:
    """
    decode the token, if error return None
    if username does not exist or username not in valid format, return None
    """
    Logger.info("Decoding username.")
    try:
        decoded_bytes = base64.urlsafe_b64decode(encrypted_text)
        if len(decoded_bytes) < 2:
            return None
        seed = decoded_bytes[0]
        cipher_body = decoded_bytes[1:]
        plain_bytes = bytearray()
        for i, byte in enumerate(cipher_body):
            key_byte = (seed + i + 828) % 256
            plain_bytes.append(byte ^ key_byte)
        usr_name = plain_bytes.rstrip(b'\x00').decode('utf-8')

        if not is_usrName_ok(usr_name):
            return None
        return usr_name
    except (binascii.Error, UnicodeDecodeError, Exception):
        return None
