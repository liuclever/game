-- 连胜竞技场数据表
USE game_tower;

-- 连胜竞技场记录表
CREATE TABLE IF NOT EXISTS arena_streak (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    current_streak INT DEFAULT 0 COMMENT '当前连胜次数',
    max_streak_today INT DEFAULT 0 COMMENT '今日最高连胜',
    total_battles_today INT DEFAULT 0 COMMENT '今日战斗次数',
    last_battle_time DATETIME COMMENT '最后战斗时间',
    last_refresh_time DATETIME COMMENT '最后刷新时间',
    claimed_rewards TEXT COMMENT '已领取的奖励(JSON)',
    claimed_grand_prize TINYINT(1) DEFAULT 0 COMMENT '是否领取大奖',
    record_date DATE COMMENT '记录日期',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_date (user_id, record_date),
    INDEX idx_max_streak (record_date, max_streak_today)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='连胜竞技场记录';

-- 历届连胜王表
CREATE TABLE IF NOT EXISTS arena_streak_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    nickname VARCHAR(50) NOT NULL,
    max_streak INT NOT NULL COMMENT '最高连胜次数',
    record_date DATE NOT NULL COMMENT '记录日期',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_date (record_date),
    INDEX idx_date (record_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='历届连胜王';
