-- ========================================
-- V40 排行榜测试数据
-- 覆盖：等级排行、战力排行、擂台排行、VIP排行
-- ========================================

SET FOREIGN_KEY_CHECKS=0;

-- ========================================
-- 1. 玩家测试数据（覆盖各等级段位和VIP等级）
-- ========================================

-- 见习阶段 (1-19级) - 不参与擂台
INSERT INTO `player` (`user_id`, `username`, `password`, `nickname`, `level`, `exp`, `prestige`, `vip_level`, `gold`, `yuanbao`) VALUES
(5001, 'test_jianxi_01', '123456', '见习小白', 5, 100, 50, 0, 1000, 100),
(5002, 'test_jianxi_02', '123456', '见习萌新', 10, 500, 200, 1, 2000, 200),
(5003, 'test_jianxi_03', '123456', '见习勇士', 15, 1000, 500, 2, 3000, 300),
(5004, 'test_jianxi_04', '123456', '见习高手', 19, 2000, 1000, 0, 4000, 400);

-- 黄阶 (20-29级)
INSERT INTO `player` (`user_id`, `username`, `password`, `nickname`, `level`, `exp`, `prestige`, `vip_level`, `gold`, `yuanbao`) VALUES
(5011, 'test_huang_01', '123456', '黄阶战士A', 20, 3000, 1500, 0, 5000, 500),
(5012, 'test_huang_02', '123456', '黄阶战士B', 22, 4000, 2000, 3, 6000, 600),
(5013, 'test_huang_03', '123456', '黄阶战士C', 25, 5000, 2500, 0, 7000, 700),
(5014, 'test_huang_04', '123456', '黄阶战士D', 27, 6000, 3000, 4, 8000, 800),
(5015, 'test_huang_05', '123456', '黄阶霸主', 29, 8000, 4000, 5, 10000, 1000);

-- 玄阶 (30-39级)
INSERT INTO `player` (`user_id`, `username`, `password`, `nickname`, `level`, `exp`, `prestige`, `vip_level`, `gold`, `yuanbao`) VALUES
(5021, 'test_xuan_01', '123456', '玄阶剑客A', 30, 10000, 5000, 0, 12000, 1200),
(5022, 'test_xuan_02', '123456', '玄阶剑客B', 33, 15000, 6000, 5, 15000, 1500),
(5023, 'test_xuan_03', '123456', '玄阶剑客C', 36, 20000, 7000, 0, 18000, 1800),
(5024, 'test_xuan_04', '123456', '玄阶霸主', 39, 25000, 8000, 6, 20000, 2000);

-- 地阶 (40-49级)
INSERT INTO `player` (`user_id`, `username`, `password`, `nickname`, `level`, `exp`, `prestige`, `vip_level`, `gold`, `yuanbao`) VALUES
(5031, 'test_di_01', '123456', '地阶武者A', 40, 30000, 10000, 0, 25000, 2500),
(5032, 'test_di_02', '123456', '地阶武者B', 44, 40000, 12000, 6, 30000, 3000),
(5033, 'test_di_03', '123456', '地阶霸主', 49, 50000, 15000, 7, 35000, 3500);

-- 天阶 (50-59级)
INSERT INTO `player` (`user_id`, `username`, `password`, `nickname`, `level`, `exp`, `prestige`, `vip_level`, `gold`, `yuanbao`) VALUES
(5041, 'test_tian_01', '123456', '天阶高手A', 50, 60000, 18000, 0, 40000, 4000),
(5042, 'test_tian_02', '123456', '天阶高手B', 55, 80000, 22000, 7, 50000, 5000),
(5043, 'test_tian_03', '123456', '天阶霸主', 59, 100000, 28000, 8, 60000, 6000);

-- 飞马 (60-69级)
INSERT INTO `player` (`user_id`, `username`, `password`, `nickname`, `level`, `exp`, `prestige`, `vip_level`, `gold`, `yuanbao`) VALUES
(5051, 'test_feima_01', '123456', '飞马骑士A', 60, 120000, 30000, 0, 70000, 7000),
(5052, 'test_feima_02', '123456', '飞马骑士B', 65, 150000, 35000, 8, 80000, 8000),
(5053, 'test_feima_03', '123456', '飞马霸主', 69, 180000, 40000, 9, 90000, 9000);

