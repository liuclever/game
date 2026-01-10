@echo off
chcp 65001 >nul
echo ========================================
echo    检查数据库表结构
echo ========================================
echo.

cd /d %~dp0..

echo 请输入你的 MySQL root 密码
echo.

echo [1/2] 检查数据库是否存在...
mysql -u root -p -e "SHOW DATABASES LIKE 'game_tower';"
echo.

echo [2/2] 检查 player 表结构...
mysql -u root -p -e "USE game_tower; DESCRIBE player;"
echo.

echo ========================================
echo 检查完成
echo ========================================
echo.
echo 如果看到 copper、vip_level 等字段，说明数据库正常
echo 如果没有这些字段，需要重新导入数据库
echo.

cd dev_helper
pause
