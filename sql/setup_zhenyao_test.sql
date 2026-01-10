-- ============================================
-- 设置镇妖测试数据：创建模拟玩家占领试炼层和炼狱层
-- ============================================

USE game_tower;

-- 清理旧的测试玩家（ID 100-105）
DELETE FROM player WHERE user_id IN (100, 101, 102, 103, 104, 105);
DELETE FROM player_beast WHERE user_id IN (100, 101, 102, 103, 104, 105);
DELETE FROM tower_state WHERE user_id IN (100, 101, 102, 103, 104, 105);

-- ============================================
-- 创建模拟玩家
-- ============================================

-- 玩家100: 战神阶（100级），可镇妖101-120层
INSERT INTO player (user_id, username, password, nickname, level, exp, gold)
VALUES (100, 'npc_zs1', '123456', '战神·烈焰', 100, 0, 10000);

-- 玩家101: 战神阶（85级），可镇妖101-120层
INSERT INTO player (user_id, username, password, nickname, level, exp, gold)
VALUES (101, 'npc_zs2', '123456', '战神·寒霜', 85, 0, 10000);

-- 玩家102: 玄武阶（75级），可镇妖81-100层
INSERT INTO player (user_id, username, password, nickname, level, exp, gold)
VALUES (102, 'npc_xw1', '123456', '玄武·青龙', 75, 0, 10000);

-- 玩家103: 飞马阶（65级），可镇妖61-80层
INSERT INTO player (user_id, username, password, nickname, level, exp, gold)
VALUES (103, 'npc_fm1', '123456', '飞马·神驹', 65, 0, 10000);

-- 玩家104: 天阶（55级），可镇妖41-60层
INSERT INTO player (user_id, username, password, nickname, level, exp, gold)
VALUES (104, 'npc_tj1', '123456', '天阶·霹雳', 55, 0, 10000);

-- 玩家105: 地阶（45级），可镇妖21-40层
INSERT INTO player (user_id, username, password, nickname, level, exp, gold)
VALUES (105, 'npc_dj1', '123456', '地阶·磐石', 45, 0, 10000);

-- ============================================
-- 为模拟玩家创建通天塔进度（满层）
-- ============================================
INSERT INTO tower_state (user_id, tower_type, current_floor, max_floor_record, today_count) VALUES
(100, 'tongtian', 120, 120, 0),
(101, 'tongtian', 120, 120, 0),
(102, 'tongtian', 100, 100, 0),
(103, 'tongtian', 80, 80, 0),
(104, 'tongtian', 60, 60, 0),
(105, 'tongtian', 40, 40, 0);

-- ============================================
-- 为模拟玩家创建幻兽（带技能）
-- ============================================

-- 玩家100的幻兽（战神阶）- 强力幻兽带多种技能
INSERT INTO player_beast (
    user_id, name, realm, race, level, nature, personality,
    hp, physical_attack, magic_attack, physical_defense, magic_defense, speed,
    combat_power, growth_rate,
    hp_aptitude, speed_aptitude, magic_attack_aptitude, physical_defense_aptitude, magic_defense_aptitude,
    lifespan, skills, counters, countered_by, is_in_team, team_position
) VALUES
(100, '炎魔神', '神界', '魔族', 90, '物系普攻', '狂暴', 
 25000, 3500, 1500, 2000, 1800, 1200, 
 45000, 98,
 95, 90, 80, 85, 82,
 '10000/10000', '["烈焰风暴","地狱之火","焚尽一切","魔神之怒"]', '神族', '冰系', 1, 1),
(100, '冰霜龙王', '神界', '龙族', 88, '法系普攻', '冷静',
 22000, 1200, 3200, 1800, 2200, 1100,
 42000, 96,
 92, 88, 95, 82, 90,
 '10000/10000', '["冰龙吐息","绝对零度","冰封千里","龙魂护体"]', '火系', '雷系', 1, 2);

-- 玩家101的幻兽（战神阶）
INSERT INTO player_beast (
    user_id, name, realm, race, level, nature, personality,
    hp, physical_attack, magic_attack, physical_defense, magic_defense, speed,
    combat_power, growth_rate,
    hp_aptitude, speed_aptitude, magic_attack_aptitude, physical_defense_aptitude, magic_defense_aptitude,
    lifespan, skills, counters, countered_by, is_in_team, team_position
) VALUES
(101, '雷霆巨兽', '天界', '神兽', 85, '物系普攻', '暴躁',
 20000, 2800, 1000, 1600, 1400, 1000,
 38000, 94,
 90, 85, 75, 88, 80,
 '10000/10000', '["雷霆万钧","电光石火","天雷滚滚"]', '', '', 1, 1),
