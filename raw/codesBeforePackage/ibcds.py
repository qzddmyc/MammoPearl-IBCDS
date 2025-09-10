import argparse
import sys


def func1():
    """处理 ibcds.exe rm --data 命令"""
    print("执行 func1: 处理 rm --data 操作")


def func2():
    """处理 ibcds.exe rm --table 命令"""
    print("执行 func2: 处理 rm --table 操作")


def func3(user, pwd):
    """处理 ibcds.exe add -u/--user 和 -p/--pwd 命令"""
    print(f"执行 func3: 处理 add 操作，用户: {user}, 密码: {pwd}")


def func4(user):
    """处理 ibcds.exe rm -u/--user 命令"""
    print(f"执行 func4: 处理 rm 用户操作，用户: {user}")


def func5(user, newpwd):
    """处理 ibcds.exe modify -u/--user 和 -n/--newpwd 命令"""
    print(f"执行 func5: 处理 modify 操作，用户: {user}, 新密码: {newpwd}")


def func6():
    """处理 ibcds.exe ls 命令"""
    print("执行 func6: 处理 ls 操作（列出信息）")


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
        else:
            return self.get_general_help()

    @staticmethod
    def get_general_help():
        return """
★  ibcds 命令行工具

使用方法:
  ibcds <command> [选项]

可用命令:
  rm      执行删除操作
  add     添加用户
  modify  修改用户密码
  ls      列出信息

查看命令详情:
  ibcds <command> -h

"""

    @staticmethod
    def get_rm_help():
        return """
★  ibcds rm - 执行删除操作

使用方法:
  ibcds rm [选项]

选项:
  --data       删除表内所有数据
  --table      删除表（执行该操作后需要重新初始化数据库）
  -u, --user   指定要删除的用户

示例:
  ibcds rm --data
  ibcds rm --table
  ibcds rm -u username

"""

    @staticmethod
    def get_add_help():
        return """
★  ibcds add - 添加用户

使用方法:
  ibcds add -u <用户名> -p <密码>

选项:
  -u, --user   用户名（必填）
  -p, --pwd    密码（必填）

示例:
  ibcds add -u usr1 -p 12345678
  ibcds add --user usr2 --pwd password

"""

    @staticmethod
    def get_modify_help():
        return """
★  ibcds modify - 修改用户密码

使用方法:
  ibcds modify -u <用户名> -n <新密码>

选项:
  -u, --user   用户名（必填）
  -n, --newpwd 新密码（必填）

示例:
  ibcds modify -u usr1 -n 87654321
  ibcds modify --user usr2 --newpwd newpassword

"""

    @staticmethod
    def get_ls_help():
        return """
★  ibcds ls - 列出所有用户信息

使用方法:
  ibcds ls

说明:
  该命令无需任何参数，直接执行即可列出信息。

示例:
  ibcds ls

"""


def check_excess_arguments(args, command):
    """检查是否有多余的参数"""
    # 根据不同命令定义最大允许的参数数量
    max_args = {
        'rm': 3,  # ibcds rm [--data|--table|-u <user>]
        'add': 5,  # ibcds add -u <user> -p <pwd>
        'modify': 5,  # ibcds modify -u <user> -n <newpwd>
        'ls': 2  # ibcds ls
    }.get(command, 1)

    if len(sys.argv) > max_args:
        raise argparse.ArgumentError(None, f"错误: 命令 '{command}' 包含过多参数")


def main():
    # 优先检查是否需要显示帮助（在解析前处理）
    if len(sys.argv) >= 2:
        command = sys.argv[1]
        # 检查全局帮助
        if command in ['-h', '--help']:
            print(CustomHelpFormatter(None).get_general_help())
            sys.exit(0)
        # 检查子命令帮助
        if len(sys.argv) >= 3 and sys.argv[2] in ['-h', '--help']:
            formatter = CustomHelpFormatter(None, command)
            print(formatter.format_help())
            sys.exit(0)

    # 当没有传入任何参数时，显示全局帮助信息
    if len(sys.argv) == 1:
        print(CustomHelpFormatter(None).get_general_help())
        sys.exit(0)

    # 创建主解析器
    parser = argparse.ArgumentParser(
        prog='ibcds',
        add_help=False,
        formatter_class=lambda prog: CustomHelpFormatter(prog))

    # 创建子命令解析器
    subparsers = parser.add_subparsers(dest='command', required=True)

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

    # 解析命令行参数
    try:
        # 先解析出命令以进行参数数量检查
        command = sys.argv[1]
        check_excess_arguments(sys.argv, command)

        # 解析所有参数
        args = parser.parse_args()
    except argparse.ArgumentError as e:
        # 参数错误时只显示错误信息，不显示帮助内容
        print(f"错误: {e.message}")
        sys.exit(1)
    except Exception as e:
        print(f"错误: 发生未知错误 - {str(e)}")
        sys.exit(1)

    # 执行相应的函数
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


if __name__ == '__main__':
    # https://www.doubao.com/thread/we59ced4036910591
    # python ibcds.py rm 2
    main()
