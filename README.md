# 乳此侦析 · 乳腺癌智能检测系统

## 项目简介

该项目为“乳腺癌检测系统”的**框架**，其中并不包含真正的检测程序。

在该项目中，你可以实现：用户登录，AI问答，拟检测等。

请注意，如果你使用了检测的功能，其得到的结果为固定数值，无任何含义。当然，如果你想要实现真正的检测，请参考[此文档](./docs/self-detect.md)。

\* 项目技术栈为：原生HTML + Python Flask

## 项目优势

[项目优势](./docs/item-advantage.md)

## 环境依赖

确保本地环境满足以下版本要求：

1. 编程语言：Python

   版本：>= 3.12

2. 数据库：SQL Server
   
   版本：Microsoft SQL Server 2022 (RTM) - 16.0.1000.6 (X64)

## 项目初始化

1. 安装Python库与数据库的初始化

    运行 deploy.bat 即可，其中包含了以下命令：
    ```batch
    pip install -r requirements.txt
    sudo sc start MSSQLSERVER
    sqlcmd -Q "CREATE DATABASE IBCDS"
    python -m init.init_database
    ```
    在此暂不提供 Linux/macOS 版本的命令。

2. 运行程序
    ```batch
    python app.py
    ```
    如果报错数据库服务未被开启，请运行：
    ```batch
    sudo sc start MSSQLSERVER
    python app.py
    ```

3. 访问页面
    ```plaintext
    http://127.0.0.1:8080
    ```

## 其他文档
### 管理员：用户信息管理

[用户信息管理](./docs/userManagement.md)

### AI api key 配置

在使用该项目的 AI 问答功能之前，你需要自行配置一些内容：[AI-key配置](./docs/apiConfig.md)

## 特殊操作

### 1. 修改项目端口

当设备的端口存在冲突时，你可以通过修改 config.yaml 中的 `PORT` 值，改变本项目使用的端口号。

### 2. 设置页面为仅访问，禁止所有与服务器相关的操作

将 /static/assets/data/vars.js 中的 `DISABLE_INTERACTION_global` 设置为 `true` 即可。

该操作会禁止用户注册、提交检测、AI交互相关的操作，并隐藏需要开启服务器的提示。

当然，如果服务器并没有开启，但该值被设定为 `false`，它会被二次检测程序更改为 `true`。

## 其他说明

### 1. 关于config文件的使用

该项目中的 `config/*.yaml` 文件会被同目录下的 `configs.py` 文件读取并整合。故需要引入配置信息时，可以从 `configs.py` 中直接引入相关的变量。

### 2. 关于数据库的连接

该项目中的数据库默认通过 windows 免密连接进行登录。若需要通过账号与密码进行登录，请前往 /config/database.yaml，将 `USE_UID_TO_LOGIN` 改为 `true`，并将 `UID` 与 `PWD` 改为你的账号密码。

### 3. 关于logs文件夹

在使用AI功能后，会在logs文件夹下生成 historical_dialogue/history.json 文件，用于存放你的AI问答记录。为便于查看，该文件采用文件而非数据库的存储方式，请勿随意修改，否则合法性检测程序会抛出异常。

在使用图片检测功能后，会将你的检测记录保存在 /logs/results 文件夹中，并按照登录用户名进行分类。用户名文件夹下的每一个文件夹即对应一次检测记录，文件夹名称为一个基于时间戳生成的字符串。所以，若需要标记某一次的检测，请将该字符串值进行一定的记录以便于查找。

另外，程序运行日志会保存在 /logs/log 文件夹中，日志会按照日期进行自动分类。