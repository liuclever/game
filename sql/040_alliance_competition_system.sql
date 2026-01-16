-- 联盟精英争霸赛系统
-- 040_alliance_competition_system.sql

-- 争霸赛届次表
CREATE TABLE IF NOT EXISTS alliance_competition_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_key VARCHAR(20) NOT NULL UNIQUE COMMENT '届次标识，格式：YYYY-MM-DD',
    session_name VARCHAR(50) NOT NULL COMMENT '届次名称',
    phase ENUM('registration', 'signup', 'battle', 'finished') NOT NULL DEFAULT 'registration' COMMENT '当前阶段：registration-报名阶段，signup-签到阶段，battle-战斗阶段，finished-已结束',
    registration_start DATETIME NOT NULL COMMENT '报名开始时间（周一0点）',
    registration_end DATETIME NOT NULL COMMENT '报名结束时间（周三23:59）',
    signup_start DATETIME NOT NULL COMMENT '签到开始时间（周四0点）',
    signup_end DATETIME NOT NULL COMMENT '签到结束时间（周日20:00）',
    battle_date DATE NOT NULL COMMENT '战斗日期',
    battle_start DATETIME NOT NULL COMMENT '战斗开始时间（20:00）',
    battle_end DATETIME NOT NULL COMMENT '战斗结束时间（22:00）',
    result_published_at DATETIME NULL COMMENT '成绩公布时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_session_key (session_key),
    INDEX idx_phase (phase),
    INDEX idx_battle_date (battle_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='争霸赛届次表';

-- 联盟报名表
CREATE TABLE IF NOT EXISTS alliance_competition_registrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL COMMENT '届次ID',
    alliance_id INT NOT NULL COMMENT '联盟ID',
    registered_by INT NOT NULL COMMENT '报名人user_id（盟主或副盟主）',
    registered_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '报名时间',
    status TINYINT NOT NULL DEFAULT 1 COMMENT '状态：1-已报名，0-已取消',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_session_alliance (session_id, alliance_id),
    INDEX idx_alliance_id (alliance_id),
    INDEX idx_session_id (session_id),
    CONSTRAINT fk_registration_session FOREIGN KEY (session_id) REFERENCES alliance_competition_sessions(id),
    CONSTRAINT fk_registration_alliance FOREIGN KEY (alliance_id) REFERENCES alliances(id),
    CONSTRAINT fk_registration_user FOREIGN KEY (registered_by) REFERENCES player(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='联盟报名表';

-- 战队等级对应表
CREATE TABLE IF NOT EXISTS alliance_competition_teams (
    id INT AUTO_INCREMENT PRIMARY KEY,
    team_key VARCHAR(20) NOT NULL UNIQUE COMMENT '战队标识：calf_tiger, white_tiger, azure_dragon, vermillion_bird, black_tortoise, god_of_war',
    team_name VARCHAR(20) NOT NULL COMMENT '战队名称：犊虎战队、白虎战队等',
    min_level INT NOT NULL COMMENT '最低等级',
    max_level INT NOT NULL COMMENT '最高等级',
    max_members INT NOT NULL DEFAULT 5 COMMENT '最多参战人数',
    min_members INT NOT NULL DEFAULT 1 COMMENT '最少参战人数',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='战队等级对应表';

-- 插入战队数据
INSERT INTO alliance_competition_teams (team_key, team_name, min_level, max_level, max_members, min_members) VALUES
('calf_tiger', '犊虎战队', 1, 39, 5, 1),
('white_tiger', '白虎战队', 40, 49, 5, 1),
('azure_dragon', '青龙战队', 50, 59, 5, 1),
('vermillion_bird', '朱雀战队', 60, 69, 5, 1),
('black_tortoise', '玄武战队', 70, 79, 5, 1),
('god_of_war', '战神战队', 80, 100, 5, 1)
ON DUPLICATE KEY UPDATE team_name=VALUES(team_name);

-- 成员签到表
CREATE TABLE IF NOT EXISTS alliance_competition_signups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL COMMENT '届次ID',
    alliance_id INT NOT NULL COMMENT '联盟ID',
    user_id INT NOT NULL COMMENT '成员user_id',
    team_key VARCHAR(20) NOT NULL COMMENT '所属战队',
    signed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '签到时间',
    status TINYINT NOT NULL DEFAULT 1 COMMENT '状态：1-已签到，0-已取消',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_session_alliance_user (session_id, alliance_id, user_id),
    INDEX idx_alliance_id (alliance_id),
    INDEX idx_session_team (session_id, team_key),
    INDEX idx_user_id (user_id),
    CONSTRAINT fk_signup_session FOREIGN KEY (session_id) REFERENCES alliance_competition_sessions(id),
    CONSTRAINT fk_signup_alliance FOREIGN KEY (alliance_id) REFERENCES alliances(id),
    CONSTRAINT fk_signup_user FOREIGN KEY (user_id) REFERENCES player(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='成员签到表';

-- 战队成员出战顺序表
CREATE TABLE IF NOT EXISTS alliance_competition_team_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL COMMENT '届次ID',
    alliance_id INT NOT NULL COMMENT '联盟ID',
    team_key VARCHAR(20) NOT NULL COMMENT '战队标识',
    user_id INT NOT NULL COMMENT '成员user_id',
    battle_order INT NOT NULL COMMENT '出战顺序（1-5）',
    adjusted_by INT NULL COMMENT '调整人user_id（盟主或副盟主）',
    adjusted_at DATETIME NULL COMMENT '调整时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_session_alliance_team_order (session_id, alliance_id, team_key, battle_order),
    UNIQUE KEY uk_session_alliance_user (session_id, alliance_id, user_id),
    INDEX idx_alliance_team (alliance_id, team_key),
    CONSTRAINT fk_team_member_session FOREIGN KEY (session_id) REFERENCES alliance_competition_sessions(id),
    CONSTRAINT fk_team_member_alliance FOREIGN KEY (alliance_id) REFERENCES alliances(id),
    CONSTRAINT fk_team_member_user FOREIGN KEY (user_id) REFERENCES player(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='战队成员出战顺序表';

-- 战斗记录表
CREATE TABLE IF NOT EXISTS alliance_competition_battles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL COMMENT '届次ID',
    round INT NOT NULL COMMENT '轮次：1-第一轮，2-第二轮，3-第三轮，4-第四轮（8强、4强、2强、决赛）',
    team_key VARCHAR(20) NOT NULL COMMENT '战队标识',
    alliance_id INT NOT NULL COMMENT '联盟ID',
    opponent_alliance_id INT NULL COMMENT '对手联盟ID',
    battle_result ENUM('win', 'lose', 'pending') NOT NULL DEFAULT 'pending' COMMENT '战斗结果',
    battle_data TEXT NULL COMMENT '战斗详细数据（JSON格式）',
    battle_time DATETIME NULL COMMENT '战斗时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_session_round (session_id, round),
    INDEX idx_alliance_id (alliance_id),
    CONSTRAINT fk_battle_session FOREIGN KEY (session_id) REFERENCES alliance_competition_sessions(id),
    CONSTRAINT fk_battle_alliance FOREIGN KEY (alliance_id) REFERENCES alliances(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='战斗记录表';

-- 个人战斗记录表（记录每个成员的战斗情况）
CREATE TABLE IF NOT EXISTS alliance_competition_personal_battles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    battle_id INT NOT NULL COMMENT '战斗ID',
    user_id INT NOT NULL COMMENT '成员user_id',
    opponent_user_id INT NULL COMMENT '对手user_id',
    battle_result ENUM('win', 'lose', 'pending') NOT NULL DEFAULT 'pending' COMMENT '个人战斗结果',
    eliminated_opponent TINYINT NOT NULL DEFAULT 0 COMMENT '是否淘汰对手：1-是，0-否',
    battle_data TEXT NULL COMMENT '战斗详细数据',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_battle_id (battle_id),
    INDEX idx_user_id (user_id),
    CONSTRAINT fk_personal_battle FOREIGN KEY (battle_id) REFERENCES alliance_competition_battles(id),
    CONSTRAINT fk_personal_battle_user FOREIGN KEY (user_id) REFERENCES player(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='个人战斗记录表';

-- 积分表
CREATE TABLE IF NOT EXISTS alliance_competition_scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL COMMENT '届次ID',
    alliance_id INT NOT NULL COMMENT '联盟ID',
    team_key VARCHAR(20) NOT NULL COMMENT '战队标识',
    team_score INT NOT NULL DEFAULT 0 COMMENT '战队积分',
    team_rank INT NULL COMMENT '战队排名',
    team_final_rank INT NULL COMMENT '战队最终排名（冠军、2强、4强、8强）',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_session_alliance_team (session_id, alliance_id, team_key),
    INDEX idx_alliance_id (alliance_id),
    INDEX idx_team_rank (team_rank),
    CONSTRAINT fk_score_session FOREIGN KEY (session_id) REFERENCES alliance_competition_sessions(id),
    CONSTRAINT fk_score_alliance FOREIGN KEY (alliance_id) REFERENCES alliances(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='战队积分表';

-- 个人积分表
CREATE TABLE IF NOT EXISTS alliance_competition_personal_scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL COMMENT '届次ID',
    user_id INT NOT NULL COMMENT '成员user_id',
    alliance_id INT NOT NULL COMMENT '联盟ID',
    team_key VARCHAR(20) NOT NULL COMMENT '战队标识',
    personal_score INT NOT NULL DEFAULT 0 COMMENT '个人积分',
    personal_rank INT NULL COMMENT '个人排名',
    eliminated_count INT NOT NULL DEFAULT 0 COMMENT '淘汰对手数量',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_session_user (session_id, user_id),
    INDEX idx_alliance_id (alliance_id),
    INDEX idx_personal_rank (personal_rank),
    INDEX idx_user_id (user_id),
    CONSTRAINT fk_personal_score_session FOREIGN KEY (session_id) REFERENCES alliance_competition_sessions(id),
    CONSTRAINT fk_personal_score_user FOREIGN KEY (user_id) REFERENCES player(user_id),
    CONSTRAINT fk_personal_score_alliance FOREIGN KEY (alliance_id) REFERENCES alliances(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='个人积分表';

-- 联盟威望表（累计所有战队的积分和个人积分）
CREATE TABLE IF NOT EXISTS alliance_competition_prestige (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL COMMENT '届次ID',
    alliance_id INT NOT NULL COMMENT '联盟ID',
    prestige INT NOT NULL DEFAULT 0 COMMENT '联盟威望（战队积分+个人积分总和）',
    alliance_rank INT NULL COMMENT '联盟排名',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_session_alliance (session_id, alliance_id),
    INDEX idx_alliance_id (alliance_id),
    INDEX idx_prestige_rank (prestige DESC, alliance_rank),
    CONSTRAINT fk_prestige_session FOREIGN KEY (session_id) REFERENCES alliance_competition_sessions(id),
    CONSTRAINT fk_prestige_alliance FOREIGN KEY (alliance_id) REFERENCES alliances(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='联盟威望表';

-- 奖励表
CREATE TABLE IF NOT EXISTS alliance_competition_rewards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL COMMENT '届次ID',
    reward_type ENUM('team', 'alliance', 'elite') NOT NULL COMMENT '奖励类型：team-战队奖励，alliance-全盟奖励，elite-精英奖励',
    alliance_id INT NULL COMMENT '联盟ID（战队奖励和全盟奖励）',
    user_id INT NULL COMMENT '用户ID（精英奖励）',
    team_key VARCHAR(20) NULL COMMENT '战队标识（战队奖励）',
    `rank` INT NOT NULL COMMENT '排名',
    reward_data TEXT NOT NULL COMMENT '奖励数据（JSON格式，包含物品ID和数量）',
    claimed TINYINT NOT NULL DEFAULT 0 COMMENT '是否已领取：1-已领取，0-未领取',
    claimed_at DATETIME NULL COMMENT '领取时间',
    claim_deadline DATETIME NOT NULL COMMENT '最迟领取时间（下周六）',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_session_type (session_id, reward_type),
    INDEX idx_alliance_id (alliance_id),
    INDEX idx_user_id (user_id),
    INDEX idx_claimed (claimed),
    CONSTRAINT fk_reward_session FOREIGN KEY (session_id) REFERENCES alliance_competition_sessions(id),
    CONSTRAINT fk_reward_alliance FOREIGN KEY (alliance_id) REFERENCES alliances(id),
    CONSTRAINT fk_reward_user FOREIGN KEY (user_id) REFERENCES player(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='奖励表';