(101, '圣光天使', '天界', '仙族', 82, '法系普攻', '温和',
 18000, 800, 2600, 1400, 1800, 950,
 35000, 92,
 88, 82, 92, 80, 88,
 '10000/10000', '["圣光普照","神圣审判","治愈之光"]', '暗系', '暗系', 1, 2);

-- 玩家102的幻兽（玄武阶）
INSERT INTO player_beast (
    user_id, name, realm, race, level, nature, personality,
    hp, physical_attack, magic_attack, physical_defense, magic_defense, speed,
    combat_power, growth_rate,
    hp_aptitude, speed_aptitude, magic_attack_aptitude, physical_defense_aptitude, magic_defense_aptitude,
    lifespan, skills, counters, countered_by, is_in_team, team_position
) VALUES
(102, '青龙使者', '天界', '龙族', 75, '法系普攻', '睿智',
 15000, 900, 2200, 1300, 1500, 850,
 30000, 90,
 85, 80, 88, 82, 85,
 '10000/10000', '["青龙破空","龙卷风暴","苍龙护甲"]', '虎族', '凤族', 1, 1),
(102, '玄武盾卫', '天界', '龟族', 73, '物系普攻', '沉稳',
 18000, 1800, 600, 2000, 1600, 600,
 28000, 88,
 90, 70, 65, 92, 85,
 '10000/10000', '["玄武护盾","铁壁防御","龟息大法"]', '', '雷系', 1, 2);

-- 玩家103的幻兽（飞马阶）
INSERT INTO player_beast (
    user_id, name, realm, race, level, nature, personality,
    hp, physical_attack, magic_attack, physical_defense, magic_defense, speed,
    combat_power, growth_rate,
    hp_aptitude, speed_aptitude, magic_attack_aptitude, physical_defense_aptitude, magic_defense_aptitude,
    lifespan, skills, counters, countered_by, is_in_team, team_position
) VALUES
(103, '飞马骑士', '人界', '马族', 65, '物系普攻', '勇敢',
 12000, 1600, 500, 1100, 900, 900,
 22000, 85,
 80, 85, 60, 78, 75,
 '10000/10000', '["天马流星拳","飞马踏云","马踏连营"]', '', '', 1, 1),
(103, '风之精灵', '仙界', '精灵族', 63, '法系普攻', '活泼',
 10000, 500, 1400, 800, 1200, 1000,
 18000, 82,
 75, 90, 85, 72, 80,
 '10000/10000', '["风之刃","疾风步","风暴之眼"]', '土系', '土系', 1, 2);

-- 玩家104的幻兽（天阶）
INSERT INTO player_beast (
    user_id, name, realm, race, level, nature, personality,
    hp, physical_attack, magic_attack, physical_defense, magic_defense, speed,
    combat_power, growth_rate,
    hp_aptitude, speed_aptitude, magic_attack_aptitude, physical_defense_aptitude, magic_defense_aptitude,
    lifespan, skills, counters, countered_by, is_in_team, team_position
) VALUES
(104, '霹雳战士', '人界', '人族', 55, '物系普攻', '刚毅',
 9000, 1200, 400, 900, 700, 750,
 16000, 78,
 75, 78, 55, 75, 70,
 '10000/10000', '["霹雳斩","雷电拳","电光剑"]', '', '水系', 1, 1),
(104, '火焰术士', '人界', '人族', 53, '法系普攻', '热情',
 7500, 350, 1100, 700, 900, 700,
 14000, 75,
 70, 75, 80, 68, 75,
 '10000/10000', '["火球术","烈焰喷射","火焰护盾"]', '草系', '水系', 1, 2);

-- 玩家105的幻兽（地阶）
INSERT INTO player_beast (
    user_id, name, realm, race, level, nature, personality,
    hp, physical_attack, magic_attack, physical_defense, magic_defense, speed,
    combat_power, growth_rate,
    hp_aptitude, speed_aptitude, magic_attack_aptitude, physical_defense_aptitude, magic_defense_aptitude,
    lifespan, skills, counters, countered_by, is_in_team, team_position
) VALUES
(105, '石甲巨人', '人界', '石族', 45, '物系普攻', '笨拙',
 8000, 900, 300, 1000, 600, 500,
 12000, 70,
 72, 60, 50, 80, 65,
 '10000/10000', '["巨石碾压","山崩地裂"]', '草系', '水系', 1, 1),
(105, '水晶法师', '人界', '人族', 43, '法系普攻', '聪慧',
 6000, 280, 800, 550, 750, 600,
 10000, 68,
 65, 70, 75, 60, 72,
 '10000/10000', '["水晶射线","魔法盾"]', '', '物理系', 1, 2);

-- ============================================
-- 让模拟玩家占领对应层数
-- ============================================

