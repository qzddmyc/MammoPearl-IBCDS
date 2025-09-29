import os
from typing import Tuple, Union

from src.utils import generate_short_unique_time_str, get_current_time, write_to_file
from src.utils_ai import get_reply_from_ai_and_save_json, INIT_check_if_json_available, check_and_get_full_json_by_v1
from src.utils_ai import check_if_unresolved_msg_resolves_and_get_it
from config.configs import BASE_CONFIG, AI_CONFIG

DOTS = '..' if os.path.basename(os.getcwd()) == 'src' else '.'


# 处理函数。True: 阳性，有概率是; False: 阴性，无事
def v1_inner(pic: bytes) -> Tuple[bool, float]:
    base_path = "../static/assets/pth"
    ...
    return False, 0.869


# Pass in a binary image file and the name (with suffix) of the image.
# Return the detection result formatted [True/False(to string), accuracy, the relative path of the directory].
def detect_if_Breast_Cancer_picture(pic: bytes, picName: str, usr: str) -> Tuple[str, str, str]:
    folder_path = os.path.join(DOTS, "logs", 'results', usr, generate_short_unique_time_str())
    try:
        os.makedirs(folder_path, exist_ok=True)
        print(f"文件夹创建成功：{folder_path}")
    except Exception as e:
        print(f"文件夹创建时失败：{e}")

    output_path = os.path.join(folder_path, picName)
    try:
        with open(output_path, 'wb') as f:
            f.write(pic)
        print(f"图片已成功保存至: {output_path}")
    except Exception as e:
        print(f"保存图片时出错: {e}")

    RES_TF, RES_ACC = v1_inner(pic)

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

    return res_A, res_B, folder_path


# 注意，这个函数只会返回bool作为是否将内容成功提交至AI，并不会返回AI的回复内容。原因是AI的回复需要时间，所以调用此函数后，不会及时返回回答。
# 调用该函数后，
#   若返回值为True，前端需要setInterval持续查询json中任务的完成状态。
#   若返回值为False，表示用户的问题处于未提交状态，不需更新页面。
def get_reply_in_ques_by_ai(usr_ipt):
    file_path = os.path.join(DOTS, *AI_CONFIG['HISTORY_PATH'])
    folder_path = os.path.dirname(file_path)
    if folder_path and not os.path.exists(folder_path):
        # 二次确认。在服务开启时已确认文件夹初始化
        try:
            os.makedirs(folder_path, exist_ok=True)
            print(f"文件夹创建成功：{folder_path}")
        except Exception as e:
            print(f"文件夹创建时失败：{e}")
    isOK, msg = get_reply_from_ai_and_save_json(usr_ipt, file_path)
    return isOK, msg


def init_for_AI_model() -> bool:
    file_path = os.path.join(DOTS, *AI_CONFIG['HISTORY_PATH'])
    canContinue = INIT_check_if_json_available(file_path)
    return canContinue


def get_all_json_data() -> Tuple[bool, Union[str, list], bool]:
    file_path = os.path.join(DOTS, *AI_CONFIG['HISTORY_PATH'])
    isOK, data, containUnresolved = check_and_get_full_json_by_v1(file_path)
    if not isOK:
        return False, data, False
    return isOK, data, containUnresolved


def check_status_or_get_newest_reply():
    file_path = os.path.join(DOTS, *AI_CONFIG['HISTORY_PATH'])
    isResolved, msg, shouldAbort = check_if_unresolved_msg_resolves_and_get_it(file_path)
    return isResolved, msg, shouldAbort
