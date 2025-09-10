# 乳此侦析 · 乳腺癌智能检测系统



### 项目初始化

1. 安装Python三方库
```shell
pip install -r requirements.txt
```

2. 开启数据库服务
```shell
sudo sc start MSSQLSERVER
```

3. 建立数据库
```shell
sqlcmd -Q "IBCDS"
```

4. 初始化数据库
```shell
python -m init.init_database
```

5. 运行程序
```shell
python app.py
```

6. 访问页面
```plaintext
http://127.0.0.1:8080
```



### 特殊操作

#### 1. 清除数据库数据
使用以下命令运行模块，并按照提示操作即可。
```shell
python -m Admin-Operation.cleardata
```

#### 2. 修改项目端口
修改config.yaml中的PORT值即可。

参考命令：
```shell
vim ./config/config.yaml
```

#### 3. 设置页面为仅访问，禁止所有与服务器相关的操作
将 /static/assets/data/vars.js 中的 `DISABLE_INTERACTION_global` 设置为 `true` 即可。

该操作会禁止用户注册、提交检测相关的操作，并隐藏需要开启服务器的提示。

当然，如果服务器并没有开启，该值会自动被设置为 `true`。

参考命令：
```shell
vim ./static/assets/data/vars.js
```



### 文件说明

#### 1. Admin-Operation
存放清除数据库所使用的文件，可以选择性清空表的数据，或删除整张表。

#### 2. config
项目配置文件夹。

包含：
- config.yaml：项目配置文件。导入方式：`from config.configs import BASE_CONFIG`
- database.yaml：数据库配置文件。导入方式：`from config.configs import DATABASE_CONFIG`
- configs.py：用于解析yaml文件并生成字典

#### 3. init
用于数据库的初始化。

使用方法见[项目初始化第4条](#项目初始化)。

#### 4. logs
在页面中使用了检测服务后自动生成。

会按照页面中使用的用户名自动分组；每组内文件夹的索引为基于该文件夹创建时间纳秒时间戳的十六进制数。

#### 5. src
Python主代码。

包含：
- utils.py：项目所依赖的工具函数
- utils_db.py：数据库所依赖的所有接口
- v1.py：检测与结果保存流程需要的所有函数

#### 6. static
项目静态文件。

包含：
- assets：项目所需的静态资源。
  - data：页面所需的js静态文本与常量
  - img：网页图标
  - pth：由pytorch训练得到的结果文件，用于检测
  - ResultTemplates：检测结果的模版文件
- css：所有css文件
- js：所有js文件

#### 7. templates
Flase框架用于存放模版文件的文件夹。包含了所有的html文件。
