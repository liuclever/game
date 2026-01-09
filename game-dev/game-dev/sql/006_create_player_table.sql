-- ============================================
-- 创建玩家基础信息表和镇妖占领表
-- ============================================

USE game_tower;

-- 玩家基础信息表
CREATE TABLE IF NOT EXISTS player (
    user_id INT PRIMARY KEY,
    nickname VARCHAR(50) NOT NULL DEFAULT '' COMMENT '昵称',
    level INT NOT NULL DEFAULT 1 COMMENT '玩家等级(1-100)',
    exp INT NOT NULL DEFAULT 0 COMMENT '当前经验值',
    gold INT NOT NULL DEFAULT 0 COMMENT '金币',
    silver_diamond INT NOT NULL DEFAULT 0 COMMENT '宝石',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='玩家基础信息表';

-- 镇妖占领表
CREATE TABLE IF NOT EXISTS zhenyao_floor (
    id INT AUTO_INCREMENT PRIMARY KEY,
    floor INT NOT NULL COMMENT '层数(1-120)',
    occupant_id INT DEFAULT NULL COMMENT '占领者ID',
    occupant_name VARCHAR(50) DEFAULT '' COMMENT '占领者昵称',
    occupy_time DATETIME DEFAULT NULL COMMENT '占领时间',
    expire_time DATETIME DEFAULT NULL COMMENT '到期时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_floor (floor),
    INDEX idx_occupant (occupant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='镇妖占领表';

-- 初始化测试用户（满级100级）
INSERT IGNORE INTO player (user_id, nickname, level, exp, gold) 
VALUES (1, '测试玩家', 100, 0, 10000);

-- 初始化镇妖层数（1-120层）
INSERT IGNORE INTO zhenyao_floor (floor) VALUES
(1),(2),(3),(4),(5),(6),(7),(8),(9),(10),
(11),(12),(13),(14),(15),(16),(17),(18),(19),(20),
(21),(22),(23),(24),(25),(26),(27),(28),(29),(30),
(31),(32),(33),(34),(35),(36),(37),(38),(39),(40),
(41),(42),(43),(44),(45),(46),(47),(48),(49),(50),
(51),(52),(53),(54),(55),(56),(57),(58),(59),(60),
(61),(62),(63),(64),(65),(66),(67),(68),(69),(70),
(71),(72),(73),(74),(75),(76),(77),(78),(79),(80),
(81),(82),(83),(84),(85),(86),(87),(88),(89),(90),
(91),(92),(93),(94),(95),(96),(97),(98),(99),(100),
(101),(102),(103),(104),(105),(106),(107),(108),(109),(110),
(111),(112),(113),(114),(115),(116),(117),(118),(119),(120);
