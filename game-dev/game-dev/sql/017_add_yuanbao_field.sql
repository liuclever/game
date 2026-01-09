-- ============================================
-- 添加元宝字段到玩家表
-- ============================================

USE game_tower;

-- 添加元宝字段（如果已存在会报错，忽略即可）
ALTER TABLE player 
ADD COLUMN yuanbao INT NOT NULL DEFAULT 0 COMMENT '元宝' AFTER gold;

-- 给测试玩家一些元宝
UPDATE player SET yuanbao = 197837, gold = 1091581 WHERE user_id = 1;