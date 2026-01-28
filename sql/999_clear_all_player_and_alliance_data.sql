-- ============================================================
-- 清理所有玩家和联盟数据 - 正式上线前执行
-- 警告：此脚本将删除所有玩家和联盟相关数据，不可恢复！
-- 执行前请务必备份数据库！
-- ============================================================

USE game_tower;

-- 创建临时存储过程来安全地清除表
DELIMITER $$

DROP PROCEDURE IF EXISTS safe_truncate_table$$

CREATE PROCEDURE safe_truncate_table(IN table_name VARCHAR(64))
BEGIN
    DECLARE table_exists INT DEFAULT 0;
    
    -- 检查表是否存在
    SELECT COUNT(*) INTO table_exists
    FROM information_schema.tables 
    WHERE table_schema = 'game_tower' 
    AND table_name = table_name;
    
    -- 如果表存在，则清空
    IF table_exists > 0 THEN
        SET @sql = CONCAT('DELETE FROM `', table_name, '` WHERE 1=1');
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
        
        -- 重置自增ID
        SET @sql = CONCAT('ALTER TABLE `', table_name, '` AUTO_INCREMENT = 1');
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
END$$

DELIMITER ;

-- 禁用外键检查
SET FOREIGN_KEY_CHECKS=0;

-- ============================================================
-- 第一部分：清理联盟相关数据
-- ============================================================

-- 联盟争霸赛相关表
CALL safe_truncate_table('alliance_competition_sessions');
CALL safe_truncate_table('alliance_competition_registrations');
CALL safe_truncate_table('alliance_competition_teams');
CALL safe_truncate_table('alliance_competition_signups');
CALL safe_truncate_table('alliance_competition_team_members');
CALL safe_truncate_table('alliance_competition_battles');
CALL safe_truncate_table('alliance_competition_personal_battles');
CALL safe_truncate_table('alliance_competition_scores');
CALL safe_truncate_table('alliance_competition_personal_scores');
CALL safe_truncate_table('alliance_competition_prestige');
CALL safe_truncate_table('alliance_competition_rewards');

-- 联盟盟战相关表
CALL safe_truncate_table('alliance_war_checkin');
CALL safe_truncate_table('alliance_war_battle_records');
CALL safe_truncate_table('alliance_war_honor_exchange');
CALL safe_truncate_table('alliance_land_occupation');
CALL safe_truncate_table('alliance_land_battle_duel');
CALL safe_truncate_table('alliance_land_battle_round');
CALL safe_truncate_table('alliance_land_battle');
CALL safe_truncate_table('alliance_land_registration');
CALL safe_truncate_table('alliance_army_signups');
CALL safe_truncate_table('alliance_war_session_config');

-- 联盟基础数据表
CALL safe_truncate_table('alliance_training_participants');
CALL safe_truncate_table('alliance_training_rooms');
CALL safe_truncate_table('alliance_item_storage');
CALL safe_truncate_table('alliance_beast_storage');
CALL safe_truncate_table('alliance_activities');
CALL safe_truncate_table('alliance_chat_messages');
CALL safe_truncate_table('alliance_war_honor_effects');
CALL safe_truncate_table('alliance_war_scores');
CALL safe_truncate_table('alliance_army_assignments');
CALL safe_truncate_table('alliance_members');
CALL safe_truncate_table('alliance_talents');
CALL safe_truncate_table('alliance_buildings');
CALL safe_truncate_table('alliance_quit_records');
CALL safe_truncate_table('alliances');

-- ============================================================
-- 第二部分：清理玩家相关数据
-- ============================================================

-- 玩家战斗记录
CALL safe_truncate_table('arena_battle_log');
CALL safe_truncate_table('arena_daily_challenge');
CALL safe_truncate_table('arena_streak_history');
CALL safe_truncate_table('arena_streak');
CALL safe_truncate_table('arena_stats');
CALL safe_truncate_table('arena');
CALL safe_truncate_table('battlefield_battle_log');
CALL safe_truncate_table('battlefield_signup');
CALL safe_truncate_table('spar_battle_log');
CALL safe_truncate_table('spar_records');
CALL safe_truncate_table('zhenyao_battle_log');
CALL safe_truncate_table('zhenyao_daily_count');
CALL safe_truncate_table('zhenyao_floor');

