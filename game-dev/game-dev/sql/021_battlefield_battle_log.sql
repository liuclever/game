-- 021 古战场战斗记录表
USE game_tower;

-- 古战场单场对战战报表（用于昨日战况 + 详细战报）
CREATE TABLE IF NOT EXISTS battlefield_battle_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    battlefield_type VARCHAR(10) NOT NULL COMMENT '战场类型（tiger猛虎战场/crane飞鹤战场）',
    period INT NOT NULL COMMENT '战场期数',
    round_num INT NOT NULL COMMENT '第几轮',
    match_num INT NOT NULL COMMENT '本轮第几场',
    first_user_id INT NOT NULL COMMENT '前置玩家ID（用于昨日战况列表左侧）',
    first_user_name VARCHAR(50) NOT NULL COMMENT '前置玩家昵称',
    second_user_id INT NOT NULL COMMENT '对手玩家ID',
    second_user_name VARCHAR(50) NOT NULL COMMENT '对手玩家昵称',
    first_user_team VARCHAR(10) DEFAULT NULL COMMENT '前置玩家阵营（red/blue，可选）',
    second_user_team VARCHAR(10) DEFAULT NULL COMMENT '对手阵营（red/blue，可选）',
    is_first_win TINYINT NOT NULL DEFAULT 0 COMMENT '前置玩家是否获胜(1=胜,0=负)',
    result_label VARCHAR(20) DEFAULT '' COMMENT '前置玩家结果描述（失败/小败/小胜/完美胜利等）',
    battle_data TEXT COMMENT '战斗详情(JSON，结构与镇妖/擂台战报一致)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_type_period (battlefield_type, period),
    INDEX idx_type_period_round (battlefield_type, period, round_num),
    INDEX idx_first_user (first_user_id),
    INDEX idx_second_user (second_user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='古战场战斗记录表';
