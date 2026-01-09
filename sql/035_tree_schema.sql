-- ============================================
-- 古树（每周幸运数字）Schema（可重复执行）
--
-- 业务：
-- - 每周（周一~周日）玩家每天领取 1 个数字（0~100），一周最多 7 个；
-- - 周日开奖 7 个数字，并按命中数量发放 1~5 星礼包（可领奖一次）。
-- ============================================

USE game_tower;

-- 每周开奖（全服共享）
CREATE TABLE IF NOT EXISTS tree_week (
  week_start DATE NOT NULL COMMENT '周一日期（该周的 week_start）',
  winning_numbers_json TEXT NULL COMMENT '开奖数字 JSON 数组（7个，0~100）',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (week_start)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='古树每周开奖信息';

-- 玩家每周记录
CREATE TABLE IF NOT EXISTS tree_player_week (
  user_id INT NOT NULL,
  week_start DATE NOT NULL COMMENT '周一日期（与 tree_week.week_start 对齐）',
  my_numbers_json TEXT NULL COMMENT '玩家本周数字 JSON 数组（最多7个）',
  last_draw_date DATE NULL COMMENT '上次领取数字日期（用于每日一次）',
  claimed_at DATETIME NULL COMMENT '领奖时间（周日一次）',
  claim_star INT NOT NULL DEFAULT 0 COMMENT '领奖星级（1~5；未领奖为0）',
  match_count INT NOT NULL DEFAULT 0 COMMENT '命中数量（0~7）',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id, week_start),
  KEY idx_tree_player_week_week (week_start)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='古树玩家每周记录';


