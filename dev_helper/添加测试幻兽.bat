@echo off
chcp 65001 >nul
echo ========================================
echo 添加测试幻兽
echo ========================================
echo.

echo 此脚本将为玩家添加测试幻兽，用于测试战斗系统
echo.
echo 【将添加的幻兽】
echo 玩家1: 青龙、朱雀、白虎、玄武 (4只，30级)
echo 玩家2: 麒麟、凤凰、龙龟、九尾狐 (4只，30级)
echo.

set /p confirm="确认执行？(y/n): "
if /i not "%confirm%"=="y" (
    echo 已取消
    pause
    exit /b
)

echo.
echo 正在执行SQL脚本...
echo.

mysql -u root -p game_dev < dev_helper/添加测试幻兽.sql

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo ✅ 测试幻兽添加成功！
    echo ========================================
    echo.
    echo 【下一步】
    echo 1. 刷新游戏页面
    echo 2. 进入"幻兽管理"查看
    echo 3. 测试连胜竞技场、擂台等战斗功能
    echo.
) else (
    echo.
    echo ========================================
    echo ❌ 执行失败
    echo ========================================
    echo.
    echo 【可能的原因】
    echo 1. MySQL未启动
    echo 2. 数据库名称不正确（默认：game_dev）
    echo 3. 用户名或密码不正确（默认：root）
    echo 4. player_beast表不存在
    echo.
    echo 【解决方法】
    echo 1. 检查MySQL服务是否运行
    echo 2. 修改批处理文件中的数据库连接信息
    echo 3. 确保数据库已初始化
    echo.
)

pause
