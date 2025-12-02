import sys
import atexit

from config.configs import DATABASE_CONFIG
from src.utils_db import execute_non_query, if_table_exists, check_if_server_started
from src.logger_config import Logger


def truncate_table(table_name) -> bool:
    """ 删除一个表内的所有数据 """
    if not if_table_exists(table_name):
        print('表不存在，清空内容失败。')
        Logger.warning(f"[Admin] Truncate table data failure: table '{table_name}' does not exist.")
        return False
    query = f"DELETE FROM {table_name}"
    _result = execute_non_query(query)
    if not _result:
        Logger.error(f"[Admin] Truncate table data failure: "
                     f"error in database while executing non-query, table '{table_name}'.")
    else:
        Logger.info(f"[Admin] Truncate table data success: table '{table_name}'.")
    return _result


def delete_table(table_name) -> bool:
    """ 删除一整张表 """
    if not if_table_exists(table_name):
        print('表不存在，删除失败。')
        Logger.warning(f"[Admin] Delete table failure: table '{table_name}' does not exist.")
        return False
    query = f"DROP TABLE IF EXISTS {table_name}"
    _result = execute_non_query(query)
    if not _result:
        Logger.error(f"[Admin] Delete table failure: "
                     f"error in database while executing non-query, table '{table_name}'.")
    else:
        Logger.info(f"[Admin] Delete table success: table '{table_name}'.")
    return _result


def main():
    t = DATABASE_CONFIG['TableName_U']
    print(f"警告：此脚本用于清空或删除{t}表，请谨慎操作！")
    print(f"""
    1. 清除表{t}中所有存储的信息。
    2. 直接删除表{t}。此后，你需要重新运行初始化程序。
    *. 退出。
    """)
    choice = input("Your choice: ")
    if choice == '1':
        r = truncate_table(t)
        if r:
            print(f'清除表{t}的数据完成。')
    elif choice == '2':
        r = delete_table(t)
        if r:
            print(f'删除表{t}成功。')
    else:
        Logger.info("[Admin] Admin took a quick glance at model 'Admin-Operation.cleardata', but did nothing.")
        print('无事发生。')


def _end_func() -> None:
    Logger.info("+" * 10 + " Model Admin-Operation.cleardata stop " + "+" * 10)
    print("执行完成。")


if __name__ == "__main__":
    # python -m Admin-Operation.cleardata
    Logger.info("+" * 10 + " Model Admin-Operation.cleardata start " + "+" * 10)
    atexit.register(_end_func)
    print("检测数据库服务中...")
    if not check_if_server_started():
        print("数据库服务未开启。")
        sys.exit(-1)
    main()
