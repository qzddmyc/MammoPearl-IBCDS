import bcrypt
import pyodbc
from config.configs import DATABASE_CONFIG
from src.logger_config import Logger
from src.utils import secret_a_string


def get_db_connection(printError=True) -> pyodbc.Connection | None:
    """
    连接数据库，并返回一个connection
    :param printError: 是否在连接数据库错误时输出错误
    """
    try:
        if not DATABASE_CONFIG['USE_UID_TO_LOGIN']:
            connection = pyodbc.connect(
                f"DRIVER={DATABASE_CONFIG['DRIVER']};"
                f"SERVER={DATABASE_CONFIG['SERVER']};"
                f"DATABASE={DATABASE_CONFIG['DB_NAME']};"
                f"Trusted_Connection={DATABASE_CONFIG['trusted_connection']}")
        else:
            connection = pyodbc.connect(
                f"DRIVER={DATABASE_CONFIG['DRIVER']};"
                f"SERVER={DATABASE_CONFIG['SERVER']};"
                f"DATABASE={DATABASE_CONFIG['DB_NAME']};"
                f"UID={DATABASE_CONFIG['UID']};"
                f"PWD={DATABASE_CONFIG['PWD']}"
            )
        _mode = 'user id and password' if DATABASE_CONFIG['USE_UID_TO_LOGIN'] else 'password-free login for windows'
        Logger.info(f"Database root: connection got, login mode: {_mode}")
        return connection
    except Exception as e:
        if printError:
            print(f"数据库连接错误: {e}")
        Logger.error(f"Database root: get connection error: {e}")
        return None


def check_if_server_started() -> bool:
    """检查数据库服务是否开启，不会额外输出任何信息"""
    Logger.info('Start to check server status of database service')
    connection = get_db_connection(False)
    if connection:
        connection.close()
        Logger.info('Database connection success')
        return True
    Logger.error("Database connection failure, user didn't start the database service")
    return False


def execute_query(query, params=None):
    """执行SQL查询并返回结果"""
    conn = get_db_connection()
    if not conn:
        Logger.error('Database root: get connection error while trying to exec a query')
        return None
    try:
        with conn.cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            if cursor.description:
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
                Logger.info(f"Database root: query operation success, result returned.")
                return [dict(zip(columns, row)) for row in rows]
            else:
                Logger.info(f"Database root: query operation success, an empty result returned.")
                return []
    except Exception as e:
        Logger.error(f"Database root: query operation error: {e}")
        return None
    finally:
        conn.close()


def execute_non_query(query, params=None):
    """执行非查询操作(INSERT, UPDATE, DELETE)"""
    conn = get_db_connection()
    if not conn:
        Logger.error('Database root: get connection error while trying to exec a non-query operation')
        return False

    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        conn.commit()
        conn.close()
        Logger.info(f"Database root: non-query operation success.")
        return True
    except Exception as e:
        Logger.error(f"Database root: non-query operation exec error: {e}")
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
            if not (table_name.isidentifier() and column_name.isidentifier()):
                Logger.error(f'[Test env] Database root: error happened while trying to check if a value exist: '
                             f'invalid table name or column name')
                raise ValueError("非法的表名或列名")

            query = f"SELECT COUNT(1) FROM {table_name} WHERE {column_name} = ?"
            cursor.execute(query, value)
            return cursor.fetchone()[0] > 0
    finally:
        Logger.info(f"Database root: check value exist function called.")
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
            Logger.warning(f"Database root: something error may happened in executing a query, by check table exist")
            return False

        table_count = result[0]['table_count']
        Logger.info(f"Database root: 'if table exists' function called, correct result returned")
        return table_count > 0

    except Exception as e:
        Logger.error(f"Database root: unexpected exception while trying to check if table exists: {e}")
        return False


