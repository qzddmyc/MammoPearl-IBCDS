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



### 管理员行为指南

> 该项目提供了两份供管理员管理用户信息的接口：一份为python文件，包含基于控制台的交互式UI操作；另一份为二进制可执行文件，可以在终端通过命令行使用。

#### 1. UI 操作

1. 清除数据库数据

> 包含了清空表内数据与删除整张表的操作。

使用以下命令运行模块，并按照提示操作即可。
```shell
python -m Admin-Operation.cleardata
```

2. 操作用户信息

> 包含修改密码、新增用户、删除用户操作。

使用以下命令运行模块，并按照提示操作即可。
```shell
python -m Admin-Operation.modifydata
```

#### 2. 命令行操作

1. 使用方式

可以按以下示例使用该命令行工具（该指令会输出帮助信息）：
```shell
bin/ibcds -h
```

当然，也可以将"**项目路径/bin**"添加至环境变量并重启设备，即可在**项目根目录下（终端位置）**直接使用`ibcds -h`执行该命令。
值得注意的是，`ibcds`并不是一个全局可用的命令，它依赖本项目中的部分文件。

2. 源代码及打包方式

该文件打包前的源代码位于raw/codesBeforePackage/ibcds.py，打包方式如下：

- 前置条件（请根据命令自行检查）：
```shell
pip install pyinstaller
rm -r bin
```

- 打包并放入bin文件夹下：
```shell
cp raw/codesBeforePackage/ibcds.py ibcds.py
pyinstaller -F ibcds.py
rm ibcds.spec
rm -r build
rm ibcds.py
mkdir -p bin
mv dist/* bin/
rmdir dist
```
注意，打包时的.py文件必须位于项目根目录下，否则会无法执行。



### 特殊操作

#### 1. 修改项目端口
修改config.yaml中的PORT值即可。

参考命令：
```shell
vim ./config/config.yaml
```

#### 2. 设置页面为仅访问，禁止所有与服务器相关的操作
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

#### 2. bin
存放二进制文件。

#### 3. config
项目配置文件夹。

包含：
- config.yaml：项目配置文件。导入方式：`from config.configs import BASE_CONFIG`
- database.yaml：数据库配置文件。导入方式：`from config.configs import DATABASE_CONFIG`
- configs.py：用于解析yaml文件并生成字典

#### 4. init
数据库初始化文件夹。包含了初始化程序与sql语句。

#### 5. logs
在页面中使用了检测服务后自动生成。

会按照页面中使用的用户名自动分组；每组内文件夹的索引为基于该文件夹创建时间纳秒时间戳的十六进制数。

#### 6. src
Python主代码。

包含：
- utils.py：项目所依赖的工具函数
- utils_db.py：数据库所依赖的所有接口
- v1.py：检测与结果保存流程需要的所有函数

#### 7. static
项目静态文件。

包含：
- assets：项目所需的静态资源。
  - data：页面所需的js静态文本与常量
  - img：网页图标
  - pth：由pytorch训练得到的结果文件，用于检测
  - ResultTemplates：检测结果的模版文件
- css：所有css文件
- js：所有js文件

#### 8. templates
Flask框架用于存放模版文件的文件夹。包含了所有的html文件。