-- 天龙 (70-79级)
INSERT INTO `player` (`user_id`, `username`, `password`, `nickname`, `level`, `exp`, `prestige`, `vip_level`, `gold`, `yuanbao`) VALUES
(5061, 'test_tianlong_01', '123456', '天龙战神A', 70, 200000, 45000, 0, 100000, 10000),
(5062, 'test_tianlong_02', '123456', '天龙战神B', 75, 250000, 55000, 9, 120000, 12000),
(5063, 'test_tianlong_03', '123456', '天龙霸主', 79, 300000, 65000, 10, 150000, 15000);

-- 战神 (80-100级)
INSERT INTO `player` (`user_id`, `username`, `password`, `nickname`, `level`, `exp`, `prestige`, `vip_level`, `gold`, `yuanbao`) VALUES
(5071, 'test_zhanshen_01', '123456', '战神无敌A', 80, 350000, 70000, 0, 180000, 18000),
(5072, 'test_zhanshen_02', '123456', '战神无敌B', 85, 400000, 80000, 10, 200000, 20000),
(5073, 'test_zhanshen_03', '123456', '战神无敌C', 90, 500000, 100000, 10, 250000, 25000),
(5074, 'test_zhanshen_04', '123456', '战神霸主', 100, 999999, 200000, 10, 500000, 50000);


-- ========================================
-- 2. 幻兽测试数据（设置战力，用于战力排行）
-- ========================================

-- 见习阶段玩家的幻兽（低战力）
INSERT INTO `player_beast` (`user_id`, `template_id`, `name`, `nickname`, `realm`, `race`, `level`, `nature`, `hp`, `physical_attack`, `magic_attack`, `physical_defense`, `magic_defense`, `speed`, `combat_power`, `is_in_team`, `team_position`) VALUES
(5001, 1, '血螳螂', '小螳螂', '人界', '虫族', 5, '物系', 50, 10, 5, 8, 5, 10, 500, 1, 1),
(5002, 1, '血螳螂', '小螳螂', '人界', '虫族', 10, '物系', 80, 15, 8, 12, 8, 15, 800, 1, 1),
(5003, 1, '血螳螂', '小螳螂', '人界', '虫族', 15, '物系', 120, 22, 12, 18, 12, 22, 1200, 1, 1),
(5004, 1, '血螳螂', '小螳螂', '人界', '虫族', 19, '物系', 150, 28, 15, 22, 15, 28, 1500, 1, 1);

-- 黄阶玩家的幻兽
INSERT INTO `player_beast` (`user_id`, `template_id`, `name`, `nickname`, `realm`, `race`, `level`, `nature`, `hp`, `physical_attack`, `magic_attack`, `physical_defense`, `magic_defense`, `speed`, `combat_power`, `is_in_team`, `team_position`) VALUES
(5011, 2, '火麒麟', '小火', '地界', '兽族', 20, '物系', 200, 35, 20, 28, 20, 35, 2000, 1, 1),
(5012, 2, '火麒麟', '小火', '地界', '兽族', 22, '物系', 250, 42, 25, 35, 25, 42, 2500, 1, 1),
(5013, 2, '火麒麟', '小火', '地界', '兽族', 25, '物系', 300, 50, 30, 42, 30, 50, 3000, 1, 1),
(5014, 2, '火麒麟', '小火', '地界', '兽族', 27, '物系', 350, 58, 35, 48, 35, 58, 3500, 1, 1),
(5015, 2, '火麒麟', '小火', '地界', '兽族', 29, '物系', 400, 65, 40, 55, 40, 65, 4000, 1, 1);

