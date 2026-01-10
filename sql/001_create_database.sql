-- ============================================
-- 创建数据库和用户
-- 执行用户: root
-- ============================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS game_tower 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 创建独立用户（如果已存在则跳过）
-- 用户名: root
-- 密码: 123456 (请修改为更安全的密码)
CREATE USER IF NOT EXISTS 'root'@'localhost' IDENTIFIED BY '123456';
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY '123456';

-- 授予该用户对 game_tower 数据库的全部权限
GRANT ALL PRIVILEGES ON game_tower.* TO 'root'@'localhost';
GRANT ALL PRIVILEGES ON game_tower.* TO 'root'@'%';

-- 刷新权限
FLUSH PRIVILEGES;

USE game_tower;
