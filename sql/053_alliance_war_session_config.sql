-- 053 盟战届次配置表
USE game_tower;

-- 盟战届次配置表（存储当前届次）
CREATE TABLE IF NOT EXISTS alliance_war_session_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(50) NOT NULL UNIQUE COMMENT '配置键',
    session_number INT NOT NULL DEFAULT 1 COMMENT '当前届次',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_config_key (config_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='盟战届次配置表';

-- 初始化当前届次为1
INSERT INTO alliance_war_session_config (config_key, session_number)
VALUES ('current_session', 1)
ON DUPLICATE KEY UPDATE session_number = 1;
