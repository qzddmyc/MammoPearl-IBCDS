import re
import sys
import atexit
from config.configs import DATABASE_CONFIG
from src.logger_config import Logger
from src.utils import generate_user_id, is_usrPwd_ok, is_usrName_ok, secret_a_string
from src.utils_db import if_table_exists, execute_query, save_User, \
    update_UserAccount_password, delete_user_by_username, check_if_server_started
from tabulate import tabulate
import wcwidth


def chinese_aware_ljust(s, width):
    """中文-aware的左对齐函数"""
    str_width = wcwidth.wcswidth(str(s))
    spaces_needed = max(0, width - str_width)
    return str(s) + ' ' * spaces_needed


def printUsers(table, item):
    """
    输出表table中所有键为item的项。返回是否有值及带有值的列表。
    """
    # 查询所有用户名
    usernames = execute_query(f"SELECT {item} FROM {table}")

    print("查询到存在的用户信息如下：")
    if usernames is None:
        print("Error: Query failure in func printUsers.")
        Logger.error("[Admin] Query failure in func printUsers.")
        return False, []
    if not usernames:
        print("当前不存在用户信息。")
        Logger.warning("[Admin] Print an empty info of user list.")
        return False, []

    indexed_usernames = []
    max_width = 0
    for i, row in enumerate(usernames, start=1):
        username = str(row[item])
        indexed_username = f"{i}. {username}"
        indexed_usernames.append(indexed_username)

        current_width = wcwidth.wcswidth(indexed_username)
        if current_width > max_width:
            max_width = current_width

    header_width = max(max_width, wcwidth.wcswidth(item))

    headers = [item]
    table_data = [[chinese_aware_ljust(name, header_width)] for name in indexed_usernames]

    # tablefmt: grid/fancy_grid/pipe/simple
    print(tabulate(table_data, headers=headers, tablefmt="grid", colalign=("left",)))
    Logger.info("[Admin] Print user list.")

    return True, indexed_usernames


def main():
    t = DATABASE_CONFIG['TableName_U']
    if not if_table_exists(t):
        print(f'表{t}不存在，无法对数据进行修改。')
        return
    print(f'此脚本用于修改表{t}中的数据，仅限管理员使用。')
    print("""
    1. 修改已存在用户的密码。
    2. 新增用户。
    3. 删除已存在的用户。
    *. 退出。
    """)
    choice = input('Your choice: ')
    print()

    def func_in_1_3():
        # 输出用户列表并获取用户的输入索引。返回格式为: (是否错误, 被选中的用户名)
        isPrint, _usrList = printUsers(t, DATABASE_CONFIG['ColName_NAME'])
        print()
        if not isPrint:
            return False, None
        try:
            _idx = int(input('Enter your index: '))
            if _idx <= 0 or _idx > len(_usrList):
                raise ValueError
        except ValueError:
            print("\n索引值错误。")
            Logger.warning("[Admin] Get user input error: Index out of range.")
            return False, None
        _uname = re.match(r'^\d+\. (.+)$', _usrList[_idx - 1]).group(1)
        return True, _uname

    if choice == '1':
        isOk, uname = func_in_1_3()
        if not isOk:
            return
        new_pwd = input('Enter your new password: ')
        print()
        if not is_usrPwd_ok(new_pwd):
            print("密码格式错误。需要6-18位的英文、数字、下划线。")
            Logger.warning(f"[Admin] Modify password error: password format error, "
                           f"for user '{secret_a_string(uname)}'")
            return
        isChanged = update_UserAccount_password(uname, new_pwd)
        if isChanged:
            print('密码修改成功。')
            Logger.info(f"[Admin] Modify password success, user '{secret_a_string(uname)}'")
            return
        Logger.error(f"[Admin] Modify password failure, user '{secret_a_string(uname)}'")
        print('发生异常，修改失败。')
        return
    elif choice == '2':
        uname = input('User name: ')
        if not is_usrName_ok(uname):
            print('\n用户名格式错误。需要至多10位的中文、英文、数字、下划线、减号。')
            Logger.warning(f"[Admin] Appending user error: username format error.")
            return
        pwd = input('User password: ')
        if not is_usrPwd_ok(pwd):
            print("\n密码格式错误。需要6-18位的英文、数字、下划线。")
            Logger.warning(f"[Admin] Appending user error: password format error.")
            return
        print()
        idid = generate_user_id()
        info = save_User(idid, uname, pwd)
        if not info['success']:
            print('新增失败：' + info['info'])
            Logger.error(f"[Admin] Append new user failure.")  # detailed logs are written in 'save_User'
            return
        print('新增用户操作完成。')
        Logger.error(f"[Admin] Append new user success.")  # detailed logs are written in 'save_User'
        return
    elif choice == '3':
        isOk, uname = func_in_1_3()
        print()
        if not isOk:
            return
        tf = input(f"确认删除用户: \"{uname}\"? (y/n): ")
        print()
        if tf == 'y' or tf == 'Y':
            isDeleted = delete_user_by_username(uname)
            if not isDeleted:
                print("删除用户未成功。")
                Logger.error(f"[Admin] Delete user failure, maybe database error, user '{secret_a_string(uname)}'.")
                return
            Logger.info(f"[Admin] Delete user success, user '{secret_a_string(uname)}'.")
            print("用户删除完成。")
            return
        Logger.info(f"[Admin] Admin cancelled the operation of deleting user.")
        print("操作取消，无事发生。")
        return
    else:
        Logger.info("[Admin] Admin took a quick glance at model 'Admin-Operation.modifydata', but did nothing.")
        print("无事发生。")
    return


def _end_func() -> None:
    Logger.info("+" * 10 + " Model Admin-Operation.modifydata stop " + "+" * 10)
    print('执行完成。')


if __name__ == '__main__':
    # python -m Admin-Operation.modifydata
    Logger.info("+" * 10 + " Model Admin-Operation.modifydata start " + "+" * 10)
    atexit.register(_end_func)
    print("检测数据库服务中...")
    if not check_if_server_started():
        print("数据库服务未开启。")
        sys.exit(-1)
    main()
