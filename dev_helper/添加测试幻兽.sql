-- 快速添加测试幻兽
-- 用于测试战斗系统（连胜竞技场、擂台、切磋等）

-- 说明：
-- 1. 修改 user_id 为你的玩家ID
-- 2. 执行此脚本
-- 3. 刷新游戏页面
-- 4. 进入幻兽管理查看

-- ============================================
-- 给玩家1添加4只出战幻兽
-- ============================================

-- 删除已有的幻兽（可选，避免重复）
-- DELETE FROM player_beast WHERE user_id = 1;

-- 1. 青龙（物理攻击型）
INSERT INTO player_beast (
    user_id, template_id, name, level, exp, realm,
    hp_current, hp_max,
    physical_attack, magic_attack,
    physical_defense, magic_defense, speed,
    hp_aptitude, physical_attack_aptitude, magic_attack_aptitude,
    physical_defense_aptitude, magic_defense_aptitude, speed_aptitude,
    hp_star, physical_attack_star, magic_attack_star,
    physical_defense_star, magic_defense_star, speed_star,
    is_in_team, team_position, created_at
)
VALUES (
    1,              -- user_id (修改为你的玩家ID)
    1,              -- template_id (青龙)
    '神·青龙',      -- name
    30,             -- level
    0,              -- exp
    1,              -- realm (1=凡界)
    3000, 3000,     -- hp_current, hp_max
    500, 200,       -- physical_attack, magic_attack
    200, 150,       -- physical_defense, magic_defense
    180,            -- speed
    120, 130, 100,  -- hp_aptitude, physical_attack_aptitude, magic_attack_aptitude
    110, 100, 120,  -- physical_defense_aptitude, magic_defense_aptitude, speed_aptitude
    5, 5, 3,        -- hp_star, physical_attack_star, magic_attack_star
    4, 3, 5,        -- physical_defense_star, magic_defense_star, speed_star
    1,              -- is_in_team (1=出战)
    1,              -- team_position (第1个位置)
    NOW()           -- created_at
);

-- 2. 朱雀（法术攻击型）
INSERT INTO player_beast (
    user_id, template_id, name, level, exp, realm,
    hp_current, hp_max,
    physical_attack, magic_attack,
    physical_defense, magic_defense, speed,
    hp_aptitude, physical_attack_aptitude, magic_attack_aptitude,
    physical_defense_aptitude, magic_defense_aptitude, speed_aptitude,
    hp_star, physical_attack_star, magic_attack_star,
    physical_defense_star, magic_defense_star, speed_star,
    is_in_team, team_position, created_at
)
VALUES (
    1,              -- user_id
    2,              -- template_id (朱雀)
    '神·朱雀',      -- name
    30,             -- level
    0,              -- exp
    1,              -- realm
    2800, 2800,     -- hp_current, hp_max
    200, 550,       -- physical_attack, magic_attack
    150, 220,       -- physical_defense, magic_defense
    190,            -- speed
    110, 100, 140,  -- aptitudes
    100, 120, 130,
    4, 3, 5,        -- stars
    3, 5, 5,
    1,              -- is_in_team
    2,              -- team_position (第2个位置)
    NOW()
);

-- 3. 白虎（防御型）
INSERT INTO player_beast (
    user_id, template_id, name, level, exp, realm,
    hp_current, hp_max,
    physical_attack, magic_attack,
    physical_defense, magic_defense, speed,
    hp_aptitude, physical_attack_aptitude, magic_attack_aptitude,
    physical_defense_aptitude, magic_defense_aptitude, speed_aptitude,
    hp_star, physical_attack_star, magic_attack_star,
    physical_defense_star, magic_defense_star, speed_star,
    is_in_team, team_position, created_at
)
VALUES (
    1,              -- user_id
    3,              -- template_id (白虎)
    '神·白虎',      -- name
    30,             -- level
    0,              -- exp
    1,              -- realm
    3500, 3500,     -- hp_current, hp_max
    400, 300,       -- physical_attack, magic_attack
    300, 280,       -- physical_defense, magic_defense
    150,            -- speed
    140, 120, 110,  -- aptitudes
    130, 130, 100,
    5, 4, 4,        -- stars
    5, 5, 3,
    1,              -- is_in_team
    3,              -- team_position (第3个位置)
    NOW()
);

-- 4. 玄武（坦克型）
INSERT INTO player_beast (
    user_id, template_id, name, level, exp, realm,
    hp_current, hp_max,
    physical_attack, magic_attack,
    physical_defense, magic_defense, speed,
    hp_aptitude, physical_attack_aptitude, magic_attack_aptitude,
    physical_defense_aptitude, magic_defense_aptitude, speed_aptitude,
    hp_star, physical_attack_star, magic_attack_star,
    physical_defense_star, magic_defense_star, speed_star,
    is_in_team, team_position, created_at
)
VALUES (
    1,              -- user_id
    4,              -- template_id (玄武)
    '神·玄武',      -- name
    30,             -- level
    0,              -- exp
    1,              -- realm
    4000, 4000,     -- hp_current, hp_max
    350, 250,       -- physical_attack, magic_attack
    350, 350,       -- physical_defense, magic_defense
    120,            -- speed
    150, 110, 100,  -- aptitudes
    140, 140, 90,
    5, 4, 3,        -- stars
    5, 5, 2,
    1,              -- is_in_team
    4,              -- team_position (第4个位置)
    NOW()
);

