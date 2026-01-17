/*
 Navicat Premium Data Transfer

 Source Server         : 本机
 Source Server Type    : MySQL
 Source Server Version : 80041
 Source Host           : localhost:3306
 Source Schema         : game_tower

 Target Server Type    : MySQL
 Target Server Version : 80041
 File Encoding         : 65001

 Date: 31/12/2025 13:33:08
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for alliance_activities
-- ----------------------------
DROP TABLE IF EXISTS `alliance_activities`;
CREATE TABLE `alliance_activities`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `alliance_id` int(0) NOT NULL,
  `event_type` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `actor_user_id` int(0) NULL DEFAULT NULL,
  `actor_name` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `target_user_id` int(0) NULL DEFAULT NULL,
  `target_name` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `item_name` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `item_quantity` int(0) NULL DEFAULT NULL,
  `created_at` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_alliance_activity`(`alliance_id`, `created_at`) USING BTREE,
  CONSTRAINT `alliance_activities_ibfk_1` FOREIGN KEY (`alliance_id`) REFERENCES `alliances` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 10 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for alliance_army_assignments
-- ----------------------------
DROP TABLE IF EXISTS `alliance_army_assignments`;
CREATE TABLE `alliance_army_assignments`  (
  `alliance_id` int(0) NOT NULL,
  `user_id` int(0) NOT NULL,
  `army` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `signed_at` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`alliance_id`, `user_id`) USING BTREE,
  INDEX `idx_alliance_id`(`alliance_id`) USING BTREE,
  INDEX `idx_user_id`(`user_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for alliance_army_signups
-- ----------------------------
DROP TABLE IF EXISTS `alliance_army_signups`;
CREATE TABLE `alliance_army_signups`  (
  `id` bigint(0) UNSIGNED NOT NULL AUTO_INCREMENT,
  `registration_id` bigint(0) UNSIGNED NOT NULL,
  `alliance_id` int(0) NOT NULL,
  `army` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` bigint(0) NOT NULL,
  `signup_order` int(0) NOT NULL,
  `hp_state` json NULL,
  `status` tinyint(0) NOT NULL DEFAULT 1,
  `created_at` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_registration_user`(`registration_id`, `user_id`) USING BTREE,
  INDEX `idx_registration_order`(`registration_id`, `signup_order`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for alliance_beast_storage
-- ----------------------------
DROP TABLE IF EXISTS `alliance_beast_storage`;
CREATE TABLE `alliance_beast_storage`  (
  `id` int(0) NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `alliance_id` int(0) NOT NULL COMMENT '联盟ID',
  `owner_user_id` int(0) NOT NULL COMMENT '寄存者用户ID',
  `beast_id` int(0) NOT NULL COMMENT '幻兽ID',
  `stored_at` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '寄存时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uniq_beast`(`beast_id`) USING BTREE,
  INDEX `idx_alliance`(`alliance_id`) USING BTREE,
  INDEX `idx_owner`(`owner_user_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '联盟幻兽室寄存记录' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for alliance_buildings
-- ----------------------------
DROP TABLE IF EXISTS `alliance_buildings`;
CREATE TABLE `alliance_buildings`  (
  `alliance_id` int(0) NOT NULL,
  `building_key` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `level` int(0) NOT NULL DEFAULT 1,
  PRIMARY KEY (`alliance_id`, `building_key`) USING BTREE,
  CONSTRAINT `alliance_buildings_ibfk_1` FOREIGN KEY (`alliance_id`) REFERENCES `alliances` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for alliance_chat_messages
-- ----------------------------
DROP TABLE IF EXISTS `alliance_chat_messages`;
CREATE TABLE `alliance_chat_messages`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `alliance_id` int(0) NOT NULL COMMENT '联盟ID',
  `user_id` int(0) NOT NULL COMMENT '发送者ID',
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '消息内容',
  `created_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发送时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_alliance_id`(`alliance_id`) USING BTREE,
  INDEX `idx_created_at`(`created_at`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '联盟聊天记录' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for alliance_item_storage
-- ----------------------------
DROP TABLE IF EXISTS `alliance_item_storage`;
CREATE TABLE `alliance_item_storage`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `alliance_id` int(0) NOT NULL,
  `owner_user_id` int(0) NOT NULL,
  `item_id` int(0) NOT NULL,
  `quantity` int(0) NOT NULL DEFAULT 0,
  `stored_at` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_alliance_item_storage`(`alliance_id`) USING BTREE,
  INDEX `idx_owner_item`(`owner_user_id`, `item_id`) USING BTREE,
  CONSTRAINT `alliance_item_storage_ibfk_1` FOREIGN KEY (`alliance_id`) REFERENCES `alliances` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `alliance_item_storage_ibfk_2` FOREIGN KEY (`owner_user_id`) REFERENCES `player` (`user_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for alliance_land_battle
-- ----------------------------
DROP TABLE IF EXISTS `alliance_land_battle`;
CREATE TABLE `alliance_land_battle`  (
  `id` bigint(0) UNSIGNED NOT NULL AUTO_INCREMENT,
  `land_id` int(0) NOT NULL,
  `left_registration_id` bigint(0) UNSIGNED NOT NULL,
  `right_registration_id` bigint(0) UNSIGNED NOT NULL,
  `phase` tinyint(0) NOT NULL DEFAULT 0,
  `current_round` int(0) NOT NULL DEFAULT 0,
  `started_at` datetime(0) NULL DEFAULT NULL,
  `finished_at` datetime(0) NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_land_phase`(`land_id`, `phase`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for alliance_land_battle_duel
-- ----------------------------
DROP TABLE IF EXISTS `alliance_land_battle_duel`;
CREATE TABLE `alliance_land_battle_duel`  (
  `id` bigint(0) UNSIGNED NOT NULL AUTO_INCREMENT,
  `round_id` bigint(0) UNSIGNED NOT NULL,
  `attacker_signup_id` bigint(0) UNSIGNED NOT NULL,
  `defender_signup_id` bigint(0) UNSIGNED NOT NULL,
  `attacker_result` tinyint(0) NOT NULL,
  `log_json` json NOT NULL,
  `created_at` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_round`(`round_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for alliance_land_battle_round
-- ----------------------------
DROP TABLE IF EXISTS `alliance_land_battle_round`;
CREATE TABLE `alliance_land_battle_round`  (
  `id` bigint(0) UNSIGNED NOT NULL AUTO_INCREMENT,
  `battle_id` bigint(0) UNSIGNED NOT NULL,
  `round_no` int(0) NOT NULL,
  `left_alive` int(0) NOT NULL,
  `right_alive` int(0) NOT NULL,
  `status` tinyint(0) NOT NULL DEFAULT 0,
  `started_at` datetime(0) NULL DEFAULT NULL,
  `finished_at` datetime(0) NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_battle_round`(`battle_id`, `round_no`) USING BTREE,
  INDEX `idx_battle`(`battle_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for alliance_land_registration
-- ----------------------------
DROP TABLE IF EXISTS `alliance_land_registration`;
CREATE TABLE `alliance_land_registration`  (
  `id` bigint(0) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '报名记录ID',
  `land_id` int(0) NOT NULL COMMENT '土地ID',
  `alliance_id` int(0) NOT NULL COMMENT '联盟ID，关联 alliances.id',
  `army` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '报名军团（dragon/tiger）',
  `registration_time` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '报名时间',
  `cost` int(0) NOT NULL DEFAULT 0 COMMENT '报名消耗',
  `status` tinyint(0) NOT NULL DEFAULT 1 COMMENT '报名状态：1-已报名，2-待审核，3-已生效，0-已取消',
  `bye_waiting_round` int(0) NULL DEFAULT NULL,
  `last_bye_round` int(0) NULL DEFAULT NULL,
  `created_at` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_land_alliance`(`land_id`, `alliance_id`) USING BTREE,
  INDEX `idx_land_id`(`land_id`) USING BTREE,
  INDEX `idx_alliance_id`(`alliance_id`) USING BTREE,
  CONSTRAINT `fk_alliance_land_registration_alliance` FOREIGN KEY (`alliance_id`) REFERENCES `alliances` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '土地报名联盟关联表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for alliance_members
-- ----------------------------
DROP TABLE IF EXISTS `alliance_members`;
CREATE TABLE `alliance_members`  (
  `alliance_id` int(0) NOT NULL,
  `user_id` int(0) NOT NULL,
  `role` tinyint(0) NULL DEFAULT 0 COMMENT '1: 盟主, 0: 成员',
  `contribution` int(0) NULL DEFAULT 0,
  `army_type` tinyint(0) NOT NULL DEFAULT 0 COMMENT '0-未报名,1-飞龙军,2-伏虎军',
  `joined_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`) USING BTREE,
  INDEX `idx_alliance`(`alliance_id`) USING BTREE,
  INDEX `idx_alliance_members_army`(`alliance_id`, `army_type`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for alliance_talents
-- ----------------------------
DROP TABLE IF EXISTS `alliance_talents`;
CREATE TABLE `alliance_talents`  (
  `alliance_id` int(0) NOT NULL,
  `talent_key` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `research_level` int(0) NULL DEFAULT 1,
  PRIMARY KEY (`alliance_id`, `talent_key`) USING BTREE,
  CONSTRAINT `alliance_talents_ibfk_1` FOREIGN KEY (`alliance_id`) REFERENCES `alliances` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for alliance_training_participants
-- ----------------------------
DROP TABLE IF EXISTS `alliance_training_participants`;
CREATE TABLE `alliance_training_participants`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `room_id` int(0) NOT NULL,
  `user_id` int(0) NOT NULL,
  `joined_at` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `claimed_at` datetime(0) NULL DEFAULT NULL,
  `reward_amount` int(0) NULL DEFAULT 0,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_room_user`(`room_id`, `user_id`) USING BTREE,
  INDEX `idx_user_joined`(`user_id`, `joined_at`) USING BTREE,
  CONSTRAINT `alliance_training_participants_ibfk_1` FOREIGN KEY (`room_id`) REFERENCES `alliance_training_rooms` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `alliance_training_participants_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `player` (`user_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for alliance_training_rooms
-- ----------------------------
DROP TABLE IF EXISTS `alliance_training_rooms`;
CREATE TABLE `alliance_training_rooms`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `alliance_id` int(0) NOT NULL,
  `creator_user_id` int(0) NOT NULL,
  `title` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `status` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'ongoing',
  `max_participants` tinyint(0) NOT NULL DEFAULT 4,
  `created_at` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `completed_at` datetime(0) NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_alliance_training`(`alliance_id`) USING BTREE,
  INDEX `creator_user_id`(`creator_user_id`) USING BTREE,
  CONSTRAINT `alliance_training_rooms_ibfk_1` FOREIGN KEY (`alliance_id`) REFERENCES `alliances` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `alliance_training_rooms_ibfk_2` FOREIGN KEY (`creator_user_id`) REFERENCES `player` (`user_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for alliance_war_honor_effects
-- ----------------------------
DROP TABLE IF EXISTS `alliance_war_honor_effects`;
CREATE TABLE `alliance_war_honor_effects`  (
  `id` bigint(0) UNSIGNED NOT NULL AUTO_INCREMENT,
  `alliance_id` int(0) NOT NULL,
  `effect_key` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '配置 key',
  `effect_type` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'xp/fire 等类别',
  `cost` int(0) NOT NULL DEFAULT 0 COMMENT '兑换消耗战功',
  `started_at` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `expires_at` datetime(0) NOT NULL,
  `created_by` int(0) NOT NULL COMMENT '发起兑换的 user_id',
  `created_at` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_alliance_effect`(`alliance_id`, `effect_key`) USING BTREE,
  INDEX `idx_effect_expiration`(`alliance_id`, `effect_type`, `expires_at`) USING BTREE,
  CONSTRAINT `fk_honor_effects_alliance` FOREIGN KEY (`alliance_id`) REFERENCES `alliances` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '联盟战功兑换效果记录，约定持续 24 小时' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for alliances
-- ----------------------------
DROP TABLE IF EXISTS `alliances`;
CREATE TABLE `alliances`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `leader_id` int(0) NOT NULL,
  `level` int(0) NULL DEFAULT 1,
  `exp` int(0) NULL DEFAULT 0,
  `notice` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `created_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP,
  `funds` int(0) NULL DEFAULT 0,
  `crystals` int(0) NULL DEFAULT 0,
  `prosperity` int(0) NULL DEFAULT 0,
  `war_honor` int(0) NULL DEFAULT 0 COMMENT '当前联盟战功',
  `war_honor_history` int(0) NULL DEFAULT 0 COMMENT '历史累计战功',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `name`(`name`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for arena
-- ----------------------------
DROP TABLE IF EXISTS `arena`;
CREATE TABLE `arena`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `rank_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '等级阶段名称（黄阶/玄阶/地阶/天阶/飞马/天龙/战神）',
  `arena_type` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '场次类型（normal普通场/gold黄金场）',
  `champion_user_id` int(0) NULL DEFAULT NULL COMMENT '当前擂主用户ID，NULL表示空置',
  `champion_nickname` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '擂主昵称',
  `consecutive_wins` int(0) NOT NULL DEFAULT 0 COMMENT '连胜场次',
  `prize_pool` int(0) NOT NULL DEFAULT 0 COMMENT '奖池球数',
  `last_battle_time` datetime(0) NULL DEFAULT NULL COMMENT '最后战斗时间',
  `created_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_rank_type`(`rank_name`, `arena_type`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 99 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '擂台表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for arena_battle_log
-- ----------------------------
DROP TABLE IF EXISTS `arena_battle_log`;
CREATE TABLE `arena_battle_log`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `arena_type` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '场次类型（normal普通场/gold黄金场）',
  `rank_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '等级阶段名称（黄阶/玄阶/地阶/天阶/飞马/天龙/战神）',
  `challenger_id` int(0) NOT NULL COMMENT '挑战者ID',
  `challenger_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '挑战者昵称',
  `champion_id` int(0) NOT NULL COMMENT '擂主ID',
  `champion_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '擂主昵称',
  `is_challenger_win` tinyint(0) NOT NULL DEFAULT 0 COMMENT '是否挑战成功(1=成功,0=失败)',
  `battle_data` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '战斗详情(JSON)',
  `created_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_challenger`(`challenger_id`) USING BTREE,
  INDEX `idx_champion`(`champion_id`) USING BTREE,
  INDEX `idx_created`(`created_at`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '擂台挑战战斗记录表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for arena_daily_challenge
-- ----------------------------
DROP TABLE IF EXISTS `arena_daily_challenge`;
CREATE TABLE `arena_daily_challenge`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `user_id` int(0) NOT NULL,
  `challenge_date` date NOT NULL,
  `challenge_count` int(0) NOT NULL DEFAULT 0,
  `created_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_user_date`(`user_id`, `challenge_date`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 9 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '擂台每日挑战次数' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for arena_stats
-- ----------------------------
DROP TABLE IF EXISTS `arena_stats`;
CREATE TABLE `arena_stats`  (
  `user_id` int(0) NOT NULL,
  `rank_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '等级阶段名称',
  `success_count` int(0) NOT NULL DEFAULT 0 COMMENT '守擂成功次数（达成10连胜次数）',
  `updated_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`user_id`, `rank_name`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '擂台守擂统计表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for battlefield_battle_log
-- ----------------------------
DROP TABLE IF EXISTS `battlefield_battle_log`;
CREATE TABLE `battlefield_battle_log`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `battlefield_type` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '战场类型（tiger猛虎战场/crane飞鹤战场）',
  `period` int(0) NOT NULL COMMENT '战场期数',
  `round_num` int(0) NOT NULL COMMENT '第几轮',
  `match_num` int(0) NOT NULL COMMENT '本轮第几场',
  `first_user_id` int(0) NOT NULL COMMENT '前置玩家ID（用于昨日战况列表左侧）',
  `first_user_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '前置玩家昵称',
  `second_user_id` int(0) NOT NULL COMMENT '对手玩家ID',
  `second_user_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '对手玩家昵称',
  `first_user_team` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '前置玩家阵营（red/blue，可选）',
  `second_user_team` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '对手阵营（red/blue，可选）',
  `is_first_win` tinyint(0) NOT NULL DEFAULT 0 COMMENT '前置玩家是否获胜(1=胜,0=负)',
  `result_label` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '前置玩家结果描述（失败/小败/小胜/完美胜利等）',
  `battle_data` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '战斗详情(JSON，结构与镇妖/擂台战报一致)',
  `created_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_type_period`(`battlefield_type`, `period`) USING BTREE,
  INDEX `idx_type_period_round`(`battlefield_type`, `period`, `round_num`) USING BTREE,
  INDEX `idx_first_user`(`first_user_id`) USING BTREE,
  INDEX `idx_second_user`(`second_user_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 369 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '古战场战斗记录表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for battlefield_signup
-- ----------------------------
DROP TABLE IF EXISTS `battlefield_signup`;
CREATE TABLE `battlefield_signup`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `user_id` int(0) NOT NULL COMMENT '玩家ID',
  `battlefield_type` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '战场类型（tiger猛虎战场/crane飞鹤战场）',
  `signup_date` date NOT NULL COMMENT '报名日期',
  `signup_time` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '报名时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uniq_user_type_date`(`user_id`, `battlefield_type`, `signup_date`) USING BTREE,
  INDEX `idx_type_date`(`battlefield_type`, `signup_date`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 431 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '古战场报名表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for beast_bone
-- ----------------------------
DROP TABLE IF EXISTS `beast_bone`;
CREATE TABLE `beast_bone`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `user_id` int(0) NOT NULL COMMENT '玩家ID',
  `beast_id` int(0) NULL DEFAULT NULL COMMENT '装备到的幻兽ID（未装备时为NULL）',
  `template_id` int(0) NOT NULL COMMENT '战骨模板ID',
  `slot` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '槽位：头骨/胸骨/臂骨/手骨/腿骨/尾骨/元魂',
  `level` int(0) NOT NULL DEFAULT 1 COMMENT '等级',
  `stage` int(0) NOT NULL DEFAULT 1 COMMENT '阶段',
  `hp_flat` int(0) NOT NULL DEFAULT 0 COMMENT '气血加成（固定值）',
  `attack_flat` int(0) NOT NULL DEFAULT 0 COMMENT '攻击加成（固定值）',
  `physical_defense_flat` int(0) NOT NULL DEFAULT 0 COMMENT '物防加成（固定值）',
  `magic_defense_flat` int(0) NOT NULL DEFAULT 0 COMMENT '法防加成（固定值）',
  `speed_flat` int(0) NOT NULL DEFAULT 0 COMMENT '速度加成（固定值）',
  `created_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP(0) COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_user_id`(`user_id`) USING BTREE,
  INDEX `idx_beast_id`(`beast_id`) USING BTREE,
  INDEX `idx_user_beast`(`user_id`, `beast_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 149 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '玩家战骨表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for cultivation_config
-- ----------------------------
DROP TABLE IF EXISTS `cultivation_config`;
CREATE TABLE `cultivation_config`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `duration_hours` int(0) NOT NULL COMMENT '修行时长(小时)',
  `prestige_reward` int(0) NOT NULL COMMENT '声望奖励',
  `gold_cost` int(0) NULL DEFAULT 0 COMMENT '金币消耗',
  `description` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '描述',
  `created_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 226 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '修行配置表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for king_challenge_rank
-- ----------------------------
DROP TABLE IF EXISTS `king_challenge_rank`;
CREATE TABLE `king_challenge_rank`  (
  `user_id` int(0) NOT NULL,
  `area_index` int(0) NOT NULL DEFAULT 1 COMMENT '赛区编号（1=一赛区，2=二赛区）',
  `rank_position` int(0) NOT NULL COMMENT '在赛区内的排名（1起）',
  `win_streak` int(0) NOT NULL DEFAULT 0 COMMENT '连胜场次',
  `total_wins` int(0) NOT NULL DEFAULT 0 COMMENT '总胜场',
  `total_losses` int(0) NOT NULL DEFAULT 0 COMMENT '总负场',
  `today_challenges` int(0) NOT NULL DEFAULT 0 COMMENT '今日挑战次数',
  `last_challenge_date` date NULL DEFAULT NULL COMMENT '上次挑战日期',
  `updated_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`user_id`) USING BTREE,
  INDEX `idx_area_rank`(`area_index`, `rank_position`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '召唤之王挑战赛排名表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for king_reward_claimed
-- ----------------------------
DROP TABLE IF EXISTS `king_reward_claimed`;
CREATE TABLE `king_reward_claimed`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `user_id` int(0) NOT NULL,
  `season` int(0) NOT NULL DEFAULT 1 COMMENT '赛季编号',
  `reward_tier` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '奖励档位（冠军/亚军/四强等）',
  `claimed_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_user_season`(`user_id`, `season`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '召唤之王奖励领取记录' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for level_config
-- ----------------------------
DROP TABLE IF EXISTS `level_config`;
CREATE TABLE `level_config`  (
  `level` int(0) NOT NULL COMMENT '等级',
  `prestige_required` int(0) NOT NULL COMMENT '晋级所需声望',
  `rank_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '阶位名称',
  `created_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`level`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '等级配置表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for manor_land
-- ----------------------------
DROP TABLE IF EXISTS `manor_land`;
CREATE TABLE `manor_land`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `user_id` int(0) NOT NULL,
  `land_index` int(0) NOT NULL COMMENT '0-9:普通土地, 10:黄土地, 11:银土地, 12:金土地',
  `status` tinyint(0) NOT NULL DEFAULT 0 COMMENT '0:未开启, 1:空闲, 2:种植中',
  `tree_type` int(0) NULL DEFAULT 0 COMMENT '种植的种类：1, 2, 4, 6, 8株',
  `plant_time` datetime(0) NULL DEFAULT NULL COMMENT '种植开始时间',
  `created_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_user_land`(`user_id`, `land_index`) USING BTREE,
  INDEX `idx_user_id`(`user_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 14 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '庄园土地表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for mosoul_global_pity
-- ----------------------------
DROP TABLE IF EXISTS `mosoul_global_pity`;
CREATE TABLE `mosoul_global_pity`  (
  `counter_key` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `count` int(0) NOT NULL DEFAULT 0,
  `pity_threshold` int(0) NOT NULL DEFAULT 0,
  `soul_charm_consumed_global` int(0) NOT NULL DEFAULT 0,
  `created_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP(0),
  `copper_consumed_global` bigint(0) UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`counter_key`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for mosoul_hunting_state
-- ----------------------------
DROP TABLE IF EXISTS `mosoul_hunting_state`;
CREATE TABLE `mosoul_hunting_state`  (
  `user_id` int(0) NOT NULL,
  `field_type` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'normal',
  `normal_available_npcs` json NOT NULL,
  `advanced_available_npcs` json NOT NULL,
  `soul_charm_consumed` int(0) NOT NULL DEFAULT 0,
  `copper_consumed` int(0) NOT NULL DEFAULT 0,
  `created_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`user_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for player
-- ----------------------------
DROP TABLE IF EXISTS `player`;
CREATE TABLE `player`  (
  `user_id` int(0) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '账号',
  `password` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '密码',
  `nickname` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '昵称',
  `level` int(0) NOT NULL DEFAULT 1 COMMENT '玩家等级(1-100)',
  `exp` int(0) NOT NULL DEFAULT 0 COMMENT '当前经验值',
  `gold` int(0) NOT NULL DEFAULT 0 COMMENT '金币',
  `yuanbao` int(0) NOT NULL DEFAULT 0 COMMENT '元宝',
  `silver_diamond` int(0) NOT NULL DEFAULT 0 COMMENT '宝石',
  `dice` int(0) NOT NULL DEFAULT 0 COMMENT '骰子数量',
  `created_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP(0),
  `prestige` int(0) NOT NULL DEFAULT 0 COMMENT '当前声望',
  `cultivation_start` datetime(0) NULL DEFAULT NULL COMMENT '修行开始时间',
  `cultivation_duration` int(0) NULL DEFAULT 0 COMMENT '修行时长(秒)',
  `cultivation_reward` int(0) NULL DEFAULT 0 COMMENT '修行预计奖励声望',
  `location` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '落龙镇',
  `last_map_move_at` datetime(0) NULL DEFAULT NULL,
  `moving_to` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `is_summon_king` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否是召唤之王（1=是）',
  `enhancement_stone` int(0) NOT NULL DEFAULT 0 COMMENT 'enhancement stone',
  `vip_level` int(0) NULL DEFAULT 0,
  `vip_exp` int(0) NULL DEFAULT 0,
  `crystal_tower` int(0) NULL DEFAULT 0 COMMENT '水晶塔活力值',
  `charm` int(0) NULL DEFAULT 0 COMMENT '魅力值',
  `energy` int(0) NULL DEFAULT 100 COMMENT '活力值',
  `last_energy_recovery_time` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上次体力恢复时间',
  `cultivation_start_time` datetime(0) NULL DEFAULT NULL,
  `cultivation_area` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `cultivation_dungeon` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `last_dice_grant_date` date NULL DEFAULT NULL,
  `inspire_expire_time` datetime(0) NULL DEFAULT NULL,
  `first_recharge_claimed` tinyint(0) NULL DEFAULT 0 COMMENT '首充是否已领取',
  PRIMARY KEY (`user_id`) USING BTREE,
  UNIQUE INDEX `uk_username`(`username`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4053 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '玩家基础信息表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for player_bag
-- ----------------------------
DROP TABLE IF EXISTS `player_bag`;
CREATE TABLE `player_bag`  (
  `user_id` int(0) NOT NULL,
  `bag_level` int(0) NOT NULL DEFAULT 1 COMMENT '背包等级 1-10',
  `capacity` int(0) NOT NULL DEFAULT 50 COMMENT '背包容量（格子数）',
  `created_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`user_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '玩家背包信息表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for player_beast
-- ----------------------------
DROP TABLE IF EXISTS `player_beast`;
CREATE TABLE `player_beast`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `user_id` int(0) NOT NULL,
  `template_id` int(0) NOT NULL DEFAULT 0,
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '幻兽名称',
  `nickname` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '幻兽昵称（可自定义）',
  `realm` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '境界(神界/天界等)',
  `race` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '种族(虫族/龙族等)',
  `level` int(0) NOT NULL DEFAULT 1 COMMENT '等级',
  `exp` int(0) NOT NULL DEFAULT 0 COMMENT '当前经验',
  `nature` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '物系' COMMENT '特性(法系普攻/物系普攻等)',
  `personality` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '性格',
  `hp` int(0) NOT NULL COMMENT '气血',
  `physical_attack` int(0) NOT NULL COMMENT '物攻',
  `magic_attack` int(0) NOT NULL COMMENT '法攻',
  `physical_defense` int(0) NOT NULL COMMENT '物防',
  `magic_defense` int(0) NOT NULL COMMENT '法防',
  `speed` int(0) NOT NULL COMMENT '速度',
  `combat_power` int(0) NULL DEFAULT 0 COMMENT '综合战力',
  `growth_rate` int(0) NULL DEFAULT 0 COMMENT '成长率',
  `hp_aptitude` int(0) NULL DEFAULT 0 COMMENT '气血资质',
  `speed_aptitude` int(0) NULL DEFAULT 0 COMMENT '速度资质',
  `physical_attack_aptitude` int(0) NULL DEFAULT 0 COMMENT '物攻资质',
  `magic_attack_aptitude` int(0) NULL DEFAULT 0 COMMENT '法攻资质',
  `physical_defense_aptitude` int(0) NULL DEFAULT 0 COMMENT '物防资质',
  `magic_defense_aptitude` int(0) NULL DEFAULT 0 COMMENT '法防资质',
  `lifespan` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '10000/10000' COMMENT '寿命',
  `skills` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '技能列表(JSON格式)',
  `counters` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '克制',
  `countered_by` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '被克',
  `attack_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'physical' COMMENT '攻击类型（physical/magic）',
  `is_in_team` tinyint(1) NULL DEFAULT 0 COMMENT '是否在战斗队',
  `team_position` int(0) NULL DEFAULT 0 COMMENT '战斗队位置',
  `created_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_user_team`(`user_id`, `is_in_team`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 747 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '玩家幻兽表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for player_daily_activity
-- ----------------------------
DROP TABLE IF EXISTS `player_daily_activity`;
CREATE TABLE `player_daily_activity`  (
  `user_id` int(0) NOT NULL,
  `activity_value` int(0) NULL DEFAULT 0,
  `last_updated_date` date NULL DEFAULT NULL,
  `completed_tasks` json NULL,
  PRIMARY KEY (`user_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for player_dungeon_progress
-- ----------------------------
DROP TABLE IF EXISTS `player_dungeon_progress`;
CREATE TABLE `player_dungeon_progress`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `user_id` int(0) NOT NULL,
  `dungeon_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `current_floor` int(0) NULL DEFAULT 1,
  `total_floors` int(0) NULL DEFAULT 35,
  `created_at` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP(0),
  `floor_cleared` tinyint(1) NULL DEFAULT 1,
  `floor_event_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT 'beast',
  `loot_claimed` tinyint(1) NULL DEFAULT 1,
  `resets_today` int(0) NULL DEFAULT 0,
  `last_reset_date` date NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_user_dungeon`(`user_id`, `dungeon_name`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 113 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for player_effect
-- ----------------------------
DROP TABLE IF EXISTS `player_effect`;
CREATE TABLE `player_effect`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `user_id` int(0) NOT NULL,
  `effect_key` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `end_time` datetime(0) NOT NULL,
  `created_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_user_effect`(`user_id`, `effect_key`) USING BTREE,
  INDEX `idx_end_time`(`end_time`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for player_gift_claim
-- ----------------------------
DROP TABLE IF EXISTS `player_gift_claim`;
CREATE TABLE `player_gift_claim`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `user_id` int(0) NOT NULL,
  `gift_key` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `claimed_at` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_user_gift`(`user_id`, `gift_key`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for player_immortalize_pool
-- ----------------------------
DROP TABLE IF EXISTS `player_immortalize_pool`;
CREATE TABLE `player_immortalize_pool`  (
  `user_id` int(0) NOT NULL COMMENT '玩家ID',
  `pool_level` tinyint(0) NOT NULL DEFAULT 1 COMMENT '化仙池等级',
  `current_exp` bigint(0) NOT NULL DEFAULT 0 COMMENT '化仙池当前可用经验',
  `formation_level` tinyint(0) NOT NULL DEFAULT 0 COMMENT '化仙阵等级',
  `formation_started_at` datetime(0) NULL DEFAULT NULL COMMENT '化仙阵开始时间',
  `formation_ends_at` datetime(0) NULL DEFAULT NULL COMMENT '化仙阵结束时间',
  `formation_last_grant_at` datetime(0) NULL DEFAULT NULL COMMENT '化仙阵最近一次结算时间',
  `created_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`user_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '玩家化仙池状态' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for player_inventory
-- ----------------------------
DROP TABLE IF EXISTS `player_inventory`;
CREATE TABLE `player_inventory`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `user_id` int(0) NOT NULL,
  `item_id` int(0) NOT NULL COMMENT '物品ID',
  `quantity` int(0) NOT NULL DEFAULT 1 COMMENT '数量',
  `is_temporary` tinyint(0) NOT NULL DEFAULT 0 COMMENT '是否临时存放（0=正式，1=临时）',
  `created_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_user_item_temp`(`user_id`, `item_id`, `is_temporary`) USING BTREE,
  INDEX `idx_user_id`(`user_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2543 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '玩家背包表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for player_manor
-- ----------------------------
DROP TABLE IF EXISTS `player_manor`;
CREATE TABLE `player_manor`  (
  `user_id` int(0) NOT NULL,
  `total_harvest_count` int(0) NULL DEFAULT 0 COMMENT '累计收获次数',
  `total_gold_earned` bigint(0) NULL DEFAULT 0 COMMENT '累计获得铜钱',
  `created_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`user_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '玩家庄园扩展表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for player_month_card
-- ----------------------------
DROP TABLE IF EXISTS `player_month_card`;
CREATE TABLE `player_month_card`  (
  `id` bigint(0) UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` bigint(0) UNSIGNED NOT NULL,
  `month` tinyint(0) UNSIGNED NOT NULL,
  `start_date` datetime(0) NOT NULL,
  `end_date` datetime(0) NOT NULL,
  `days_total` smallint(0) UNSIGNED NOT NULL DEFAULT 30,
  `days_claimed` smallint(0) UNSIGNED NOT NULL DEFAULT 0,
  `last_claim_date` date NULL DEFAULT NULL,
  `status` enum('pending','active','expired') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'active',
  `initial_reward` int(0) NOT NULL DEFAULT 1000,
  `daily_reward` int(0) NOT NULL DEFAULT 200,
  `initial_reward_claimed` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uniq_user_month`(`user_id`, `month`) USING BTREE,
  INDEX `idx_user_status`(`user_id`, `status`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 12 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for player_mosoul
-- ----------------------------
DROP TABLE IF EXISTS `player_mosoul`;
CREATE TABLE `player_mosoul`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `user_id` int(0) NOT NULL,
  `template_id` int(0) NOT NULL,
  `level` int(0) NOT NULL DEFAULT 1,
  `exp` int(0) NOT NULL DEFAULT 0,
  `beast_id` int(0) NULL DEFAULT NULL,
  `slot_index` tinyint(0) UNSIGNED NULL DEFAULT NULL COMMENT '槽位索引（1-8）',
  `created_at` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_beast_slot`(`beast_id`, `slot_index`) USING BTREE,
  INDEX `idx_user_id`(`user_id`) USING BTREE,
  INDEX `idx_beast_id`(`beast_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 596 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for player_spirit
-- ----------------------------
DROP TABLE IF EXISTS `player_spirit`;
CREATE TABLE `player_spirit`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `user_id` int(0) NOT NULL COMMENT '玩家ID',
  `beast_id` int(0) NULL DEFAULT NULL COMMENT '装备到的幻兽ID（未装备时为NULL）',
  `element` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '元素：earth/fire/water/wood/metal/god',
  `race` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '种族：兽族/龙族/虫族/飞禽/神兽等',
  `line1_attr` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `line1_value_bp` int(0) NOT NULL DEFAULT 0,
  `line1_unlocked` tinyint(0) NOT NULL DEFAULT 0,
  `line1_locked` tinyint(0) NOT NULL DEFAULT 0,
  `line2_attr` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `line2_value_bp` int(0) NOT NULL DEFAULT 0,
  `line2_unlocked` tinyint(0) NOT NULL DEFAULT 0,
  `line2_locked` tinyint(0) NOT NULL DEFAULT 0,
  `line3_attr` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `line3_value_bp` int(0) NOT NULL DEFAULT 0,
  `line3_unlocked` tinyint(0) NOT NULL DEFAULT 0,
  `line3_locked` tinyint(0) NOT NULL DEFAULT 0,
  `created_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_user_id`(`user_id`) USING BTREE,
  INDEX `idx_beast_id`(`beast_id`) USING BTREE,
  INDEX `idx_user_beast`(`user_id`, `beast_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 172 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '玩家战灵' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for player_talent_levels
-- ----------------------------
DROP TABLE IF EXISTS `player_talent_levels`;
CREATE TABLE `player_talent_levels`  (
  `user_id` int(0) NOT NULL,
  `talent_key` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `level` int(0) NULL DEFAULT 0,
  PRIMARY KEY (`user_id`, `talent_key`) USING BTREE,
  CONSTRAINT `player_talent_levels_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `player` (`user_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for refine_pot_log
-- ----------------------------
DROP TABLE IF EXISTS `refine_pot_log`;
CREATE TABLE `refine_pot_log`  (
  `id` bigint(0) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '记录ID',
  `user_id` bigint(0) UNSIGNED NOT NULL COMMENT '玩家ID',
  `main_beast_id` bigint(0) UNSIGNED NOT NULL COMMENT '主幻兽ID',
  `material_beast_id` bigint(0) UNSIGNED NOT NULL COMMENT '副幻兽ID',
  `attr_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性类型',
  `before_value` int(0) NOT NULL COMMENT '炼妖前属性值',
  `after_value` int(0) NOT NULL COMMENT '炼妖后属性值',
  `delta` int(0) NOT NULL COMMENT '属性变化值',
  `diff_x` int(0) NOT NULL COMMENT '属性差值',
  `cost_gold` int(0) UNSIGNED NOT NULL DEFAULT 0 COMMENT '消耗铜钱',
  `cost_pill` int(0) UNSIGNED NOT NULL DEFAULT 0 COMMENT '消耗炼魂丹',
  `created_at` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_user_id`(`user_id`) USING BTREE,
  INDEX `idx_main_beast_id`(`main_beast_id`) USING BTREE,
  INDEX `idx_created_at`(`created_at`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '炼妖日志表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for spirit_account
-- ----------------------------
DROP TABLE IF EXISTS `spirit_account`;
CREATE TABLE `spirit_account`  (
  `user_id` int(0) NOT NULL,
  `spirit_power` int(0) NOT NULL DEFAULT 0 COMMENT '灵力',
  `unlocked_elements` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '已解锁元素列表(JSON)',
  `free_refine_date` date NULL DEFAULT NULL COMMENT '当日免费洗练计数对应日期',
  `free_refine_used` int(0) NOT NULL DEFAULT 0 COMMENT '当日已使用免费洗练次数',
  `created_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`user_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '战灵账户' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for task_reward_claims
-- ----------------------------
DROP TABLE IF EXISTS `task_reward_claims`;
CREATE TABLE `task_reward_claims`  (
  `id` int(0) UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` int(0) UNSIGNED NOT NULL,
  `reward_key` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `claimed_at` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uniq_user_reward`(`user_id`, `reward_key`) USING BTREE,
  INDEX `idx_reward_key`(`reward_key`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 9 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '任务奖励领取记录' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for tower_state
-- ----------------------------
DROP TABLE IF EXISTS `tower_state`;
CREATE TABLE `tower_state`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `user_id` int(0) NOT NULL,
  `tower_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'tongtian',
  `current_floor` int(0) NOT NULL DEFAULT 1,
  `max_floor_record` int(0) NOT NULL DEFAULT 1,
  `today_count` int(0) NOT NULL DEFAULT 0,
  `last_challenge_date` date NULL DEFAULT NULL,
  `created_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_user_tower`(`user_id`, `tower_type`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 371 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '闯塔状态表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for zhenyao_battle_log
-- ----------------------------
DROP TABLE IF EXISTS `zhenyao_battle_log`;
CREATE TABLE `zhenyao_battle_log`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `floor` int(0) NOT NULL COMMENT '层数',
  `attacker_id` int(0) NOT NULL COMMENT '挑战者ID',
  `attacker_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '挑战者昵称',
  `defender_id` int(0) NOT NULL COMMENT '被挑战者ID',
  `defender_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '被挑战者昵称',
  `is_success` tinyint(0) NOT NULL DEFAULT 0 COMMENT '是否成功(1=成功,0=失败)',
  `remaining_seconds` int(0) NOT NULL DEFAULT 0 COMMENT '剩余秒数(挑战时)',
  `battle_data` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '战斗详情(JSON)',
  `created_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_floor`(`floor`) USING BTREE,
  INDEX `idx_attacker`(`attacker_id`) USING BTREE,
  INDEX `idx_defender`(`defender_id`) USING BTREE,
  INDEX `idx_created`(`created_at`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 67 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '镇妖挑战记录表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for zhenyao_daily_count
-- ----------------------------
DROP TABLE IF EXISTS `zhenyao_daily_count`;
CREATE TABLE `zhenyao_daily_count`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `user_id` int(0) NOT NULL,
  `trial_count` int(0) NOT NULL DEFAULT 0 COMMENT '试炼层已用次数',
  `hell_count` int(0) NOT NULL DEFAULT 0 COMMENT '炼狱层已用次数',
  `count_date` date NOT NULL COMMENT '统计日期',
  `created_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_user_date`(`user_id`, `count_date`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 15 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '镇妖每日次数表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for zhenyao_floor
-- ----------------------------
DROP TABLE IF EXISTS `zhenyao_floor`;
CREATE TABLE `zhenyao_floor`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `floor` int(0) NOT NULL COMMENT '层数(1-120)',
  `occupant_id` int(0) NULL DEFAULT NULL COMMENT '占领者ID',
  `occupant_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '占领者昵称',
  `occupy_time` datetime(0) NULL DEFAULT NULL COMMENT '占领时间',
  `expire_time` datetime(0) NULL DEFAULT NULL COMMENT '到期时间',
  `created_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP(0),
  `rewarded` tinyint(1) NULL DEFAULT 0,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_floor`(`floor`) USING BTREE,
  INDEX `idx_occupant`(`occupant_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 481 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '镇妖占领表' ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;


-- ----------------------------
-- Table structure for recharge_order
-- ----------------------------
DROP TABLE IF EXISTS `recharge_order`;
CREATE TABLE `recharge_order`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `out_trade_no` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '商户订单号',
  `trade_no` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '支付宝交易号',
  `user_id` int(0) NOT NULL COMMENT '用户ID',
  `product_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '商品ID',
  `amount` decimal(10, 2) NOT NULL COMMENT '支付金额(元)',
  `status` enum('pending','paid','failed','refunded') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT 'pending' COMMENT '订单状态',
  `yuanbao_granted` int(0) NULL DEFAULT 0 COMMENT '发放的宝石数量',
  `bonus_granted` int(0) NULL DEFAULT 0 COMMENT '首充奖励宝石',
  `created_at` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `paid_at` datetime(0) NULL DEFAULT NULL COMMENT '支付时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `out_trade_no`(`out_trade_no`) USING BTREE,
  INDEX `idx_user_id`(`user_id`) USING BTREE,
  INDEX `idx_status`(`status`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '充值订单表' ROW_FORMAT = Dynamic;