-- 玄阶玩家的幻兽
INSERT INTO `player_beast` (`user_id`, `template_id`, `name`, `nickname`, `realm`, `race`, `level`, `nature`, `hp`, `physical_attack`, `magic_attack`, `physical_defense`, `magic_defense`, `speed`, `combat_power`, `is_in_team`, `team_position`) VALUES
(5021, 3, '玄武', '小玄', '天界', '神兽', 30, '法系', 500, 50, 70, 65, 65, 55, 5000, 1, 1),
(5022, 3, '玄武', '小玄', '天界', '神兽', 33, '法系', 600, 60, 85, 78, 78, 65, 6000, 1, 1),
(5023, 3, '玄武', '小玄', '天界', '神兽', 36, '法系', 700, 70, 100, 90, 90, 75, 7000, 1, 1),
(5024, 3, '玄武', '小玄', '天界', '神兽', 39, '法系', 800, 80, 115, 105, 105, 85, 8000, 1, 1);

-- 地阶玩家的幻兽
INSERT INTO `player_beast` (`user_id`, `template_id`, `name`, `nickname`, `realm`, `race`, `level`, `nature`, `hp`, `physical_attack`, `magic_attack`, `physical_defense`, `magic_defense`, `speed`, `combat_power`, `is_in_team`, `team_position`) VALUES
(5031, 4, '青龙', '小青', '神界', '龙族', 40, '法系', 1000, 90, 130, 120, 120, 95, 10000, 1, 1),
(5032, 4, '青龙', '小青', '神界', '龙族', 44, '法系', 1200, 110, 160, 145, 145, 115, 12000, 1, 1),
(5033, 4, '青龙', '小青', '神界', '龙族', 49, '法系', 1500, 135, 195, 175, 175, 140, 15000, 1, 1);

-- 天阶玩家的幻兽
INSERT INTO `player_beast` (`user_id`, `template_id`, `name`, `nickname`, `realm`, `race`, `level`, `nature`, `hp`, `physical_attack`, `magic_attack`, `physical_defense`, `magic_defense`, `speed`, `combat_power`, `is_in_team`, `team_position`) VALUES
(5041, 5, '白虎', '小白', '神界', '兽族', 50, '物系', 1800, 200, 120, 180, 150, 170, 18000, 1, 1),
(5042, 5, '白虎', '小白', '神界', '兽族', 55, '物系', 2200, 240, 145, 220, 185, 205, 22000, 1, 1),
(5043, 5, '白虎', '小白', '神界', '兽族', 59, '物系', 2800, 300, 180, 270, 230, 255, 28000, 1, 1);

-- 飞马玩家的幻兽
INSERT INTO `player_beast` (`user_id`, `template_id`, `name`, `nickname`, `realm`, `race`, `level`, `nature`, `hp`, `physical_attack`, `magic_attack`, `physical_defense`, `magic_defense`, `speed`, `combat_power`, `is_in_team`, `team_position`) VALUES
(5051, 6, '朱雀', '小朱', '神界', '飞禽', 60, '法系', 3000, 200, 350, 250, 300, 280, 30000, 1, 1),
(5052, 6, '朱雀', '小朱', '神界', '飞禽', 65, '法系', 3500, 235, 410, 295, 355, 330, 35000, 1, 1),
(5053, 6, '朱雀', '小朱', '神界', '飞禽', 69, '法系', 4000, 270, 470, 340, 405, 375, 40000, 1, 1);

-- 天龙玩家的幻兽
INSERT INTO `player_beast` (`user_id`, `template_id`, `name`, `nickname`, `realm`, `race`, `level`, `nature`, `hp`, `physical_attack`, `magic_attack`, `physical_defense`, `magic_defense`, `speed`, `combat_power`, `is_in_team`, `team_position`) VALUES
(5061, 7, '神龙', '小龙', '神界', '龙族', 70, '物系', 4500, 400, 300, 380, 350, 350, 45000, 1, 1),
(5062, 7, '神龙', '小龙', '神界', '龙族', 75, '物系', 5500, 480, 360, 455, 420, 420, 55000, 1, 1),
(5063, 7, '神龙', '小龙', '神界', '龙族', 79, '物系', 6500, 560, 420, 535, 495, 490, 65000, 1, 1);

