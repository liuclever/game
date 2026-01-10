@echo off
chcp 65001 >nul
echo ========================================
echo 部署连胜竞技场真实战斗系统
echo ========================================
echo.

echo 【修改的文件】
echo ✓ interfaces/routes/arena_streak_routes.py
echo ✓ interfaces/client/src/views/ArenaStreak.vue
echo ✓ interfaces/client/src/views/ArenaStreakBattleReport.vue
echo.

echo 【部署步骤】
echo.
echo 1. 重启后端服务
echo    - 停止当前运行的后端服务 (Ctrl+C)
echo    - 重新运行: python interfaces/web_api/app.py
echo.
echo 2. 重启前端服务
echo    - 停止当前运行的前端服务 (Ctrl+C)
echo    - 重新运行: npm run dev
echo.
echo 3. 清除浏览器缓存
echo    - 按 Ctrl+Shift+Delete
echo    - 或者使用无痕模式测试
echo.

echo 【验证步骤】
echo.
echo 1. 登录游戏
echo 2. 进入竞技主页 -^> 连胜竞技场
echo 3. 点击"切磋"按钮
echo 4. 查看战报页面
echo.
echo 预期结果:
echo ✓ 战报显示真实的战斗过程
echo ✓ 简略版战报显示（前6条）
echo ✓ 可以展开查看详细战报
echo ✓ 连胜记录正确更新
echo ✓ 胜利时连胜+1，失败时连胜归零
echo.

echo 【后端日志检查】
echo 查看后端控制台，应该看到战斗计算过程
echo 如果有错误，会显示详细的错误堆栈
echo.

echo 【前端检查】
echo 打开浏览器控制台 (F12)
echo 查看是否有 JavaScript 错误
echo 检查 sessionStorage 是否正确存储战报数据
echo.

echo ========================================
echo 部署完成！
echo ========================================
echo.
echo 详细文档: dev_helper/连胜竞技场-真实战斗集成完成.md
echo 测试指南: dev_helper/测试连胜竞技场战斗.bat
echo.
pause
