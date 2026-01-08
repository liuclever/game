-- 020 擂台战斗记录表
USE game_tower;

-- 擂台挑战战报表（用于擂台动态 + 详细战报）
CREATE TABLE IF NOT EXISTS arena_battle_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    arena_type VARCHAR(10) NOT NULL COMMENT '场次类型（normal普通场/gold黄金场）',
    rank_name VARCHAR(20) NOT NULL COMMENT '等级阶段名称（黄阶/玄阶/地阶/天阶/飞马/天龙/战神）',
    challenger_id INT NOT NULL COMMENT '挑战者ID',
    challenger_name VARCHAR(50) NOT NULL COMMENT '挑战者昵称',
    champion_id INT NOT NULL COMMENT '擂主ID',
    champion_name VARCHAR(50) NOT NULL COMMENT '擂主昵称',
    is_challenger_win TINYINT NOT NULL DEFAULT 0 COMMENT '是否挑战成功(1=成功,0=失败)',
    battle_data TEXT COMMENT '战斗详情(JSON)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_challenger (challenger_id),
    INDEX idx_champion (champion_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='擂台挑战战斗记录表';
