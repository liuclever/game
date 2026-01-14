-- 签到系统更新
USE game_tower;

-- 添加签到相关字段的存储过程（安全添加，避免重复执行报错）
DROP PROCEDURE IF EXISTS add_signin_fields;
DELIMITER //
CREATE PROCEDURE add_signin_fields()
BEGIN
    -- 添加 last_signin_date 字段
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'player'
          AND COLUMN_NAME = 'last_signin_date'
    ) THEN
        ALTER TABLE player 
        ADD COLUMN last_signin_date DATE DEFAULT NULL COMMENT '上次签到日期'
        AFTER location;
    END IF;
    
    -- 添加 consecutive_signin_days 字段
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'player'
          AND COLUMN_NAME = 'consecutive_signin_days'
    ) THEN
        ALTER TABLE player 
        ADD COLUMN consecutive_signin_days INT NOT NULL DEFAULT 0 COMMENT '连续签到天数'
        AFTER last_signin_date;
    END IF;
END //
DELIMITER ;

CALL add_signin_fields();
DROP PROCEDURE IF EXISTS add_signin_fields;

