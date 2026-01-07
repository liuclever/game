-- 029_task_rewards.sql
-- 任务奖励领取记录表

CREATE TABLE IF NOT EXISTS `task_reward_claims` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `user_id` INT UNSIGNED NOT NULL,
    `reward_key` VARCHAR(64) NOT NULL,
    `claimed_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uniq_user_reward` (`user_id`, `reward_key`),
    KEY `idx_reward_key` (`reward_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='任务奖励领取记录';
