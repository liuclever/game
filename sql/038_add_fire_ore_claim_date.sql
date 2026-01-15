-- 038_add_fire_ore_claim_date.sql
-- 为 player 表添加火能原石领取日期字段

-- 添加字段（如果不存在）
SET @dbname = DATABASE();
SET @tablename = 'player';
SET @columnname = 'last_fire_ore_claim_date';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (TABLE_SCHEMA = @dbname)
      AND (TABLE_NAME = @tablename)
      AND (COLUMN_NAME = @columnname)
  ) > 0,
  "SELECT 'Column already exists.'",
  CONCAT("ALTER TABLE ", @tablename, " ADD COLUMN ", @columnname, " DATE DEFAULT NULL COMMENT '最后领取火能原石日期'")
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;
