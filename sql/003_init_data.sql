-- ============================================
-- 初始化测试数据
-- ============================================

USE game_tower;

-- 清空旧数据（可选）
-- TRUNCATE TABLE player_beast;
-- TRUNCATE TABLE tower_state;

-- 插入测试玩家幻兽数据（已存在则跳过）
INSERT IGNORE INTO player_beast (
    user_id, name, realm, race, level, nature, personality,
    hp, physical_attack, magic_attack, physical_defense, magic_defense, speed,
    combat_power, growth_rate,
    hp_aptitude, speed_aptitude, magic_attack_aptitude, physical_defense_aptitude, magic_defense_aptitude,
    lifespan, skills, counters, countered_by,
    is_in_team, team_position
) VALUES
(1, '圣灵蚁', '神界', '虫族', 84, '法系普攻', '勇敢',
 31215, 28375, 28375, 5339, 7074, 2024,
 10974, 1440,
 1327, 1606, 1974, 1158, 1489,
 '10000/10000', '["高级闪避", "高级雷击", "高级必杀", "高级致盲", "打书"]',
 '物防类、法系高速', '法防类、物系高速',
 1, 1),

(1, '神·朱雀', '天界', '飞禽', 84, '法系普攻', '冷静',
 48000, 25000, 26000, 6000, 7200, 1800,
 9500, 1320,
 1200, 1400, 1850, 1100, 1350,
 '10000/10000', '["高级火焰", "高级必杀", "高级反击"]',
 '物系低速', '法防类',
 1, 2),

(1, '霸王龙VI(绝版)', '天界', '龙族', 84, '物系普攻', '暴躁',
 52000, 30000, 18000, 5500, 4400, 1600,
 10200, 1380,
 1350, 1200, 1100, 1250, 1050,
 '10000/10000', '["高级撕咬", "高级必杀", "高级防御"]',
 '法防类', '物防类',
 1, 3),

(1, '神·青龙', '天界', '龙族', 84, '法系普攻', '稳重',
 50000, 27000, 28500, 7000, 8400, 2200,
 10800, 1400,
 1300, 1550, 1900, 1200, 1420,
 '10000/10000', '["高级雷击", "高级必杀", "高级闪避", "高级防御"]',
 '物防类', '法防类、物系高速',
 1, 4);

-- 初始化闯塔状态（已存在则跳过）
INSERT IGNORE INTO tower_state (user_id, tower_type, current_floor, max_floor_record, today_count) VALUES
(1, 'tongtian', 1, 1, 0),
(1, 'longwen', 1, 1, 0),
(1, 'zhanling', 1, 1, 0);
