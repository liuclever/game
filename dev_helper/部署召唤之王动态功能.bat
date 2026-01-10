@echo off
chcp 65001 >nul
echo ========================================
echo 部署召唤之王动态功能
echo ========================================
echo.

echo 【修改内容】
echo ✓ 创建挑战记录表 (king_challenge_logs)
echo ✓ 挑战时保存记录
echo ✓ 添加获取动态API (/api/king/dynamics)
echo ✓ 前端显示真实动态
echo.

set /p confirm="确认执行SQL脚本？(y/n): "
if /i not "%confirm%"=="y" (
    echo 已取消
    pause
    exit /b
)

echo.
echo 正在执行SQL脚本...
echo.

mysql -u root -p game_dev < sql/014_king_challenge_logs.sql

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo ✅ SQL脚本执行成功！
    echo ========================================
    echo.
    echo 【下一步】
    echo 1. 重启后端服务
    echo 2. 刷新前端页面
    echo 3. 进入召唤之王挑战赛
    echo 4. 进行几次挑战
    echo 5. 查看动态是否显示真实记录
    echo.
) else (
    echo.
    echo ========================================
    echo ❌ SQL脚本执行失败
    echo ========================================
    echo.
    echo 【可能的原因】
    echo 1. MySQL未启动
    echo 2. 数据库名称不正确（默认：game_dev）
    echo 3. 用户名或密码不正确（默认：root）
    echo.
)

pause
