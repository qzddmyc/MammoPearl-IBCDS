import os
from typing import Tuple, Union

from src.utils import generate_short_unique_time_str, get_current_time, write_to_file, \
    save_a_picture, generate_user_id, secret_a_string, encode_username, decode_username
from src.utils_ai import get_reply_from_ai_and_save_json, INIT_check_if_json_available, check_and_get_full_json_by_v1
from src.utils_ai import check_if_unresolved_msg_resolves_and_get_it
from src.utils_db import check_if_usr_exist, verify_UserAccount_password, save_User
from src.utils_crypto import encrypt_data, decrypt_data, generate_random_key_for_crypto
from config.configs import BASE_CONFIG, AI_CONFIG
from src.logger_config import Logger

DOTS = '..' if os.path.basename(os.getcwd()) == 'src' else '.'


def v1_inner(pic: bytes, base_path: str, pic_name: str) -> Tuple[bool, float]:
    """
    处理函数。True: 阳性，患病； False: 阴性，不患病
    :param pic: The picture to check if ill or not.
    :param base_path: The path uses for saving result pictures, you should not save the original picture.
    :param pic_name: The name of the original picture.
    :return: Judge result, Accuracy
    """

    # pth_file_path = os.path.join(DOTS, 'static', 'assets', 'pth', '???.pth')

    # if you wanna save a picture, use this:
    #   pic_bytes_info = ???
    #   new_pic_name = ???
    #   _, _suffix = os.path.splitext(pic_name)
    #   new_pic_path = os.path.join(base_path, new_pic_name + _suffix)
    #   isSaved = save_a_picture(pic_bytes_info, new_pic_path)

    # add your own logic here
    ...

    # here just gave a static value
    return False, 0.869


def detect_if_Breast_Cancer_picture(pic: bytes, picName: str, usrToken: str) -> Tuple[str, str, str]:
    """
    Pass in a binary image file and the name (with suffix) of the image.
    :param pic: The picture
    :param picName: The name of the picture
    :param usrToken: The user token of who was logged in
    :return: the detection result formatted [True/False(to Chinese str), accuracy, the relative path of the directory]
    """
    if usrToken == "" or not usrToken:
        usr = BASE_CONFIG['DEFAULT_USER']
    else:
        encodeOk, usr = token_to_username_and_check_existence(usrToken)
        if not encodeOk:
            Logger.error('Warn: User token decode error in detecting pics!')
            usr = BASE_CONFIG['DEFAULT_USER']
    folder_path = os.path.join(DOTS, "logs", 'results', usr, generate_short_unique_time_str())
    try:
        os.makedirs(folder_path, exist_ok=True)
        Logger.info(
            f"success in making directory: {folder_path}, in Func 'detect_if_Breast_Cancer_picture', in File 'v1.py'")
    except Exception as e:
        Logger.error(
            f"error in making directory: {folder_path}, error info: {e}, "
            f"in Func 'detect_if_Breast_Cancer_picture', in File 'v1.py'")

    output_path = os.path.join(folder_path, picName)
    if save_a_picture(pic, output_path):
        Logger.info(f"success in saving picture to: {output_path}, "
                    f"in Func 'detect_if_Breast_Cancer_picture', in File 'v1.py'")
    else:
        # logs were written in func 'save_a_picture'
        print(f"警告：图片'{output_path}'保存失败。详情见日志")

    RES_TF, RES_ACC = v1_inner(pic, folder_path, picName)

    # be careful that func showResultModal() in detect-main.js also uses name "阴性".
    res_A = '阳性' if RES_TF else '阴性'
    res_B = f"{(round(RES_ACC * 1000) / 10)}%"

    now = get_current_time()
    absolute_path_of_folder = os.path.abspath(folder_path)
    absolute_path_of_pic = os.path.abspath(output_path)

    corresponding_color = 'red' if RES_TF else 'blue'

    change_items_for_md = {
        '${usr}': usr,
        '${time}': now,
        '${imgNameWithSuffix}': picName,
        '${color}': corresponding_color,
        '${result}': res_A,
        '${accuracy}': res_B,
        '${folder}': absolute_path_of_folder
    }

    change_items_for_txt = {
        '${usr}': usr,
        '${time}': now,
        '${imgFullPath}': absolute_path_of_pic,
        '${result}': res_A,
        '${accuracy}': res_B,
        '${folder}': absolute_path_of_folder
    }

    template_path_md = os.path.join(DOTS, *BASE_CONFIG['TEMPLATE_PATH'], BASE_CONFIG['TEMPLATE_FILE_NAME_MD'])
    template_path_txt = os.path.join(DOTS, *BASE_CONFIG['TEMPLATE_PATH'], BASE_CONFIG['TEMPLATE_FILE_NAME_TXT'])

    with open(template_path_md, 'r', encoding='utf-8') as f_md:
        md_content = f_md.read()
        for k, v in change_items_for_md.items():
            md_content = md_content.replace(k, v)
        write_to_file(os.path.join(folder_path, f'{BASE_CONFIG['RESULT_FILE_NAME']}.md'), md_content)

    with open(template_path_txt, 'r', encoding='utf-8') as f_txt:
        txt_content = f_txt.read()
        for k, v in change_items_for_txt.items():
            txt_content = txt_content.replace(k, v)
        write_to_file(os.path.join(folder_path, f'{BASE_CONFIG['RESULT_FILE_NAME']}.txt'), txt_content)

    Logger.info(f"Read templates and save detect result success, user: {usr}, folder: {absolute_path_of_folder}")

    return res_A, res_B, folder_path


