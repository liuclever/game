-- ============================================================
-- 添加魔魂槽位索引字段
-- 兼容 MySQL 5.7+
-- ============================================================

USE game_tower;

-- 检查并添加 slot_index 字段
-- 注意：MySQL 5.7 不支持 ADD COLUMN IF NOT EXISTS，所以使用存储过程判断
DROP PROCEDURE IF EXISTS add_slot_index_column;
DELIMITER //
CREATE PROCEDURE add_slot_index_column()
BEGIN
    IF NOT EXISTS (
        SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = 'game_tower' 
        AND TABLE_NAME = 'player_mosoul' 
        AND COLUMN_NAME = 'slot_index'
    ) THEN
        ALTER TABLE player_mosoul 
        ADD COLUMN slot_index TINYINT UNSIGNED DEFAULT NULL COMMENT '槽位索引（1-8）' 
        AFTER beast_id;
    END IF;
END //
DELIMITER ;
CALL add_slot_index_column();
DROP PROCEDURE IF EXISTS add_slot_index_column;

-- 检查并添加唯一索引
DROP PROCEDURE IF EXISTS add_beast_slot_index;
DELIMITER //
CREATE PROCEDURE add_beast_slot_index()
BEGIN
    IF NOT EXISTS (
        SELECT * FROM INFORMATION_SCHEMA.STATISTICS 
        WHERE TABLE_SCHEMA = 'game_tower' 
        AND TABLE_NAME = 'player_mosoul' 
        AND INDEX_NAME = 'uk_beast_slot'
    ) THEN
        ALTER TABLE player_mosoul 
        ADD UNIQUE INDEX uk_beast_slot (beast_id, slot_index);
    END IF;
END //
DELIMITER ;
CALL add_beast_slot_index();
DROP PROCEDURE IF EXISTS add_beast_slot_index;
