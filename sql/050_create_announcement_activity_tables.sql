-- ============================================
-- 开服活动相关数据表
-- ============================================

USE game_tower;

-- 新人战力榜奖励发放记录表
CREATE TABLE IF NOT EXISTS activity_power_ranking_reward (
    id INT AUTO_INCREMENT PRIMARY KEY,
    activity_id VARCHAR(50) NOT NULL COMMENT '活动ID',
    level_bracket INT NOT NULL COMMENT '等级段(29/39/49/59)',
    rank_position INT NOT NULL COMMENT '排名',
    user_id INT NOT NULL COMMENT '玩家ID',
    nickname VARCHAR(50) DEFAULT '' COMMENT '玩家昵称',
    combat_power BIGINT DEFAULT 0 COMMENT '战力',
    reward_items TEXT COMMENT '奖励内容(JSON)',
    is_claimed TINYINT(1) DEFAULT 0 COMMENT '是否已领取',
    finalized_at DATETIME DEFAULT NULL COMMENT '榜单确定时间',
    claimed_at DATETIME DEFAULT NULL COMMENT '领取时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_activity_bracket_rank (activity_id, level_bracket, rank_position),
    INDEX idx_user_id (user_id),
    INDEX idx_activity_bracket (activity_id, level_bracket)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='新人战力榜奖励发放记录';

-- 轮盘抽奖记录表
CREATE TABLE IF NOT EXISTS activity_wheel_lottery (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '玩家ID',
    activity_id VARCHAR(50) NOT NULL DEFAULT 'wheel_lottery' COMMENT '活动ID',
    draw_count INT DEFAULT 0 COMMENT '累计抽奖次数',
    fragment_count INT DEFAULT 0 COMMENT '当前碎片数量',
    round_count INT DEFAULT 0 COMMENT '当前轮次已抽次数(0-9)',
    last_draw_at DATETIME DEFAULT NULL COMMENT '最后抽奖时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_activity (user_id, activity_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='轮盘抽奖记录';

-- 通用活动领取记录表
CREATE TABLE IF NOT EXISTS activity_claims (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '玩家ID',
    activity_id VARCHAR(50) NOT NULL COMMENT '活动ID',
    claim_key VARCHAR(100) NOT NULL COMMENT '领取标识',
    claim_date DATE DEFAULT NULL COMMENT '领取日期(用于每日限购)',
    claim_count INT DEFAULT 1 COMMENT '领取次数',
    extra_data TEXT COMMENT '额外数据(JSON)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_activity_claim (user_id, activity_id, claim_key, claim_date),
    INDEX idx_user_activity (user_id, activity_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='通用活动领取记录';

-- 活动榜单定时任务状态表
CREATE TABLE IF NOT EXISTS activity_finalize_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    activity_id VARCHAR(50) NOT NULL COMMENT '活动ID',
    level_bracket INT DEFAULT NULL COMMENT '等级段(用于战力榜)',
    finalize_type VARCHAR(50) NOT NULL COMMENT '结算类型',
    finalized_at DATETIME DEFAULT NULL COMMENT '结算时间',
    is_rewards_sent TINYINT(1) DEFAULT 0 COMMENT '是否已发放奖励',
    rewards_sent_at DATETIME DEFAULT NULL COMMENT '奖励发放时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_activity_bracket (activity_id, level_bracket, finalize_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='活动结算日志';