-- 战神阶层数 (101-120)
-- 试炼层：101-110，炼狱层：111-120

-- 玩家100占领试炼层105
UPDATE zhenyao_floor SET 
    occupant_id = 100, 
    occupant_name = '战神·烈焰',
    occupy_time = NOW(),
    expire_time = DATE_ADD(NOW(), INTERVAL 30 MINUTE)
WHERE floor = 105;

-- 玩家101占领炼狱层115
UPDATE zhenyao_floor SET 
    occupant_id = 101, 
    occupant_name = '战神·寒霜',
    occupy_time = NOW(),
    expire_time = DATE_ADD(NOW(), INTERVAL 30 MINUTE)
WHERE floor = 115;

-- 玄武阶层数 (81-100)
-- 试炼层：81-90，炼狱层：91-100

-- 玩家102占领试炼层85
UPDATE zhenyao_floor SET 
    occupant_id = 102, 
    occupant_name = '玄武·青龙',
    occupy_time = NOW(),
    expire_time = DATE_ADD(NOW(), INTERVAL 30 MINUTE)
WHERE floor = 85;

-- 玩家102也占领炼狱层95
UPDATE zhenyao_floor SET 
    occupant_id = 102, 
    occupant_name = '玄武·青龙',
    occupy_time = NOW(),
    expire_time = DATE_ADD(NOW(), INTERVAL 30 MINUTE)
WHERE floor = 95;

-- 飞马阶层数 (61-80)
-- 试炼层：61-70，炼狱层：71-80

-- 玩家103占领试炼层65
UPDATE zhenyao_floor SET 
    occupant_id = 103, 
    occupant_name = '飞马·神驹',
    occupy_time = NOW(),
    expire_time = DATE_ADD(NOW(), INTERVAL 30 MINUTE)
WHERE floor = 65;

-- 玩家103也占领炼狱层75
UPDATE zhenyao_floor SET 
    occupant_id = 103, 
    occupant_name = '飞马·神驹',
    occupy_time = NOW(),
    expire_time = DATE_ADD(NOW(), INTERVAL 30 MINUTE)
WHERE floor = 75;

-- 天阶层数 (41-60)
-- 试炼层：41-50，炼狱层：51-60

-- 玩家104占领试炼层45
UPDATE zhenyao_floor SET 
    occupant_id = 104, 
    occupant_name = '天阶·霹雳',
    occupy_time = NOW(),
    expire_time = DATE_ADD(NOW(), INTERVAL 30 MINUTE)
WHERE floor = 45;

-- 玩家104也占领炼狱层55
UPDATE zhenyao_floor SET 
    occupant_id = 104, 
    occupant_name = '天阶·霹雳',
    occupy_time = NOW(),
    expire_time = DATE_ADD(NOW(), INTERVAL 30 MINUTE)
WHERE floor = 55;

-- 地阶层数 (21-40)
-- 试炼层：21-30，炼狱层：31-40

-- 玩家105占领试炼层25
UPDATE zhenyao_floor SET 
    occupant_id = 105, 
    occupant_name = '地阶·磐石',
    occupy_time = NOW(),
    expire_time = DATE_ADD(NOW(), INTERVAL 30 MINUTE)
WHERE floor = 25;

-- 玩家105也占领炼狱层35
UPDATE zhenyao_floor SET 
    occupant_id = 105, 
    occupant_name = '地阶·磐石',
    occupy_time = NOW(),
    expire_time = DATE_ADD(NOW(), INTERVAL 30 MINUTE)
WHERE floor = 35;

-- ============================================
-- 完成！显示占领情况
-- ============================================
SELECT 
    floor AS '层数',
    occupant_name AS '占领者',
    CASE 
        WHEN floor BETWEEN 101 AND 110 THEN '战神试炼层'
        WHEN floor BETWEEN 111 AND 120 THEN '战神炼狱层'
        WHEN floor BETWEEN 81 AND 90 THEN '玄武试炼层'
        WHEN floor BETWEEN 91 AND 100 THEN '玄武炼狱层'
        WHEN floor BETWEEN 61 AND 70 THEN '飞马试炼层'
        WHEN floor BETWEEN 71 AND 80 THEN '飞马炼狱层'
        WHEN floor BETWEEN 41 AND 50 THEN '天阶试炼层'
        WHEN floor BETWEEN 51 AND 60 THEN '天阶炼狱层'
        WHEN floor BETWEEN 21 AND 30 THEN '地阶试炼层'
        WHEN floor BETWEEN 31 AND 40 THEN '地阶炼狱层'
        ELSE '其他层'
    END AS '层类型',
    expire_time AS '占领到期时间'
FROM zhenyao_floor
WHERE occupant_id IS NOT NULL
ORDER BY floor;
