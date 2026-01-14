-- 010 修行系统表
-- 修行系统：玩家通过修行获得声望，声望足够后可以晋级

USE game_tower;

-- 安全添加字段的存储过程
DROP PROCEDURE IF EXISTS add_column_if_not_exists;
DELIMITER //
CREATE PROCEDURE add_column_if_not_exists(
    IN table_name VARCHAR(64),
    IN column_name VARCHAR(64),
    IN column_definition VARCHAR(255)
)
BEGIN
    DECLARE column_exists INT DEFAULT 0;
    SELECT COUNT(*) INTO column_exists
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = table_name
      AND COLUMN_NAME = column_name;
    
    IF column_exists = 0 THEN
        SET @sql = CONCAT('ALTER TABLE ', table_name, ' ADD COLUMN ', column_name, ' ', column_definition);
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
END //
DELIMITER ;

-- 玩家表添加修行和声望相关字段
CALL add_column_if_not_exists('player', 'prestige', 'INT NOT NULL DEFAULT 0 COMMENT "当前声望"');
CALL add_column_if_not_exists('player', 'cultivation_start', 'DATETIME DEFAULT NULL COMMENT "修行开始时间"');
CALL add_column_if_not_exists('player', 'cultivation_duration', 'INT DEFAULT 0 COMMENT "修行时长(秒)"');
CALL add_column_if_not_exists('player', 'cultivation_reward', 'INT DEFAULT 0 COMMENT "修行预计奖励声望"');
CALL add_column_if_not_exists('player', 'location', 'VARCHAR(50) DEFAULT "落龙镇" COMMENT "当前位置"');
CALL add_column_if_not_exists('player', 'inspire_expire_time', 'DATETIME DEFAULT NULL COMMENT "鼓舞效果过期时间"');

-- 清理存储过程
DROP PROCEDURE IF EXISTS add_column_if_not_exists;

-- 修行配置表
CREATE TABLE IF NOT EXISTS cultivation_config (
    id INT PRIMARY KEY AUTO_INCREMENT,
    duration_hours INT NOT NULL COMMENT '修行时长(小时)',
    prestige_reward INT NOT NULL COMMENT '声望奖励',
    gold_cost INT DEFAULT 0 COMMENT '金币消耗',
    description VARCHAR(100) COMMENT '描述',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='修行配置表';

-- 插入修行配置
INSERT IGNORE INTO cultivation_config (duration_hours, prestige_reward, gold_cost, description) VALUES
(1, 50, 0, '修行1小时'),
(2, 120, 0, '修行2小时'),
(4, 280, 0, '修行4小时'),
(8, 650, 0, '修行8小时'),
(12, 1100, 0, '修行12小时');
