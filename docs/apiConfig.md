# AI api key配置

如果你需要使用此网站中的AI问答功能，你需要自行配置一个key，配置方式如下：

1. 前往<a href="https://account.siliconflow.cn/zh/login" target="_blank">硅基流动</a>中文站注册一个账号并登录

2. 前往<a href="https://cloud.siliconflow.cn/me/account/ak" target="_blank">API密钥</a>页面，点击“新建API密钥”，创建一个属于你自己的密钥

3. 将你获得的密钥保存至电脑的环境变量中（推荐保存为用户变量）：
    - 变量名为：SiliconCloudApi
    - 变量值为：你获取到的API key

你可以在此复制这个变量名：
```plaintext
SiliconCloudApi
```

> 当然，如果变量名SiliconCloudApi存在冲突，请前往 /config/ai.yaml 中修改`ENV_NAME`变量的值

<br/>

### 附：Windows系统中环境变量的配置

Wins + R 打开运行窗口，输入以下命令即可
```plaintext
rundll32.exe sysdm.cpl,EditEnvironmentVariables
```
