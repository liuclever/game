-- 召唤之王挑战记录表
-- 用于显示预选赛动态

CREATE TABLE IF NOT EXISTS king_challenge_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    challenger_id INT NOT NULL COMMENT '挑战者ID',
    challenger_name VARCHAR(50) NOT NULL COMMENT '挑战者昵称',
    defender_id INT NOT NULL COMMENT '防守者ID',
    defender_name VARCHAR(50) NOT NULL COMMENT '防守者昵称',
    challenger_wins BOOLEAN NOT NULL COMMENT '挑战者是否胜利',
    challenger_rank_before INT NOT NULL COMMENT '挑战者挑战前排名',
    challenger_rank_after INT NOT NULL COMMENT '挑战者挑战后排名',
    defender_rank_before INT NOT NULL COMMENT '防守者挑战前排名',
    defender_rank_after INT NOT NULL COMMENT '防守者挑战后排名',
    area_index INT NOT NULL COMMENT '赛区编号',
    challenge_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '挑战时间',
    INDEX idx_area_time (area_index, challenge_time),
    INDEX idx_challenger (challenger_id, challenge_time),
    INDEX idx_defender (defender_id, challenge_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='召唤之王挑战记录';

-- 说明：
-- 1. 每次挑战都会记录一条日志
-- 2. 用于显示预选赛动态
-- 3. 可以查询某个玩家的挑战历史
-- 4. 可以查询某个赛区的最新动态
