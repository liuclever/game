-- 修复背包容量和拆分超过99的物品
-- 执行前请备份数据

USE game_tower;

-- 1. 更新背包容量：1级=60，每级+15
-- 根据背包等级重新计算容量
UPDATE player_bag 
SET capacity = 60 + (bag_level - 1) * 15;

-- 2. 移除唯一约束（允许同一物品占用多个格子）
-- 先检查约束是否存在，存在则删除
SET @constraint_exists = (
    SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS 
    WHERE CONSTRAINT_SCHEMA = 'game_tower' 
    AND TABLE_NAME = 'player_inventory' 
    AND CONSTRAINT_NAME = 'uk_user_item_temp'
);

-- 删除唯一约束
ALTER TABLE player_inventory DROP INDEX uk_user_item_temp;

-- 3. 拆分超过99个的物品
-- 这个需要通过存储过程来处理

DELIMITER //

CREATE PROCEDURE split_oversized_items()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_id INT;
    DECLARE v_user_id INT;
    DECLARE v_item_id INT;
    DECLARE v_quantity INT;
    DECLARE v_is_temporary TINYINT;
    DECLARE v_created_at DATETIME;
    DECLARE v_remaining INT;
    DECLARE v_split_qty INT;
    
    -- 查找所有数量超过99的物品
    DECLARE cur CURSOR FOR 
        SELECT id, user_id, item_id, quantity, is_temporary, created_at 
        FROM player_inventory 
        WHERE quantity > 99;
    
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    OPEN cur;
    
    read_loop: LOOP
        FETCH cur INTO v_id, v_user_id, v_item_id, v_quantity, v_is_temporary, v_created_at;
        IF done THEN
            LEAVE read_loop;
        END IF;
        
        -- 将原物品数量改为99
        UPDATE player_inventory SET quantity = 99 WHERE id = v_id;
        
        -- 剩余数量
        SET v_remaining = v_quantity - 99;
        
        -- 插入新的格子（每个最多99）
        WHILE v_remaining > 0 DO
            SET v_split_qty = LEAST(v_remaining, 99);
            
            INSERT INTO player_inventory (user_id, item_id, quantity, is_temporary, created_at)
            VALUES (v_user_id, v_item_id, v_split_qty, v_is_temporary, v_created_at);
            
            SET v_remaining = v_remaining - v_split_qty;
        END WHILE;
    END LOOP;
    
    CLOSE cur;
END //

DELIMITER ;

-- 执行存储过程
CALL split_oversized_items();

-- 删除存储过程
DROP PROCEDURE IF EXISTS split_oversized_items;

-- 查看修复后的结果
SELECT '修复后的背包容量:' as info;
SELECT user_id, bag_level, capacity FROM player_bag;

SELECT '修复后的物品（检查是否还有超过99的）:' as info;
SELECT * FROM player_inventory WHERE quantity > 99;
