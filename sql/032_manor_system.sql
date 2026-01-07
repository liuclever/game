-- ============================================
-- 庄园系统表
-- ============================================

USE game_tower;

-- 庄园土地表
CREATE TABLE IF NOT EXISTS manor_land (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    land_index INT NOT NULL COMMENT '0-9:普通土地, 10:黄土地, 11:银土地, 12:金土地',
    status TINYINT NOT NULL DEFAULT 0 COMMENT '0:未开启, 1:空闲, 2:种植中',
    tree_type INT DEFAULT 0 COMMENT '种植的种类：1, 2, 4, 6, 8株',
    plant_time DATETIME DEFAULT NULL COMMENT '种植开始时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_land (user_id, land_index),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='庄园土地表';

-- 玩家庄园扩展表
CREATE TABLE IF NOT EXISTS player_manor (
    user_id INT PRIMARY KEY,
    total_harvest_count INT DEFAULT 0 COMMENT '累计收获次数',
    total_gold_earned BIGINT DEFAULT 0 COMMENT '累计获得铜钱',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='玩家庄园扩展表';
