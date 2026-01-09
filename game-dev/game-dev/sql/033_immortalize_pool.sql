CREATE TABLE IF NOT EXISTS player_immortalize_pool (
    user_id INT PRIMARY KEY COMMENT '玩家ID',
    pool_level TINYINT NOT NULL DEFAULT 1 COMMENT '化仙池等级',
    current_exp BIGINT NOT NULL DEFAULT 0 COMMENT '化仙池当前可用经验',
    formation_level TINYINT NOT NULL DEFAULT 0 COMMENT '化仙阵等级',
    formation_started_at DATETIME DEFAULT NULL COMMENT '化仙阵开始时间',
    formation_ends_at DATETIME DEFAULT NULL COMMENT '化仙阵结束时间',
    formation_last_grant_at DATETIME DEFAULT NULL COMMENT '化仙阵最近一次结算时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='玩家化仙池状态';
