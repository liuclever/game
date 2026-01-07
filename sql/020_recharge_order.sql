-- 充值订单表
CREATE TABLE IF NOT EXISTS recharge_order (
    id INT AUTO_INCREMENT PRIMARY KEY,
    out_trade_no VARCHAR(64) NOT NULL UNIQUE COMMENT '商户订单号',
    trade_no VARCHAR(64) DEFAULT NULL COMMENT '支付宝交易号',
    user_id INT NOT NULL COMMENT '用户ID',
    product_id VARCHAR(32) NOT NULL COMMENT '商品ID',
    amount DECIMAL(10,2) NOT NULL COMMENT '支付金额(元)',
    status ENUM('pending', 'paid', 'failed', 'refunded') DEFAULT 'pending' COMMENT '订单状态',
    yuanbao_granted INT DEFAULT 0 COMMENT '发放的元宝数量',
    bonus_granted INT DEFAULT 0 COMMENT '首充奖励元宝',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    paid_at DATETIME DEFAULT NULL COMMENT '支付时间',
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='充值订单表';

-- 给player表添加首充标记和VIP经验字段（如果不存在）
ALTER TABLE player ADD COLUMN IF NOT EXISTS first_recharge_claimed TINYINT DEFAULT 0 COMMENT '首充是否已领取';
ALTER TABLE player ADD COLUMN IF NOT EXISTS vip_exp INT DEFAULT 0 COMMENT 'VIP经验(累计充值金额*100)';