-- 战神玩家的幻兽
INSERT INTO `player_beast` (`user_id`, `template_id`, `name`, `nickname`, `realm`, `race`, `level`, `nature`, `hp`, `physical_attack`, `magic_attack`, `physical_defense`, `magic_defense`, `speed`, `combat_power`, `is_in_team`, `team_position`) VALUES
(5071, 8, '鲲鹏', '小鹏', '神界', '神兽', 80, '物系', 7000, 600, 450, 570, 530, 530, 70000, 1, 1),
(5072, 8, '鲲鹏', '小鹏', '神界', '神兽', 85, '物系', 8000, 680, 510, 650, 605, 600, 80000, 1, 1),
(5073, 8, '鲲鹏', '小鹏', '神界', '神兽', 90, '物系', 10000, 850, 640, 810, 755, 750, 100000, 1, 1),
(5074, 8, '鲲鹏', '小鹏', '神界', '神兽', 100, '物系', 20000, 1500, 1200, 1450, 1350, 1400, 200000, 1, 1);

-- 给部分玩家添加第二只出战幻兽（增加战力排行多样性）
INSERT INTO `player_beast` (`user_id`, `template_id`, `name`, `nickname`, `realm`, `race`, `level`, `nature`, `hp`, `physical_attack`, `magic_attack`, `physical_defense`, `magic_defense`, `speed`, `combat_power`, `is_in_team`, `team_position`) VALUES
(5015, 1, '血螳螂', '副螳螂', '人界', '虫族', 25, '物系', 200, 35, 20, 28, 20, 35, 2000, 1, 2),
(5024, 2, '火麒麟', '副火', '地界', '兽族', 35, '物系', 500, 60, 35, 50, 35, 55, 5000, 1, 2),
(5033, 3, '玄武', '副玄', '天界', '神兽', 45, '法系', 1200, 100, 150, 130, 130, 110, 12000, 1, 2),
(5074, 7, '神龙', '副龙', '神界', '龙族', 95, '物系', 15000, 1200, 900, 1150, 1050, 1100, 150000, 1, 2);


-- ========================================
-- 3. 擂台战斗记录（用于擂台英豪榜）
-- ========================================

-- 黄阶擂台记录 - 历史记录（总英豪榜）
INSERT INTO `arena_battle_log` (`arena_type`, `rank_name`, `challenger_id`, `challenger_name`, `champion_id`, `champion_name`, `is_challenger_win`, `battle_data`, `created_at`) VALUES
-- 5015黄阶霸主 守擂成功5次（历史）
('normal', '黄阶', 5011, '黄阶战士A', 5015, '黄阶霸主', 0, '{"is_victory": false}', '2026-01-01 10:00:00'),
('normal', '黄阶', 5012, '黄阶战士B', 5015, '黄阶霸主', 0, '{"is_victory": false}', '2026-01-02 10:00:00'),
('normal', '黄阶', 5013, '黄阶战士C', 5015, '黄阶霸主', 0, '{"is_victory": false}', '2026-01-03 10:00:00'),
('normal', '黄阶', 5011, '黄阶战士A', 5015, '黄阶霸主', 0, '{"is_victory": false}', '2026-01-04 10:00:00'),
('normal', '黄阶', 5014, '黄阶战士D', 5015, '黄阶霸主', 0, '{"is_victory": false}', '2026-01-05 10:00:00'),
-- 5014黄阶战士D 守擂成功3次（历史）
('normal', '黄阶', 5011, '黄阶战士A', 5014, '黄阶战士D', 0, '{"is_victory": false}', '2026-01-01 11:00:00'),
('normal', '黄阶', 5012, '黄阶战士B', 5014, '黄阶战士D', 0, '{"is_victory": false}', '2026-01-02 11:00:00'),
('normal', '黄阶', 5013, '黄阶战士C', 5014, '黄阶战士D', 0, '{"is_victory": false}', '2026-01-03 11:00:00'),
-- 5012黄阶战士B 守擂成功2次（历史）
('normal', '黄阶', 5011, '黄阶战士A', 5012, '黄阶战士B', 0, '{"is_victory": false}', '2026-01-01 12:00:00'),
('normal', '黄阶', 5013, '黄阶战士C', 5012, '黄阶战士B', 0, '{"is_victory": false}', '2026-01-02 12:00:00');

