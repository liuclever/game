@echo off
chcp 65001 >nul
echo ========================================
echo    强制重建数据库
echo ========================================
echo.
echo ⚠️ 警告：此操作会删除所有现有数据！
echo.
pause

cd /d %~dp0..

set /p MYSQL_PASS=请输入 MySQL root 密码: 
echo.

echo [1/4] 停止所有连接并删除数据库...
mysql -u root -p%MYSQL_PASS% -e "DROP DATABASE IF EXISTS game_tower;"
if %errorlevel% neq 0 (
    echo ❌ 删除失败！可能有程序正在使用数据库
    echo 请先停止后端服务（Ctrl+C），然后重试
    cd dev_helper
    pause
    exit /b 1
)
echo ✅ 旧数据库已删除
echo.

echo [2/4] 创建新数据库...
mysql -u root -p%MYSQL_PASS% -e "CREATE DATABASE game_tower CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
if %errorlevel% neq 0 (
    echo ❌ 创建失败！
    cd dev_helper
    pause
    exit /b 1
)
echo ✅ 新数据库已创建
echo.

echo [3/4] 导入完整表结构...
if not exist "game_tower.sql" (
    echo ❌ 找不到 game_tower.sql 文件！
    cd dev_helper
    pause
    exit /b 1
)

mysql -u root -p%MYSQL_PASS% game_tower < game_tower.sql
if %errorlevel% neq 0 (
    echo ❌ 导入失败！
    cd dev_helper
    pause
    exit /b 1
)
echo ✅ 表结构导入成功
echo.

echo [4/4] 验证表结构...
mysql -u root -p%MYSQL_PASS% -e "USE game_tower; DESCRIBE player;" > temp_check.txt
findstr /C:"copper" temp_check.txt >nul
if %errorlevel% equ 0 (
    echo ✅ copper 字段存在
) else (
    echo ❌ copper 字段不存在！导入可能失败
)

findstr /C:"vip_level" temp_check.txt >nul
if %errorlevel% equ 0 (
    echo ✅ vip_level 字段存在
) else (
    echo ❌ vip_level 字段不存在！导入可能失败
)

del temp_check.txt

echo.
echo ========================================
echo    ✅ 数据库重建完成！
echo ========================================
echo.
echo 下一步：
echo 1. 重启后端服务（Ctrl+C 停止，然后重新运行 启动后端.bat）
echo 2. 刷新浏览器
echo.

cd dev_helper
pause
