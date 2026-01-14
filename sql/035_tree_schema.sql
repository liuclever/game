-- ============================================
-- 古树（幸运古树）Schema（可重复执行）
--
-- 业务：
-- - 周一至周六：每天领取 1 个红果实幸运数字（01~100），累计最多 6 个；
-- - 周日：领取 1 个蓝果实幸运数字（01~100），累计最多 1 个；
-- - 每周幸运数字：红果实 6 个 + 蓝果实 1 个；
-- - 当周幸运数字在下周一统一公布；
-- - 玩家获奖后需手动领取，奖励有效期为一周（下次公布时未领取则作废）。
--
-- 兼容：
-- - 早期版本使用 my_numbers_json / winning_numbers_json 存 7 个数字列表；
-- - 新版本增加红/蓝字段，但仍同步写入旧字段，方便平滑升级。
-- ============================================

USE game_tower;

-- 每周开奖（全服共享）
CREATE TABLE IF NOT EXISTS tree_week (
  week_start DATE NOT NULL COMMENT '周一日期（该周的 week_start）',
  announce_date DATE NULL COMMENT '公布日期（下周一）',
  winning_red_numbers_json TEXT NULL COMMENT '当周幸运红果实数字 JSON 数组（6个，01~100）',
  winning_blue_number INT NULL COMMENT '当周幸运蓝果实数字（01~100）',
  winning_numbers_json TEXT NULL COMMENT '兼容字段：7个数字列表（红6+蓝1）',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (week_start)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='古树每周开奖信息';

-- 玩家每周记录
CREATE TABLE IF NOT EXISTS tree_player_week (
  user_id INT NOT NULL,
  week_start DATE NOT NULL COMMENT '周一日期（与 tree_week.week_start 对齐）',
  red_numbers_json TEXT NULL COMMENT '本周红果实数字 JSON 数组（最多6个）',
  blue_number INT NULL COMMENT '本周蓝果实数字（周日领取，01~100）',
  my_numbers_json TEXT NULL COMMENT '兼容字段：7个数字列表（红<=6 + 可选蓝1）',
  last_draw_date DATE NULL COMMENT '上次领取数字日期（用于每日一次）',
  claimed_at DATETIME NULL COMMENT '领奖时间（有效期内一次）',
  claim_star INT NOT NULL DEFAULT 0 COMMENT '领奖星级（1~5；未领奖为0）',
  match_count INT NOT NULL DEFAULT 0 COMMENT '命中数量（0~7）',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id, week_start),
  KEY idx_tree_player_week_week (week_start)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='古树玩家每周记录';

-- ===== 幂等增量升级（MySQL 兼容）=====
-- 说明：MySQL 不支持 ADD COLUMN IF NOT EXISTS，因此用 information_schema 做判断后动态执行。

-- tree_week.announce_date
SET @col_exists := (
  SELECT COUNT(*)
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'tree_week' AND COLUMN_NAME = 'announce_date'
);
SET @sql := IF(@col_exists = 0, 'ALTER TABLE tree_week ADD COLUMN announce_date DATE NULL COMMENT ''公布日期（下周一）''', 'SELECT ''ok: tree_week.announce_date exists''');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- tree_week.winning_red_numbers_json
SET @col_exists := (
  SELECT COUNT(*)
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'tree_week' AND COLUMN_NAME = 'winning_red_numbers_json'
);
SET @sql := IF(@col_exists = 0, 'ALTER TABLE tree_week ADD COLUMN winning_red_numbers_json TEXT NULL COMMENT ''当周幸运红果实数字 JSON 数组（6个）''', 'SELECT ''ok: tree_week.winning_red_numbers_json exists''');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- tree_week.winning_blue_number
SET @col_exists := (
  SELECT COUNT(*)
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'tree_week' AND COLUMN_NAME = 'winning_blue_number'
);
SET @sql := IF(@col_exists = 0, 'ALTER TABLE tree_week ADD COLUMN winning_blue_number INT NULL COMMENT ''当周幸运蓝果实数字（01~100）''', 'SELECT ''ok: tree_week.winning_blue_number exists''');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- tree_player_week.red_numbers_json
SET @col_exists := (
  SELECT COUNT(*)
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'tree_player_week' AND COLUMN_NAME = 'red_numbers_json'
);
SET @sql := IF(@col_exists = 0, 'ALTER TABLE tree_player_week ADD COLUMN red_numbers_json TEXT NULL COMMENT ''本周红果实数字 JSON 数组（最多6个）''', 'SELECT ''ok: tree_player_week.red_numbers_json exists''');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- tree_player_week.blue_number
SET @col_exists := (
  SELECT COUNT(*)
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'tree_player_week' AND COLUMN_NAME = 'blue_number'
);
SET @sql := IF(@col_exists = 0, 'ALTER TABLE tree_player_week ADD COLUMN blue_number INT NULL COMMENT ''本周蓝果实数字（周日领取）''', 'SELECT ''ok: tree_player_week.blue_number exists''');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;


