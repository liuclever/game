-- ============================================
-- 龙宫之谜（活动副本）Schema（可重复执行）
--
-- 业务：
-- - 每日免费进入 1 次；第 2/3 次需重置（200 元宝），每日最多 2 次重置；
-- - 3 个关卡按顺序挑战；每关胜利出现 1 个“龙宫宝箱”，需手动领取；
-- - 宝箱掉落：进化神草/进化圣水晶/进化碎片（20/10/70）
-- - 次日刷新（按 play_date 分区）。
-- ============================================

USE game_tower;

CREATE TABLE IF NOT EXISTS dragonpalace_daily_state (
  user_id INT NOT NULL,
  play_date DATE NOT NULL COMMENT '日期（每天刷新）',

  resets_used INT NOT NULL DEFAULT 0 COMMENT '当日已重置次数（0~2）',
  status VARCHAR(32) NOT NULL DEFAULT 'not_started' COMMENT 'not_started/in_progress/failed/completed',
  current_stage INT NOT NULL DEFAULT 1 COMMENT '当前关卡（1~3）',

  stage1_success TINYINT NOT NULL DEFAULT 0,
  stage1_report_json LONGTEXT NULL,
  stage1_reward_item_id INT NULL,
  stage1_reward_claimed TINYINT NOT NULL DEFAULT 0,

  stage2_success TINYINT NOT NULL DEFAULT 0,
  stage2_report_json LONGTEXT NULL,
  stage2_reward_item_id INT NULL,
  stage2_reward_claimed TINYINT NOT NULL DEFAULT 0,

  stage3_success TINYINT NOT NULL DEFAULT 0,
  stage3_report_json LONGTEXT NULL,
  stage3_reward_item_id INT NULL,
  stage3_reward_claimed TINYINT NOT NULL DEFAULT 0,

  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id, play_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='龙宫之谜：玩家每日进度与战报/领奖状态';


