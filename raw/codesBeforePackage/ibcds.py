import sys
import argparse
import wcwidth
from tabulate import tabulate

from config.configs import DATABASE_CONFIG
from src.utils import is_usrName_ok, is_usrPwd_ok, generate_user_id
from src.utils_db import check_if_server_started, if_table_exists, execute_non_query, save_User, check_if_usr_exist, \
    delete_user_by_username, update_UserAccount_password, execute_query


class ExecException(Exception):
    """执行异常时raise该错误即可，程序自动退出"""
    pass


def exec_success_showInfo_and_exit(info):
    """执行成功时调用此函数，会输出成功信息并退出"""
    print(info)
    sys.exit(0)


def func1():
    """处理 ibcds.exe rm --data 命令"""
    t = DATABASE_CONFIG['TableName_U']
    if not if_table_exists(t):
        raise ExecException(f'Error: Table "{t}" does not exist.')
    query = f"DELETE FROM {t}"
    if execute_non_query(query):
        exec_success_showInfo_and_exit(f'Success in clearing info in table "{t}".')
    else:
        raise ExecException(f'Error in executing query: "{query}".')


def func2():
    """处理 ibcds.exe rm --table 命令"""
    t = DATABASE_CONFIG['TableName_U']
    if not if_table_exists(t):
        raise ExecException(f'Error: Table "{t}" does not exist.')
    query = f"DROP TABLE IF EXISTS {t}"
    if execute_non_query(query):
        exec_success_showInfo_and_exit(f'Success in dropping table "{t}".')
    else:
        raise ExecException(f'Error in executing query: "{query}".')


def func3(user, pwd):
    """处理 ibcds.exe add -u/--user 和 -p/--pwd 命令"""
    if not is_usrName_ok(user):
        raise ExecException(
            f'User name "{user}" is invalid, it should match ' + r'"^[\u4e00-\u9fa5a-zA-Z0-9_-]{1,10}$"')
    if not is_usrPwd_ok(pwd):
        raise ExecException(f'Password "{pwd}" is invalid, it should match ' + r'"^[a-zA-Z0-9_]{6,18}$"')
    idid = generate_user_id()
    info = save_User(idid, user, pwd)
    match info['code']:
        case 0:
            exec_success_showInfo_and_exit(f'Success in appending user "{user}".')
        case 1:
            raise ExecException(f'Odd error in appending user: id generated repeated. You can try your command again.')
        case 2:
            raise ExecException(f'Error: user name {user} already exists.')
        case 3:
            raise ExecException('Error happened in database.')
        case _:
            raise ExecException('You will not get this information.')


def func4(user):
    """处理 ibcds.exe rm -u/--user 命令"""
    if not check_if_usr_exist(user):
        raise ExecException(f'Error: user "{user}" does not exist.')
    if not delete_user_by_username(user):
        raise ExecException('Error happened in database.')
    exec_success_showInfo_and_exit(f'Success in deleting user "{user}".')


def func5(user, newpwd):
    """处理 ibcds.exe modify -u/--user 和 -n/--newpwd 命令"""
    if not check_if_usr_exist(user):
        raise ExecException(f'Error: user "{user}" does not exist.')
    if not is_usrPwd_ok(newpwd):
        raise ExecException(f'Password "{newpwd}" is invalid, it should match ' + r'"^[a-zA-Z0-9_]{6,18}$"')
    if not update_UserAccount_password(user, newpwd):
        raise ExecException('Error happened in database.')
    exec_success_showInfo_and_exit(f'Success in updating password of "{user}".')


