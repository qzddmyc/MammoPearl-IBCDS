from config.configs import DATABASE_CONFIG
from src.utils import generate_user_id
from src.utils_db import execute_non_query, if_table_exists, execute_query, save_User
from tabulate import tabulate
import wcwidth


def chinese_aware_ljust(s, width):
    """中文-aware的左对齐函数"""
    # 计算字符串实际显示宽度
    str_width = wcwidth.wcswidth(str(s))
    # 计算需要补充的空格数
    spaces_needed = max(0, width - str_width)
    return str(s) + ' ' * spaces_needed


# 输出表table中所有键为item的项。返回是否有值。
def printUsers(table, item) -> bool:
    # 查询所有用户名
    usernames = execute_query(f"SELECT {item} FROM {table}")

    print()
    print("查询到存在的用户信息如下：")
    if usernames is None:
        print("Error: Query failure in func printUsers.")
        return False
    if not usernames:
        return False

    max_width = max(wcwidth.wcswidth(str(row[item])) for row in usernames)
    header_width = max(max_width, wcwidth.wcswidth(item))

    headers = [item]
    table_data = [[chinese_aware_ljust(str(row[item]), header_width)] for row in usernames]

    # tablefmt: grid/fancy_grid/pipe/simple
    print(tabulate(table_data, headers=headers, tablefmt="grid", colalign=("left",)))
    print()
    return True


def main():
    t = DATABASE_CONFIG['TableName_U']
    if not if_table_exists(t):
        print(f'表{t}不存在，无法对数据进行修改。')
    else:
        print(f'此脚本用于修改表{t}中的数据，仅限管理员使用。')
        print("""
    1. 修改已存在用户的密码。
    2. 新增用户。
    3. 删除已存在的用户。
    *. 退出。
        """)
        choice = input('Your choice: ')
        if choice == '1':
            isPrint = printUsers(t, DATABASE_CONFIG['ColName_NAME'])
        elif choice == '2':
            # 这部分临时使用，需要重写
            usrName = input('用户名：')
            pwd = input('密码：')
            idid = generate_user_id()
            info = save_User(idid, usrName, pwd)
            print(info)
        elif choice == '3':
            ...
        else:
            ...
    print('执行完成。')


if __name__ == '__main__':
    # python -m Admin-Operation.modifydata
    main()
