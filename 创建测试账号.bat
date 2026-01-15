@echo off
chcp 65001 >nul
echo ========================================
echo    创建测试账号脚本
echo ========================================
echo.

echo [提示] 将创建20个50级测试账号
echo        每个账号都有追风狼幻兽并已上阵
echo.
echo 按任意键开始...
pause >nul

echo.
echo [步骤1] 测试数据库连接...
python test_db_connection.py
if errorlevel 1 (
    echo.
    echo ❌ 数据库连接测试失败，请检查配置
    pause
    exit /b 1
)

echo.
echo [步骤2] 开始创建测试账号...
echo.

python create_test_accounts.py

pause
