CREATE TABLE IF NOT EXISTS `player_month_card` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `user_id` BIGINT UNSIGNED NOT NULL,
    `month` TINYINT UNSIGNED NOT NULL,
    `start_date` DATETIME NOT NULL,
    `end_date` DATETIME NOT NULL,
    `days_total` SMALLINT UNSIGNED NOT NULL DEFAULT 30,
    `days_claimed` SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    `last_claim_date` DATE NULL,
    `status` ENUM('pending', 'active', 'expired') NOT NULL DEFAULT 'active',
    `initial_reward` INT NOT NULL DEFAULT 1000,
    `daily_reward` INT NOT NULL DEFAULT 200,
    `initial_reward_claimed` TINYINT(1) NOT NULL DEFAULT 0,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uniq_user_month` (`user_id`, `month`),
    KEY `idx_user_status` (`user_id`, `status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