def get_reply_in_ques_by_ai(usr_ipt) -> Tuple[bool, str]:
    """
    注意，这个函数只会返回bool作为是否将内容成功提交至AI，并不会返回AI的回复内容。原因是AI的回复需要时间，所以调用此函数后，不会及时返回回答。
    调用该函数后，
    若返回值为True，前端需要setInterval持续查询json中任务的完成状态。
    若返回值为False，表示用户的问题处于未提交状态，不需更新页面。
    :param usr_ipt: The questions asked by user to the AI
    :return: [is submission success, message]
    """
    file_path = os.path.join(DOTS, *AI_CONFIG['HISTORY_PATH'])
    folder_path = os.path.dirname(file_path)
    if folder_path and not os.path.exists(folder_path):
        # double confirmation
        Logger.warning(f"Double check triggered: The directory '{folder_path}' uses in Func 'get_reply_in_ques_by_ai' "
                       f"does not exist, it should be created before. In File 'v1.py'")
        try:
            os.makedirs(folder_path, exist_ok=True)
            Logger.info(f"continue by the previous log: directory created successfully")
        except Exception as e:
            Logger.warning(f"continue by the previous log: directory created failure: {e}")
    isOK, msg = get_reply_from_ai_and_save_json(usr_ipt, file_path)
    if not isOK:
        Logger.warning(f"Submitting the request to AI error: {msg}, in Func 'get_reply_in_ques_by_ai', in File 'v1.py'")
    else:
        Logger.info(f"Submitting the request to AI and write unresolved message to file successfully")
    return isOK, msg


def init_for_AI_model() -> bool:
    """
    Init for the AI model, includes init the file, check the format, and delete the unresolved messages.
    :return: Is initial success
    """
    Logger.info(f"Start to initiate for AI history file")
    file_path = os.path.join(DOTS, *AI_CONFIG['HISTORY_PATH'])
    canContinue = INIT_check_if_json_available(file_path)
    if canContinue:
        Logger.info("Initiation for AI history file successfully")
    # While failure, logs will be written in Func 'INIT_check_if_json_available'.
    return canContinue


