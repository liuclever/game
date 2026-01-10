@echo off
chcp 65001 >nul
echo ========================================
echo 部署切磋功能
echo ========================================
echo.

echo [1/1] 创建切磋战绩表...
mysql -u root -p123456 game_tower < ../sql/spar_records.sql
if %errorlevel% neq 0 (
    echo ❌ 创建表失败！
    pause
    exit /b 1
)

echo.
echo ✅ 切磋功能部署完成！
echo.
echo 功能说明：
echo - 点击任何页面的玩家名字进入玩家主页
echo - 在玩家主页的战绩旁边点击"切磋"按钮
echo - 瞬间显示切磋结果（包括战斗过程和战绩统计）
echo.
pause
