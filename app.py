import os
from flask import Flask, render_template, request, jsonify
from src.v1 import detect_if_Breast_Cancer_picture, get_reply_in_ques_by_ai, init_for_AI_model
from src.utils import open_file_with_explorer, generate_user_id
from src.utils_db import check_if_usr_exist, verify_UserAccount_password, save_User, check_if_server_started
from config.configs import BASE_CONFIG

app = Flask(__name__)


@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')


@app.route('/detect.html')
def detect():
    return render_template('detect.html')


@app.route('/ques.html')
def question():
    return render_template('ques.html')


@app.route('/login.html')
def login():
    return render_template('login.html')


@app.route('/api/check_conn', methods=['POST'])
def check_conn():
    text_data = request.data.decode('utf-8')
    if text_data == 'hello':
        return jsonify({
            'success': True
        })
    return jsonify({
        'success': False
    })


# according to the picture, return the result about is cancer or not.
@app.route('/api/v1', methods=['POST'])
def api_v1():
    file = request.files['image_data']

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


# get the relative path ends with the random dir, and the suffix 'md' or 'txt',
# then open 'path/{BASE_CONFIG['RESULT_FILE_NAME']}.(md|txt)' file
@app.route('/api/open_file', methods=['POST'])
def api_open_file():
    data = request.get_json()
    file_path = data.get('dir_path', '')
    file_type = data.get('file_type', '')

    # if not file_path or not file_type:
    #     return jsonify({
    #         'success': False,
    #         'message': 'ERROR-IN-TEST: Fail to Get Json Data in /api/open_file.'
    #     })

    relative_path_for_utils = os.path.join(file_path, f'{BASE_CONFIG['RESULT_FILE_NAME']}.{file_type}')
    is_open, msg = open_file_with_explorer(relative_path_for_utils)

    return jsonify({
        'success': is_open,
        'message': msg
    })


@app.route('/api/login', methods=['POST'])
def api_login():
    username = request.form.get('usrName')
    password = request.form.get('usrPwd')

    if check_if_usr_exist(username):
        IsPwdCorrect = verify_UserAccount_password(username, password)
        if IsPwdCorrect:
            return jsonify({
                'success': True,
                'message': '登录成功。即将跳转至主页'
            })
        return jsonify({
            'success': False,
            'message': '登录失败：密码错误'
        })
    else:
        spec_id = generate_user_id()
        info = save_User(spec_id, username, password)
        if not info['success']:
            return jsonify({
                'success': False,
                'message': f'注册失败：{info['message']}'
            })
        return jsonify({
            'success': True,
            'message': '注册成功，已自动登录。即将跳转至主页'
        })


@app.route('/api/send_msg_to_ai', methods=['POST'])
def send_msg_to_ai():
    usrIpt = request.data.decode('utf-8')
    success, msg = get_reply_in_ques_by_ai(usrIpt)
    return jsonify({
        'success': success,
        'data': msg
    })


if __name__ == '__main__':
    print("检测数据库服务中...")
    if check_if_server_started():
        if init_for_AI_model():
            app.run(debug=False, port=BASE_CONFIG['PORT'])
        else:
            print("AI的文件相关功能初始化异常，请根据输出信息自行检查。")
    else:
        print("数据库服务未开启。")
