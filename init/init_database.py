import os
from src.utils_db import execute_query, get_db_connection
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

        # print(f"成功执行: {file_path}")
        return True
    except Exception as e:
        print(f"执行SQL文件失败 ({file_path}): {e}")
        return False


def main():
    print("开始初始化数据库...")

    db_exists = check_database_exists()
    if not db_exists:
        print(f"错误：数据库 '{DATABASE_CONFIG['DB_NAME']}' 不存在，无法继续初始化")
        return

    # 项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 执行初始化脚本
    for path in DATABASE_CONFIG['initial_file_paths']:
        init_sql_path = os.path.join(project_root, *path)
        if os.path.exists(init_sql_path):
            if not execute_sql_file(init_sql_path):
                print("执行初始化脚本失败，初始化终止")
                return
        else:
            print(f"未找到初始化脚本: {init_sql_path}，初始化终止")
            return
        print(f'- 文件：{init_sql_path} 执行完成')
    print("数据库初始化完成!")


if __name__ == "__main__":
    check = input(f'确定初始化你的{DATABASE_CONFIG['DB_NAME']}数据库吗？你需要保证该数据库已存在。(y/n) :')
    if check == 'y' or check == 'Y':
        main()
    else:
        print('取消执行。')
