-- 签到记录表
-- 用于记录玩家每天的签到情况，支持补签功能

CREATE TABLE IF NOT EXISTS player_signin_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '玩家ID',
    signin_date DATE NOT NULL COMMENT '签到日期',
    is_makeup TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否补签(0=正常签到,1=补签)',
    reward_copper INT NOT NULL DEFAULT 0 COMMENT '获得的铜钱',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    UNIQUE KEY uk_user_date (user_id, signin_date),
    KEY idx_user_id (user_id),
    KEY idx_signin_date (signin_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='玩家签到记录表';