-- ============================================
-- 给玩家2添加4只出战幻兽（用于测试对战）
-- ============================================

-- 1. 麒麟
INSERT INTO player_beast (
    user_id, template_id, name, level, exp, realm,
    hp_current, hp_max,
    physical_attack, magic_attack,
    physical_defense, magic_defense, speed,
    hp_aptitude, physical_attack_aptitude, magic_attack_aptitude,
    physical_defense_aptitude, magic_defense_aptitude, speed_aptitude,
    hp_star, physical_attack_star, magic_attack_star,
    physical_defense_star, magic_defense_star, speed_star,
    is_in_team, team_position, created_at
)
VALUES (
    2, 5, '神·麒麟', 30, 0, 1,
    3200, 3200,
    450, 450,
    220, 220, 170,
    125, 125, 125, 115, 115, 115,
    5, 5, 5, 4, 4, 4,
    1, 1, NOW()
);

-- 2. 凤凰
INSERT INTO player_beast (
    user_id, template_id, name, level, exp, realm,
    hp_current, hp_max,
    physical_attack, magic_attack,
    physical_defense, magic_defense, speed,
    hp_aptitude, physical_attack_aptitude, magic_attack_aptitude,
    physical_defense_aptitude, magic_defense_aptitude, speed_aptitude,
    hp_star, physical_attack_star, magic_attack_star,
    physical_defense_star, magic_defense_star, speed_star,
    is_in_team, team_position, created_at
)
VALUES (
    2, 6, '神·凤凰', 30, 0, 1,
    2900, 2900,
    250, 600,
    180, 250, 200,
    115, 105, 145, 105, 125, 135,
    4, 3, 5, 3, 5, 5,
    1, 2, NOW()
);

-- 3. 龙龟
INSERT INTO player_beast (
    user_id, template_id, name, level, exp, realm,
    hp_current, hp_max,
    physical_attack, magic_attack,
    physical_defense, magic_defense, speed,
    hp_aptitude, physical_attack_aptitude, magic_attack_aptitude,
    physical_defense_aptitude, magic_defense_aptitude, speed_aptitude,
    hp_star, physical_attack_star, magic_attack_star,
    physical_defense_star, magic_defense_star, speed_star,
    is_in_team, team_position, created_at
)
VALUES (
    2, 7, '神·龙龟', 30, 0, 1,
    3800, 3800,
    380, 280,
    320, 320, 140,
    145, 115, 105, 135, 135, 95,
    5, 4, 3, 5, 5, 3,
    1, 3, NOW()
);

-- 4. 九尾狐
INSERT INTO player_beast (
    user_id, template_id, name, level, exp, realm,
    hp_current, hp_max,
    physical_attack, magic_attack,
    physical_defense, magic_defense, speed,
    hp_aptitude, physical_attack_aptitude, magic_attack_aptitude,
    physical_defense_aptitude, magic_defense_aptitude, speed_aptitude,
    hp_star, physical_attack_star, magic_attack_star,
    physical_defense_star, magic_defense_star, speed_star,
    is_in_team, team_position, created_at
)
VALUES (
    2, 8, '神·九尾狐', 30, 0, 1,
    2700, 2700,
    300, 580,
    160, 240, 210,
    110, 110, 145, 100, 125, 140,
    4, 4, 5, 3, 5, 5,
    1, 4, NOW()
);

-- ============================================
-- 验证
-- ============================================

-- 查看玩家1的幻兽
SELECT 
    id, name, level, hp_max, 
    physical_attack, magic_attack,
    physical_defense, magic_defense, speed,
    is_in_team, team_position
FROM player_beast 
WHERE user_id = 1
ORDER BY team_position;

-- 查看玩家2的幻兽
SELECT 
    id, name, level, hp_max, 
    physical_attack, magic_attack,
    physical_defense, magic_defense, speed,
    is_in_team, team_position
FROM player_beast 
WHERE user_id = 2
ORDER BY team_position;

-- ============================================
-- 说明
-- ============================================

-- 执行此脚本后：
-- 1. 玩家1 拥有 4只出战幻兽（青龙、朱雀、白虎、玄武）
-- 2. 玩家2 拥有 4只出战幻兽（麒麟、凤凰、龙龟、九尾狐）
-- 3. 所有幻兽都是30级，属性均衡
-- 4. 可以直接测试战斗系统

-- 如果需要修改玩家ID：
-- 1. 将所有 user_id = 1 改为你的玩家ID
-- 2. 将所有 user_id = 2 改为对手的玩家ID

-- 如果需要删除测试数据：
-- DELETE FROM player_beast WHERE user_id IN (1, 2);
