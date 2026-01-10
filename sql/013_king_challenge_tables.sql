-- 013 召唤之王挑战赛表
-- 召唤之王挑战赛功能相关表

USE game_tower;

-- 召唤之王挑战赛排名表
CREATE TABLE IF NOT EXISTS king_challenge_rank (
    user_id INT NOT NULL,
    area_index INT NOT NULL DEFAULT 1 COMMENT '赛区编号（1=一赛区，2=二赛区）',
    rank_position INT NOT NULL COMMENT '在赛区内的排名（1起）',
    win_streak INT NOT NULL DEFAULT 0 COMMENT '连胜场次',
    total_wins INT NOT NULL DEFAULT 0 COMMENT '总胜场',
    total_losses INT NOT NULL DEFAULT 0 COMMENT '总负场',
    today_challenges INT NOT NULL DEFAULT 0 COMMENT '今日挑战次数',
    last_challenge_date DATE DEFAULT NULL COMMENT '上次挑战日期',
    last_challenge_time DATETIME DEFAULT NULL COMMENT '最后挑战时间（用于冷却）',
    is_registered TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否已报名本周',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id),
    INDEX idx_area_rank (area_index, rank_position)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='召唤之王挑战赛排名表';

-- 召唤之王奖励领取记录表
CREATE TABLE IF NOT EXISTS king_reward_claimed (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    season INT NOT NULL DEFAULT 1 COMMENT '赛季编号',
    reward_tier VARCHAR(20) NOT NULL COMMENT '奖励档位（冠军/亚军/四强等）',
    claimed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_season (user_id, season)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='召唤之王奖励领取记录';

-- 给player表添加召唤之王标识（使用存储过程安全添加）
DROP PROCEDURE IF EXISTS add_king_column;
DELIMITER //
CREATE PROCEDURE add_king_column()
BEGIN
    DECLARE column_exists INT DEFAULT 0;
    SELECT COUNT(*) INTO column_exists
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'player'
      AND COLUMN_NAME = 'is_summon_king';
    
    IF column_exists = 0 THEN
        ALTER TABLE player ADD COLUMN is_summon_king TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否是召唤之王（1=是）';
    END IF;
END //
DELIMITER ;

CALL add_king_column();
DROP PROCEDURE IF EXISTS add_king_column;

-- 召唤之王正赛阶段表
CREATE TABLE IF NOT EXISTS king_final_stage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    season INT NOT NULL COMMENT '赛季编号',
    user_id INT NOT NULL COMMENT '玩家ID',
    stage VARCHAR(20) NOT NULL COMMENT '阶段：32/16/8/4/2/champion',
    match_id INT DEFAULT NULL COMMENT '对战ID',
    opponent_id INT DEFAULT NULL COMMENT '对手ID',
    is_bye TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否轮空',
    is_winner TINYINT(1) DEFAULT NULL COMMENT '是否胜利（NULL=未比赛）',
    battle_time DATETIME DEFAULT NULL COMMENT '战斗时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_season_stage (season, stage),
    INDEX idx_user (user_id),
    INDEX idx_match (match_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='召唤之王正赛阶段表';

-- 召唤之王赛季配置表
CREATE TABLE IF NOT EXISTS king_season_config (
    season INT PRIMARY KEY COMMENT '赛季编号',
    start_date DATE NOT NULL COMMENT '赛季开始日期（周一）',
    end_date DATE NOT NULL COMMENT '赛季结束日期（周日）',
    status VARCHAR(20) NOT NULL DEFAULT 'registration' COMMENT '状态：registration/preliminary/final/finished',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='召唤之王赛季配置表';

-- 添加字段的存储过程（安全添加，避免重复执行报错）
DROP PROCEDURE IF EXISTS add_king_fields;
DELIMITER //
CREATE PROCEDURE add_king_fields()
BEGIN
    -- 添加 last_challenge_time 字段
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'king_challenge_rank'
          AND COLUMN_NAME = 'last_challenge_time'
    ) THEN
        ALTER TABLE king_challenge_rank 
        ADD COLUMN last_challenge_time DATETIME DEFAULT NULL COMMENT '最后挑战时间（用于冷却）'
        AFTER last_challenge_date;
    END IF;
    
    -- 添加 is_registered 字段
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'king_challenge_rank'
          AND COLUMN_NAME = 'is_registered'
    ) THEN
        ALTER TABLE king_challenge_rank 
        ADD COLUMN is_registered TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否已报名本周'
        AFTER last_challenge_time;
    END IF;
END //
DELIMITER ;

CALL add_king_fields();
DROP PROCEDURE IF EXISTS add_king_fields;
