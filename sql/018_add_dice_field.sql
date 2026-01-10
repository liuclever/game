-- 为 player 表增加 dice 字段
ALTER TABLE player ADD COLUMN dice INT NOT NULL DEFAULT 0 COMMENT '骰子数量' AFTER yuanbao;
UPDATE player SET dice = 10 WHERE dice = 0;
