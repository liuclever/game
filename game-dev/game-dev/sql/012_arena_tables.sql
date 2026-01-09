-- 012 擂台系统表
-- 擂台竞技功能相关表

USE game_tower;

-- 擂台表
CREATE TABLE IF NOT EXISTS arena (
    id INT PRIMARY KEY AUTO_INCREMENT,
    rank_name VARCHAR(20) NOT NULL COMMENT '等级阶段名称（黄阶/玄阶/地阶/天阶/飞马/天龙/战神）',
    arena_type VARCHAR(10) NOT NULL COMMENT '场次类型（normal普通场/gold黄金场）',
    champion_user_id INT DEFAULT NULL COMMENT '当前擂主用户ID，NULL表示空置',
    champion_nickname VARCHAR(50) DEFAULT NULL COMMENT '擂主昵称',
    consecutive_wins INT NOT NULL DEFAULT 0 COMMENT '连胜场次',
    prize_pool INT NOT NULL DEFAULT 0 COMMENT '奖池球数',
    last_battle_time DATETIME DEFAULT NULL COMMENT '最后战斗时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_rank_type (rank_name, arena_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='擂台表';

-- 守擂统计表（记录玩家达成十连胜的次数）
CREATE TABLE IF NOT EXISTS arena_stats (
    user_id INT NOT NULL,
    rank_name VARCHAR(20) NOT NULL COMMENT '等级阶段名称',
    success_count INT NOT NULL DEFAULT 0 COMMENT '守擂成功次数（达成10连胜次数）',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, rank_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='擂台守擂统计表';

-- 初始化各等级阶段的擂台（普通场和黄金场）
INSERT IGNORE INTO arena (rank_name, arena_type) VALUES
('黄阶', 'normal'), ('黄阶', 'gold'),
('玄阶', 'normal'), ('玄阶', 'gold'),
('地阶', 'normal'), ('地阶', 'gold'),
('天阶', 'normal'), ('天阶', 'gold'),
('飞马', 'normal'), ('飞马', 'gold'),
('天龙', 'normal'), ('天龙', 'gold'),
('战神', 'normal'), ('战神', 'gold');
