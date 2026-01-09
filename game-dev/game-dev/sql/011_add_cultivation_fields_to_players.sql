-- game/sql/011_add_cultivation_fields_to_players.sql
-- 修行系统：为玩家表添加修行状态字段
USE game_tower;

-- 添加修行字段（如果已存在会报错，可忽略）
ALTER TABLE player ADD COLUMN cultivation_start_time DATETIME DEFAULT NULL COMMENT '修行开始时间';
ALTER TABLE player ADD COLUMN cultivation_area VARCHAR(50) DEFAULT NULL COMMENT '修行区域';
ALTER TABLE player ADD COLUMN cultivation_dungeon VARCHAR(50) DEFAULT NULL COMMENT '修行副本';

-- 如果上面的命令报错说字段已存在，说明已经添加过了，可以忽略错误
