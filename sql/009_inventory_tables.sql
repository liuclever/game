-- 009 背包系统表
-- 玩家背包和物品存储相关表

USE game_tower;

-- 玩家背包物品表
CREATE TABLE IF NOT EXISTS player_inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    item_id INT NOT NULL COMMENT '物品ID',
    quantity INT NOT NULL DEFAULT 1 COMMENT '数量',
    is_temporary TINYINT NOT NULL DEFAULT 0 COMMENT '是否临时存放（0=正式，1=临时）',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    UNIQUE KEY uk_user_item_temp (user_id, item_id, is_temporary)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='玩家背包表';

-- 玩家背包信息表
CREATE TABLE IF NOT EXISTS player_bag (
    user_id INT PRIMARY KEY,
    bag_level INT NOT NULL DEFAULT 1 COMMENT '背包等级 1-10',
    capacity INT NOT NULL DEFAULT 100 COMMENT '背包容量（格子数）',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='玩家背包信息表';
