@echo off
chcp 65001 >nul
echo 添加签到奖励字段...
mysql -u root -p123456 game_tower < ../sql/signin_rewards_column.sql
echo 完成！
pause
