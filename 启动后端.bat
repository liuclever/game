@echo off
chcp 65001 >nul
echo ========================================
echo    游戏后端服务启动脚本
echo ========================================
echo.

echo [1/2] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)
python --version
echo.

echo [2/2] 启动 Flask 后端服务...
echo 后端地址: http://127.0.0.1:5000
echo.
echo 提示: 按 Ctrl+C 可停止服务
echo ========================================
echo.

python -m interfaces.web_api.app

pause
