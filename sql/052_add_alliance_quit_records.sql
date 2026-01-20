-- 添加联盟退出记录表，用于实现48小时加入限制
USE game_tower;

CREATE TABLE IF NOT EXISTS alliance_quit_records (
    user_id INT NOT NULL PRIMARY KEY,
    quit_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '退出联盟的时间',
    FOREIGN KEY (user_id) REFERENCES player(user_id) ON DELETE CASCADE,
    INDEX idx_quit_at (quit_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='记录玩家退出联盟的时间，用于48小时加入限制';
