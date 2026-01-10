@echo off
chcp 65001 >nul
echo ========================================
echo    导入数据库表结构
echo ========================================
echo.

cd /d %~dp0..

echo 请输入你的 MySQL root 密码
echo.

echo [1/3] 删除旧数据库...
mysql -u root -p -e "DROP DATABASE IF EXISTS game_tower;"
if %errorlevel% neq 0 (
    echo ❌ 删除数据库失败！
    echo 请检查 MySQL 是否正在运行
    cd dev_helper
    pause
    exit /b 1
)
echo ✅ 旧数据库已删除
echo.

echo [2/3] 创建新数据库...
mysql -u root -p -e "CREATE DATABASE game_tower CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
if %errorlevel% neq 0 (
    echo ❌ 创建数据库失败！
    cd dev_helper
    pause
    exit /b 1
)
echo ✅ 数据库创建成功
echo.

echo [3/3] 导入完整表结构（可能需要一些时间）...
echo.

if exist "game_tower.sql" (
    echo 找到完整的 game_tower.sql，正在导入...
    mysql -u root -p game_tower < game_tower.sql
    if %errorlevel% neq 0 (
        echo ❌ 导入失败！
        cd dev_helper
        pause
        exit /b 1
    )
    echo ✅ 导入成功！
) else (
    echo ❌ 找不到 game_tower.sql 文件！
    echo 请确保文件在项目根目录
    cd dev_helper
    pause
    exit /b 1
)

echo.
echo ========================================
echo    ✅ 数据库导入完成！
echo ========================================
echo.
echo 数据库信息：
echo - 数据库名: game_tower
echo - 字符集: utf8mb4
echo - 所有表和字段已创建
echo.
echo 下一步：
echo 1. 重启后端服务（Ctrl+C 停止，然后重新运行 启动后端.bat）
echo 2. 刷新浏览器
echo.

cd dev_helper
pause
