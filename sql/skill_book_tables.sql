-- ============================================================
-- 技能书系统数据库表结构
-- ============================================================

-- ------------------------------------------------------------
-- 打书记录表
-- 记录每次使用技能书的详细信息（用于数据分析）
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS skill_book_log (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID',
    user_id         BIGINT UNSIGNED NOT NULL COMMENT '玩家ID',
    beast_id        BIGINT UNSIGNED NOT NULL COMMENT '幻兽ID',
    beast_name      VARCHAR(100) DEFAULT '' COMMENT '幻兽名称（冗余字段，方便查询）',
    skill_book_id   INT UNSIGNED NOT NULL COMMENT '技能书道具ID',
    skill_book_name VARCHAR(100) DEFAULT '' COMMENT '技能书名称',
    new_skill       VARCHAR(100) NOT NULL COMMENT '新学习的技能名称',
    action_type     VARCHAR(20) NOT NULL COMMENT '操作类型：add（新增）/ replace（替换）',
    replaced_skill  VARCHAR(100) DEFAULT NULL COMMENT '被替换的技能名称（如果是替换操作）',
    skills_before   JSON DEFAULT NULL COMMENT '打书前的技能列表',
    skills_after    JSON DEFAULT NULL COMMENT '打书后的技能列表',
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '打书时间',
    
    INDEX idx_user_id (user_id),
    INDEX idx_beast_id (beast_id),
    INDEX idx_skill_book_id (skill_book_id),
    INDEX idx_created_at (created_at),
    INDEX idx_action_type (action_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='打书记录表';


-- ------------------------------------------------------------
-- 视图：玩家打书统计
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW v_user_skill_book_stats AS
SELECT 
    user_id,
    COUNT(*) as total_uses,
    SUM(CASE WHEN action_type = 'add' THEN 1 ELSE 0 END) as add_count,
    SUM(CASE WHEN action_type = 'replace' THEN 1 ELSE 0 END) as replace_count,
    MAX(created_at) as last_use_time
FROM skill_book_log
GROUP BY user_id;


-- ------------------------------------------------------------
-- 视图：技能书使用热度统计
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW v_skill_book_popularity AS
SELECT 
    skill_book_id,
    skill_book_name,
    new_skill,
    COUNT(*) as use_count
FROM skill_book_log
GROUP BY skill_book_id, skill_book_name, new_skill
ORDER BY use_count DESC;