-- 黄阶擂台记录 - 本周记录（周英豪榜，假设今天是2026-01-14）
INSERT INTO `arena_battle_log` (`arena_type`, `rank_name`, `challenger_id`, `challenger_name`, `champion_id`, `champion_name`, `is_challenger_win`, `battle_data`, `created_at`) VALUES
-- 5014本周守擂成功4次
('normal', '黄阶', 5011, '黄阶战士A', 5014, '黄阶战士D', 0, '{"is_victory": false}', '2026-01-10 10:00:00'),
('normal', '黄阶', 5012, '黄阶战士B', 5014, '黄阶战士D', 0, '{"is_victory": false}', '2026-01-11 10:00:00'),
('normal', '黄阶', 5013, '黄阶战士C', 5014, '黄阶战士D', 0, '{"is_victory": false}', '2026-01-12 10:00:00'),
('normal', '黄阶', 5015, '黄阶霸主', 5014, '黄阶战士D', 0, '{"is_victory": false}', '2026-01-13 10:00:00'),
-- 5015本周守擂成功2次
('normal', '黄阶', 5011, '黄阶战士A', 5015, '黄阶霸主', 0, '{"is_victory": false}', '2026-01-10 11:00:00'),
('normal', '黄阶', 5012, '黄阶战士B', 5015, '黄阶霸主', 0, '{"is_victory": false}', '2026-01-11 11:00:00'),
-- 5012本周守擂成功1次
('normal', '黄阶', 5011, '黄阶战士A', 5012, '黄阶战士B', 0, '{"is_victory": false}', '2026-01-10 12:00:00');

-- 玄阶擂台记录
INSERT INTO `arena_battle_log` (`arena_type`, `rank_name`, `challenger_id`, `challenger_name`, `champion_id`, `champion_name`, `is_challenger_win`, `battle_data`, `created_at`) VALUES
-- 5024玄阶霸主 历史+本周
('normal', '玄阶', 5021, '玄阶剑客A', 5024, '玄阶霸主', 0, '{"is_victory": false}', '2026-01-01 10:00:00'),
('normal', '玄阶', 5022, '玄阶剑客B', 5024, '玄阶霸主', 0, '{"is_victory": false}', '2026-01-02 10:00:00'),
('normal', '玄阶', 5023, '玄阶剑客C', 5024, '玄阶霸主', 0, '{"is_victory": false}', '2026-01-03 10:00:00'),
('normal', '玄阶', 5021, '玄阶剑客A', 5024, '玄阶霸主', 0, '{"is_victory": false}', '2026-01-10 10:00:00'),
('normal', '玄阶', 5022, '玄阶剑客B', 5024, '玄阶霸主', 0, '{"is_victory": false}', '2026-01-11 10:00:00'),
-- 5022玄阶剑客B
('normal', '玄阶', 5021, '玄阶剑客A', 5022, '玄阶剑客B', 0, '{"is_victory": false}', '2026-01-10 11:00:00'),
('normal', '玄阶', 5023, '玄阶剑客C', 5022, '玄阶剑客B', 0, '{"is_victory": false}', '2026-01-11 11:00:00');

-- 地阶擂台记录
INSERT INTO `arena_battle_log` (`arena_type`, `rank_name`, `challenger_id`, `challenger_name`, `champion_id`, `champion_name`, `is_challenger_win`, `battle_data`, `created_at`) VALUES
('normal', '地阶', 5031, '地阶武者A', 5033, '地阶霸主', 0, '{"is_victory": false}', '2026-01-01 10:00:00'),
('normal', '地阶', 5032, '地阶武者B', 5033, '地阶霸主', 0, '{"is_victory": false}', '2026-01-02 10:00:00'),
('normal', '地阶', 5031, '地阶武者A', 5033, '地阶霸主', 0, '{"is_victory": false}', '2026-01-10 10:00:00'),
('normal', '地阶', 5032, '地阶武者B', 5033, '地阶霸主', 0, '{"is_victory": false}', '2026-01-11 10:00:00'),
('normal', '地阶', 5031, '地阶武者A', 5032, '地阶武者B', 0, '{"is_victory": false}', '2026-01-10 11:00:00');