def get_all_json_data() -> Tuple[bool, Union[str, list], bool]:
    """
    Get the history.json for init(or when refreshing the page), allow at most one unresolved message at the top size.
    If contains unresolved message, the app should be now querying for the answer,
        and the front-end will consistently query for the reply.
    :return: [if something error happened; error message or the full data; if the first message is unresolved]
    """
    file_path = os.path.join(DOTS, *AI_CONFIG['HISTORY_PATH'])
    isOK, data, containUnresolved = check_and_get_full_json_by_v1(file_path)
    if not isOK:
        Logger.error(f"Func 'check_and_get_full_json_by_v1' returned a wrong status: {data}, "
                     f"in Func 'get_all_json_data', in File 'v1.py'")
        return False, data, False
    # Success logs are written in func check_and_get_full_json_by_v1.
    return isOK, data, containUnresolved


def check_status_or_get_newest_reply():
    """
    This function is uses by front-end for a consistent query for the AI's reply.
    :return: [Is AI's reply got; AI's reply or the error message; Should the front-end abort query]
    """
    file_path = os.path.join(DOTS, *AI_CONFIG['HISTORY_PATH'])
    isResolved, msg, shouldAbort = check_if_unresolved_msg_resolves_and_get_it(file_path)
    if isResolved:
        Logger.info('Trough query, found AI already replied the quiz. Consistent querying ends')
    if shouldAbort:
        Logger.error(f"Trough query, found something error while checking AI's reply: {msg}")
    if not isResolved and not shouldAbort:
        Logger.info('Trough query, found AI still working...')
    return isResolved, msg, shouldAbort


def login_for_user(s_username: str, s_password: str, key: str, iv: str) -> Tuple[bool, str, str]:
    """ s_username & s_password are base64 """
    if not s_username or not s_password or not key or not iv:
        return False, 'parameters missing', ''
    username = decrypt_data(s_username, key, iv)
    password = decrypt_data(s_password, key, iv)
    if not check_if_usr_exist(username):
        return False, '登录失败：用户不存在，请先注册', ''
    IsPwdCorrect = verify_UserAccount_password(username, password)
    if IsPwdCorrect:
        token_uname = encode_username(username)
        if not token_uname:
            Logger.error('Fatal: get token from userName error!')
            return False, '登录成功，但令牌生成失败', ''
        return True, '登录成功。即将跳转至主页', token_uname
    Logger.warning(f"Login failure: user '{secret_a_string(username)}' gave an error password.")
    return False, '登录失败：密码错误', ''


def register_for_user(s_username: str, s_password: str, key: str, iv: str) -> Tuple[bool, str]:
    if not s_username or not s_password or not key or not iv:
        return False, 'parameters missing'
    username = decrypt_data(s_username, key, iv)
    password = decrypt_data(s_password, key, iv)
    if not username.strip() or not password.strip():
        return False, '注册失败：账号或密码不能为空值'
    if check_if_usr_exist(username):
        return False, '注册失败：用户已存在，请直接登录'
    spec_id = generate_user_id()
    info = save_User(spec_id, username, password)
    if not info['success']:
        Logger.error('Fatal: error happened in register_for_user!')
        return False, f'注册失败：{info['message']}'
    Logger.info(f'User register success: user {secret_a_string(username)}.')
    return True, '注册成功，请继续登录'


def token_to_crypto_username(token: str) -> Tuple[bool, str, str, str]:
    encodeOk, uname = token_to_username_and_check_existence(token)
    if not encodeOk:
        Logger.error(f'decode username error, and func token_to_crypto_username returns a false.')
        return False, '', '', ''
    key, iv = generate_random_key_for_crypto(), generate_random_key_for_crypto()
    s_uname = encrypt_data(uname, key, iv)
    return True, s_uname, key, iv


def token_to_username_and_check_existence(t: str) -> Tuple[bool, str]:
    raw_uname = decode_username(t)
    if not raw_uname or not check_if_usr_exist(raw_uname):
        Logger.error(f'decode username error in func token_to_username_and_check_existence')
        return False, ''
    return True, raw_uname
