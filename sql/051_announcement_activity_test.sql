-- ============================================
-- 开服活动数据表及测试数据
-- 用途：创建活动相关表并初始化测试数据
-- ============================================

USE game_tower;

-- 1. 新人战力榜奖励发放记录表
CREATE TABLE IF NOT EXISTS activity_power_ranking_reward (
    id INT AUTO_INCREMENT PRIMARY KEY,
    activity_id VARCHAR(50) NOT NULL COMMENT '活动ID',
    level_bracket INT NOT NULL COMMENT '等级段(29/39/49/59)',
    rank_position INT NOT NULL COMMENT '排名',
    user_id INT NOT NULL COMMENT '玩家ID',
    nickname VARCHAR(50) DEFAULT '' COMMENT '玩家昵称',
    combat_power BIGINT DEFAULT 0 COMMENT '战力',
    reward_items TEXT COMMENT '奖励内容(JSON)',
    is_claimed TINYINT(1) DEFAULT 0 COMMENT '是否已领取',
    finalized_at DATETIME DEFAULT NULL COMMENT '榜单确定时间',
    claimed_at DATETIME DEFAULT NULL COMMENT '领取时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_activity_bracket_rank (activity_id, level_bracket, rank_position),
    INDEX idx_user_id (user_id),
    INDEX idx_activity_bracket (activity_id, level_bracket)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='新人战力榜奖励发放记录';

-- 2. 轮盘抽奖记录表
CREATE TABLE IF NOT EXISTS activity_wheel_lottery (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '玩家ID',
    activity_id VARCHAR(50) NOT NULL DEFAULT 'wheel_lottery' COMMENT '活动ID',
    draw_count INT DEFAULT 0 COMMENT '累计抽奖次数',
    fragment_count INT DEFAULT 0 COMMENT '当前碎片数量',
    round_count INT DEFAULT 0 COMMENT '当前轮次已抽次数(0-9)',
    last_draw_at DATETIME DEFAULT NULL COMMENT '最后抽奖时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_activity (user_id, activity_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='轮盘抽奖记录';

-- 3. 通用活动领取记录表
CREATE TABLE IF NOT EXISTS activity_claims (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '玩家ID',
    activity_id VARCHAR(50) NOT NULL COMMENT '活动ID',
    claim_key VARCHAR(100) NOT NULL COMMENT '领取标识',
    claim_date DATE DEFAULT NULL COMMENT '领取日期(用于每日限购)',
    claim_count INT DEFAULT 1 COMMENT '领取次数',
    extra_data TEXT COMMENT '额外数据(JSON)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_activity_claim (user_id, activity_id, claim_key, claim_date),
    INDEX idx_user_activity (user_id, activity_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='通用活动领取记录';

-- 4. 活动榜单定时任务状态表
CREATE TABLE IF NOT EXISTS activity_finalize_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    activity_id VARCHAR(50) NOT NULL COMMENT '活动ID',
    level_bracket INT DEFAULT NULL COMMENT '等级段(用于战力榜)',
    finalize_type VARCHAR(50) NOT NULL COMMENT '结算类型',
    finalized_at DATETIME DEFAULT NULL COMMENT '结算时间',
    is_rewards_sent TINYINT(1) DEFAULT 0 COMMENT '是否已发放奖励',
    rewards_sent_at DATETIME DEFAULT NULL COMMENT '奖励发放时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_activity_bracket (activity_id, level_bracket, finalize_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='活动结算日志';

-- ============================================
-- 测试数据：为指定用户创建可体验活动的数据
-- 使用方式：修改 @test_user_id 变量为需要测试的用户ID
-- ============================================

-- 设置测试用户ID（修改这里的值来测试不同用户）
SET @test_user_id = 1;

-- 确保测试用户存在并有足够的资源
-- 更新测试用户的元宝、宝石、等级等属性以便体验活动
UPDATE player SET 
    yuanbao = COALESCE(yuanbao, 0) + 100000,     -- 给予10万元宝用于测试
    silver_diamond = COALESCE(silver_diamond, 0) + 500,  -- 给予500宝石用于测试霸王龙和返利活动
    level = CASE WHEN level > 59 THEN level ELSE 25 END  -- 如果等级>59则保持，否则设为25级以便测试29级战力榜
WHERE user_id = @test_user_id;

-- 为战力榜测试创建不同等级段的玩家数据
-- 29级段玩家（20-29级）
INSERT IGNORE INTO player (user_id, nickname, level, exp, gold, yuanbao, silver_diamond) VALUES
(20052, '测试玩家A', 25, 0, 100000, 10000, 100),
(1002, '测试玩家B', 28, 0, 100000, 10000, 100),
(4057, '测试玩家C', 29, 0, 100000, 10000, 100);

-- 39级段玩家（30-39级）
INSERT IGNORE INTO player (user_id, nickname, level, exp, gold, yuanbao, silver_diamond) VALUES
(1004, '测试玩家D', 35, 0, 100000, 10000, 100),
(1005, '测试玩家E', 38, 0, 100000, 10000, 100);

-- 49级段玩家（40-49级）
INSERT IGNORE INTO player (user_id, nickname, level, exp, gold, yuanbao, silver_diamond) VALUES
(1006, '测试玩家F', 45, 0, 100000, 10000, 100),
(1007, '测试玩家G', 49, 0, 100000, 10000, 100);

-- 59级段玩家（50-59级）
INSERT IGNORE INTO player (user_id, nickname, level, exp, gold, yuanbao, silver_diamond) VALUES
(1008, '测试玩家H', 55, 0, 100000, 10000, 100),
(1009, '测试玩家I', 59, 0, 100000, 10000, 100);

-- 为测试玩家添加幻兽（用于战力计算）
-- 幻兽战力 = combat_power 字段
-- 注意：player_beast.race 默认值为 ''（空字符串），不显式写入会导致前端显示“未知种族”
INSERT IGNORE INTO player_beast (user_id, name, realm, race, level, nature, hp, physical_attack, magic_attack, physical_defense, magic_defense, speed, combat_power, is_in_team, team_position) VALUES
-- 20052的幻兽
(20052, '火焰龙', '天界', '兽族', 25, '物系', 1000, 200, 100, 150, 100, 120, 50000, 1, 1),
-- 1002的幻兽
(20052, '冰霜凤凰', '天界', '羽族', 28, '法系', 900, 100, 250, 100, 150, 150, 60000, 1, 1),
-- 4057的幻兽
(20052, '雷电虎', '神界', '兽族', 29, '物系', 1200, 300, 150, 200, 120, 130, 80000, 1, 1),
-- 1004的幻兽
(20052, '暗影狼', '天界', '兽族', 35, '物系', 1500, 350, 200, 250, 150, 140, 100000, 1, 1),
-- 1005的幻兽
(20052, '圣光鹿', '神界', '兽族', 38, '法系', 1400, 200, 400, 180, 220, 160, 120000, 1, 1),
-- 1006的幻兽
(20052, '岩石巨人', '天界', '兽族', 45, '物系', 2000, 400, 150, 400, 200, 80, 150000, 1, 1),
-- 1007的幻兽
(20052, '风之精灵', '神界', '水族', 49, '法系', 1600, 250, 500, 200, 300, 200, 180000, 1, 1),
-- 1008的幻兽
(20052, '烈焰凤凰', '神界', '羽族', 55, '法系', 2200, 300, 600, 250, 350, 180, 220000, 1, 1),
-- 1009的幻兽
(20052, '冥界魔龙', '神界', '兽族', 59, '物系', 2800, 600, 400, 450, 300, 150, 280000, 1, 1);

-- 确保 player 表有 yuanbao 字段
-- 如果字段不存在则添加
SET @col_exists = (SELECT COUNT(*) FROM information_schema.columns 
                   WHERE table_schema = DATABASE() 
                   AND table_name = 'player' 
                   AND column_name = 'yuanbao');
SET @sql = IF(@col_exists = 0, 
              'ALTER TABLE player ADD COLUMN yuanbao INT DEFAULT 0 COMMENT ''元宝''',
              'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 确保 player 表有 prestige 字段（声望）
SET @col_exists = (SELECT COUNT(*) FROM information_schema.columns 
                   WHERE table_schema = DATABASE() 
                   AND table_name = 'player' 
                   AND column_name = 'prestige');
SET @sql = IF(@col_exists = 0, 
              'ALTER TABLE player ADD COLUMN prestige INT DEFAULT 0 COMMENT ''声望''',
              'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SELECT '开服活动数据表创建完成！' AS message;
SELECT CONCAT('已为用户ID=', @test_user_id, ' 添加测试资源：10万元宝、500宝石') AS message;
SELECT '已创建9个测试玩家(ID: 20052-1009)用于战力榜测试' AS message;

