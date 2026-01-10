-- ============================================
-- 添加登录功能和镇妖挑战记录
-- ============================================

USE game_tower;

-- 1. 修改玩家表，添加登录字段
ALTER TABLE player 
ADD COLUMN username VARCHAR(50) NOT NULL DEFAULT '' COMMENT '账号' AFTER user_id,
ADD COLUMN password VARCHAR(100) NOT NULL DEFAULT '' COMMENT '密码' AFTER username,
ADD UNIQUE KEY uk_username (username);

-- 2. 更新测试用户（账号test1，密码123456，满级）
UPDATE player SET username = 'test1', password = '123456' WHERE user_id = 1;

-- 3. 插入第二个测试用户（账号test2，密码123456，满级）
INSERT IGNORE INTO player (user_id, username, password, nickname, level, exp, gold) 
VALUES (2, 'test2', '123456', '测试玩家2', 100, 0, 10000);

-- 4. 为第二个测试用户创建闯塔进度（满层）
INSERT IGNORE INTO tower_state (user_id, tower_type, current_floor, max_floor_record, today_count)
VALUES (2, 'tongtian', 120, 120, 0);

-- 5. 创建镇妖挑战记录表
CREATE TABLE IF NOT EXISTS zhenyao_battle_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    floor INT NOT NULL COMMENT '层数',
    attacker_id INT NOT NULL COMMENT '挑战者ID',
    attacker_name VARCHAR(50) NOT NULL COMMENT '挑战者昵称',
    defender_id INT NOT NULL COMMENT '被挑战者ID',
    defender_name VARCHAR(50) NOT NULL COMMENT '被挑战者昵称',
    is_success TINYINT NOT NULL DEFAULT 0 COMMENT '是否成功(1=成功,0=失败)',
    remaining_seconds INT NOT NULL DEFAULT 0 COMMENT '剩余秒数(挑战时)',
    battle_data TEXT COMMENT '战斗详情(JSON)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_floor (floor),
    INDEX idx_attacker (attacker_id),
    INDEX idx_defender (defender_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='镇妖挑战记录表';

-- 6. 创建镇妖每日次数表
CREATE TABLE IF NOT EXISTS zhenyao_daily_count (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    trial_count INT NOT NULL DEFAULT 0 COMMENT '试炼层已用次数',
    hell_count INT NOT NULL DEFAULT 0 COMMENT '炼狱层已用次数',
    count_date DATE NOT NULL COMMENT '统计日期',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_date (user_id, count_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='镇妖每日次数表';

-- 7. 为第二个测试用户初始化背包
INSERT IGNORE INTO player_bag (user_id, bag_level, capacity) VALUES (2, 1, 50);

-- 8. 为第二个测试用户创建幻兽
INSERT IGNORE INTO player_beast (
    user_id, name, realm, race, level, nature, personality,
    hp, physical_attack, magic_attack, physical_defense, magic_defense, speed,
    combat_power, growth_rate,
    hp_aptitude, speed_aptitude, magic_attack_aptitude, physical_defense_aptitude, magic_defense_aptitude,
    lifespan, skills, counters, countered_by, is_in_team, team_position
) VALUES
(2, '炎龙', '天界', '龙族', 80, '物系普攻', '勇猛', 
 12000, 1800, 800, 1200, 1000, 600, 
 28000, 95,
 90, 85, 75, 88, 82,
 '10000/10000', '["龙息","烈焰冲击","龙鳞护体"]', '虫族', '冰系', 1, 1),
(2, '冰凤', '天界', '飞禽', 75, '法系普攻', '冷静',
 10000, 600, 1600, 900, 1400, 700,
 25000, 92,
 85, 90, 92, 80, 88,
 '10000/10000', '["冰霜新星","凤凰涅槃","寒冰屏障"]', '龙族', '火系', 1, 2),
(2, '雷神兽', '神界', '神兽', 85, '物系普攻', '狂暴',
 15000, 2000, 1000, 1500, 1200, 550,
 32000, 98,
 95, 80, 82, 90, 85,
 '10000/10000', '["雷霆万钧","神威","天罚"]', '', '', 1, 3);

-- 9. 给测试用户一些镇妖符（物品ID 7001）
-- INSERT IGNORE INTO player_inventory (user_id, item_id, quantity) VALUES (1, 7001, 100);
-- INSERT IGNORE INTO player_inventory (user_id, item_id, quantity) VALUES (2, 7001, 100);
