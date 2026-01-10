@echo off
chcp 65001 >nul
echo ========================================
echo    快速测试数据库连接
echo ========================================
echo.

cd /d %~dp0..
python -c "from infrastructure.db.connection import get_connection; conn = get_connection(); print('✅ 数据库连接成功！'); conn.close()"

if %errorlevel% neq 0 (
    echo.
    echo ❌ 数据库连接失败！
    echo.
    echo 请检查：
    echo 1. MySQL 服务是否启动
    echo 2. infrastructure\db\connection.py 中的密码是否正确
    echo 3. 数据库 game_tower 是否已创建
    echo.
) else (
    echo.
    echo 数据库配置正确，可以启动项目了！
    echo.
)

cd dev_helper
pause