def save_User(UserID: str, UserName: str, UserPwd: str) -> dict:
    """
    保存一个新的用户。包含数据独立性检验
    :return: a dict contains:
            - success: if user saved successfully
            - info: message
            - code: the error code, uses for command line tool
    """

    if check_value_exists(DATABASE_CONFIG['TableName_U'], DATABASE_CONFIG['ColName_ID'], UserID):
        Logger.warning(f"An odd thing happened: generated a repeated userId")
        return {
            'success': False,
            'info': 'Odd Event: generated userId repeated.',
            'code': 1
        }

    if check_if_usr_exist(UserName):
        Logger.warning(f"Trying to add a duplicate user to the database")
        return {'success': False, 'info': '用户名重复！', 'code': 2}

    def hash_password(password: str) -> bytes:
        """将明文密码转换为哈希值"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed

    hashed_pwd = hash_password(UserPwd)

    query = f"""
                INSERT INTO {DATABASE_CONFIG['TableName_U']} ({DATABASE_CONFIG['ColName_ID']}, 
                {DATABASE_CONFIG['ColName_NAME']}, {DATABASE_CONFIG['ColName_PWD']}) 
                VALUES (?, ?, ?)
            """
    values = (UserID, UserName, hashed_pwd)

    success = execute_non_query(query, values)
    if not success:
        Logger.error(f"Failure while exec a query operation, while saving a new user")
        return {'success': False, 'info': '向数据库进行添加操作时发生错误！', 'code': 3}
    Logger.info(f"Save new user '{secret_a_string(UserName)}' success")
    return {'success': True, 'info': 'ok', 'code': 0}


def verify_UserAccount_password(UserName: str, UserPwd: str) -> bool:
    """给定用户的Name与输入的密码，判断密码与数据库中的密码是否一致。需要独立判断用户名是否存在"""

    if not check_if_usr_exist(UserName):
        Logger.warning(f"Trying to check password of a missing user")
        return False

    def get_UserAccount_password(__UserName):
        """查询指定用户的密码"""
        query = f"""
                    SELECT {DATABASE_CONFIG['ColName_PWD']}
                    FROM {DATABASE_CONFIG['TableName_U']}
                    WHERE {DATABASE_CONFIG['ColName_NAME']} = ?
                """
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
        Logger.warning(f"Get empty result while trying to get password of user {secret_a_string(UserName)}.")
        return False

    Logger.info(f"Checking password for user: {secret_a_string(UserName)}")
    return verify_password(UserPwd, password_in_database)


def update_UserAccount_password(UserName: str, new_password: str) -> bool:
    """给定用户Name与新密码，将数据库中对应的密码更新为新密码的哈希值"""

    if not check_if_usr_exist(UserName):
        Logger.warning(f"Trying to undate password for a missing user")
        return False

    def hash_new_password(password: str) -> bytes:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt)

    def update_password_in_db(usrname: str, hashed_password: bytes) -> bool:
        query = f"""
                    UPDATE {DATABASE_CONFIG['TableName_U']}
                    SET {DATABASE_CONFIG['ColName_PWD']} = ?
                    WHERE {DATABASE_CONFIG['ColName_NAME']} = ?
                """
        params = (hashed_password, usrname)
        return execute_non_query(query, params)

    hashed_new_password = hash_new_password(new_password)
    _result = update_password_in_db(UserName, hashed_new_password)

    if not _result:
        Logger.error(f"Error in database while updating password for user {secret_a_string(UserName)}")
    return _result


def check_if_usr_exist(uname: str) -> bool:
    """检测一个用户在数据库中是否存在"""
    Logger.info(f"Trying to check if user {secret_a_string(uname)} in database...")
    return check_value_exists(DATABASE_CONFIG['TableName_U'], DATABASE_CONFIG['ColName_NAME'], uname)


def delete_user_by_username(username: str) -> bool:
    """根据用户名删除用户记录"""
    Logger.info(f"Trying to deleting user {secret_a_string(username)} from database...")
    delete_query = f"DELETE FROM {DATABASE_CONFIG['TableName_U']} WHERE {DATABASE_CONFIG['ColName_NAME']} = ?"
    result = execute_non_query(delete_query, (username,))
    return result
