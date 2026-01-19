-- 为联盟成员表新增历史总贡献点字段
-- 历史总贡献点：累计所有获得的贡献点，只增不减
USE game_tower;

-- 检查字段是否已存在，如果不存在则添加
SET @col_exists = 0;
SELECT COUNT(*) INTO @col_exists
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'game_tower'
  AND TABLE_NAME = 'alliance_members'
  AND COLUMN_NAME = 'total_contribution';

SET @sql = IF(@col_exists = 0,
    'ALTER TABLE alliance_members ADD COLUMN total_contribution INT DEFAULT 0 COMMENT ''历史总贡献点（累计，只增不减）'' AFTER contribution',
    'SELECT ''字段 total_contribution 已存在，跳过添加'' AS message');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 初始化 total_contribution：确保至少等于当前的 contribution
-- 如果 total_contribution 为 NULL 或小于 contribution，则设置为 contribution
UPDATE alliance_members
SET total_contribution = GREATEST(COALESCE(total_contribution, 0), contribution)
WHERE total_contribution IS NULL OR total_contribution < contribution;
