-- ============================================
-- 创建数据表
-- ============================================

USE game_tower;

-- 闯塔状态表
CREATE TABLE IF NOT EXISTS tower_state (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    tower_type VARCHAR(20) NOT NULL DEFAULT 'tongtian',
    current_floor INT NOT NULL DEFAULT 1,
    max_floor_record INT NOT NULL DEFAULT 1,
    today_count INT NOT NULL DEFAULT 0,
    last_challenge_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_tower (user_id, tower_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='闯塔状态表';

-- 玩家幻兽表
CREATE TABLE IF NOT EXISTS player_beast (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(50) NOT NULL COMMENT '幻兽名称',
    realm VARCHAR(20) NOT NULL COMMENT '境界(神界/天界等)',
    race VARCHAR(20) DEFAULT '' COMMENT '种族(虫族/龙族等)',
    level INT NOT NULL DEFAULT 1 COMMENT '等级',
    nature VARCHAR(20) NOT NULL DEFAULT '物系' COMMENT '特性(法系普攻/物系普攻等)',
    personality VARCHAR(20) DEFAULT '' COMMENT '性格',
    hp INT NOT NULL COMMENT '气血',
    physical_attack INT NOT NULL COMMENT '物攻',
    magic_attack INT NOT NULL COMMENT '法攻',
    physical_defense INT NOT NULL COMMENT '物防',
    magic_defense INT NOT NULL COMMENT '法防',
    speed INT NOT NULL COMMENT '速度',
    combat_power INT DEFAULT 0 COMMENT '综合战力',
    growth_rate INT DEFAULT 0 COMMENT '成长率',
    hp_aptitude INT DEFAULT 0 COMMENT '气血资质',
    speed_aptitude INT DEFAULT 0 COMMENT '速度资质',
    magic_attack_aptitude INT DEFAULT 0 COMMENT '法攻资质',
    physical_defense_aptitude INT DEFAULT 0 COMMENT '物防资质',
    magic_defense_aptitude INT DEFAULT 0 COMMENT '法防资质',
    lifespan VARCHAR(20) DEFAULT '10000/10000' COMMENT '寿命',
    skills TEXT COMMENT '技能列表(JSON格式)',
    counters VARCHAR(100) DEFAULT '' COMMENT '克制',
    countered_by VARCHAR(100) DEFAULT '' COMMENT '被克',
    is_in_team TINYINT(1) DEFAULT 0 COMMENT '是否在战斗队',
    team_position INT DEFAULT 0 COMMENT '战斗队位置',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_team (user_id, is_in_team),
    UNIQUE KEY uk_user_beast (user_id, name, realm)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='玩家幻兽表';
