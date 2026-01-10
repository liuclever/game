-- 联盟报名土地关联表
-- 记录每块土地的联盟报名信息，包括报名时间、消耗与状态
CREATE TABLE IF NOT EXISTS alliance_land_registration (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '报名记录ID',
    land_id INT NOT NULL COMMENT '土地ID，关联 lands.id',
    alliance_id INT NOT NULL COMMENT '联盟ID，关联 alliances.id',
    army VARCHAR(16) DEFAULT NULL COMMENT '报名军团（dragon/tiger）',
    registration_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '报名时间',
    cost INT NOT NULL DEFAULT 0 COMMENT '报名消耗（资源/货币数值）',
    status TINYINT NOT NULL DEFAULT 1 COMMENT '报名状态：1-已报名，2-待审核，3-已生效，0-已取消',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_land_alliance (land_id, alliance_id),
    INDEX idx_land_id (land_id),
    INDEX idx_alliance_id (alliance_id),
    CONSTRAINT fk_alliance_land_registration_land FOREIGN KEY (land_id) REFERENCES lands(id),
    CONSTRAINT fk_alliance_land_registration_alliance FOREIGN KEY (alliance_id) REFERENCES alliances(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='土地报名联盟关联表';
