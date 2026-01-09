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
