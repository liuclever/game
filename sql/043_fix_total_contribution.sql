-- 修复历史总贡献点数据
-- 确保 total_contribution 至少等于 contribution（历史总贡献点应该 >= 现有贡献点）
USE game_tower;

-- 修复：如果 total_contribution 小于 contribution，则设置为 contribution
-- 这确保历史总贡献点永远不会小于现有贡献点
UPDATE alliance_members
SET total_contribution = GREATEST(COALESCE(total_contribution, 0), contribution)
WHERE total_contribution IS NULL 
   OR total_contribution < contribution;

-- 显示修复结果
SELECT 
    user_id,
    contribution AS 现有贡献点,
    total_contribution AS 历史总贡献点,
    CASE 
        WHEN total_contribution >= contribution THEN '✓ 正常'
        ELSE '✗ 需要修复'
    END AS 状态
FROM alliance_members
ORDER BY user_id
LIMIT 20;
