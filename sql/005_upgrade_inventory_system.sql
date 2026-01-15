-- ============================================
-- 升级背包系统：添加背包容量和临时背包功能
-- ============================================

USE game_tower;

-- 1. 创建背包信息表（存储背包等级和容量）
CREATE TABLE IF NOT EXISTS player_bag (
    user_id INT PRIMARY KEY,
    bag_level INT NOT NULL DEFAULT 1 COMMENT '背包等级 1-10',
    capacity INT NOT NULL DEFAULT 50 COMMENT '背包容量（格子数）',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='玩家背包信息表';

-- 2. 修改背包物品表，添加临时存放字段（如果字段不存在）
-- 注意：如果字段已存在会报错，可忽略
ALTER TABLE player_inventory 
ADD COLUMN is_temporary TINYINT NOT NULL DEFAULT 0 COMMENT '是否临时存放（0=正式，1=临时）' AFTER quantity;

-- 3. 删除原有的唯一键约束（如果存在）
-- 因为现在同一物品可能同时存在于正式和临时背包
ALTER TABLE player_inventory DROP INDEX uk_user_item;

-- 4. 创建新的唯一键约束（user_id + item_id + is_temporary）
ALTER TABLE player_inventory 
ADD UNIQUE KEY uk_user_item_temp (user_id, item_id, is_temporary);

-- 5. 为现有用户初始化背包信息
INSERT IGNORE INTO player_bag (user_id, bag_level, capacity) 
SELECT DISTINCT user_id, 1, 50 FROM player_inventory;

-- 6. 确保用户1有背包信息
INSERT IGNORE INTO player_bag (user_id, bag_level, capacity) VALUES (1, 1, 50);
