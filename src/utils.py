import re
import hashlib
import time
import os
import sys
import json
import subprocess
import uuid
from filelock import BaseFileLock
from typing import Tuple, Union, Dict, List
from datetime import datetime
from config.configs import BASE_CONFIG, AI_CONFIG


def generate_short_unique_time_str():
    timestamp_ns = time.time_ns()
    hex_str = hex(timestamp_ns)[2:]
    return hex_str


def open_file_with_explorer(relative_path: str) -> Tuple[bool, str]:
    try:
        absolute_path = os.path.abspath(relative_path)

        if not os.path.exists(absolute_path):
            return False, f"打开失败: 文件不存在 - {absolute_path}"

        if sys.platform.startswith('win'):
            # Windows系统
            os.startfile(absolute_path)
        elif sys.platform.startswith('darwin'):
            # macOS系统
            subprocess.run(['open', absolute_path], check=True)
        elif sys.platform.startswith('linux'):
            # Linux系统
            subprocess.run(['xdg-open', absolute_path], check=True)
        else:
            return False, f"打开失败: 不支持的操作系统 - {sys.platform}"

        return True, "打开成功"

    except Exception as e:
        return False, f"打开失败: {str(e)}"


# save content to normal file, if the file or its dir not exist, this func will create it and give a Warning.
def write_to_file(file_path: str, content: str) -> Tuple[bool, str]:
    try:
        # 去掉文件名部分，获取目录路径
        directory = os.path.dirname(file_path)

        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(
                f'{BASE_CONFIG['COLORS']['red']}Warning: {BASE_CONFIG['COLORS']['cyan']}'
                f'The directory(ies) for your wanted file does not exist.{BASE_CONFIG['COLORS']["reset"]}')

        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

        return True, f"成功将内容写入文件: {os.path.abspath(file_path)}"

    except Exception as e:
        return False, f"写入文件失败: {str(e)}"


def get_current_time() -> str:
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y年%m月%d日 %H:%M:%S")
    return formatted_time


# generate a VARCHAR(64) (relatively) unique id for users
def generate_user_id() -> str:
    timestamp = str(int(time.time() * 1000))
    uuid_str = str(uuid.uuid4()).replace('-', '')
    combined = timestamp + uuid_str
    hash_obj = hashlib.sha256(combined.encode())
    return hash_obj.hexdigest()[:64]


def is_usrName_ok(name: str) -> bool:
    pattern = r'^[\u4e00-\u9fa5a-zA-Z0-9_-]{1,10}$'
    return bool(re.match(pattern, name))


def is_usrPwd_ok(pwd: str) -> bool:
    pattern = r'^[a-zA-Z0-9_]{6,18}$'
    return bool(re.match(pattern, pwd))


def save_json(data: Union[Dict, List, str], file_path: str, lock: BaseFileLock) -> Tuple[bool, str]:
    # 你不需要保证数据被json化
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
            print(
                f'{BASE_CONFIG['COLORS']['red']}Warning: {BASE_CONFIG['COLORS']['cyan']}'
                f'The directory in func utils.save_json does not exist.{BASE_CONFIG['COLORS']["reset"]}')
        with lock:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        return True, 'ok'
    except Exception as e:
        return False, f"Save JSON file error: {str(e)}."


# 包含路径存在性与合理性的检查
def read_json(file_path: str, lock: BaseFileLock) -> Tuple[bool, Union[Dict, List, str]]:
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
        return True, data
    except json.JSONDecodeError:
        return False, 'JSON decode error.'
    except Exception as e:
        return False, f'Read JSON file error: {str(e)}.'
