-- 联盟兵营报名表
CREATE TABLE IF NOT EXISTS alliance_army_assignments (
    alliance_id INT NOT NULL,
    user_id INT NOT NULL,
    army ENUM('dragon', 'tiger') NOT NULL,
    signed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (alliance_id, user_id),
    INDEX idx_army_alliance (alliance_id, army),
    CONSTRAINT fk_army_alliance FOREIGN KEY (alliance_id) REFERENCES alliances(id),
    CONSTRAINT fk_army_user FOREIGN KEY (user_id) REFERENCES player(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='联盟兵营报名（飞龙军/伏虎军）';
