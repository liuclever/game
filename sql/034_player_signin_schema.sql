-- ============================================
-- 玩家签到（Schema 合并脚本，可重复执行）
-- 覆盖内容：
-- 1) player.copper              铜钱字段（若你的库已由旧脚本创建则会跳过）
-- 2) player.last_signin_date     上次签到日期
-- 3) player.signin_streak        连续签到天数（用于>=5天×2与中断重置）
--
-- 说明：
-- - MySQL 不支持 `ADD COLUMN IF NOT EXISTS`（该语法常见于 MariaDB），因此统一用 information_schema 做幂等判断。
-- - 本脚本用于协作开发环境的增量升级：可直接重复执行，不会破坏已有数据。
-- ============================================

USE game_tower;

-- 1) copper
SET @col_exists := (
  SELECT COUNT(*)
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'player'
    AND COLUMN_NAME = 'copper'
);
SET @sql := IF(
  @col_exists = 0,
  'ALTER TABLE player ADD COLUMN copper BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT ''铜钱''',
  'SELECT ''ok: player.copper already exists'''
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 2) last_signin_date
SET @col_exists := (
  SELECT COUNT(*)
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'player'
    AND COLUMN_NAME = 'last_signin_date'
);
SET @sql := IF(
  @col_exists = 0,
  'ALTER TABLE player ADD COLUMN last_signin_date DATE NULL DEFAULT NULL COMMENT ''上次签到日期''',
  'SELECT ''ok: player.last_signin_date already exists'''
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 3) signin_streak
SET @col_exists := (
  SELECT COUNT(*)
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'player'
    AND COLUMN_NAME = 'signin_streak'
);
SET @sql := IF(
  @col_exists = 0,
  'ALTER TABLE player ADD COLUMN signin_streak INT NOT NULL DEFAULT 0 COMMENT ''连续签到天数''',
  'SELECT ''ok: player.signin_streak already exists'''
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;


