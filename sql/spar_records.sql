-- 切磋战绩表
CREATE TABLE IF NOT EXISTS spar_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    attacker_id INT NOT NULL COMMENT '发起切磋的玩家ID',
    defender_id INT NOT NULL COMMENT '被切磋的玩家ID',
    is_victory TINYINT(1) NOT NULL DEFAULT 0 COMMENT '发起者是否胜利',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '切磋时间',
    INDEX idx_attacker (attacker_id),
    INDEX idx_defender (defender_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='切磋战绩记录';
