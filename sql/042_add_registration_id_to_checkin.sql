-- 042 为盟战签到表添加 registration_id 字段
-- 将签到与报名记录关联，实现每次报名只能签到一次的逻辑

USE game_tower;

-- 添加 registration_id 字段
ALTER TABLE alliance_war_checkin 
ADD COLUMN registration_id BIGINT UNSIGNED NULL COMMENT '关联的报名记录ID，关联 alliance_land_registration.id' AFTER user_id;

-- 添加索引
ALTER TABLE alliance_war_checkin 
ADD INDEX idx_registration_id (registration_id);

-- 添加外键约束
ALTER TABLE alliance_war_checkin 
ADD CONSTRAINT fk_checkin_registration 
FOREIGN KEY (registration_id) REFERENCES alliance_land_registration(id) ON DELETE SET NULL;

-- 更新现有签到记录：尝试关联到对应的报名记录
-- 注意：这个更新可能无法完全匹配所有历史记录，但至少为后续签到提供基础
UPDATE alliance_war_checkin c
INNER JOIN alliance_land_registration r 
    ON c.alliance_id = r.alliance_id 
    AND c.checkin_date >= DATE(r.registration_time)
    AND c.checkin_date <= DATE_ADD(r.registration_time, INTERVAL 3 DAY)
SET c.registration_id = r.id
WHERE r.status IN (1, 2, 3, 4, 6)  -- 活跃状态
AND c.registration_id IS NULL;
