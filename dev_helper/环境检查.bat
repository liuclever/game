@echo off
chcp 65001 >nul
echo ========================================
echo    环境检查工具
echo ========================================
echo.

echo [检查 Python]
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python 已安装
    python --version
) else (
    echo ❌ Python 未安装或未添加到环境变量
    echo.
    echo 请安装 Python 3.10 或更高版本
    echo 下载地址: https://www.python.org/downloads/
    echo.
    echo ⚠️ 安装时务必勾选 "Add Python to PATH"
)
echo.

echo [检查 pip]
pip --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ pip 已安装
    pip --version
) else (
    echo ❌ pip 未安装或未添加到环境变量
)
echo.

echo [检查 Node.js]
node --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Node.js 已安装
    node --version
) else (
    echo ❌ Node.js 未安装或未添加到环境变量
    echo.
    echo 请安装 Node.js 18 或更高版本
    echo 下载地址: https://nodejs.org/
)
echo.

echo [检查 npm]
npm --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ npm 已安装
    npm --version
) else (
    echo ❌ npm 未安装（通常随 Node.js 一起安装）
)
echo.

echo [检查 MySQL]
mysql --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ MySQL 已安装
    mysql --version
) else (
    echo ⚠️ MySQL 未安装或未添加到环境变量
    echo.
    echo 请安装 MySQL 8.0
    echo 下载地址: https://dev.mysql.com/downloads/mysql/
)
echo.

echo ========================================
echo    检查完成
echo ========================================
echo.
echo 如果有 ❌ 标记，请先安装对应的软件
echo 详细安装步骤请查看: dev_helper\环境安装指南.md
echo.
pause
