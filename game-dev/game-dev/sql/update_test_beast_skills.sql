-- 为测试用玩家设置规范技能名，方便在镇妖战报中观察技能触发

USE game_tower;

-- 玩家1（测试玩家 / test1）和 玩家2（测试玩家2 / test2）
-- 将其出战幻兽（is_in_team=1）的技能统一设置为一组可触发的主动技能
-- 包含：高级连击、高级必杀、高级雷击、高级毒攻

UPDATE player_beast
SET skills = '["高级连击","高级必杀","高级雷击","高级毒攻"]'
WHERE user_id IN (1, 2) AND is_in_team = 1;

-- 如需一并修改镇妖NPC测试号（100-105），可以取消下面的注释
-- UPDATE player_beast
-- SET skills = '["高级连击","高级必杀","高级雷击","高级毒攻"]'
-- WHERE user_id IN (100,101,102,103,104,105) AND is_in_team = 1;
