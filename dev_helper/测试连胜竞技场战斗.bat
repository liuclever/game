@echo off
chcp 65001 >nul
echo ========================================
echo 测试连胜竞技场真实战斗系统
echo ========================================
echo.

echo 【测试步骤】
echo 1. 确保后端服务已启动
echo 2. 确保前端服务已启动
echo 3. 登录游戏
echo 4. 进入竞技主页 -^> 连胜竞技场
echo 5. 点击"切磋"按钮
echo 6. 查看战报页面
echo.

echo 【检查项目】
echo ✓ 战斗是否使用真实战斗引擎（不是随机胜负）
echo ✓ 战报是否显示真实的战斗过程
echo ✓ 简略版战报是否显示（前6条）
echo ✓ 详细战报是否可以展开查看
echo ✓ 连胜记录是否正确更新
echo ✓ 胜利时连胜+1，失败时连胜归零
echo.

echo 【后端日志检查】
echo 查看后端控制台，应该看到：
echo - 获取双方幻兽队伍
echo - 执行 PVP 战斗
echo - 生成战报日志
echo - 更新连胜记录
echo.

echo 【前端检查】
echo 1. 战报页面应该显示：
echo    - 双方玩家名称
echo    - 战斗结果（胜利/失败）
echo    - 当前连胜次数
echo    - 简略战报（前6条）
echo    - 可展开的详细战报
echo.
echo 2. 战报格式应该类似：
echo    [回合1] 『玩家A』的幻兽X攻击『玩家B』的幻兽Y，气血-1234
echo    [回合2] 『玩家B』的幻兽Y使用高级必杀攻击『玩家A』的幻兽X，气血-5678
echo.

echo 【常见问题】
echo Q: 战报显示"战斗过程无记录"
echo A: 检查后端是否正确返回 battle_logs 和 detail_logs
echo.
echo Q: 战报显示"玩家不存在"或"没有出战幻兽"
echo A: 确保双方都有出战幻兽（在幻兽管理中设置出战）
echo.
echo Q: 战斗结果总是随机
echo A: 检查后端是否正确集成了 run_pvp_battle 函数
echo.

echo ========================================
echo 按任意键关闭...
pause >nul
