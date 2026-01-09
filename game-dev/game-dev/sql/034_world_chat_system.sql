USE game_tower;

-- 世界聊天消息表
CREATE TABLE IF NOT EXISTS world_chat_message (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '发送者ID',
    nickname VARCHAR(50) NOT NULL COMMENT '发送者昵称',
    message_type VARCHAR(20) NOT NULL DEFAULT 'normal' COMMENT '消息类型：normal=普通喊话, summon_king=召唤之王置顶',
    content VARCHAR(200) NOT NULL COMMENT '消息内容（最多200字符）',
    is_pinned TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否置顶（召唤之王消息）',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '发送时间',
    INDEX idx_user (user_id),
    INDEX idx_type_created (message_type, created_at),
    INDEX idx_pinned (is_pinned, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='世界聊天消息表';
