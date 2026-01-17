-- ============================================
-- 创建战骨表
-- ============================================

USE game_tower;

-- 玩家战骨表
CREATE TABLE IF NOT EXISTS beast_bone (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '玩家ID',
    beast_id INT DEFAULT NULL COMMENT '装备到的幻兽ID（未装备时为NULL）',
    template_id INT NOT NULL COMMENT '战骨模板ID',
    slot VARCHAR(20) NOT NULL COMMENT '槽位：头骨/胸骨/臂骨/手骨/腿骨/尾骨/元魂',
    level INT NOT NULL DEFAULT 1 COMMENT '等级',
    stage INT NOT NULL DEFAULT 1 COMMENT '阶段',
    hp_flat INT NOT NULL DEFAULT 0 COMMENT '气血加成（固定值）',
    attack_flat INT NOT NULL DEFAULT 0 COMMENT '攻击加成（固定值）',
    physical_defense_flat INT NOT NULL DEFAULT 0 COMMENT '物防加成（固定值）',
    magic_defense_flat INT NOT NULL DEFAULT 0 COMMENT '法防加成（固定值）',
    speed_flat INT NOT NULL DEFAULT 0 COMMENT '速度加成（固定值）',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_user_id (user_id),
    INDEX idx_beast_id (beast_id),
    INDEX idx_user_beast (user_id, beast_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='玩家战骨表';