-- 天阶擂台记录
INSERT INTO `arena_battle_log` (`arena_type`, `rank_name`, `challenger_id`, `challenger_name`, `champion_id`, `champion_name`, `is_challenger_win`, `battle_data`, `created_at`) VALUES
('normal', '天阶', 5041, '天阶高手A', 5043, '天阶霸主', 0, '{"is_victory": false}', '2026-01-01 10:00:00'),
('normal', '天阶', 5042, '天阶高手B', 5043, '天阶霸主', 0, '{"is_victory": false}', '2026-01-02 10:00:00'),
('normal', '天阶', 5041, '天阶高手A', 5043, '天阶霸主', 0, '{"is_victory": false}', '2026-01-10 10:00:00'),
('normal', '天阶', 5042, '天阶高手B', 5043, '天阶霸主', 0, '{"is_victory": false}', '2026-01-11 10:00:00'),
('normal', '天阶', 5041, '天阶高手A', 5042, '天阶高手B', 0, '{"is_victory": false}', '2026-01-10 11:00:00');

-- 飞马擂台记录
INSERT INTO `arena_battle_log` (`arena_type`, `rank_name`, `challenger_id`, `challenger_name`, `champion_id`, `champion_name`, `is_challenger_win`, `battle_data`, `created_at`) VALUES
('normal', '飞马', 5051, '飞马骑士A', 5053, '飞马霸主', 0, '{"is_victory": false}', '2026-01-01 10:00:00'),
('normal', '飞马', 5052, '飞马骑士B', 5053, '飞马霸主', 0, '{"is_victory": false}', '2026-01-02 10:00:00'),
('normal', '飞马', 5051, '飞马骑士A', 5053, '飞马霸主', 0, '{"is_victory": false}', '2026-01-10 10:00:00'),
('normal', '飞马', 5052, '飞马骑士B', 5053, '飞马霸主', 0, '{"is_victory": false}', '2026-01-11 10:00:00'),
('normal', '飞马', 5051, '飞马骑士A', 5052, '飞马骑士B', 0, '{"is_victory": false}', '2026-01-10 11:00:00');

-- 天龙擂台记录
INSERT INTO `arena_battle_log` (`arena_type`, `rank_name`, `challenger_id`, `challenger_name`, `champion_id`, `champion_name`, `is_challenger_win`, `battle_data`, `created_at`) VALUES
('normal', '天龙', 5061, '天龙战神A', 5063, '天龙霸主', 0, '{"is_victory": false}', '2026-01-01 10:00:00'),
('normal', '天龙', 5062, '天龙战神B', 5063, '天龙霸主', 0, '{"is_victory": false}', '2026-01-02 10:00:00'),
('normal', '天龙', 5061, '天龙战神A', 5063, '天龙霸主', 0, '{"is_victory": false}', '2026-01-10 10:00:00'),
('normal', '天龙', 5062, '天龙战神B', 5063, '天龙霸主', 0, '{"is_victory": false}', '2026-01-11 10:00:00'),
('normal', '天龙', 5061, '天龙战神A', 5062, '天龙战神B', 0, '{"is_victory": false}', '2026-01-10 11:00:00');

