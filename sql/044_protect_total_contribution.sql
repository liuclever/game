-- 创建触发器保护历史总贡献点不被减少
-- 这个触发器确保 total_contribution 只增不减

USE game_tower;

-- 删除已存在的触发器（如果存在）
DROP TRIGGER IF EXISTS protect_total_contribution;

-- 创建触发器：在更新 alliance_members 表之前检查
-- 确保 total_contribution 不会被减少
-- 注意：使用单条语句创建触发器，不使用 DELIMITER

CREATE TRIGGER protect_total_contribution
BEFORE UPDATE ON alliance_members
FOR EACH ROW
BEGIN
    -- 核心逻辑：历史总贡献点只增不减
    
    -- 关键点：在 MySQL 的 BEFORE UPDATE 触发器中
    -- 如果 UPDATE 语句中没有显式设置 total_contribution，则 NEW.total_contribution = OLD.total_contribution
    -- 如果 UPDATE 语句中显式设置了 total_contribution，则 NEW.total_contribution 会被设置为新值
    
    -- 最重要的保护：确保 total_contribution 永远不会减少
    -- 如果 NEW.total_contribution < OLD.total_contribution，强制恢复为 OLD.total_contribution
    IF OLD.total_contribution IS NOT NULL THEN
        IF NEW.total_contribution IS NULL OR NEW.total_contribution < OLD.total_contribution THEN
            SET NEW.total_contribution = OLD.total_contribution;
        END IF;
    END IF;
    
    -- 额外保护：确保 total_contribution 至少等于 contribution（防止数据异常）
    -- 但前提是不能小于 OLD.total_contribution（历史总贡献点只增不减）
    IF NEW.total_contribution IS NOT NULL AND NEW.contribution IS NOT NULL THEN
        IF NEW.total_contribution < NEW.contribution THEN
            -- 如果 total_contribution < contribution，需要修正
            -- 但必须确保不会减少（至少等于 OLD.total_contribution）
            SET NEW.total_contribution = GREATEST(
                COALESCE(OLD.total_contribution, 0),
                NEW.contribution
            );
        END IF;
    END IF;
END;

-- 验证触发器创建成功
SELECT 'Trigger protect_total_contribution created successfully' AS message;
