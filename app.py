import os
import sys
import logging
import threading
from flask import Flask, render_template, request, jsonify

from src.v1 import detect_if_Breast_Cancer_picture, get_reply_in_ques_by_ai, init_for_AI_model, get_all_json_data
from src.v1 import check_status_or_get_newest_reply, login_or_register_for_user
from src.utils import open_file_in_system, check_web_conn
from src.utils_db import check_if_server_started
from src.utils_ai import check_if_environ_created
from config.configs import BASE_CONFIG
from src.logger_config import Logger

app = Flask(__name__)

__Counter_get_status = 0

logging.getLogger('werkzeug').setLevel(logging.ERROR)


def print_tips():
    print(f" * Running on http://127.0.0.1:{BASE_CONFIG['PORT']}")
    print(f"{BASE_CONFIG['COLORS']['yellow']}Press CTRL+C to quit{BASE_CONFIG['COLORS']['reset']}")


@app.route('/')
@app.route('/index.html')
def index():
    Logger.info('GET /index.html')
    return render_template('index.html')


@app.route('/detect.html')
def detect():
    Logger.info('GET /detect.html')
    return render_template('detect.html')


@app.route('/ques.html')
def question():
    Logger.info('GET /ques.html')
    return render_template('ques.html')


@app.route('/login.html')
def login():
    Logger.info('GET /login.html')
    return render_template('login.html')


@app.route('/advan.html')
def advance():
    Logger.info('GET /advan.html')
    return render_template('advan.html')


@app.route('/api/check_conn', methods=['POST'])
def check_conn():
    Logger.info('POST /api/check_conn')
    text_data = request.get_data(as_text=True)
    if text_data == 'hello':
        return jsonify({
            'success': True
        })
    return jsonify({
        'success': False
    })


@app.route('/api/v1', methods=['POST'])
def api_v1():
    """ according to the picture, return the result about is cancer or not. """
    Logger.info('POST /api/v1')
    file = request.files.get('image_data')

    if not file:
        Logger.error('No image found in the request.')
        return jsonify({
            'success': False,
            'message': 'No images found through submitted request.'
        })

    pic_bytes = file.read()
    pic_name = file.filename
    usr = request.form.get('usr')
    if not usr:
        usr = BASE_CONFIG['DEFAULT_USER']

    RES_TF, RES_ACC, dir_path = detect_if_Breast_Cancer_picture(pic_bytes, pic_name, usr)

    return jsonify({
        'success': True,
        'RES_TF': RES_TF,
        'RES_ACC': RES_ACC,
        'relative_dir_path': dir_path
    })


@app.route('/api/open_file', methods=['POST'])
def api_open_file():
    """
    get the relative path ends with the random dir, and the suffix 'md' or 'txt',
    then open 'path/{BASE_CONFIG['RESULT_FILE_NAME']}.(md|txt)' file
    """
    Logger.info('POST /api/open_file')
    data = request.get_json()
    file_path = data.get('dir_path', '')
    file_type = data.get('file_type', '')

    if not file_path or not file_path:
        return jsonify({
            'success': False,
            'message': 'parameters missing'
        })

    relative_path_for_utils = os.path.join(file_path, f'{BASE_CONFIG['RESULT_FILE_NAME']}.{file_type}')
    is_open, msg = open_file_in_system(relative_path_for_utils)

    return jsonify({
        'success': is_open,
        'message': msg
    })


@app.route('/api/login', methods=['POST'])
def api_login():
    Logger.info('POST /api/login')

    data = request.get_json()
    username = data.get('usrName', '')
    password = data.get('usrPwd', '')

    success, message = login_or_register_for_user(username, password)
    return jsonify({
        'success': success,
        'message': message
    })


@app.route('/api/send_msg_to_ai', methods=['POST'])
def send_msg_to_ai():
    Logger.info('POST /api/send_msg_to_ai')
    usrIpt = request.get_data(as_text=True)
    success, msg = get_reply_in_ques_by_ai(usrIpt)
    return jsonify({
        'success': success,
        'data': msg
    })


@app.route('/api/get_full_json', methods=['GET'])
def get_full_json():
    # use this func to init QA list
    Logger.info('GET /api/get_full_json')
    success, data, containUnresolved = get_all_json_data()
    if not success:
        return jsonify({
            'success': False,
            'data': data,
            'unresolved': False
        })
    return jsonify({
        'success': True,
        'data': data,
        'unresolved': containUnresolved
    })


@app.route('/api/get_status', methods=['GET'])
def get_status():
    """ this func is uses to check if AI replied the query, it may be a consistent call to this func """
    global __Counter_get_status
    __Counter_get_status += 1
    Logger.info(f'GET /api/get_status - {__Counter_get_status}')
    isResolved, msg, shouldAbort = check_status_or_get_newest_reply()
    if isResolved or shouldAbort:
        # Other logs were written in func 'check_status_or_get_newest_reply'
        __Counter_get_status = 0
    return jsonify({
        'resolve': isResolved,
        'message': msg,
        'error': shouldAbort
    })


@app.route('/api/check_api_environ', methods=['GET'])
def check_api_environ():
    Logger.info('GET /api/check_api_environ')
    return jsonify({
        'exist': check_if_environ_created()
    })


@app.route('/api/logger', methods=['POST'])
def write_logger():
    Logger.info('POST /api/logger')
    data = request.get_json()
    _undefined = 'undefined'
    logger_level = data.get('logger_level', _undefined)
    logger_message = data.get('logger_message', _undefined)
    if logger_level == _undefined:
        return jsonify({
            'success': False,
            'message': 'undefined logger message'
        })
    match logger_level:
        case 'info':
            Logger.info(logger_message)
        case 'warning':
            Logger.warning(logger_message)
        case 'error':
            Logger.error(logger_message)
        case 'critical':
            Logger.critical(logger_message)
        case _:
            Logger.warning(f"Got an undefined log level: {logger_level}, along with message: {logger_message}")
            return jsonify({
                'success': False,
                'message': f'unknown logger level: {logger_level}'
            })
    return jsonify({
        'success': True,
        'message': 'ok'
    })


def main():
    Logger.info("+" * 20 + " Service start " + "+" * 20)
    # Log of 'service stop' is written in src.utils_ai._shutdown_thread_pool, after closing thread pool.
    print(" * 联网检测中 " + "-" * 17, end='\t')
    if not check_web_conn():
        print("检测到网络未连接。")
        sys.exit(-1)
    print("成功")
    print(" * 检测数据库服务中 " + "-" * 11, end='\t')
    if not check_if_server_started():
        print("数据库服务未开启。")
        sys.exit(-1)
    print("成功")
    print(" * 初始化AI历史记录文件中 " + "-" * 5, end='\t')
    if not init_for_AI_model():
        print("AI的文件相关功能初始化异常，请根据日志自行检查。")
        sys.exit(-1)
    print("成功")
    _timer = threading.Timer(interval=0.5, function=print_tips)
    _timer.start()
    app.run(debug=False, port=BASE_CONFIG['PORT'])


if __name__ == '__main__':
    main()
