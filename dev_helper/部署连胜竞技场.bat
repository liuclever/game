@echo off
chcp 65001 >nul
echo ========================================
echo    部署连胜竞技场功能
echo ========================================
echo.

cd /d %~dp0..

echo [1/3] 导入数据库表...
mysql -u root -p game_tower < sql/arena_streak_tables.sql
if %errorlevel% neq 0 (
    echo ❌ 数据库导入失败！
    echo 请检查 MySQL 是否运行，密码是否正确
    cd dev_helper
    pause
    exit /b 1
)
echo ✅ 数据库表创建成功
echo.

echo [2/3] 后端代码已就绪
echo ✅ API 路由: interfaces/routes/arena_streak_routes.py
echo ✅ 已注册到 Flask 应用
echo.

echo [3/3] 前端代码已就绪
echo ✅ 页面组件: interfaces/client/src/views/ArenaStreak.vue
echo ✅ 路由配置: /arena/streak
echo ✅ 主页按钮: 竞技 → /arena/streak
echo.

echo ========================================
echo    ✅ 部署完成！
echo ========================================
echo.
echo 下一步：
echo 1. 重启后端服务（Ctrl+C 停止，然后重新运行 启动后端.bat）
echo 2. 刷新前端（如果前端在运行，会自动热更新）
echo 3. 在游戏首页点击"竞技"按钮测试
echo.
echo 功能说明：
echo - 开放时间：每天 8:00-23:00
echo - 匹配规则：同等级段位（1-10, 11-20...）
echo - 连胜机制：胜利+1，失败归零
echo - 活力消耗：6连胜前80，6连胜后15
echo - 连胜奖励：1-6连胜可领取奖励
echo - 排行榜：今日连胜榜 + 历届连胜王
echo.

cd dev_helper
pause
