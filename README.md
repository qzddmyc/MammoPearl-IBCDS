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



### 用户信息管理

[用户信息管理](./docs/userManagement.md)



### AI api key配置

[AI-key配置](./docs/apiConfig.md)



### 特殊操作

#### 1. 修改项目端口
修改config.yaml中的PORT值即可。

#### 2. 设置页面为仅访问，禁止所有与服务器相关的操作
将 /static/assets/data/vars.js 中的 `DISABLE_INTERACTION_global` 设置为 `true` 即可。

该操作会禁止用户注册、提交检测、AI交互相关的操作，并隐藏需要开启服务器的提示。

当然，如果服务器并没有开启，该值会自动被设置为 `true`。
