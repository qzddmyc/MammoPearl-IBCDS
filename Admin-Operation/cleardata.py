from config.configs import DATABASE_CONFIG
from src.utils_db import execute_non_query, if_table_exists


def truncate_table(table_name) -> bool:
    """ 删除一个表内的所有数据 """
    if not if_table_exists(table_name):
        print('表不存在，清空内容失败。')
        return False
    query = f"DELETE FROM {table_name}"
    return execute_non_query(query)


def delete_table(table_name) -> bool:
    """ 删除一整张表 """
    if not if_table_exists(table_name):
        print('表不存在，删除失败。')
        return False
    query = f"DROP TABLE IF EXISTS {table_name}"
    return execute_non_query(query)


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
        print('无事发生。')
    print("执行完成。")


if __name__ == "__main__":
    main()
