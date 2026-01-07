-- 联盟表
CREATE TABLE IF NOT EXISTS alliances (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    leader_id INT NOT NULL,
    level INT DEFAULT 1,
    exp INT DEFAULT 0,
    funds INT DEFAULT 0,
    crystals INT DEFAULT 0,
    prosperity INT DEFAULT 0,
    war_honor INT DEFAULT 0 COMMENT '当前联盟战功',
    war_honor_history INT DEFAULT 0 COMMENT '历史累计战功',
    notice TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 联盟建筑等级表
CREATE TABLE IF NOT EXISTS alliance_buildings (
    alliance_id INT NOT NULL,
    building_key VARCHAR(32) NOT NULL,
    level INT NOT NULL DEFAULT 1,
    PRIMARY KEY (alliance_id, building_key),
    FOREIGN KEY (alliance_id) REFERENCES alliances(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 联盟天赋研究表
CREATE TABLE IF NOT EXISTS alliance_talents (
    alliance_id INT NOT NULL,
    talent_key VARCHAR(16) NOT NULL,
    research_level INT DEFAULT 1,
    PRIMARY KEY (alliance_id, talent_key),
    FOREIGN KEY (alliance_id) REFERENCES alliances(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 玩家天赋等级表
CREATE TABLE IF NOT EXISTS player_talent_levels (
    user_id INT NOT NULL,
    talent_key VARCHAR(16) NOT NULL,
    level INT DEFAULT 0,
    PRIMARY KEY (user_id, talent_key),
    FOREIGN KEY (user_id) REFERENCES player(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 联盟成员表
CREATE TABLE IF NOT EXISTS alliance_members (
    alliance_id INT NOT NULL,
    user_id INT NOT NULL PRIMARY KEY,
    role TINYINT DEFAULT 0,
    contribution INT DEFAULT 0,
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (alliance_id) REFERENCES alliances(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 联盟聊天消息表
CREATE TABLE IF NOT EXISTS alliance_chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    alliance_id INT NOT NULL,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_alliance_id (alliance_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 联盟战功月度累计表
CREATE TABLE IF NOT EXISTS alliance_war_scores (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    alliance_id INT NOT NULL,
    season_key CHAR(7) NOT NULL COMMENT '自然月，格式 YYYY-MM',
    score INT NOT NULL DEFAULT 0,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_alliance_season (alliance_id, season_key),
    CONSTRAINT fk_war_scores_alliance FOREIGN KEY (alliance_id) REFERENCES alliances(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='联盟战功月度积分';

-- 联盟战功兑换记录表
CREATE TABLE IF NOT EXISTS alliance_war_honor_effects (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    alliance_id INT NOT NULL,
    effect_key VARCHAR(32) NOT NULL COMMENT '配置 key',
    effect_type VARCHAR(16) NOT NULL COMMENT 'xp/fire 等类别',
    cost INT NOT NULL DEFAULT 0 COMMENT '兑换消耗战功',
    started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    created_by INT NOT NULL COMMENT '发起兑换的 user_id',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_alliance_effect (alliance_id, effect_key),
    KEY idx_effect_expiration (alliance_id, effect_type, expires_at),
    CONSTRAINT fk_honor_effects_alliance FOREIGN KEY (alliance_id) REFERENCES alliances(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='联盟战功兑换效果记录，约定持续 24 小时';

-- NOTE: war_honor / war_honor_history 字段用于分别存储当前战功与历史战功累计，如需迁移旧数据请在后续脚本中补齐。

-- 联盟动态表
CREATE TABLE IF NOT EXISTS alliance_activities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    alliance_id INT NOT NULL,
    event_type VARCHAR(16) NOT NULL,
    actor_user_id INT DEFAULT NULL,
    actor_name VARCHAR(32) DEFAULT NULL,
    target_user_id INT DEFAULT NULL,
    target_name VARCHAR(32) DEFAULT NULL,
    item_name VARCHAR(32) DEFAULT NULL,
    item_quantity INT DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_alliance_activity (alliance_id, created_at),
    FOREIGN KEY (alliance_id) REFERENCES alliances(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 联盟幻兽寄存表
CREATE TABLE IF NOT EXISTS alliance_beast_storage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    alliance_id INT NOT NULL,
    owner_user_id INT NOT NULL,
    beast_id INT NOT NULL,
    stored_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_beast_storage (beast_id),
    INDEX idx_alliance_storage (alliance_id),
    FOREIGN KEY (alliance_id) REFERENCES alliances(id),
    FOREIGN KEY (owner_user_id) REFERENCES player(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 联盟道具寄存表
CREATE TABLE IF NOT EXISTS alliance_item_storage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    alliance_id INT NOT NULL,
    owner_user_id INT NOT NULL,
    item_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    stored_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_alliance_item_storage (alliance_id),
    INDEX idx_owner_item (owner_user_id, item_id),
    FOREIGN KEY (alliance_id) REFERENCES alliances(id),
    FOREIGN KEY (owner_user_id) REFERENCES player(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 联盟修行房间
CREATE TABLE IF NOT EXISTS alliance_training_rooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    alliance_id INT NOT NULL,
    creator_user_id INT NOT NULL,
    title VARCHAR(32) NOT NULL,
    status VARCHAR(16) NOT NULL DEFAULT 'ongoing',
    max_participants TINYINT NOT NULL DEFAULT 4,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME DEFAULT NULL,
    INDEX idx_alliance_training (alliance_id),
    FOREIGN KEY (alliance_id) REFERENCES alliances(id),
    FOREIGN KEY (creator_user_id) REFERENCES player(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 联盟修行参与者
CREATE TABLE IF NOT EXISTS alliance_training_participants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_id INT NOT NULL,
    user_id INT NOT NULL,
    joined_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    claimed_at DATETIME DEFAULT NULL,
    reward_amount INT DEFAULT 0,
    UNIQUE KEY uk_room_user (room_id, user_id),
    INDEX idx_user_joined (user_id, joined_at),
    FOREIGN KEY (room_id) REFERENCES alliance_training_rooms(id),
    FOREIGN KEY (user_id) REFERENCES player(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