def func6():
    """处理 ibcds.exe ls 命令"""

    def chinese_aware_ljust(s, width):
        """中文-aware的左对齐函数"""
        str_width = wcwidth.wcswidth(str(s))
        spaces_needed = max(0, width - str_width)
        return str(s) + ' ' * spaces_needed

    table = DATABASE_CONFIG['TableName_U']
    item = DATABASE_CONFIG['ColName_NAME']

    usernames = execute_query(f"SELECT {item} FROM {table}")

    if usernames is None:
        raise ExecException("Error: Query failure, something went wrong with database.")
    if not usernames:
        raise ExecException("Empty information.")

    max_width = max(wcwidth.wcswidth(str(row[item])) for row in usernames)
    header_width = max(max_width, wcwidth.wcswidth(item))

    headers = [item]
    table_data = [[chinese_aware_ljust(str(row[item]), header_width)] for row in usernames]
    print('\nFound the following information:')
    exec_success_showInfo_and_exit(tabulate(table_data, headers=headers, tablefmt="grid", colalign=("left",)))


def global_error(message):
    print(f'\nError: {message}', file=sys.stderr)
    info = ("\nTips: 'ibcds -h' list available subcommands and some concept guides."
            "\n      See 'ibcds <command> -h' to read about a specific subcommand.")
    print(info, file=sys.stderr)
    sys.exit(1)


class NoHelpOnErrorParser(argparse.ArgumentParser):
    def error(self, message):
        # sys.stderr.write(f'{self.prog}: error: {message}\n')
        global_error(message)


# 自定义帮助信息格式化器
class CustomHelpFormatter(argparse.HelpFormatter):
    def __init__(self, parser, command=None):
        super().__init__(parser)
        self.command = command

    def format_help(self):
        if self.command == 'rm':
            return self.get_rm_help()
        elif self.command == 'add':
            return self.get_add_help()
        elif self.command == 'modify':
            return self.get_modify_help()
        elif self.command == 'ls':
            return self.get_ls_help()
        elif self.command is None:
            return self.get_general_help()
        else:
            global_error(f"Unknown command in getting help: {self.command}")

    @staticmethod
    def get_general_help():
        return """
ibcds 命令行工具

使用方法:
  ibcds <command> [选项]

可用命令:
  rm      执行删除操作
  add     添加用户
  modify  修改用户密码
  ls      列出所有用户信息

查看命令详情:
  ibcds <command> -h
  
注意：
  所有操作均无二次确认，请谨慎操作"""

    @staticmethod
    def get_rm_help():
        return """
ibcds rm - 执行删除操作

使用方法:
  ibcds rm [选项]

选项:
  --data       删除表内所有数据
  --table      删除表（执行该操作后需要重新初始化数据库）
  -u, --user   指定要删除的用户

示例:
  ibcds rm --data
  ibcds rm --table
  ibcds rm -u username"""

    @staticmethod
    def get_add_help():
        return """
ibcds add - 添加用户

使用方法:
  ibcds add -u <用户名> -p <密码>

选项:
  -u, --user   用户名（必填）
  -p, --pwd    密码（必填）

示例:
  ibcds add -u usr1 -p 12345678
  ibcds add --user usr2 --pwd password"""

    @staticmethod
    def get_modify_help():
        return """
ibcds modify - 修改用户密码

使用方法:
  ibcds modify -u <用户名> -n <新密码>

选项:
  -u, --user   用户名
  -n, --newpwd 新密码

示例:
  ibcds modify -u usr1 -n 87654321
  ibcds modify --user usr2 --newpwd newpassword"""

    @staticmethod
    def get_ls_help():
        return """
ibcds ls - 列出所有用户信息

使用方法:
  ibcds ls

说明:
  该命令无需任何参数，直接执行即可列出信息。

示例:
  ibcds ls"""


# def check_excess_arguments(args, command):
#     """检查是否有多余的参数。不再使用，采用argparse库自带的错误分析机制"""
#     # 根据不同命令定义最大允许的参数数量
#     len_args = {
#         'rm': 3,  # ibcds rm [--data|--table|-u <user>]
#         'add': 6,  # ibcds add -u <user> -p <pwd>
#         'modify': 6,  # ibcds modify -u <user> -n <newpwd>
#         'ls': 2  # ibcds ls
#     }.get(command, -1)
#
#     if command == 'rm' and len(args) > 2 and (args[2] == '-u' or args[2] == '--user'):
#         len_args += 1
#
#     if len_args == -1:
#         if len(args) == 2:
#             raise argparse.ArgumentError(None, f"Unexpected command: {command}")
#         raise argparse.ArgumentError(None,
#                                      f"Unexpected command: {command}, unexpected arguments: {' '.join(args[2:])}")
#
#     if len(sys.argv) > len_args:
#         raise argparse.ArgumentError(None, f"Command '{command}' contains more arguments than expected")
#     return


