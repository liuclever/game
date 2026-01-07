-- ============================================================
-- 魔魂系统数据库表结构
-- ============================================================

-- ------------------------------------------------------------
-- 魔魂实例表
-- 存储玩家拥有的魔魂实例
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS mosoul_instances (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '魔魂实例ID',
    user_id         BIGINT UNSIGNED NOT NULL COMMENT '所属玩家ID',
    template_id     INT UNSIGNED NOT NULL COMMENT '魔魂模板ID（对应配置文件中的id）',
    level           TINYINT UNSIGNED NOT NULL DEFAULT 1 COMMENT '当前等级（1-10）',
    exp             INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '当前经验值',
    beast_id        BIGINT UNSIGNED DEFAULT NULL COMMENT '装备到的幻兽ID（NULL表示在储魂器中）',
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_user_id (user_id),
    INDEX idx_beast_id (beast_id),
    INDEX idx_template_id (template_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='魔魂实例表';


-- ------------------------------------------------------------
-- 幻兽魔魂装备表
-- 记录幻兽装备的魔魂（可通过 mosoul_instances.beast_id 关联，此表用于快速查询）
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS beast_mosoul_equip (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID',
    beast_id        BIGINT UNSIGNED NOT NULL COMMENT '幻兽ID',
    user_id         BIGINT UNSIGNED NOT NULL COMMENT '玩家ID',
    mosoul_id       BIGINT UNSIGNED NOT NULL COMMENT '魔魂实例ID',
    slot_index      TINYINT UNSIGNED NOT NULL COMMENT '槽位索引（0-9）',
    equipped_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '装备时间',
    
    UNIQUE KEY uk_beast_slot (beast_id, slot_index),
    UNIQUE KEY uk_mosoul (mosoul_id),
    INDEX idx_user_id (user_id),
    INDEX idx_beast_id (beast_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='幻兽魔魂装备表';


-- ------------------------------------------------------------
-- 猎魂状态表
-- 记录玩家当前的猎魂状态（可点击的NPC等）
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS mosoul_hunting_state (
    user_id                     BIGINT UNSIGNED PRIMARY KEY COMMENT '玩家ID',
    field_type                  VARCHAR(20) NOT NULL DEFAULT 'normal' COMMENT '当前场景类型（normal/advanced）',
    normal_available_npcs       JSON NOT NULL DEFAULT '["amy"]' COMMENT '普通场可点击NPC列表',
    advanced_available_npcs     JSON NOT NULL DEFAULT '["walter_adv"]' COMMENT '高级场可点击NPC列表',
    updated_at                  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='猎魂状态表';


-- ------------------------------------------------------------
-- 全服保底计数器表
-- 高级场凯文30000次保底机制
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS mosoul_global_pity (
    counter_key     VARCHAR(50) PRIMARY KEY COMMENT '计数器键名',
    count           INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '当前计数',
    pity_threshold  INT UNSIGNED NOT NULL DEFAULT 30000 COMMENT '保底阈值',
    last_pity_at    DATETIME DEFAULT NULL COMMENT '上次触发保底的时间',
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='全服保底计数器表';

-- 初始化高级场凯文保底计数器
INSERT IGNORE INTO mosoul_global_pity (counter_key, count, pity_threshold) 
VALUES ('kevin_adv_pity', 0, 30000);


-- ------------------------------------------------------------
-- 猎魂记录表（可选，用于数据分析）
-- 记录每次猎魂的详细信息
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS mosoul_hunting_log (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID',
    user_id         BIGINT UNSIGNED NOT NULL COMMENT '玩家ID',
    field_type      VARCHAR(20) NOT NULL COMMENT '场景类型',
    npc_id          VARCHAR(50) NOT NULL COMMENT 'NPC ID',
    cost            INT UNSIGNED NOT NULL COMMENT '花费',
    cost_type       VARCHAR(20) NOT NULL COMMENT '货币类型',
    result_grade    VARCHAR(50) NOT NULL COMMENT '获得的魔魂等级',
    result_template INT UNSIGNED DEFAULT NULL COMMENT '获得的魔魂模板ID',
    is_waste        TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否废魂',
    is_pity         TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否保底触发',
    copper_gained   INT UNSIGNED DEFAULT 0 COMMENT '废魂售卖获得铜钱',
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '猎魂时间',
    
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    INDEX idx_result_grade (result_grade)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='猎魂记录表';


-- ------------------------------------------------------------
-- 魔魂升级记录表（可选，用于数据分析）
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS mosoul_upgrade_log (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID',
    user_id         BIGINT UNSIGNED NOT NULL COMMENT '玩家ID',
    target_soul_id  BIGINT UNSIGNED NOT NULL COMMENT '目标魔魂ID',
    before_level    TINYINT UNSIGNED NOT NULL COMMENT '升级前等级',
    after_level     TINYINT UNSIGNED NOT NULL COMMENT '升级后等级',
    exp_gained      INT UNSIGNED NOT NULL COMMENT '获得的经验',
    material_count  INT UNSIGNED NOT NULL COMMENT '消耗的材料数量',
    material_ids    JSON DEFAULT NULL COMMENT '消耗的材料ID列表',
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '升级时间',
    
    INDEX idx_user_id (user_id),
    INDEX idx_target_soul_id (target_soul_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='魔魂升级记录表';


-- ============================================================
-- 视图：玩家储魂器统计
-- ============================================================
CREATE OR REPLACE VIEW v_user_soul_storage AS
SELECT 
    user_id,
    COUNT(*) as soul_count,
    SUM(CASE WHEN beast_id IS NULL THEN 1 ELSE 0 END) as storage_count,
    SUM(CASE WHEN beast_id IS NOT NULL THEN 1 ELSE 0 END) as equipped_count
FROM mosoul_instances
GROUP BY user_id;


-- ============================================================
-- 视图：幻兽魔魂装备详情
-- ============================================================
CREATE OR REPLACE VIEW v_beast_mosoul_detail AS
SELECT 
    m.beast_id,
    m.user_id,
    COUNT(*) as equipped_count,
    GROUP_CONCAT(m.template_id ORDER BY m.id) as template_ids,
    GROUP_CONCAT(m.level ORDER BY m.id) as levels
FROM mosoul_instances m
WHERE m.beast_id IS NOT NULL
GROUP BY m.beast_id, m.user_id;
