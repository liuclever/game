-- 014 测试数据
-- 添加测试用物品和数据

USE game_tower;

-- 更新测试用户的声望值（便于测试）
UPDATE player SET prestige = 100 WHERE user_id = 1;
UPDATE player SET prestige = 50 WHERE user_id = 2;

-- 添加测试用鼓舞丹（物品ID 8001）
INSERT INTO player_inventory (user_id, item_id, quantity, is_temporary)
VALUES (1, 8001, 10, 0), (2, 8001, 10, 0)
ON DUPLICATE KEY UPDATE quantity = quantity + 10;

-- 添加测试用捕捉球（物品ID 4002捕捉球, 4003强力捕捉球）
INSERT INTO player_inventory (user_id, item_id, quantity, is_temporary)
VALUES (1, 4002, 50, 0), (1, 4003, 20, 0), (2, 4002, 50, 0), (2, 4003, 20, 0)
ON DUPLICATE KEY UPDATE quantity = quantity + 10;

-- 添加测试用强力草（物品ID 5001）
INSERT INTO player_inventory (user_id, item_id, quantity, is_temporary)
VALUES (1, 5001, 20, 0), (2, 5001, 20, 0)
ON DUPLICATE KEY UPDATE quantity = quantity + 10;

-- 添加测试用追魂法宝（物品ID 5002）
INSERT INTO player_inventory (user_id, item_id, quantity, is_temporary)
VALUES (1, 5002, 10, 0), (2, 5002, 10, 0)
ON DUPLICATE KEY UPDATE quantity = quantity + 5;

-- 添加测试用技能书口袋（物品ID 5003）
INSERT INTO player_inventory (user_id, item_id, quantity, is_temporary)
VALUES (1, 5003, 5, 0), (2, 5003, 5, 0)
ON DUPLICATE KEY UPDATE quantity = quantity + 2;
