-- 添加 diamond_spent 字段用于追踪消耗的宝石数量
-- VIP等级将根据此字段计算

ALTER TABLE player ADD COLUMN IF NOT EXISTS diamond_spent INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '累计消耗宝石数';

-- 添加 copper 字段（铜钱）
ALTER TABLE player ADD COLUMN IF NOT EXISTS copper BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '铜钱';

-- 添加 daily_copper_date 字段（每日铜钱领取日期）
ALTER TABLE player ADD COLUMN IF NOT EXISTS daily_copper_date DATE NULL DEFAULT NULL COMMENT '每日铜钱领取日期';

-- 添加 claimed_gift_levels 字段（已领取的VIP礼包等级）
ALTER TABLE player ADD COLUMN IF NOT EXISTS claimed_gift_levels VARCHAR(100) NULL DEFAULT '' COMMENT '已领取的VIP礼包等级';

-- 添加 first_recharge_claimed 字段（首充是否已领取）
ALTER TABLE player ADD COLUMN IF NOT EXISTS first_recharge_claimed TINYINT(1) NOT NULL DEFAULT 0 COMMENT '首充是否已领取';
