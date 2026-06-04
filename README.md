# 乳此侦析 · 乳腺癌智能检测系统

## 项目简介

该项目为基于**乳腺 X 光图像**的乳腺癌检测系统，包含**乳腺癌病变预测**、**AI 知识解答**等功能。

技术栈：HTML/CSS/JS + Python/Flask

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

将 static/js/data/vars.js 中的 `DISABLE_INTERACTION_global` 设置为 `true` 即可。

该操作会禁止用户注册、提交检测、AI交互相关的操作，并隐藏需要开启服务器的提示。

当然，如果服务器并没有开启，但该值被设定为 `false`，它会被二次检测程序更改为 `true`。

## 其他说明

### 1. 关于config文件的使用

该项目中的 `config/*.yaml` 文件会被同目录下的 `configs.py` 文件读取并整合。故需要引入配置信息时，可以从 `configs.py` 中直接引入相关的变量。

### 2. 关于数据库的连接

该项目中的数据库默认通过 windows 免密连接进行登录。若需要通过账号与密码进行登录，请前往 config/database.yaml，将 `USE_UID_TO_LOGIN` 改为 `true`，并将 `UID` 与 `PWD` 改为你的账号密码。

### 3. 关于logs文件夹

在使用AI功能后，会在logs文件夹下生成 historical_dialogue/history.json 文件，用于存放你的AI问答记录。为便于查看，该文件采用文件而非数据库的存储方式，请勿随意修改，否则合法性检测程序会抛出异常。

在使用 X 光图检测功能后，会将你的检测记录保存在 logs/results 文件夹中，并按照登录用户名进行分类。用户名文件夹下的每一个文件夹即对应一次检测记录，文件夹名称为一个基于时间戳生成的字符串。所以，若需要标记某一次的检测，请将该字符串值进行一定的记录以便于查找。

另外，程序运行日志会保存在 logs/log 文件夹中，日志会按照日期进行自动分类。

### 4. 关于深度学习

你可以前往[这个仓库](https://github.com/qzddmyc/MammoPearl-Training)，以了解本项目中**机器学习**相关的内容。本项目采用的是其深度学习路线的产出结果。

当然，在本项目的 `static/assets/example_pics/` 文件夹下，存放了四张可以用作检测的样例图片，可以使用这些图片做测试。

**声明**：本项目检测结果仅供参考，不可替代执业医师的临床诊断，不能作为确诊依据。

### 5. 关于模型权重文件的分片

由于 GitHub 仓库本身的限制，大于 100MB 的文件无法被上传；所以在本仓库中，对两份模型权重文件进行了分片处理，分片与重组脚本位于[这里](./src/manage_weights.py)。

分片方法如下，仅供展示，不需要执行：
```bash
python -c "from src.manage_weights import split_files; split_files()"
```

在项目初始化时，这些分片文件会被自动重组。**你不需要对分片进行手动重组**，也不要干预 `static/assets/pth/` 中的文件，以免发生错误。

> 另外，由于权重文件导致本仓库较大，你可以使用以下命令来拉取本仓库：
> ```bash
> git clone https://ghfast.top/https://github.com/qzddmyc/MammoPearl-IBCDS.git
> ```
