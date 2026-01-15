-- ============================================
-- 添加联盟修行时长字段
-- ============================================

USE game_tower;

-- 为联盟修行房间表添加修行时长字段
ALTER TABLE alliance_training_rooms 
ADD COLUMN duration_hours INT NOT NULL DEFAULT 2 COMMENT '修行时长（小时），默认2小时' AFTER max_participants;

-- 为现有数据设置默认值（2小时）
UPDATE alliance_training_rooms SET duration_hours = 2 WHERE duration_hours IS NULL OR duration_hours = 0;
