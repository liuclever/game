-- 为联盟成员表新增阵营字段
USE game_tower;

ALTER TABLE alliance_members
    ADD COLUMN army_type TINYINT NOT NULL DEFAULT 0 COMMENT '0-未报名,1-飞龙军,2-伏虎军'
        AFTER contribution;

CREATE INDEX idx_alliance_members_army ON alliance_members (alliance_id, army_type);
