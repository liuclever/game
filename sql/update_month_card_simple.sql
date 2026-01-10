-- 简化月卡表：每个玩家只有一个月卡
-- 先删除旧数据和约束
DELETE FROM player_month_card;

-- 移除旧的唯一约束（如果存在）
ALTER TABLE player_month_card DROP INDEX IF EXISTS uniq_user_month;

-- 添加新的唯一约束（每个玩家只能有一条记录）
ALTER TABLE player_month_card ADD UNIQUE KEY uniq_user (user_id);
