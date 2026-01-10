@echo off
chcp 65001 >nul
echo ========================================
echo 创建召唤之王挑战记录表
echo ========================================
echo.

echo 正在执行SQL脚本...
echo 数据库: game_tower
echo 文件: sql/014_king_challenge_logs.sql
echo.

mysql -u root -p game_tower < sql/014_king_challenge_logs.sql

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo ✅ 表创建成功！
    echo ========================================
    echo.
    echo 表名: king_challenge_logs
    echo.
    echo 【下一步】
    echo 重启后端服务即可使用
    echo.
) else (
    echo.
    echo ========================================
    echo ❌ 创建失败
    echo ========================================
    echo.
    echo 请检查：
    echo 1. MySQL是否运行
    echo 2. 数据库名称是否正确（game_tower）
    echo 3. 用户名密码是否正确
    echo.
)

pause
