-- 038 切磋战斗记录表
USE game_tower;

-- 切磋战斗记录表（用于动态记录）
CREATE TABLE IF NOT EXISTS spar_battle_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    attacker_id INT NOT NULL COMMENT '挑战者ID',
    attacker_name VARCHAR(50) NOT NULL COMMENT '挑战者昵称',
    defender_id INT NOT NULL COMMENT '被挑战者ID',
    defender_name VARCHAR(50) NOT NULL COMMENT '被挑战者昵称',
    is_attacker_win TINYINT NOT NULL DEFAULT 0 COMMENT '挑战者是否获胜(1=胜,0=负)',
    battle_data TEXT COMMENT '战斗详情(JSON)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_attacker (attacker_id),
    INDEX idx_defender (defender_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='切磋战斗记录表';
