-- 添加签到累计奖励已领取记录字段
ALTER TABLE player ADD COLUMN IF NOT EXISTS signin_rewards_claimed VARCHAR(50) DEFAULT '';

-- 说明：signin_rewards_claimed 存储已领取的奖励天数，用逗号分隔，例如 "7,15,30"
