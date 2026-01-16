@echo off
chcp 65001 >nul
echo ========================================
echo    测试数据库连接
echo ========================================
echo.

python test_db_connection.py

pause
