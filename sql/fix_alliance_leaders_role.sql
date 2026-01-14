-- ============================================
-- 修复联盟盟主角色：确保联盟创建者的role字段为1（盟主）
-- ============================================

USE game_tower;

-- 更新所有联盟的创建者（leader_id对应的用户）的role为1（盟主）
UPDATE alliance_members am
INNER JOIN alliances a ON am.alliance_id = a.id
SET am.role = 1
WHERE am.user_id = a.leader_id
  AND am.role != 1;

-- 显示修复结果
SELECT 
    a.id AS alliance_id,
    a.name AS alliance_name,
    a.leader_id,
    am.user_id,
    am.role,
    CASE 
        WHEN am.user_id = a.leader_id AND am.role = 1 THEN '正确'
        WHEN am.user_id = a.leader_id AND am.role != 1 THEN '错误'
        ELSE '成员'
    END AS status
FROM alliances a
LEFT JOIN alliance_members am ON a.id = am.alliance_id
WHERE am.user_id = a.leader_id
ORDER BY a.id;
