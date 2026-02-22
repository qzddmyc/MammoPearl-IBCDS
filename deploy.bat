@echo off
chcp 65001 > nul 2>&1
echo ==============================================
echo           开始执行IBCDS系统部署脚本
echo ==============================================

echo.
echo [1/4] 正在安装Python三方库...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 错误：Python三方库安装失败，请检查网络连接
    pause
    exit /b 1
)
echo [1/4] Python三方库安装完成

echo.
echo [2/4] 正在启动MSSQLSERVER数据库服务...
sudo sc start MSSQLSERVER
if %errorlevel% neq 0 (
    echo 错误：数据库服务启动失败
    pause
    exit /b 1
) else (
    echo [2/4] MSSQLSERVER数据库服务启动成功
)

echo.
echo [3/4] 正在创建IBCDS数据库...
sqlcmd -Q "CREATE DATABASE IBCDS"
if %errorlevel% equ 0 (
    echo [3/4] IBCDS数据库创建成功
) else (
    echo 错误：数据库创建失败
    pause
    exit /b 1
)

echo.
echo [4/4] 正在初始化数据库...
python -m init.init_database
if %errorlevel% neq 0 (
    echo 错误：数据库初始化失败
    pause
    exit /b 1
)
echo [4/4] 数据库初始化完成

echo.
echo ==============================================
echo           IBCDS系统部署完成！
echo ==============================================
pause