测试古战场的方法：
方法一：直接操作数据库（推荐，最快）
批量创建测试玩家
sql
-- 在数据库中直接插入31或32个测试玩家
INSERT INTO players (username, level, ...) VALUES 
('test_player_1', 25, ...),
('test_player_2', 30, ...),
...
('test_player_31', 35, ...);
模拟报名
sql
-- 直接往战场报名表插入数据
INSERT INTO battlefield_signups (player_id, team, battlefield_type, signup_time) VALUES
(test_id_1, 'red', 'tiger', NOW()),
(test_id_2, 'blue', 'tiger', NOW()),
...;
手动触发战斗流程
调用后端的战斗结算API或定时任务
检查奖励发放结果