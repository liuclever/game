-- 022 古战场报名表
USE game_tower;

-- 古战场报名记录（按天）
CREATE TABLE IF NOT EXISTS battlefield_signup (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '玩家ID',
    battlefield_type VARCHAR(10) NOT NULL COMMENT '战场类型（tiger猛虎战场/crane飞鹤战场）',
    signup_date DATE NOT NULL COMMENT '报名日期',
    signup_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '报名时间',
    UNIQUE KEY uniq_user_type_date (user_id, battlefield_type, signup_date),
    INDEX idx_type_date (battlefield_type, signup_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='古战场报名表';
