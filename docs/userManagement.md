# 用户信息管理

该项目提供了两份供管理员管理用户信息的接口：一份为python文件，包含基于控制台的交互式UI操作；另一份为二进制可执行文件，可以在终端通过命令行使用。

---

### UI 操作

1. 清除数据库数据

> 包含清空表内数据与删除整张表的操作

使用以下命令运行模块，并按照提示操作即可。
```shell
python -m Admin-Operation.cleardata
```

2. 操作用户信息

> 包含修改密码、新增用户、删除用户操作

使用以下命令运行模块，并按照提示操作即可。
```shell
python -m Admin-Operation.modifydata
```

<br/>

### 命令行操作

1. 使用方式

可以按以下示例使用该命令行工具（该指令会输出帮助信息）：
```shell
bin/ibcds -h
```

当然，也可以将"**项目路径/bin**"添加至环境变量并重启设备，即可在**项目根目录下**（终端位置）直接使用`ibcds -h`执行该命令。

值得注意的是，`ibcds`并不是一个全局可用的命令，它依赖本项目中的部分文件。

2. 源代码及打包方式

该二进制文件的源代码位于raw/codesBeforePackage/ibcds.py，打包方式如下：

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
注意，打包时的.py文件必须位于项目根目录下，否则会无法执行。给出的命令行中已实现文件的移动操作。
