-- 执行所有SQL脚本
-- 按顺序执行各个模块的SQL文件

USE game_tower;

-- 基础表（如已执行过可跳过）
-- source 001_xxx.sql
-- source 002_create_tables.sql
-- ...

-- 功能模块表
source 009_inventory_tables.sql;
source 010_cultivation_system.sql;
source 011_level_config.sql;
source 012_arena_tables.sql;
source 013_king_challenge_tables.sql;

-- 测试数据（可选）
source 014_test_data.sql;

SELECT '所有SQL脚本执行完成' AS message;
