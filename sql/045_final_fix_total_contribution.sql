-- 最终修复历史总贡献点数据
-- 这个脚本会修复所有数据问题，确保历史总贡献点正确

USE game_tower;

-- 步骤1: 确保 total_contribution 至少等于 contribution
UPDATE alliance_members
SET total_contribution = GREATEST(COALESCE(total_contribution, 0), contribution)
WHERE total_contribution IS NULL OR total_contribution < contribution;

-- 步骤2: 显示修复结果
SELECT 
    COUNT(*) as 总成员数,
    SUM(CASE WHEN total_contribution > contribution THEN 1 ELSE 0 END) as 历史总贡献点大于现有贡献点,
    SUM(CASE WHEN total_contribution = contribution THEN 1 ELSE 0 END) as 历史总贡献点等于现有贡献点,
    SUM(CASE WHEN total_contribution < contribution THEN 1 ELSE 0 END) as 历史总贡献点小于现有贡献点
FROM alliance_members;

-- 步骤3: 显示一些示例数据
SELECT 
    user_id,
    contribution AS 现有贡献点,
    total_contribution AS 历史总贡献点,
    total_contribution - contribution AS 差值,
    CASE 
        WHEN total_contribution > contribution THEN '正常（消耗过贡献点）'
        WHEN total_contribution = contribution THEN '可能未消耗过贡献点'
        ELSE '异常'
    END AS 状态
FROM alliance_members
ORDER BY total_contribution - contribution DESC
LIMIT 20;
