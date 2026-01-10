@echo off
chcp 65001 >nul
echo ========================================
echo    启动后端服务
echo ========================================
echo.
echo 后端地址: http://127.0.0.1:5000
echo.
echo 按 Ctrl+C 可以停止服务
echo ========================================
echo.

cd /d %~dp0..
python -m interfaces.web_api.app

if %errorlevel% neq 0 (
    echo.
    echo ❌ 后端启动失败！
    echo.
    echo 可能的原因：
    echo 1. Python 未安装或未添加到环境变量
    echo 2. 依赖包未安装（运行 首次安装依赖.bat）
    echo 3. 数据库连接配置错误
    echo.
    cd dev_helper
    pause
)
