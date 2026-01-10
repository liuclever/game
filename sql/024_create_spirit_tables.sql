-- ============================================
-- 创建战灵（Spirit）系统相关表
-- ============================================

USE game_tower;

-- 玩家战灵账户（灵力、解锁孔位、每日免费洗练等）
CREATE TABLE IF NOT EXISTS spirit_account (
    user_id INT PRIMARY KEY,
    spirit_power INT NOT NULL DEFAULT 0 COMMENT '灵力',
    unlocked_elements TEXT NOT NULL COMMENT '已解锁元素列表(JSON)',
    free_refine_date DATE DEFAULT NULL COMMENT '当日免费洗练计数对应日期',
    free_refine_used INT NOT NULL DEFAULT 0 COMMENT '当日已使用免费洗练次数',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='战灵账户';

-- 玩家战灵（含 3 条词条；value_bp=1 表示 0.01%）
CREATE TABLE IF NOT EXISTS player_spirit (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '玩家ID',
    beast_id INT DEFAULT NULL COMMENT '装备到的幻兽ID（未装备时为NULL）',

    element VARCHAR(10) NOT NULL COMMENT '元素：earth/fire/water/wood/metal/god',
    race VARCHAR(20) NOT NULL DEFAULT '' COMMENT '种族：兽族/龙族/虫族/飞禽/神兽等',

    line1_attr VARCHAR(50) NOT NULL DEFAULT '',
    line1_value_bp INT NOT NULL DEFAULT 0,
    line1_unlocked TINYINT NOT NULL DEFAULT 0,
    line1_locked TINYINT NOT NULL DEFAULT 0,

    line2_attr VARCHAR(50) NOT NULL DEFAULT '',
    line2_value_bp INT NOT NULL DEFAULT 0,
    line2_unlocked TINYINT NOT NULL DEFAULT 0,
    line2_locked TINYINT NOT NULL DEFAULT 0,

    line3_attr VARCHAR(50) NOT NULL DEFAULT '',
    line3_value_bp INT NOT NULL DEFAULT 0,
    line3_unlocked TINYINT NOT NULL DEFAULT 0,
    line3_locked TINYINT NOT NULL DEFAULT 0,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_user_id (user_id),
    INDEX idx_beast_id (beast_id),
    INDEX idx_user_beast (user_id, beast_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='玩家战灵';
