-- 战场奖励领取记录表
-- 用于记录玩家每期战场的奖励领取状态

CREATE TABLE IF NOT EXISTS battlefield_reward_claims (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '玩家ID',
    battlefield_type VARCHAR(10) NOT NULL COMMENT '战场类型（tiger/crane）',
    period INT NOT NULL COMMENT '期数',
    
    -- 奖励类型标记
    is_king BOOLEAN DEFAULT FALSE COMMENT '是否战王',
    camp_team VARCHAR(10) DEFAULT NULL COMMENT '所属阵营（red/blue）',
    kills INT DEFAULT 0 COMMENT '击杀数（胜场数）',
    
    -- 领取状态
    king_reward_claimed BOOLEAN DEFAULT FALSE COMMENT '战王奖励是否已领取',
    camp_reward_claimed BOOLEAN DEFAULT FALSE COMMENT '阵营奖励是否已领取',
    kill_reward_claimed BOOLEAN DEFAULT FALSE COMMENT '杀敌奖励是否已领取',
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- 唯一索引：每个玩家每期每个战场只有一条记录
    UNIQUE KEY uk_user_period_type (user_id, battlefield_type, period),
    INDEX idx_period_type (battlefield_type, period),
    INDEX idx_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='战场奖励领取记录';
