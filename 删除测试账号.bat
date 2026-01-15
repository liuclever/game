@echo off
chcp 65001 >nul
echo ========================================
echo    删除测试账号脚本
echo ========================================
echo.

echo [警告] 此操作将删除所有 test_lv50_* 测试账号
echo        及其所有相关数据（幻兽、背包等）
echo.
echo 按任意键继续...
pause >nul

echo.
python delete_test_accounts.py

pause