def main():
    # 优先检查是否需要显示帮助（在解析前处理）
    if len(sys.argv) >= 2:
        command = sys.argv[1]
        # 检查全局帮助
        if command in ['-h', '--help']:
            if len(sys.argv) > 2:
                global_error(f"Unexpected argument(s): {' '.join(sys.argv[2:])}")
            print(CustomHelpFormatter(None).get_general_help())
            sys.exit(0)
        # 检查子命令帮助
        if len(sys.argv) >= 3 and sys.argv[2] in ['-h', '--help']:
            if len(sys.argv) > 3:
                global_error(f"Unexpected argument(s): {' '.join(sys.argv[3:])}")
            formatter = CustomHelpFormatter(None, command)
            print(formatter.format_help())
            sys.exit(0)

    # 当没有传入任何参数时，显示全局帮助信息
    if len(sys.argv) == 1:
        print(CustomHelpFormatter(None).get_general_help())
        sys.exit(0)

    # 创建主解析器
    parser = NoHelpOnErrorParser(
        prog='ibcds',
        add_help=False,
        formatter_class=lambda prog: CustomHelpFormatter(prog))

    # 创建子命令解析器
    subparsers = parser.add_subparsers(dest='command',
                                       required=True,
                                       parser_class=NoHelpOnErrorParser)

    # 处理 rm 子命令
    rm_parser = subparsers.add_parser(
        'rm',
        add_help=False,
        formatter_class=lambda prog: CustomHelpFormatter(prog, 'rm'))
    rm_group = rm_parser.add_mutually_exclusive_group(required=True)
    rm_group.add_argument('--data', action='store_true')
    rm_group.add_argument('--table', action='store_true')
    rm_group.add_argument('-u', '--user')

    # 处理 add 子命令
    add_parser = subparsers.add_parser(
        'add',
        add_help=False,
        formatter_class=lambda prog: CustomHelpFormatter(prog, 'add'))
    add_parser.add_argument('-u', '--user', required=True)
    add_parser.add_argument('-p', '--pwd', required=True)

    # 处理 modify 子命令
    modify_parser = subparsers.add_parser(
        'modify',
        add_help=False,
        formatter_class=lambda prog: CustomHelpFormatter(prog, 'modify'))
    modify_parser.add_argument('-u', '--user', required=True)
    modify_parser.add_argument('-n', '--newpwd', required=True)

    # 处理 ls 子命令
    ls_parser = subparsers.add_parser(
        'ls',
        add_help=False,
        formatter_class=lambda prog: CustomHelpFormatter(prog, 'ls'))

    args = None
    try:
        # command = sys.argv[1]
        # check_excess_arguments(sys.argv, command)
        args = parser.parse_args()
    except argparse.ArgumentError as e:
        global_error(e)
    except Exception as e:
        print(f"错误: 发生未知错误 - {str(e)}")
        sys.exit(1)

    try:
        if args.command == 'rm':
            if args.data:
                func1()
            elif args.table:
                func2()
            elif args.user:
                func4(args.user)
        elif args.command == 'add':
            func3(args.user, args.pwd)
        elif args.command == 'modify':
            func5(args.user, args.newpwd)
        elif args.command == 'ls':
            func6()
    except ExecException as e:
        print(e, file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    # https://www.doubao.com/thread/we59ced4036910591
    # doc: https://docs.python.org/zh-cn/3.13/library/argparse.html
    # to test, run: python -m raw.codesBeforePackage.ibcds
    if not check_if_server_started():
        print('数据库服务未开启')
        sys.exit(1)
    main()
