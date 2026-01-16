@echo off
chcp 65001 >nul
echo ========================================
echo    游戏前端服务启动脚本
echo ========================================
echo.

echo [1/3] 检查 Node.js 环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Node.js，请先安装 Node.js 18+
    pause
    exit /b 1
)
node --version
echo.

echo [2/3] 检查前端目录...
if not exist "interfaces\client" (
    echo [错误] 未找到前端目录 interfaces\client
    pause
    exit /b 1
)
echo 前端目录: interfaces\client
echo.

echo [3/3] 启动 Vite 开发服务器...
echo 前端地址: http://localhost:5173
echo.
echo 提示: 按 Ctrl+C 可停止服务
echo ========================================
echo.

cd interfaces\client
npm run dev

pause
