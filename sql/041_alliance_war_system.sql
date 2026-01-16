-- 041 盟战系统完整表结构
USE game_tower;

-- 盟战签到表
CREATE TABLE IF NOT EXISTS alliance_war_checkin (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    alliance_id INT NOT NULL,
    user_id INT NOT NULL,
    war_phase VARCHAR(10) NOT NULL COMMENT 'first/second',
    war_weekday INT NOT NULL COMMENT '0=周一, 3=周四',
    checkin_date DATE NOT NULL COMMENT '签到日期',
    checkin_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    copper_reward INT NOT NULL DEFAULT 30000,
    PRIMARY KEY (id),
    UNIQUE KEY uk_alliance_user_phase_date (alliance_id, user_id, war_phase, war_weekday, checkin_date),
    INDEX idx_alliance_phase_date (alliance_id, war_phase, war_weekday, checkin_date),
    INDEX idx_user_date (user_id, checkin_date),
    CONSTRAINT fk_war_checkin_alliance FOREIGN KEY (alliance_id) REFERENCES alliances(id),
    CONSTRAINT fk_war_checkin_user FOREIGN KEY (user_id) REFERENCES player(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='盟战签到表';

-- 盟战战绩表（记录每次盟战的对战情况）
CREATE TABLE IF NOT EXISTS alliance_war_battle_records (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    battle_id BIGINT UNSIGNED COMMENT '关联alliance_land_battle.id',
    alliance_id INT NOT NULL,
    opponent_alliance_id INT NOT NULL,
    land_id INT NOT NULL,
    army_type VARCHAR(10) NOT NULL COMMENT 'dragon/tiger',
    war_phase VARCHAR(10) NOT NULL COMMENT 'first/second',
    war_date DATE NOT NULL,
    battle_result VARCHAR(10) NOT NULL COMMENT 'win/lose',
    honor_gained INT NOT NULL DEFAULT 0 COMMENT '获得的战功',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_alliance_date (alliance_id, war_date),
    INDEX idx_alliance_phase (alliance_id, war_phase, war_date),
    INDEX idx_battle_id (battle_id),
    CONSTRAINT fk_war_record_alliance FOREIGN KEY (alliance_id) REFERENCES alliances(id),
    CONSTRAINT fk_war_record_opponent FOREIGN KEY (opponent_alliance_id) REFERENCES alliances(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='盟战战绩表';

-- 赛季奖励发放记录表
CREATE TABLE IF NOT EXISTS alliance_season_rewards (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    alliance_id INT NOT NULL,
    season_key CHAR(7) NOT NULL COMMENT 'YYYY-MM',
    rank INT NOT NULL,
    copper_reward INT NOT NULL DEFAULT 0,
    items_json TEXT COMMENT '奖励物品JSON',
    distributed_at DATETIME DEFAULT NULL COMMENT '发放时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_alliance_season (alliance_id, season_key),
    INDEX idx_season_rank (season_key, rank),
    CONSTRAINT fk_season_reward_alliance FOREIGN KEY (alliance_id) REFERENCES alliances(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='赛季奖励发放记录';

-- 战功兑换记录表
CREATE TABLE IF NOT EXISTS alliance_war_honor_exchange (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    alliance_id INT NOT NULL,
    user_id INT NOT NULL COMMENT '兑换操作者（盟主或副盟主）',
    exchange_type VARCHAR(20) NOT NULL COMMENT 'fire_crystal/gold_bag',
    honor_cost INT NOT NULL,
    item_id INT NOT NULL,
    item_name VARCHAR(32) NOT NULL,
    item_quantity INT NOT NULL DEFAULT 1,
    exchanged_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_alliance_date (alliance_id, exchanged_at),
    INDEX idx_user_date (user_id, exchanged_at),
    CONSTRAINT fk_honor_exchange_alliance FOREIGN KEY (alliance_id) REFERENCES alliances(id),
    CONSTRAINT fk_honor_exchange_user FOREIGN KEY (user_id) REFERENCES player(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='战功兑换记录表';

-- 如果lands表不存在，创建基础表
CREATE TABLE IF NOT EXISTS lands (
    id INT NOT NULL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    land_type VARCHAR(20) NOT NULL COMMENT 'land/stronghold',
    daily_reward_copper INT NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='土地/据点基础表';

-- 初始化土地数据
-- 更新土地数据，使用与前端一致的名称和ID
DELETE FROM lands WHERE id IN (1, 2, 3, 4, 5);
INSERT INTO lands (id, name, land_type, daily_reward_copper) VALUES
(1, '林中空地1号土地', 'land', 10000),
(2, '幻灵镇1号土地', 'land', 10000),
(4, '林中空地1号据点', 'stronghold', 5000),
(5, '幻灵镇1号据点', 'stronghold', 5000);

-- 土地占领表（记录当前占领情况）
CREATE TABLE IF NOT EXISTS alliance_land_occupation (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    land_id INT NOT NULL,
    alliance_id INT NOT NULL,
    occupied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    war_phase VARCHAR(10) NOT NULL COMMENT 'first/second',
    war_date DATE NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_land_id (land_id),
    INDEX idx_alliance_date (alliance_id, occupied_at),
    CONSTRAINT fk_occupation_land FOREIGN KEY (land_id) REFERENCES lands(id) ON DELETE CASCADE,
    CONSTRAINT fk_occupation_alliance FOREIGN KEY (alliance_id) REFERENCES alliances(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='土地占领表';
