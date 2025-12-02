import os
import sys
import atexit
from src.logger_config import Logger
from src.utils_db import execute_query, get_db_connection, check_if_server_started
from config.configs import DATABASE_CONFIG


def check_database_exists():
    """检查数据库是否存在"""
    query = f"SELECT COUNT(*) FROM sys.databases WHERE name = '{DATABASE_CONFIG['DB_NAME']}'"
    result = execute_query(query)
    return result[0][''] if result else False


def execute_sql_file(file_path):
    """执行SQL脚本文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            sql_script = file.read()

        conn = get_db_connection()
        if not conn:
            raise Exception("无法建立数据库连接")

        with conn.cursor() as cursor:
            cursor.execute(sql_script)
            conn.commit()

        return True
    except Exception as e:
        print(f"执行SQL文件失败 ({file_path}): {e}")
        Logger.error(f"[DB init] Sql file '{file_path}' execution error: {e}")
        return False


def main():
    print("开始初始化数据库...")

    db_exists = check_database_exists()
    if not db_exists:
        print(f"错误：数据库 '{DATABASE_CONFIG['DB_NAME']}' 不存在，无法继续初始化")
        Logger.error(f"[DB init] Database initial failure, database '{DATABASE_CONFIG['DB_NAME']}' does not exist.")
        sys.exit(1)

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    for path in DATABASE_CONFIG['initial_file_paths']:
        init_sql_path = os.path.join(project_root, *path)
        if os.path.exists(init_sql_path):
            if not execute_sql_file(init_sql_path):
                print("执行初始化脚本失败，初始化终止")
                Logger.error(f"[DB init] Database initial failure: '{init_sql_path}' execution failure.")
                sys.exit(1)
        else:
            Logger.error(f"[DB init] Database initial failure: '{init_sql_path}' does not exist.")
            print(f"未找到初始化脚本: {init_sql_path}，初始化终止")
            sys.exit(1)
        print(f'- 文件：{init_sql_path} 执行完成')
        Logger.info(f"[DB init] Single step execution success: '{init_sql_path}' execution success.")
    print("数据库初始化完成!")
    Logger.info(f"[DB init] Database initial success.")
    sys.exit(0)


def _end_func() -> None:
    Logger.info("+" * 10 + " Model init.init_database stop " + "+" * 10)


if __name__ == "__main__":
    Logger.info("+" * 10 + " Model init.init_database start " + "+" * 10)
    atexit.register(_end_func)
    print("检测数据库服务中...")
    if not check_if_server_started():
        print("数据库服务未开启。")
        sys.exit(1)
    check = input(f'确定初始化你的{DATABASE_CONFIG['DB_NAME']}数据库吗？你需要保证该数据库已存在。(y/n) :')
    if check == 'y' or check == 'Y':
        main()
    else:
        Logger.info("[DB init] Admin took a quick glance at model 'init.init_database', but cancelled init database.")
        print('取消执行。')
