-- 添加幻兽经验字段
USE game_tower;

ALTER TABLE player_beast 
ADD COLUMN exp INT NOT NULL DEFAULT 0 COMMENT '当前经验' AFTER level;
