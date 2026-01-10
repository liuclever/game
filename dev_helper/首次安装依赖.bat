@echo off
chcp 65001 >nul
echo ========================================
echo    首次安装项目依赖
echo ========================================
echo.

echo [1/3] 安装 Python 后端依赖...
cd /d %~dp0..
if not exist "requirements.txt" (
    echo ❌ 找不到 requirements.txt 文件！
    echo 当前目录: %cd%
    pause
    exit /b 1
)
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Python 依赖安装失败！
    cd dev_helper
    pause
    exit /b 1
)
echo ✅ Python 依赖安装完成
echo.

echo [2/3] 进入前端目录...
if not exist "interfaces\client" (
    echo ❌ 前端目录不存在！
    cd dev_helper
    pause
    exit /b 1
)
cd interfaces\client

echo [3/3] 安装 Node.js 前端依赖（可能需要几分钟）...
call npm install
if %errorlevel% neq 0 (
    echo ❌ 前端依赖安装失败！
    cd ..\..\dev_helper
    pause
    exit /b 1
)
echo ✅ 前端依赖安装完成
echo.

cd ..\..\dev_helper

echo ========================================
echo    ✅ 所有依赖安装完成！
echo ========================================
echo.
echo 下一步：
echo 1. 配置数据库（参考 dev_helper\本地调试指南.md）
echo 2. 运行 "启动后端.bat" 启动后端服务
echo 3. 运行 "启动前端.bat" 启动前端服务
echo.
pause
