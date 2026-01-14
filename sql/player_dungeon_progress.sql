CREATE TABLE IF NOT EXISTS player_dungeon_progress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    dungeon_name VARCHAR(100) NOT NULL,
    current_floor INT DEFAULT 1,
    total_floors INT DEFAULT 35,
    floor_cleared BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_dungeon (user_id, dungeon_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 迁移脚本：为现有表添加 floor_cleared 字段
-- ALTER TABLE player_dungeon_progress ADD COLUMN floor_cleared BOOLEAN DEFAULT TRUE;