-- 召唤之王挑战赛
CALL safe_truncate_table('king_challenge_logs');
CALL safe_truncate_table('king_challenge_rank');
CALL safe_truncate_table('king_final_stage');
CALL safe_truncate_table('king_reward_claimed');

-- 玩家社交数据
CALL safe_truncate_table('friend_relation');
CALL safe_truncate_table('friend_request');
CALL safe_truncate_table('world_chat_message');
CALL safe_truncate_table('private_message');

-- 玩家活动数据
CALL safe_truncate_table('player_daily_activity');
CALL safe_truncate_table('player_gift_claim');
CALL safe_truncate_table('dragonpalace_daily_state');
CALL safe_truncate_table('mosoul_hunting_state');
CALL safe_truncate_table('mosoul_global_pity');
CALL safe_truncate_table('player_signin_records');
CALL safe_truncate_table('tree_player_week');
CALL safe_truncate_table('activity_claims');
CALL safe_truncate_table('activity_finalize_log');
CALL safe_truncate_table('activity_power_ranking_reward');
CALL safe_truncate_table('activity_wheel_lottery');
CALL safe_truncate_table('fortune_talisman_daily');
CALL safe_truncate_table('player_chest_counter');
CALL safe_truncate_table('player_diamond_exchange_log');
CALL safe_truncate_table('player_exchange_claim');
CALL safe_truncate_table('player_shop_daily_purchase');
CALL safe_truncate_table('task_reward_claims');

-- 玩家副本和修炼数据
CALL safe_truncate_table('player_dungeon_progress');

-- 玩家庄园数据
CALL safe_truncate_table('manor_land');
CALL safe_truncate_table('player_manor');

-- 玩家幻兽和装备数据
CALL safe_truncate_table('player_beast');
CALL safe_truncate_table('beast_bone');
CALL safe_truncate_table('player_mosoul');
CALL safe_truncate_table('player_spirit');
CALL safe_truncate_table('spirit_account');
CALL safe_truncate_table('refine_pot_log');

-- 玩家背包和物品
CALL safe_truncate_table('player_inventory');
CALL safe_truncate_table('player_bag');

-- 玩家系统数据
CALL safe_truncate_table('player_effect');
CALL safe_truncate_table('player_immortalize_pool');
CALL safe_truncate_table('player_month_card');
CALL safe_truncate_table('player_talent_levels');
CALL safe_truncate_table('tower_state');

-- 玩家充值订单
CALL safe_truncate_table('recharge_order');

-- 玩家基础信息表（最后清理）
CALL safe_truncate_table('player');

-- ============================================================
-- 第三部分：重置全局配置（可选）
-- ============================================================

-- 重置赛季配置（这些是全服配置表，清除后会重置赛季）
CALL safe_truncate_table('king_season_config');
CALL safe_truncate_table('tree_week');

-- 如果需要重置赛季，取消下面的注释
-- INSERT INTO king_season_config (season, start_date, end_date) 
-- VALUES (1, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 7 DAY));

-- 恢复外键检查
SET FOREIGN_KEY_CHECKS=1;

-- 删除临时存储过程
DROP PROCEDURE IF EXISTS safe_truncate_table;

-- ============================================================
-- 执行完成
-- ============================================================

-- 注意：以下系统配置表不会被清除，它们包含游戏逻辑所需的配置数据：
-- - blacklist (黑名单配置)
-- - lands (土地配置)
-- - level_config (等级配置)
-- - cultivation_config (修行配置)

SELECT '所有玩家和联盟数据已清理完成！' AS message;
SELECT '系统配置表（blacklist, lands, level_config, cultivation_config）已保留' AS note;
