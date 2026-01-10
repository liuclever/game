-- 给召唤之王挑战记录表添加战报字段

USE game_tower;

ALTER TABLE king_challenge_logs 
ADD COLUMN battle_report TEXT COMMENT '战报数据(JSON格式)' AFTER area_index;

-- 说明：
-- battle_report 字段存储战斗日志的JSON数据
-- 格式：{"battleLogs": [...], "detailLogs": [...]}
