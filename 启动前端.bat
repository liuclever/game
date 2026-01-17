@echo off
chcp 65001 >nul
echo ========================================
echo    游戏前端服务启动脚本
echo ========================================
echo.

echo [1/4] 检查 Node.js 环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Node.js，请先安装 Node.js 18+
    pause
    exit /b 1
)
node --version
echo.

echo [2/4] 检查前端目录...
if not exist "interfaces\client" (
    echo [错误] 未找到前端目录 interfaces\client
    pause
    exit /b 1
)
echo 前端目录: interfaces\client
echo.

echo [3/4] 检查并安装依赖...
if not exist "interfaces\client\node_modules" (
    echo [提示] 首次运行，正在安装依赖包...
    echo 这可能需要几分钟时间，请耐心等待...
    echo.
    cd interfaces\client
    call npm install
    if errorlevel 1 (
        echo.
        echo [错误] 依赖安装失败，请检查网络连接或尝试手动运行:
        echo   cd interfaces\client
        echo   npm install
        pause
        exit /b 1
    )
    cd ..\..
    echo.
    echo [成功] 依赖安装完成！
    echo.
) else (
    echo [提示] 依赖已安装，跳过安装步骤
    echo.
)

echo [4/4] 启动 Vite 开发服务器...
echo 前端地址: http://localhost:5173
echo.
echo 提示: 按 Ctrl+C 可停止服务
echo ========================================
echo.

cd interfaces\client
npm run dev

pause
