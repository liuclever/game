CREATE TABLE IF NOT EXISTS player_daily_activity (
    user_id INT PRIMARY KEY,
    activity_value INT DEFAULT 0,
    last_updated_date DATE,
    completed_tasks JSON,
    FOREIGN KEY (user_id) REFERENCES player(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
