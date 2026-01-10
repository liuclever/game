@echo off
chcp 65001 >nul
echo ========================================
echo    启动前端服务
echo ========================================
echo.
echo 前端地址: http://localhost:5173
echo.
echo 按 Ctrl+C 可以停止服务
echo ========================================
echo.

cd /d %~dp0..\interfaces\client

if not exist "node_modules" (
    echo ❌ 前端依赖未安装！
    echo 请先运行 "首次安装依赖.bat"
    echo.
    cd ..\..\dev_helper
    pause
    exit /b 1
)

call npm run dev

if %errorlevel% neq 0 (
    echo.
    echo ❌ 前端启动失败！
    echo.
    echo 可能的原因：
    echo 1. Node.js 未安装或版本过低
    echo 2. 依赖包未安装（运行 首次安装依赖.bat）
    echo 3. 端口 5173 被占用
    echo.
    cd ..\..\dev_helper
    pause
)
