@echo off
chcp 65001 >nul
echo ========================================
echo   游戏服务启动脚本
echo ========================================
echo.

:: 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

:: 检查 Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Node.js，请先安装 Node.js 18+
    pause
    exit /b 1
)

echo [1/3] 启动后端服务（Flask API）...
start "后端服务" cmd /k "cd /d %~dp0 && python -m interfaces.web_api.app"

echo [2/3] 等待后端服务启动...
timeout /t 3 /nobreak >nul

echo [3/3] 启动前端服务（Vue + Vite）...
start "前端服务" cmd /k "cd /d %~dp0\interfaces\client && npm run dev"

echo.
echo ========================================
echo   服务启动完成！
echo ========================================
echo.
echo   后端地址: http://127.0.0.1:5000
echo   前端地址: http://localhost:5173
echo.
echo   注意: 请确保 MySQL 数据库已启动并配置正确
echo   数据库配置: infrastructure/db/connection.py
echo ========================================
echo.
pause
