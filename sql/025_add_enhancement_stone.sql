-- ============================================
-- 添加强化石字段到玩家表
-- ============================================

USE game_tower;

-- 添加强化石字段
ALTER TABLE player ADD COLUMN IF NOT EXISTS enhancement_stone INT NOT NULL DEFAULT 0 COMMENT '强化石数量';

-- 给测试玩家初始化一些强化石
UPDATE player SET enhancement_stone = 197384 WHERE user_id = 1;
