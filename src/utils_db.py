import bcrypt
import pyodbc
from config.configs import DATABASE_CONFIG


def get_db_connection(printError=True):
    try:
        connection = pyodbc.connect(
            f"DRIVER={DATABASE_CONFIG['DRIVER']};"
            f"SERVER={DATABASE_CONFIG['SERVER']};"
            f"DATABASE={DATABASE_CONFIG['DB_NAME']};"
            f"Trusted_Connection={DATABASE_CONFIG['trusted_connection']}")
        return connection
    except Exception as e:
        if printError:
            print(f"数据库连接错误: {e}")
        return None


def check_if_server_started() -> bool:
    """检查数据库服务是否开启，不会额外输出任何信息"""
    connection = get_db_connection(False)
    if connection:
        connection.close()
        return True
    return False


def execute_query(query, params=None):
    """执行SQL查询并返回结果"""
    conn = get_db_connection()
    if not conn:
        print("无法建立数据库连接")
        return None
    try:
        with conn.cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # 处理查询结果
            if cursor.description:
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows]
            else:
                return []
    except Exception as e:
        print(f"查询执行错误: {e}")
        return None
    finally:
        conn.close()


def execute_non_query(query, params=None):
    """执行非查询操作(INSERT, UPDATE, DELETE)"""
    conn = get_db_connection()
    if not conn:
        print("无法建立数据库连接")
        return False

    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"非查询操作错误: {e}")
        conn.rollback()
        conn.close()
        return False


def check_value_exists(table_name: str, column_name: str, value: str) -> bool:
    """
    检查 SQL Server 数据库中指定表的列是否存在特定值
    :param table_name: 表名
    :param column_name: 列名
    :param value: 需要检查的值
    :return: 存在返回 True，否则 False
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 防止 SQL 注入，对表名和列名进行简单验证
            if not (table_name.isidentifier() and column_name.isidentifier()):
                raise ValueError("非法的表名或列名")

            query = f"SELECT COUNT(1) FROM {table_name} WHERE {column_name} = ?"
            cursor.execute(query, value)
            return cursor.fetchone()[0] > 0
    finally:
        conn.close()


def if_table_exists(table_name: str) -> bool:
    """ 判断指定表是否存在于数据库中 """
    query = """
        SELECT COUNT(*) AS table_count 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_NAME = ?
        """

    try:
        result = execute_query(query, (table_name,))

        if result is None:
            print(f"检查表 {table_name} 存在性时发生错误")
            return False

        # 解析查询结果
        table_count = result[0]['table_count']
        return table_count > 0

    except Exception as e:
        print(f"判断表存在性时出错: {e}")
        return False


def save_User(UserID: str, UserName: str, UserPwd: str) -> dict:
    """保存一个新的用户。包含数据独立性检验"""

    if check_value_exists(DATABASE_CONFIG['TableName_U'], DATABASE_CONFIG['ColName_ID'], UserID):
        return {
            'success': False,
            'info': 'Odd Event: generated userId repeated.',
            'code': 1
        }

    if check_if_usr_exist(UserName):
        return {'success': False, 'info': '用户名重复！', 'code': 2}

    def hash_password(password: str) -> bytes:
        """将明文密码转换为哈希值"""
        # 生成盐值并哈希密码
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed

    hashed_pwd = hash_password(UserPwd)

    query = f'INSERT INTO {DATABASE_CONFIG['TableName_U']} ({DATABASE_CONFIG['ColName_ID']}, {DATABASE_CONFIG['ColName_NAME']}, {DATABASE_CONFIG['ColName_PWD']}) VALUES (?, ?, ?)'
    values = (UserID, UserName, hashed_pwd)

    success = execute_non_query(query, values)
    if not success:
        return {'success': False, 'info': '向数据库添加密码信息错误！', 'code': 3}
    return {'success': True, 'info': 'ok', 'code': 0}


def verify_UserAccount_password(UserName: str, UserPwd: str) -> bool:
    """给定用户的Name与输入的密码，判断密码与数据库中的密码是否一致。需要独立判断用户名是否存在"""

    if not check_if_usr_exist(UserName):
        return False

    def get_UserAccount_password(__UserName):
        """查询指定用户的密码"""
        query = f"SELECT {DATABASE_CONFIG['ColName_PWD']} FROM {DATABASE_CONFIG['TableName_U']} WHERE {DATABASE_CONFIG['ColName_NAME']} = ?"
        params = (__UserName,)
        result = execute_query(query, params)

        if result:
            return result[0][DATABASE_CONFIG['ColName_PWD']]
        else:
            return None

    def verify_password(pwd: str, hashed_password: bytes) -> bool:
        """验证密码是否匹配哈希值"""
        return bcrypt.checkpw(pwd.encode('utf-8'), hashed_password)

    password_in_database = get_UserAccount_password(UserName)

    if not password_in_database:
        return False

    return verify_password(UserPwd, password_in_database)


def update_UserAccount_password(UserName: str, new_password: str) -> bool:
    """给定用户Name与新密码，将数据库中对应的密码更新为新密码的哈希值"""

    if not check_if_usr_exist(UserName):
        return False

    def hash_new_password(password: str) -> bytes:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt)

    def update_password_in_db(usrname: str, hashed_password: bytes) -> bool:
        query = f"UPDATE {DATABASE_CONFIG['TableName_U']} SET {DATABASE_CONFIG['ColName_PWD']} = ? WHERE {DATABASE_CONFIG['ColName_NAME']} = ?"
        params = (hashed_password, usrname)
        return execute_non_query(query, params)

    hashed_new_password = hash_new_password(new_password)
    return update_password_in_db(UserName, hashed_new_password)


def check_if_usr_exist(uname: str) -> bool:
    return check_value_exists(DATABASE_CONFIG['TableName_U'], DATABASE_CONFIG['ColName_NAME'], uname)


def delete_user_by_username(username: str) -> bool:
    """根据用户名删除用户记录"""
    delete_query = f"DELETE FROM {DATABASE_CONFIG['TableName_U']} WHERE {DATABASE_CONFIG['ColName_NAME']} = ?"
    result = execute_non_query(delete_query, (username,))
    return result