-- 战神擂台记录
INSERT INTO `arena_battle_log` (`arena_type`, `rank_name`, `challenger_id`, `challenger_name`, `champion_id`, `champion_name`, `is_challenger_win`, `battle_data`, `created_at`) VALUES
('normal', '战神', 5071, '战神无敌A', 5074, '战神霸主', 0, '{"is_victory": false}', '2026-01-01 10:00:00'),
('normal', '战神', 5072, '战神无敌B', 5074, '战神霸主', 0, '{"is_victory": false}', '2026-01-02 10:00:00'),
('normal', '战神', 5073, '战神无敌C', 5074, '战神霸主', 0, '{"is_victory": false}', '2026-01-03 10:00:00'),
('normal', '战神', 5071, '战神无敌A', 5074, '战神霸主', 0, '{"is_victory": false}', '2026-01-10 10:00:00'),
('normal', '战神', 5072, '战神无敌B', 5074, '战神霸主', 0, '{"is_victory": false}', '2026-01-11 10:00:00'),
('normal', '战神', 5073, '战神无敌C', 5074, '战神霸主', 0, '{"is_victory": false}', '2026-01-12 10:00:00'),
('normal', '战神', 5071, '战神无敌A', 5073, '战神无敌C', 0, '{"is_victory": false}', '2026-01-10 11:00:00'),
('normal', '战神', 5072, '战神无敌B', 5073, '战神无敌C', 0, '{"is_victory": false}', '2026-01-11 11:00:00'),
('normal', '战神', 5071, '战神无敌A', 5072, '战神无敌B', 0, '{"is_victory": false}', '2026-01-10 12:00:00');

-- 挑战成功的记录（擂主被打下来的情况）
INSERT INTO `arena_battle_log` (`arena_type`, `rank_name`, `challenger_id`, `challenger_name`, `champion_id`, `champion_name`, `is_challenger_win`, `battle_data`, `created_at`) VALUES
('normal', '黄阶', 5014, '黄阶战士D', 5012, '黄阶战士B', 1, '{"is_victory": true}', '2026-01-09 10:00:00'),
('normal', '玄阶', 5024, '玄阶霸主', 5022, '玄阶剑客B', 1, '{"is_victory": true}', '2026-01-09 10:00:00'),
('normal', '地阶', 5033, '地阶霸主', 5032, '地阶武者B', 1, '{"is_victory": true}', '2026-01-09 10:00:00');


SET FOREIGN_KEY_CHECKS=1;

-- ========================================
-- 测试数据验证SQL
-- ========================================

-- 1. 等级排行验证
-- SELECT user_id, nickname, level, prestige, vip_level FROM player WHERE user_id >= 5001 ORDER BY level DESC, prestige DESC LIMIT 20;

-- 2. 战力排行验证（总排行）
-- SELECT p.user_id, p.nickname, p.level, COALESCE(SUM(b.combat_power), 0) as power, p.vip_level
-- FROM player p LEFT JOIN player_beast b ON p.user_id = b.user_id AND b.is_in_team = 1
-- WHERE p.user_id >= 5001 GROUP BY p.user_id ORDER BY power DESC LIMIT 20;

-- 3. 战力排行验证（黄阶）
-- SELECT p.user_id, p.nickname, p.level, COALESCE(SUM(b.combat_power), 0) as power, p.vip_level
-- FROM player p LEFT JOIN player_beast b ON p.user_id = b.user_id AND b.is_in_team = 1
-- WHERE p.user_id >= 5001 AND p.level BETWEEN 20 AND 29 GROUP BY p.user_id ORDER BY power DESC;

-- 4. 擂台排行验证（黄阶总英豪榜）
-- SELECT l.champion_id as userId, p.nickname, p.level, p.vip_level,
--        SUM(CASE WHEN l.is_challenger_win = 0 THEN 1 ELSE 0 END) as successCount
-- FROM arena_battle_log l JOIN player p ON l.champion_id = p.user_id
-- WHERE l.rank_name = '黄阶' GROUP BY l.champion_id ORDER BY successCount DESC;

-- 5. 擂台排行验证（黄阶周英豪榜）
-- SELECT l.champion_id as userId, p.nickname, p.level, p.vip_level,
--        SUM(CASE WHEN l.is_challenger_win = 0 THEN 1 ELSE 0 END) as successCount
-- FROM arena_battle_log l JOIN player p ON l.champion_id = p.user_id
-- WHERE l.rank_name = '黄阶' AND l.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
-- GROUP BY l.champion_id ORDER BY successCount DESC;

-- 6. VIP排行验证（只显示VIP>0的玩家）
-- SELECT user_id, nickname, vip_level, level FROM player WHERE user_id >= 5001 AND vip_level > 0 ORDER BY vip_level DESC, level DESC;

