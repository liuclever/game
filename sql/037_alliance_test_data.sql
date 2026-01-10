-- ============================================
-- 037 联盟测试数据（可重复执行）
--
-- 目的：
-- - 建一个可用的联盟，并将其设置为盟主；
-- - 用于联调“幻兽寄存室/寄存仓库”等需要联盟身份的功能。
--
-- 说明：
-- - “是否加入联盟”的判定依据：alliance_members 表中是否存在 user_id 对应记录。
-- - 本脚本会把 user_id=4054 的联盟成员关系强制指向本脚本创建的联盟（若之前在别的联盟，会被覆盖）。
-- ============================================

USE game_tower;

SET @leader_id := 4054;
-- 注意：不同 MySQL 版本/库表可能存在 collation 差异（如 utf8mb4_general_ci vs utf8mb4_0900_ai_ci）。
-- 为避免 “Illegal mix of collations” 报错，本脚本不做 name 字段的等值比较，全部以 leader_id（INT）作为定位条件。
SET @alliance_name := CONCAT('联盟_', @leader_id);

-- 0) 确保 player 记录存在（避免 alliance_members 外键失败）
INSERT IGNORE INTO player (user_id) VALUES (@leader_id);

-- 1) 创建联盟（若已存在则复用）
INSERT INTO alliances (name, leader_id, level, exp, funds, crystals, prosperity, notice)
SELECT
  @alliance_name,
  @leader_id,
  1,
  0,
  0,
  0,
  0,
  '037测试数据：用于幻兽寄存室/联盟仓库联调'
WHERE NOT EXISTS (
  SELECT 1 FROM alliances WHERE leader_id = @leader_id
);

-- 2) 获取联盟 id
SET @alliance_id := (
  SELECT id
  FROM alliances
  WHERE leader_id = @leader_id
  ORDER BY id DESC
  LIMIT 1
);

-- 3) 确保盟主字段一致（避免历史数据不一致）
UPDATE alliances
SET leader_id = @leader_id
WHERE id = @alliance_id;

-- 4) 加入联盟（盟主 role=1；若已在别的联盟则覆盖为本联盟）
INSERT INTO alliance_members (alliance_id, user_id, role, contribution)
VALUES (@alliance_id, @leader_id, 1, 0)
ON DUPLICATE KEY UPDATE
  alliance_id = VALUES(alliance_id),
  role = VALUES(role);

-- 5) 初始化联盟建筑（最低1级；缺失则补齐）
INSERT IGNORE INTO alliance_buildings (alliance_id, building_key, level) VALUES
(@alliance_id, 'council', 1),
(@alliance_id, 'furnace', 1),
(@alliance_id, 'talent', 1),
(@alliance_id, 'beast', 1),
(@alliance_id, 'warehouse', 1);

-- 6) 初始化联盟天赋研究（缺失则补齐）
INSERT IGNORE INTO alliance_talents (alliance_id, talent_key, research_level) VALUES
(@alliance_id, 'atk', 1),
(@alliance_id, 'int', 1),
(@alliance_id, 'def', 1),
(@alliance_id, 'resist', 1),
(@alliance_id, 'spd', 1),
(@alliance_id, 'hp', 1);

-- 7) 初始化玩家天赋等级（缺失则补齐，默认0级）
INSERT IGNORE INTO player_talent_levels (user_id, talent_key, level) VALUES
(@leader_id, 'atk', 0),
(@leader_id, 'int', 0),
(@leader_id, 'def', 0),
(@leader_id, 'resist', 0),
(@leader_id, 'spd', 0),
(@leader_id, 'hp', 0);

SELECT 'ok: alliance test data prepared' AS message, @leader_id AS leader_id, @alliance_id AS alliance_id, @alliance_name AS alliance_name;


