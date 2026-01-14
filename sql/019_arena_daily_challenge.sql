-- 擂台每日挑战次数表
USE game_tower;

CREATE TABLE IF NOT EXISTS arena_daily_challenge (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    challenge_date DATE NOT NULL,
    challenge_count INT NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_date (user_id, challenge_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='擂台每日挑战次数';
