-- ============================================
-- 修复 player 表 user_id 自动递增
-- ============================================

USE game_tower;

-- 修改 user_id 为自动递增
ALTER TABLE player MODIFY user_id INT AUTO_INCREMENT;

-- 设置自动递增起始值（从当前最大值+1开始）
-- 先查询当前最大 user_id，然后设置 AUTO_INCREMENT
SET @max_id = (SELECT COALESCE(MAX(user_id), 0) + 1 FROM player);
SET @sql = CONCAT('ALTER TABLE player AUTO_INCREMENT = ', @max_id);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
