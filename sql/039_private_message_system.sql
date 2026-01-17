-- 039 私信和好友请求系统
USE game_tower;

-- 私信表
CREATE TABLE IF NOT EXISTS private_message (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT NOT NULL COMMENT '发送者ID',
    sender_name VARCHAR(50) NOT NULL COMMENT '发送者昵称',
    receiver_id INT NOT NULL COMMENT '接收者ID',
    receiver_name VARCHAR(50) NOT NULL COMMENT '接收者昵称',
    content VARCHAR(200) NOT NULL COMMENT '消息内容（最多200字符）',
    is_read TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否已读(1=已读,0=未读)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '发送时间',
    INDEX idx_sender (sender_id),
    INDEX idx_receiver (receiver_id),
    INDEX idx_receiver_created (receiver_id, created_at),
    INDEX idx_conversation (sender_id, receiver_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='私信表';

-- 好友请求表
CREATE TABLE IF NOT EXISTS friend_request (
    id INT AUTO_INCREMENT PRIMARY KEY,
    requester_id INT NOT NULL COMMENT '请求者ID',
    requester_name VARCHAR(50) NOT NULL COMMENT '请求者昵称',
    receiver_id INT NOT NULL COMMENT '接收者ID',
    receiver_name VARCHAR(50) NOT NULL COMMENT '接收者昵称',
    status VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT '状态：pending=待处理,accepted=已同意,rejected=已拒绝',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '请求时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_requester (requester_id),
    INDEX idx_receiver (receiver_id),
    INDEX idx_receiver_status (receiver_id, status),
    INDEX idx_created (created_at),
    UNIQUE KEY uk_request (requester_id, receiver_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='好友请求表';

-- 好友关系表
CREATE TABLE IF NOT EXISTS friend_relation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    friend_id INT NOT NULL COMMENT '好友ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '成为好友时间',
    INDEX idx_user (user_id),
    INDEX idx_friend (friend_id),
    UNIQUE KEY uk_friendship (user_id, friend_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='好友关系表';
