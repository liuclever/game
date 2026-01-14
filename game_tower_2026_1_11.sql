/*
Navicat MySQL Data Transfer

Source Server         : 127.0.0.1_8.0
Source Server Version : 80027
Source Host           : localhost:7778
Source Database       : game_tower

Target Server Type    : MYSQL
Target Server Version : 80027
File Encoding         : 65001

Date: 2026-01-11 18:26:44
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for alliance_activities
-- ----------------------------
DROP TABLE IF EXISTS `alliance_activities`;
CREATE TABLE `alliance_activities` (
  `id` int NOT NULL AUTO_INCREMENT,
  `alliance_id` int NOT NULL,
  `event_type` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `actor_user_id` int DEFAULT NULL,
  `actor_name` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `target_user_id` int DEFAULT NULL,
  `target_name` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `item_name` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `item_quantity` int DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_alliance_activity` (`alliance_id`,`created_at`) USING BTREE,
  CONSTRAINT `alliance_activities_ibfk_1` FOREIGN KEY (`alliance_id`) REFERENCES `alliances` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Records of alliance_activities
-- ----------------------------

-- ----------------------------
-- Table structure for alliance_army_assignments
-- ----------------------------
DROP TABLE IF EXISTS `alliance_army_assignments`;
CREATE TABLE `alliance_army_assignments` (
  `alliance_id` int NOT NULL,
  `user_id` int NOT NULL,
  `army` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `signed_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`alliance_id`,`user_id`) USING BTREE,
  KEY `idx_alliance_id` (`alliance_id`) USING BTREE,
  KEY `idx_user_id` (`user_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Records of alliance_army_assignments
-- ----------------------------

-- ----------------------------
-- Table structure for alliance_army_signups
-- ----------------------------
DROP TABLE IF EXISTS `alliance_army_signups`;
CREATE TABLE `alliance_army_signups` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `registration_id` bigint unsigned NOT NULL,
  `alliance_id` int NOT NULL,
  `army` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` bigint NOT NULL,
  `signup_order` int NOT NULL,
  `hp_state` json DEFAULT NULL,
  `status` tinyint NOT NULL DEFAULT '1',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_registration_user` (`registration_id`,`user_id`) USING BTREE,
  KEY `idx_registration_order` (`registration_id`,`signup_order`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Records of alliance_army_signups
-- ----------------------------

-- ----------------------------
-- Table structure for alliance_beast_storage
-- ----------------------------
DROP TABLE IF EXISTS `alliance_beast_storage`;
CREATE TABLE `alliance_beast_storage` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `alliance_id` int NOT NULL COMMENT '联盟ID',
  `owner_user_id` int NOT NULL COMMENT '寄存者用户ID',
  `beast_id` int NOT NULL COMMENT '幻兽ID',
  `stored_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '寄存时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uniq_beast` (`beast_id`) USING BTREE,
  KEY `idx_alliance` (`alliance_id`) USING BTREE,
  KEY `idx_owner` (`owner_user_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='联盟幻兽室寄存记录';

-- ----------------------------
-- Records of alliance_beast_storage
-- ----------------------------

-- ----------------------------
-- Table structure for alliance_buildings
-- ----------------------------
DROP TABLE IF EXISTS `alliance_buildings`;
CREATE TABLE `alliance_buildings` (
  `alliance_id` int NOT NULL,
  `building_key` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `level` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`alliance_id`,`building_key`) USING BTREE,
  CONSTRAINT `alliance_buildings_ibfk_1` FOREIGN KEY (`alliance_id`) REFERENCES `alliances` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Records of alliance_buildings
-- ----------------------------

-- ----------------------------
-- Table structure for alliance_chat_messages
-- ----------------------------
DROP TABLE IF EXISTS `alliance_chat_messages`;
CREATE TABLE `alliance_chat_messages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `alliance_id` int NOT NULL COMMENT '联盟ID',
  `user_id` int NOT NULL COMMENT '发送者ID',
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '消息内容',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '发送时间',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_alliance_id` (`alliance_id`) USING BTREE,
  KEY `idx_created_at` (`created_at`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='联盟聊天记录';

-- ----------------------------
-- Records of alliance_chat_messages
-- ----------------------------

-- ----------------------------
-- Table structure for alliance_item_storage
-- ----------------------------
DROP TABLE IF EXISTS `alliance_item_storage`;
CREATE TABLE `alliance_item_storage` (
  `id` int NOT NULL AUTO_INCREMENT,
  `alliance_id` int NOT NULL,
  `owner_user_id` int NOT NULL,
  `item_id` int NOT NULL,
  `quantity` int NOT NULL DEFAULT '0',
  `stored_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_alliance_item_storage` (`alliance_id`) USING BTREE,
  KEY `idx_owner_item` (`owner_user_id`,`item_id`) USING BTREE,
  CONSTRAINT `alliance_item_storage_ibfk_1` FOREIGN KEY (`alliance_id`) REFERENCES `alliances` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `alliance_item_storage_ibfk_2` FOREIGN KEY (`owner_user_id`) REFERENCES `player` (`user_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Records of alliance_item_storage
-- ----------------------------

-- ----------------------------
-- Table structure for alliance_land_battle
-- ----------------------------
DROP TABLE IF EXISTS `alliance_land_battle`;
CREATE TABLE `alliance_land_battle` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `land_id` int NOT NULL,
  `left_registration_id` bigint unsigned NOT NULL,
  `right_registration_id` bigint unsigned NOT NULL,
  `phase` tinyint NOT NULL DEFAULT '0',
  `current_round` int NOT NULL DEFAULT '0',
  `started_at` datetime DEFAULT NULL,
  `finished_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_land_phase` (`land_id`,`phase`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Records of alliance_land_battle
-- ----------------------------

-- ----------------------------
-- Table structure for alliance_land_battle_duel
-- ----------------------------
DROP TABLE IF EXISTS `alliance_land_battle_duel`;
CREATE TABLE `alliance_land_battle_duel` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `round_id` bigint unsigned NOT NULL,
  `attacker_signup_id` bigint unsigned NOT NULL,
  `defender_signup_id` bigint unsigned NOT NULL,
  `attacker_result` tinyint NOT NULL,
  `log_json` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_round` (`round_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Records of alliance_land_battle_duel
-- ----------------------------

-- ----------------------------
-- Table structure for alliance_land_battle_round
-- ----------------------------
DROP TABLE IF EXISTS `alliance_land_battle_round`;
CREATE TABLE `alliance_land_battle_round` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `battle_id` bigint unsigned NOT NULL,
  `round_no` int NOT NULL,
  `left_alive` int NOT NULL,
  `right_alive` int NOT NULL,
  `status` tinyint NOT NULL DEFAULT '0',
  `started_at` datetime DEFAULT NULL,
  `finished_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_battle_round` (`battle_id`,`round_no`) USING BTREE,
  KEY `idx_battle` (`battle_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Records of alliance_land_battle_round
-- ----------------------------

-- ----------------------------
-- Table structure for alliance_land_registration
-- ----------------------------
DROP TABLE IF EXISTS `alliance_land_registration`;
CREATE TABLE `alliance_land_registration` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT '报名记录ID',
  `land_id` int NOT NULL COMMENT '土地ID',
  `alliance_id` int NOT NULL COMMENT '联盟ID，关联 alliances.id',
  `army` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '报名军团（dragon/tiger）',
  `registration_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '报名时间',
  `cost` int NOT NULL DEFAULT '0' COMMENT '报名消耗',
  `status` tinyint NOT NULL DEFAULT '1' COMMENT '报名状态：1-已报名，2-待审核，3-已生效，0-已取消',
  `bye_waiting_round` int DEFAULT NULL,
  `last_bye_round` int DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_land_alliance` (`land_id`,`alliance_id`) USING BTREE,
  KEY `idx_land_id` (`land_id`) USING BTREE,
  KEY `idx_alliance_id` (`alliance_id`) USING BTREE,
  CONSTRAINT `fk_alliance_land_registration_alliance` FOREIGN KEY (`alliance_id`) REFERENCES `alliances` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='土地报名联盟关联表';

-- ----------------------------
-- Records of alliance_land_registration
-- ----------------------------

-- ----------------------------
-- Table structure for alliance_members
-- ----------------------------
DROP TABLE IF EXISTS `alliance_members`;
CREATE TABLE `alliance_members` (
  `alliance_id` int NOT NULL,
  `user_id` int NOT NULL,
  `role` tinyint DEFAULT '0' COMMENT '1: 盟主, 0: 成员',
  `contribution` int DEFAULT '0',
  `army_type` tinyint NOT NULL DEFAULT '0' COMMENT '0-未报名,1-飞龙军,2-伏虎军',
  `joined_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`) USING BTREE,
  KEY `idx_alliance` (`alliance_id`) USING BTREE,
  KEY `idx_alliance_members_army` (`alliance_id`,`army_type`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Records of alliance_members
-- ----------------------------

-- ----------------------------
-- Table structure for alliance_talents
-- ----------------------------
DROP TABLE IF EXISTS `alliance_talents`;
CREATE TABLE `alliance_talents` (
  `alliance_id` int NOT NULL,
  `talent_key` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `research_level` int DEFAULT '1',
  PRIMARY KEY (`alliance_id`,`talent_key`) USING BTREE,
  CONSTRAINT `alliance_talents_ibfk_1` FOREIGN KEY (`alliance_id`) REFERENCES `alliances` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Records of alliance_talents
-- ----------------------------

-- ----------------------------
-- Table structure for alliance_training_participants
-- ----------------------------
DROP TABLE IF EXISTS `alliance_training_participants`;
CREATE TABLE `alliance_training_participants` (
  `id` int NOT NULL AUTO_INCREMENT,
  `room_id` int NOT NULL,
  `user_id` int NOT NULL,
  `joined_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `claimed_at` datetime DEFAULT NULL,
  `reward_amount` int DEFAULT '0',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_room_user` (`room_id`,`user_id`) USING BTREE,
  KEY `idx_user_joined` (`user_id`,`joined_at`) USING BTREE,
  CONSTRAINT `alliance_training_participants_ibfk_1` FOREIGN KEY (`room_id`) REFERENCES `alliance_training_rooms` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `alliance_training_participants_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `player` (`user_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Records of alliance_training_participants
-- ----------------------------

-- ----------------------------
-- Table structure for alliance_training_rooms
-- ----------------------------
DROP TABLE IF EXISTS `alliance_training_rooms`;
CREATE TABLE `alliance_training_rooms` (
  `id` int NOT NULL AUTO_INCREMENT,
  `alliance_id` int NOT NULL,
  `creator_user_id` int NOT NULL,
  `title` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `status` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'ongoing',
  `max_participants` tinyint NOT NULL DEFAULT '4',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `completed_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_alliance_training` (`alliance_id`) USING BTREE,
  KEY `creator_user_id` (`creator_user_id`) USING BTREE,
  CONSTRAINT `alliance_training_rooms_ibfk_1` FOREIGN KEY (`alliance_id`) REFERENCES `alliances` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `alliance_training_rooms_ibfk_2` FOREIGN KEY (`creator_user_id`) REFERENCES `player` (`user_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Records of alliance_training_rooms
-- ----------------------------

-- ----------------------------
-- Table structure for alliance_war_honor_effects
-- ----------------------------
DROP TABLE IF EXISTS `alliance_war_honor_effects`;
CREATE TABLE `alliance_war_honor_effects` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `alliance_id` int NOT NULL,
  `effect_key` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '配置 key',
  `effect_type` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'xp/fire 等类别',
  `cost` int NOT NULL DEFAULT '0' COMMENT '兑换消耗战功',
  `started_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `expires_at` datetime NOT NULL,
  `created_by` int NOT NULL COMMENT '发起兑换的 user_id',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_alliance_effect` (`alliance_id`,`effect_key`) USING BTREE,
  KEY `idx_effect_expiration` (`alliance_id`,`effect_type`,`expires_at`) USING BTREE,
  CONSTRAINT `fk_honor_effects_alliance` FOREIGN KEY (`alliance_id`) REFERENCES `alliances` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='联盟战功兑换效果记录，约定持续 24 小时';

-- ----------------------------
-- Records of alliance_war_honor_effects
-- ----------------------------

-- ----------------------------
-- Table structure for alliances
-- ----------------------------
DROP TABLE IF EXISTS `alliances`;
CREATE TABLE `alliances` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `leader_id` int NOT NULL,
  `level` int DEFAULT '1',
  `exp` int DEFAULT '0',
  `notice` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `funds` int DEFAULT '0',
  `crystals` int DEFAULT '0',
  `prosperity` int DEFAULT '0',
  `war_honor` int DEFAULT '0' COMMENT '当前联盟战功',
  `war_honor_history` int DEFAULT '0' COMMENT '历史累计战功',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `name` (`name`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Records of alliances
-- ----------------------------

-- ----------------------------
-- Table structure for arena
-- ----------------------------
DROP TABLE IF EXISTS `arena`;
CREATE TABLE `arena` (
  `id` int NOT NULL AUTO_INCREMENT,
  `rank_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '等级阶段名称（黄阶/玄阶/地阶/天阶/飞马/天龙/战神）',
  `arena_type` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '场次类型（normal普通场/gold黄金场）',
  `champion_user_id` int DEFAULT NULL COMMENT '当前擂主用户ID，NULL表示空置',
  `champion_nickname` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '擂主昵称',
  `consecutive_wins` int NOT NULL DEFAULT '0' COMMENT '连胜场次',
  `prize_pool` int NOT NULL DEFAULT '0' COMMENT '奖池球数',
  `last_battle_time` datetime DEFAULT NULL COMMENT '最后战斗时间',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_rank_type` (`rank_name`,`arena_type`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=127 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='擂台表';

-- ----------------------------
-- Records of arena
-- ----------------------------
INSERT INTO `arena` VALUES ('99', '黄阶', 'normal', '4053', '123', '5', '6', '2026-01-10 19:22:18', '2026-01-10 12:40:46', '2026-01-10 19:22:18');
INSERT INTO `arena` VALUES ('100', '黄阶', 'gold', null, null, '0', '0', null, '2026-01-10 12:40:46', '2026-01-10 12:40:46');
INSERT INTO `arena` VALUES ('101', '玄阶', 'normal', null, null, '0', '0', null, '2026-01-10 12:40:46', '2026-01-10 12:40:46');
INSERT INTO `arena` VALUES ('102', '玄阶', 'gold', null, null, '0', '0', null, '2026-01-10 12:40:46', '2026-01-10 12:40:46');
INSERT INTO `arena` VALUES ('103', '地阶', 'normal', null, null, '0', '0', null, '2026-01-10 12:40:46', '2026-01-10 12:40:46');
INSERT INTO `arena` VALUES ('104', '地阶', 'gold', null, null, '0', '0', null, '2026-01-10 12:40:46', '2026-01-10 12:40:46');
INSERT INTO `arena` VALUES ('105', '天阶', 'normal', null, null, '0', '0', null, '2026-01-10 12:40:46', '2026-01-10 12:40:46');
INSERT INTO `arena` VALUES ('106', '天阶', 'gold', null, null, '0', '0', null, '2026-01-10 12:40:46', '2026-01-10 12:40:46');
INSERT INTO `arena` VALUES ('107', '飞马', 'normal', null, null, '0', '0', null, '2026-01-10 12:40:46', '2026-01-10 12:40:46');
INSERT INTO `arena` VALUES ('108', '飞马', 'gold', null, null, '0', '0', null, '2026-01-10 12:40:46', '2026-01-10 12:40:46');
INSERT INTO `arena` VALUES ('109', '天龙', 'normal', null, null, '0', '0', null, '2026-01-10 12:40:46', '2026-01-10 12:40:46');
INSERT INTO `arena` VALUES ('110', '天龙', 'gold', null, null, '0', '0', null, '2026-01-10 12:40:46', '2026-01-10 12:40:46');
INSERT INTO `arena` VALUES ('111', '战神', 'normal', null, null, '0', '0', null, '2026-01-10 12:40:46', '2026-01-10 12:40:46');
INSERT INTO `arena` VALUES ('112', '战神', 'gold', null, null, '0', '0', null, '2026-01-10 12:40:46', '2026-01-10 12:40:46');

-- ----------------------------
-- Table structure for arena_battle_log
-- ----------------------------
DROP TABLE IF EXISTS `arena_battle_log`;
CREATE TABLE `arena_battle_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `arena_type` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '场次类型（normal普通场/gold黄金场）',
  `rank_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '等级阶段名称（黄阶/玄阶/地阶/天阶/飞马/天龙/战神）',
  `challenger_id` int NOT NULL COMMENT '挑战者ID',
  `challenger_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '挑战者昵称',
  `champion_id` int NOT NULL COMMENT '擂主ID',
  `champion_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '擂主昵称',
  `is_challenger_win` tinyint NOT NULL DEFAULT '0' COMMENT '是否挑战成功(1=成功,0=失败)',
  `battle_data` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '战斗详情(JSON)',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_challenger` (`challenger_id`) USING BTREE,
  KEY `idx_champion` (`champion_id`) USING BTREE,
  KEY `idx_created` (`created_at`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='擂台挑战战斗记录表';

-- ----------------------------
-- Records of arena_battle_log
-- ----------------------------
INSERT INTO `arena_battle_log` VALUES ('5', 'normal', '黄阶', '4055', '789', '4053', '123', '0', '{\"is_victory\": false, \"attacker_wins\": 0, \"defender_wins\": 1, \"battles\": []}', '2026-01-10 12:46:13');
INSERT INTO `arena_battle_log` VALUES ('6', 'normal', '黄阶', '4055', '789', '4053', '123', '0', '{\"is_victory\": false, \"attacker_wins\": 0, \"defender_wins\": 1, \"battles\": [{\"battle_num\": 1, \"attacker_beast\": \"\", \"defender_beast\": \"\", \"winner\": \"defender\", \"rounds\": [{\"round\": 1, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 15, \"d_hp\": 13}, {\"round\": 2, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 13, \"d_hp\": 14}, {\"round\": 3, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 14, \"d_hp\": 12}, {\"round\": 4, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 12, \"d_hp\": 13}, {\"round\": 5, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 13, \"d_hp\": 11}, {\"round\": 6, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 11, \"d_hp\": 12}, {\"round\": 7, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 12, \"d_hp\": 10}, {\"round\": 8, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 10, \"d_hp\": 11}, {\"round\": 9, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 11, \"d_hp\": 9}, {\"round\": 10, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 9, \"d_hp\": 10}, {\"round\": 11, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 10, \"d_hp\": 8}, {\"round\": 12, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 8, \"d_hp\": 9}, {\"round\": 13, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 9, \"d_hp\": 7}, {\"round\": 14, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 7, \"d_hp\": 8}, {\"round\": 15, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 8, \"d_hp\": 6}, {\"round\": 16, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 6, \"d_hp\": 7}, {\"round\": 17, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 7, \"d_hp\": 5}, {\"round\": 18, \"action\": \"『789』的血螳螂使用高级吸血攻击『123』的血螳螂，气血-1\", \"a_hp\": 5, \"d_hp\": 6}, {\"round\": 19, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 6, \"d_hp\": 4}, {\"round\": 20, \"action\": \"『789』的血螳螂使用高级吸血攻击『123』的血螳螂，气血-1\", \"a_hp\": 4, \"d_hp\": 5}, {\"round\": 21, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 5, \"d_hp\": 3}, {\"round\": 22, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 3, \"d_hp\": 4}, {\"round\": 23, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 4, \"d_hp\": 2}, {\"round\": 24, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 2, \"d_hp\": 3}, {\"round\": 25, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 3, \"d_hp\": 1}, {\"round\": 26, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 1, \"d_hp\": 2}, {\"round\": 27, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 2, \"d_hp\": 0}], \"result\": \"『123』的血螳螂获胜，剩余气血2\"}]}', '2026-01-10 13:45:18');
INSERT INTO `arena_battle_log` VALUES ('7', 'normal', '黄阶', '4055', '789', '4053', '123', '0', '{\"is_victory\": false, \"attacker_wins\": 0, \"defender_wins\": 1, \"battles\": [{\"battle_num\": 1, \"attacker_beast\": \"\", \"defender_beast\": \"\", \"winner\": \"defender\", \"rounds\": [{\"round\": 1, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 15, \"d_hp\": 13}, {\"round\": 2, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 13, \"d_hp\": 14}, {\"round\": 3, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 14, \"d_hp\": 12}, {\"round\": 4, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 12, \"d_hp\": 13}, {\"round\": 5, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 13, \"d_hp\": 11}, {\"round\": 6, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 11, \"d_hp\": 12}, {\"round\": 7, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 12, \"d_hp\": 10}, {\"round\": 8, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 10, \"d_hp\": 11}, {\"round\": 9, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 11, \"d_hp\": 9}, {\"round\": 10, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 9, \"d_hp\": 10}, {\"round\": 11, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 10, \"d_hp\": 8}, {\"round\": 12, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 8, \"d_hp\": 9}, {\"round\": 13, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 9, \"d_hp\": 7}, {\"round\": 14, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 7, \"d_hp\": 8}, {\"round\": 15, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 8, \"d_hp\": 6}, {\"round\": 16, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 6, \"d_hp\": 7}, {\"round\": 17, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 7, \"d_hp\": 5}, {\"round\": 18, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 5, \"d_hp\": 6}, {\"round\": 19, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 6, \"d_hp\": 4}, {\"round\": 20, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 4, \"d_hp\": 5}, {\"round\": 21, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 5, \"d_hp\": 3}, {\"round\": 22, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 3, \"d_hp\": 4}, {\"round\": 23, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 4, \"d_hp\": 2}, {\"round\": 24, \"action\": \"『789』的血螳螂使用高级吸血攻击『123』的血螳螂，气血-1\", \"a_hp\": 2, \"d_hp\": 3}, {\"round\": 25, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 3, \"d_hp\": 1}, {\"round\": 26, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 1, \"d_hp\": 2}, {\"round\": 27, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 2, \"d_hp\": 0}], \"result\": \"『123』的血螳螂获胜，剩余气血2\"}]}', '2026-01-10 19:06:02');
INSERT INTO `arena_battle_log` VALUES ('8', 'normal', '黄阶', '4055', '789', '4053', '123', '0', '{\"is_victory\": false, \"attacker_wins\": 0, \"defender_wins\": 1, \"battles\": [{\"battle_num\": 1, \"attacker_beast\": \"\", \"defender_beast\": \"\", \"winner\": \"defender\", \"rounds\": [{\"round\": 1, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 15, \"d_hp\": 13}, {\"round\": 2, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 13, \"d_hp\": 14}, {\"round\": 3, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 14, \"d_hp\": 12}, {\"round\": 4, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 12, \"d_hp\": 13}, {\"round\": 5, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 13, \"d_hp\": 11}, {\"round\": 6, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 11, \"d_hp\": 12}, {\"round\": 7, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 12, \"d_hp\": 10}, {\"round\": 8, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 10, \"d_hp\": 11}, {\"round\": 9, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 11, \"d_hp\": 9}, {\"round\": 10, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 9, \"d_hp\": 10}, {\"round\": 11, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 10, \"d_hp\": 8}, {\"round\": 12, \"action\": \"『789』的血螳螂使用高级吸血攻击『123』的血螳螂，气血-1\", \"a_hp\": 8, \"d_hp\": 9}, {\"round\": 13, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 9, \"d_hp\": 7}, {\"round\": 14, \"action\": \"『789』的血螳螂使用高级吸血攻击『123』的血螳螂，气血-1\", \"a_hp\": 7, \"d_hp\": 8}, {\"round\": 15, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 8, \"d_hp\": 6}, {\"round\": 16, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 6, \"d_hp\": 7}, {\"round\": 17, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 7, \"d_hp\": 5}, {\"round\": 18, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 5, \"d_hp\": 6}, {\"round\": 19, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 6, \"d_hp\": 4}, {\"round\": 20, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 4, \"d_hp\": 5}, {\"round\": 21, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 5, \"d_hp\": 3}, {\"round\": 22, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 3, \"d_hp\": 4}, {\"round\": 23, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 4, \"d_hp\": 2}, {\"round\": 24, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 2, \"d_hp\": 3}, {\"round\": 25, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 3, \"d_hp\": 1}, {\"round\": 26, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 1, \"d_hp\": 2}, {\"round\": 27, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 2, \"d_hp\": 0}], \"result\": \"『123』的血螳螂获胜，剩余气血2\"}]}', '2026-01-10 19:06:17');
INSERT INTO `arena_battle_log` VALUES ('9', 'normal', '黄阶', '4055', '789', '4053', '123', '0', '{\"is_victory\": false, \"attacker_wins\": 0, \"defender_wins\": 1, \"battles\": [{\"battle_num\": 1, \"attacker_beast\": \"\", \"defender_beast\": \"\", \"winner\": \"defender\", \"rounds\": [{\"round\": 1, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 15, \"d_hp\": 13}, {\"round\": 2, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 13, \"d_hp\": 14}, {\"round\": 3, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 14, \"d_hp\": 12}, {\"round\": 4, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 12, \"d_hp\": 13}, {\"round\": 5, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 13, \"d_hp\": 11}, {\"round\": 6, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 11, \"d_hp\": 12}, {\"round\": 7, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 12, \"d_hp\": 10}, {\"round\": 8, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 10, \"d_hp\": 11}, {\"round\": 9, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 11, \"d_hp\": 9}, {\"round\": 10, \"action\": \"『789』的血螳螂使用高级吸血攻击『123』的血螳螂，气血-1\", \"a_hp\": 9, \"d_hp\": 10}, {\"round\": 11, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 10, \"d_hp\": 8}, {\"round\": 12, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 8, \"d_hp\": 9}, {\"round\": 13, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 9, \"d_hp\": 7}, {\"round\": 14, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 7, \"d_hp\": 8}, {\"round\": 15, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 8, \"d_hp\": 6}, {\"round\": 16, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 6, \"d_hp\": 7}, {\"round\": 17, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 7, \"d_hp\": 5}, {\"round\": 18, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 5, \"d_hp\": 6}, {\"round\": 19, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 6, \"d_hp\": 4}, {\"round\": 20, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 4, \"d_hp\": 5}, {\"round\": 21, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 5, \"d_hp\": 3}, {\"round\": 22, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 3, \"d_hp\": 4}, {\"round\": 23, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 4, \"d_hp\": 2}, {\"round\": 24, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 2, \"d_hp\": 3}, {\"round\": 25, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 3, \"d_hp\": 1}, {\"round\": 26, \"action\": \"『789』的血螳螂攻击『123』的血螳螂，气血-1\", \"a_hp\": 1, \"d_hp\": 2}, {\"round\": 27, \"action\": \"『123』的血螳螂攻击『789』的血螳螂，气血-1\", \"a_hp\": 2, \"d_hp\": 0}], \"result\": \"『123』的血螳螂获胜，剩余气血2\"}]}', '2026-01-10 19:22:18');

-- ----------------------------
-- Table structure for arena_daily_challenge
-- ----------------------------
DROP TABLE IF EXISTS `arena_daily_challenge`;
CREATE TABLE `arena_daily_challenge` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `challenge_date` date NOT NULL,
  `challenge_count` int NOT NULL DEFAULT '0',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_user_date` (`user_id`,`challenge_date`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='擂台每日挑战次数';

-- ----------------------------
-- Records of arena_daily_challenge
-- ----------------------------
INSERT INTO `arena_daily_challenge` VALUES ('9', '4055', '2026-01-10', '5', '2026-01-10 12:46:12', '2026-01-10 19:22:18');

-- ----------------------------
-- Table structure for arena_stats
-- ----------------------------
DROP TABLE IF EXISTS `arena_stats`;
CREATE TABLE `arena_stats` (
  `user_id` int NOT NULL,
  `rank_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '等级阶段名称',
  `success_count` int NOT NULL DEFAULT '0' COMMENT '守擂成功次数（达成10连胜次数）',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`,`rank_name`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='擂台守擂统计表';

-- ----------------------------
-- Records of arena_stats
-- ----------------------------

-- ----------------------------
-- Table structure for arena_streak
-- ----------------------------
DROP TABLE IF EXISTS `arena_streak`;
CREATE TABLE `arena_streak` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `current_streak` int DEFAULT '0' COMMENT '当前连胜次数',
  `max_streak_today` int DEFAULT '0' COMMENT '今日最高连胜',
  `total_battles_today` int DEFAULT '0' COMMENT '今日战斗次数',
  `last_battle_time` datetime DEFAULT NULL COMMENT '最后战斗时间',
  `last_refresh_time` datetime DEFAULT NULL COMMENT '最后刷新时间',
  `claimed_rewards` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci COMMENT '已领取的奖励(JSON)',
  `claimed_grand_prize` tinyint(1) DEFAULT '0' COMMENT '是否领取大奖',
  `record_date` date DEFAULT NULL COMMENT '记录日期',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_user_date` (`user_id`,`record_date`) USING BTREE,
  KEY `idx_max_streak` (`record_date`,`max_streak_today`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='连胜竞技场记录';

-- ----------------------------
-- Records of arena_streak
-- ----------------------------
INSERT INTO `arena_streak` VALUES ('1', '4053', '0', '0', '0', null, null, '[]', '0', '2026-01-09', '2026-01-09 14:59:25', '2026-01-09 14:59:25');
INSERT INTO `arena_streak` VALUES ('2', '4054', '0', '0', '0', null, '2026-01-09 20:27:34', '[]', '0', '2026-01-09', '2026-01-09 15:21:43', '2026-01-09 20:27:34');
INSERT INTO `arena_streak` VALUES ('3', '4055', '0', '1', '6', '2026-01-10 19:06:33', null, '[1]', '0', '2026-01-10', '2026-01-10 12:51:50', '2026-01-10 19:06:33');
INSERT INTO `arena_streak` VALUES ('4', '4053', '0', '0', '0', null, null, '[]', '0', '2026-01-10', '2026-01-10 13:43:48', '2026-01-10 13:43:48');
INSERT INTO `arena_streak` VALUES ('5', '4056', '0', '0', '0', null, null, '[]', '0', '2026-01-10', '2026-01-10 13:56:42', '2026-01-10 13:56:42');

-- ----------------------------
-- Table structure for arena_streak_history
-- ----------------------------
DROP TABLE IF EXISTS `arena_streak_history`;
CREATE TABLE `arena_streak_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `nickname` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `max_streak` int NOT NULL COMMENT '最高连胜次数',
  `record_date` date NOT NULL COMMENT '记录日期',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_date` (`record_date`) USING BTREE,
  KEY `idx_date` (`record_date`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='历届连胜王';

-- ----------------------------
-- Records of arena_streak_history
-- ----------------------------

-- ----------------------------
-- Table structure for battlefield_battle_log
-- ----------------------------
DROP TABLE IF EXISTS `battlefield_battle_log`;
CREATE TABLE `battlefield_battle_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `battlefield_type` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '战场类型（tiger猛虎战场/crane飞鹤战场）',
  `period` int NOT NULL COMMENT '战场期数',
  `round_num` int NOT NULL COMMENT '第几轮',
  `match_num` int NOT NULL COMMENT '本轮第几场',
  `first_user_id` int NOT NULL COMMENT '前置玩家ID（用于昨日战况列表左侧）',
  `first_user_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '前置玩家昵称',
  `second_user_id` int NOT NULL COMMENT '对手玩家ID',
  `second_user_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '对手玩家昵称',
  `first_user_team` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '前置玩家阵营（red/blue，可选）',
  `second_user_team` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '对手阵营（red/blue，可选）',
  `is_first_win` tinyint NOT NULL DEFAULT '0' COMMENT '前置玩家是否获胜(1=胜,0=负)',
  `result_label` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT '' COMMENT '前置玩家结果描述（失败/小败/小胜/完美胜利等）',
  `battle_data` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '战斗详情(JSON，结构与镇妖/擂台战报一致)',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_type_period` (`battlefield_type`,`period`) USING BTREE,
  KEY `idx_type_period_round` (`battlefield_type`,`period`,`round_num`) USING BTREE,
  KEY `idx_first_user` (`first_user_id`) USING BTREE,
  KEY `idx_second_user` (`second_user_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=369 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='古战场战斗记录表';

-- ----------------------------
-- Records of battlefield_battle_log
-- ----------------------------

-- ----------------------------
-- Table structure for battlefield_signup
-- ----------------------------
DROP TABLE IF EXISTS `battlefield_signup`;
CREATE TABLE `battlefield_signup` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL COMMENT '玩家ID',
  `battlefield_type` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '战场类型（tiger猛虎战场/crane飞鹤战场）',
  `signup_date` date NOT NULL COMMENT '报名日期',
  `signup_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '报名时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uniq_user_type_date` (`user_id`,`battlefield_type`,`signup_date`) USING BTREE,
  KEY `idx_type_date` (`battlefield_type`,`signup_date`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=431 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='古战场报名表';

-- ----------------------------
-- Records of battlefield_signup
-- ----------------------------

-- ----------------------------
-- Table structure for beast_bone
-- ----------------------------
DROP TABLE IF EXISTS `beast_bone`;
CREATE TABLE `beast_bone` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL COMMENT '玩家ID',
  `beast_id` int DEFAULT NULL COMMENT '装备到的幻兽ID（未装备时为NULL）',
  `template_id` int NOT NULL COMMENT '战骨模板ID',
  `slot` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '槽位：头骨/胸骨/臂骨/手骨/腿骨/尾骨/元魂',
  `level` int NOT NULL DEFAULT '1' COMMENT '等级',
  `stage` int NOT NULL DEFAULT '1' COMMENT '阶段',
  `hp_flat` int NOT NULL DEFAULT '0' COMMENT '气血加成（固定值）',
  `attack_flat` int NOT NULL DEFAULT '0' COMMENT '攻击加成（固定值）',
  `physical_defense_flat` int NOT NULL DEFAULT '0' COMMENT '物防加成（固定值）',
  `magic_defense_flat` int NOT NULL DEFAULT '0' COMMENT '法防加成（固定值）',
  `speed_flat` int NOT NULL DEFAULT '0' COMMENT '速度加成（固定值）',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_user_id` (`user_id`) USING BTREE,
  KEY `idx_beast_id` (`beast_id`) USING BTREE,
  KEY `idx_user_beast` (`user_id`,`beast_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=149 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='玩家战骨表';

-- ----------------------------
-- Records of beast_bone
-- ----------------------------

-- ----------------------------
-- Table structure for cultivation_config
-- ----------------------------
DROP TABLE IF EXISTS `cultivation_config`;
CREATE TABLE `cultivation_config` (
  `id` int NOT NULL AUTO_INCREMENT,
  `duration_hours` int NOT NULL COMMENT '修行时长(小时)',
  `prestige_reward` int NOT NULL COMMENT '声望奖励',
  `gold_cost` int DEFAULT '0' COMMENT '金币消耗',
  `description` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '描述',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=226 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='修行配置表';

-- ----------------------------
-- Records of cultivation_config
-- ----------------------------

-- ----------------------------
-- Table structure for dragonpalace_daily_state
-- ----------------------------
DROP TABLE IF EXISTS `dragonpalace_daily_state`;
CREATE TABLE `dragonpalace_daily_state` (
  `user_id` int NOT NULL,
  `play_date` date NOT NULL COMMENT '日期（每天刷新）',
  `resets_used` int NOT NULL DEFAULT '0' COMMENT '当日已重置次数（0~2）',
  `status` varchar(32) NOT NULL DEFAULT 'not_started' COMMENT 'not_started/in_progress/failed/completed',
  `current_stage` int NOT NULL DEFAULT '1' COMMENT '当前关卡（1~3）',
  `stage1_success` tinyint NOT NULL DEFAULT '0',
  `stage1_report_json` longtext,
  `stage1_reward_item_id` int DEFAULT NULL,
  `stage1_reward_claimed` tinyint NOT NULL DEFAULT '0',
  `stage2_success` tinyint NOT NULL DEFAULT '0',
  `stage2_report_json` longtext,
  `stage2_reward_item_id` int DEFAULT NULL,
  `stage2_reward_claimed` tinyint NOT NULL DEFAULT '0',
  `stage3_success` tinyint NOT NULL DEFAULT '0',
  `stage3_report_json` longtext,
  `stage3_reward_item_id` int DEFAULT NULL,
  `stage3_reward_claimed` tinyint NOT NULL DEFAULT '0',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`,`play_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='龙宫之谜：玩家每日进度与战报/领奖状态';

-- ----------------------------
-- Records of dragonpalace_daily_state
-- ----------------------------
INSERT INTO `dragonpalace_daily_state` VALUES ('4053', '2026-01-10', '0', 'failed', '2', '1', '{\"battles\": [{\"battle_num\": 1, \"winner\": \"\", \"rounds\": [{\"round\": 1, \"action\": \"『海龙门』的龙虾化石攻击『MOJIE』的神·朱雀，气血-70\", \"a_hp\": 2612, \"d_hp\": 3134}, {\"round\": 2, \"action\": \"『MOJIE』的神·朱雀攻击『海龙门』的龙虾化石，气血-200\", \"a_hp\": 3134, \"d_hp\": 2412}, {\"round\": 3, \"action\": \"『海龙门』的龙虾化石攻击『MOJIE』的神·朱雀，气血-70\", \"a_hp\": 2412, \"d_hp\": 3064}, {\"round\": 4, \"action\": \"『MOJIE』的神·朱雀攻击『海龙门』的龙虾化石，气血-177\", \"a_hp\": 3064, \"d_hp\": 2235}, {\"round\": 5, \"action\": \"『海龙门』的龙虾化石攻击『MOJIE』的神·朱雀，气血-69\", \"a_hp\": 2235, \"d_hp\": 2995}, {\"round\": 6, \"action\": \"『MOJIE』的神·朱雀攻击『海龙门』的龙虾化石，气血-189\", \"a_hp\": 2995, \"d_hp\": 2046}, {\"round\": 7, \"action\": \"『海龙门』的龙虾化石攻击『MOJIE』的神·朱雀，气血-70\", \"a_hp\": 2046, \"d_hp\": 2925}, {\"round\": 8, \"action\": \"『MOJIE』的神·朱雀使用高级必杀攻击『海龙门』的龙虾化石，气血-480\", \"a_hp\": 2925, \"d_hp\": 1566}, {\"round\": 9, \"action\": \"『海龙门』的龙虾化石攻击『MOJIE』的神·朱雀，气血-70\", \"a_hp\": 1566, \"d_hp\": 2855}, {\"round\": 10, \"action\": \"『MOJIE』的神·朱雀攻击『海龙门』的龙虾化石，气血-206，受到高级反震反震，自身气血-90\", \"a_hp\": 2765, \"d_hp\": 1360}, {\"round\": 11, \"action\": \"『海龙门』的龙虾化石攻击『MOJIE』的神·朱雀，气血-71\", \"a_hp\": 1360, \"d_hp\": 2694}, {\"round\": 12, \"action\": \"『MOJIE』的神·朱雀攻击『海龙门』的龙虾化石，气血-180\", \"a_hp\": 2694, \"d_hp\": 1180}, {\"round\": 13, \"action\": \"『海龙门』的龙虾化石攻击『MOJIE』的神·朱雀，气血-71\", \"a_hp\": 1180, \"d_hp\": 2623}, {\"round\": 14, \"action\": \"『MOJIE』的神·朱雀攻击『海龙门』的龙虾化石，气血-191\", \"a_hp\": 2623, \"d_hp\": 989}, {\"round\": 15, \"action\": \"『海龙门』的龙虾化石攻击『MOJIE』的神·朱雀，气血-70\", \"a_hp\": 989, \"d_hp\": 2553}, {\"round\": 16, \"action\": \"『MOJIE』的神·朱雀攻击『海龙门』的龙虾化石，气血-205\", \"a_hp\": 2553, \"d_hp\": 784}, {\"round\": 17, \"action\": \"『海龙门』的龙虾化石攻击『MOJIE』的神·朱雀，气血-70\", \"a_hp\": 784, \"d_hp\": 2483}, {\"round\": 18, \"action\": \"『MOJIE』的神·朱雀攻击『海龙门』的龙虾化石，气血-210\", \"a_hp\": 2483, \"d_hp\": 574}, {\"round\": 19, \"action\": \"『海龙门』的龙虾化石攻击『MOJIE』的神·朱雀，气血-70\", \"a_hp\": 574, \"d_hp\": 2413}, {\"round\": 20, \"action\": \"『MOJIE』的神·朱雀使用高级必杀攻击『海龙门』的龙虾化石，气血-470\", \"a_hp\": 2413, \"d_hp\": 104}, {\"round\": 21, \"action\": \"『海龙门』的龙虾化石攻击『MOJIE』的神·朱雀，气血-70\", \"a_hp\": 104, \"d_hp\": 2343}, {\"round\": 22, \"action\": \"『MOJIE』的神·朱雀攻击『海龙门』的龙虾化石，气血-195\", \"a_hp\": 2343, \"d_hp\": 0}], \"result\": \"『海龙门』的龙虾化石阵亡，『MOJIE』的神·朱雀获胜\"}, {\"battle_num\": 2, \"winner\": \"\", \"rounds\": [{\"round\": 1, \"action\": \"『海龙门』的螃蟹化石攻击『MOJIE』的神·朱雀，气血-71\", \"a_hp\": 2612, \"d_hp\": 2272}, {\"round\": 2, \"action\": \"『MOJIE』的神·朱雀攻击『海龙门』的螃蟹化石，气血-200\", \"a_hp\": 2272, \"d_hp\": 2412}, {\"round\": 3, \"action\": \"『海龙门』的螃蟹化石攻击『MOJIE』的神·朱雀，气血-69\", \"a_hp\": 2412, \"d_hp\": 2203}, {\"round\": 4, \"action\": \"『MOJIE』的神·朱雀攻击『海龙门』的螃蟹化石，气血-177\", \"a_hp\": 2203, \"d_hp\": 2235}, {\"round\": 5, \"action\": \"『海龙门』的螃蟹化石攻击『MOJIE』的神·朱雀，气血-70\", \"a_hp\": 2235, \"d_hp\": 2133}, {\"round\": 6, \"action\": \"『海龙门』的螃蟹化石触发闪避，躲开了『MOJIE』的神·朱雀的攻击\", \"a_hp\": 2133, \"d_hp\": 2235}, {\"round\": 7, \"action\": \"『海龙门』的螃蟹化石攻击『MOJIE』的神·朱雀，气血-71\", \"a_hp\": 2235, \"d_hp\": 2062}, {\"round\": 8, \"action\": \"『MOJIE』的神·朱雀攻击『海龙门』的螃蟹化石，气血-196\", \"a_hp\": 2062, \"d_hp\": 2039}, {\"round\": 9, \"action\": \"『海龙门』的螃蟹化石攻击『MOJIE』的神·朱雀，气血-70\", \"a_hp\": 2039, \"d_hp\": 1992}, {\"round\": 10, \"action\": \"『MOJIE』的神·朱雀攻击『海龙门』的螃蟹化石，气血-199\", \"a_hp\": 1992, \"d_hp\": 1840}, {\"round\": 11, \"action\": \"『海龙门』的螃蟹化石攻击『MOJIE』的神·朱雀，气血-70，受到高级反击反击，自身气血-52\", \"a_hp\": 1788, \"d_hp\": 1922}, {\"round\": 12, \"action\": \"『MOJIE』的神·朱雀使用高级必杀攻击『海龙门』的螃蟹化石，气血-522\", \"a_hp\": 1922, \"d_hp\": 1266}, {\"round\": 13, \"action\": \"『海龙门』的螃蟹化石攻击『MOJIE』的神·朱雀，气血-70\", \"a_hp\": 1266, \"d_hp\": 1852}, {\"round\": 14, \"action\": \"『MOJIE』的神·朱雀攻击『海龙门』的螃蟹化石，气血-208\", \"a_hp\": 1852, \"d_hp\": 1058}, {\"round\": 15, \"action\": \"『海龙门』的螃蟹化石攻击『MOJIE』的神·朱雀，气血-70\", \"a_hp\": 1058, \"d_hp\": 1782}, {\"round\": 16, \"action\": \"『MOJIE』的神·朱雀攻击『海龙门』的螃蟹化石，气血-200\", \"a_hp\": 1782, \"d_hp\": 858}, {\"round\": 17, \"action\": \"『海龙门』的螃蟹化石攻击『MOJIE』的神·朱雀，气血-70\", \"a_hp\": 858, \"d_hp\": 1712}, {\"round\": 18, \"action\": \"『MOJIE』的神·朱雀攻击『海龙门』的螃蟹化石，气血-178\", \"a_hp\": 1712, \"d_hp\": 680}, {\"round\": 19, \"action\": \"『海龙门』的螃蟹化石攻击『MOJIE』的神·朱雀，气血-70\", \"a_hp\": 680, \"d_hp\": 1642}, {\"round\": 20, \"action\": \"『MOJIE』的神·朱雀攻击『海龙门』的螃蟹化石，气血-183\", \"a_hp\": 1642, \"d_hp\": 497}, {\"round\": 21, \"action\": \"『海龙门』的螃蟹化石使用雷击攻击『MOJIE』的神·朱雀，气血-112\", \"a_hp\": 497, \"d_hp\": 1530}, {\"round\": 22, \"action\": \"『MOJIE』的神·朱雀攻击『海龙门』的螃蟹化石，气血-190\", \"a_hp\": 1530, \"d_hp\": 307}, {\"round\": 23, \"action\": \"『海龙门』的螃蟹化石攻击『MOJIE』的神·朱雀，气血-70\", \"a_hp\": 307, \"d_hp\": 1460}, {\"round\": 24, \"action\": \"『MOJIE』的神·朱雀攻击『海龙门』的螃蟹化石，气血-175\", \"a_hp\": 1460, \"d_hp\": 132}, {\"round\": 25, \"action\": \"『海龙门』的螃蟹化石攻击『MOJIE』的神·朱雀，气血-69\", \"a_hp\": 132, \"d_hp\": 1391}, {\"round\": 26, \"action\": \"『MOJIE』的神·朱雀使用高级必杀攻击『海龙门』的螃蟹化石，气血-517\", \"a_hp\": 1391, \"d_hp\": 0}], \"result\": \"『海龙门』的螃蟹化石阵亡，『MOJIE』的神·朱雀获胜\"}]}', '93001', '1', '0', '{\"battles\": [{\"battle_num\": 1, \"winner\": \"\", \"rounds\": [{\"round\": 1, \"action\": \"『龙宫城』的小龙女攻击『MOJIE』的神·朱雀，气血-593\", \"a_hp\": 7295, \"d_hp\": 2611}, {\"round\": 2, \"action\": \"『MOJIE』的神·朱雀攻击『龙宫城』的小龙女，气血-84，受到高级反击反击，自身气血-63\", \"a_hp\": 2548, \"d_hp\": 7211}, {\"round\": 3, \"action\": \"『龙宫城』的小龙女攻击『MOJIE』的神·朱雀，气血-595\", \"a_hp\": 7211, \"d_hp\": 1953}, {\"round\": 4, \"action\": \"『MOJIE』的神·朱雀攻击『龙宫城』的小龙女，气血-75\", \"a_hp\": 1953, \"d_hp\": 7136}, {\"round\": 5, \"action\": \"『龙宫城』的小龙女攻击『MOJIE』的神·朱雀，气血-603\", \"a_hp\": 7136, \"d_hp\": 1350}, {\"round\": 6, \"action\": \"『MOJIE』的神·朱雀攻击『龙宫城』的小龙女，气血-86\", \"a_hp\": 1350, \"d_hp\": 7050}, {\"round\": 7, \"action\": \"『龙宫城』的小龙女攻击『MOJIE』的神·朱雀，气血-592\", \"a_hp\": 7050, \"d_hp\": 758}, {\"round\": 8, \"action\": \"『MOJIE』的神·朱雀攻击『龙宫城』的小龙女，气血-87\", \"a_hp\": 758, \"d_hp\": 6963}, {\"round\": 9, \"action\": \"『龙宫城』的小龙女攻击『MOJIE』的神·朱雀，气血-605\", \"a_hp\": 6963, \"d_hp\": 153}, {\"round\": 10, \"action\": \"『MOJIE』的神·朱雀攻击『龙宫城』的小龙女，气血-82\", \"a_hp\": 153, \"d_hp\": 6881}, {\"round\": 11, \"action\": \"『龙宫城』的小龙女攻击『MOJIE』的神·朱雀，气血-591\", \"a_hp\": 6881, \"d_hp\": 0}], \"result\": \"『MOJIE』的神·朱雀阵亡，『龙宫城』的小龙女获胜\"}, {\"battle_num\": 2, \"winner\": \"\", \"rounds\": [{\"round\": 1, \"action\": \"『龙宫城』的小龙女使用高级雷击攻击『MOJIE』的霸王龙VI(绝版)，气血-966\", \"a_hp\": 6881, \"d_hp\": 2571}, {\"round\": 2, \"action\": \"『MOJIE』的霸王龙VI(绝版)攻击『龙宫城』的小龙女，气血-297\", \"a_hp\": 2571, \"d_hp\": 6584}, {\"round\": 3, \"action\": \"『龙宫城』的小龙女攻击『MOJIE』的霸王龙VI(绝版)，气血-619\", \"a_hp\": 6584, \"d_hp\": 1952}, {\"round\": 4, \"action\": \"『MOJIE』的霸王龙VI(绝版)攻击『龙宫城』的小龙女，气血-251\", \"a_hp\": 1952, \"d_hp\": 6333}, {\"round\": 5, \"action\": \"『龙宫城』的小龙女攻击『MOJIE』的霸王龙VI(绝版)，气血-618\", \"a_hp\": 6333, \"d_hp\": 1334}, {\"round\": 6, \"action\": \"『MOJIE』的霸王龙VI(绝版)使用高级撕咬攻击『龙宫城』的小龙女，气血-425\", \"a_hp\": 1334, \"d_hp\": 5908}, {\"round\": 7, \"action\": \"『龙宫城』的小龙女攻击『MOJIE』的霸王龙VI(绝版)，气血-613\", \"a_hp\": 5908, \"d_hp\": 721}, {\"round\": 8, \"action\": \"『MOJIE』的霸王龙VI(绝版)攻击『龙宫城』的小龙女，气血-297\", \"a_hp\": 721, \"d_hp\": 5611}, {\"round\": 9, \"action\": \"『龙宫城』的小龙女攻击『MOJIE』的霸王龙VI(绝版)，气血-611\", \"a_hp\": 5611, \"d_hp\": 110}, {\"round\": 10, \"action\": \"『MOJIE』的霸王龙VI(绝版)使用高级必杀攻击『龙宫城』的小龙女，气血-715\", \"a_hp\": 110, \"d_hp\": 4896}, {\"round\": 11, \"action\": \"『龙宫城』的小龙女使用连击攻击『MOJIE』的霸王龙VI(绝版)，气血-1210\", \"a_hp\": 4896, \"d_hp\": 0}], \"result\": \"『MOJIE』的霸王龙VI(绝版)阵亡，『龙宫城』的小龙女获胜\"}, {\"battle_num\": 3, \"winner\": \"\", \"rounds\": [{\"round\": 1, \"action\": \"『龙宫城』的小龙女使用高级雷击攻击『MOJIE』的圣灵蚁，气血-910\", \"a_hp\": 4896, \"d_hp\": 2839}, {\"round\": 2, \"action\": \"『MOJIE』的圣灵蚁攻击『龙宫城』的小龙女，气血-56\", \"a_hp\": 2839, \"d_hp\": 4840}, {\"round\": 3, \"action\": \"『MOJIE』的圣灵蚁触发高级闪避，躲开了『龙宫城』的小龙女的攻击\", \"a_hp\": 4840, \"d_hp\": 2839}, {\"round\": 4, \"action\": \"『MOJIE』的圣灵蚁使用高级致盲攻击『龙宫城』的小龙女，气血-44，使其法术防御下降30%，持续6回合\", \"a_hp\": 2839, \"d_hp\": 4796}, {\"round\": 5, \"action\": \"『龙宫城』的小龙女攻击『MOJIE』的圣灵蚁，气血-562\", \"a_hp\": 4796, \"d_hp\": 2277}, {\"round\": 6, \"action\": \"『MOJIE』的圣灵蚁攻击『龙宫城』的小龙女，气血-57\", \"a_hp\": 2277, \"d_hp\": 4739}, {\"round\": 7, \"action\": \"『MOJIE』的圣灵蚁触发高级闪避，躲开了『龙宫城』的小龙女的攻击\", \"a_hp\": 4739, \"d_hp\": 2277}, {\"round\": 8, \"action\": \"『MOJIE』的圣灵蚁攻击『龙宫城』的小龙女，气血-56\", \"a_hp\": 2277, \"d_hp\": 4683}, {\"round\": 9, \"action\": \"『龙宫城』的小龙女攻击『MOJIE』的圣灵蚁，气血-570\", \"a_hp\": 4683, \"d_hp\": 1707}, {\"round\": 10, \"action\": \"『MOJIE』的圣灵蚁攻击『龙宫城』的小龙女，气血-56\", \"a_hp\": 1707, \"d_hp\": 4627}, {\"round\": 11, \"action\": \"『龙宫城』的小龙女使用连击攻击『MOJIE』的圣灵蚁，气血-1118\", \"a_hp\": 4627, \"d_hp\": 589}, {\"round\": 12, \"action\": \"『MOJIE』的圣灵蚁攻击『龙宫城』的小龙女，气血-56\", \"a_hp\": 589, \"d_hp\": 4571}, {\"round\": 13, \"action\": \"『龙宫城』的小龙女使用高级雷击攻击『MOJIE』的圣灵蚁，气血-902\", \"a_hp\": 4571, \"d_hp\": 0}], \"result\": \"『MOJIE』的圣灵蚁阵亡，『龙宫城』的小龙女获胜\"}, {\"battle_num\": 4, \"winner\": \"\", \"rounds\": [{\"round\": 1, \"action\": \"『MOJIE』的神·青龙触发高级闪避，躲开了『龙宫城』的小龙女的攻击\", \"a_hp\": 4571, \"d_hp\": 3533}, {\"round\": 2, \"action\": \"『MOJIE』的神·青龙攻击『龙宫城』的小龙女，气血-78\", \"a_hp\": 3533, \"d_hp\": 4493}, {\"round\": 3, \"action\": \"『龙宫城』的小龙女攻击『MOJIE』的神·青龙，气血-573\", \"a_hp\": 4493, \"d_hp\": 2960}, {\"round\": 4, \"action\": \"『MOJIE』的神·青龙攻击『龙宫城』的小龙女，气血-78\", \"a_hp\": 2960, \"d_hp\": 4415}, {\"round\": 5, \"action\": \"『龙宫城』的小龙女攻击『MOJIE』的神·青龙，气血-571\", \"a_hp\": 4415, \"d_hp\": 2389}, {\"round\": 6, \"action\": \"『MOJIE』的神·青龙攻击『龙宫城』的小龙女，气血-84\", \"a_hp\": 2389, \"d_hp\": 4331}, {\"round\": 7, \"action\": \"『龙宫城』的小龙女攻击『MOJIE』的神·青龙，气血-584\", \"a_hp\": 4331, \"d_hp\": 1805}, {\"round\": 8, \"action\": \"『MOJIE』的神·青龙使用高级必杀攻击『龙宫城』的小龙女，气血-190\", \"a_hp\": 1805, \"d_hp\": 4141}, {\"round\": 9, \"action\": \"『龙宫城』的小龙女攻击『MOJIE』的神·青龙，气血-578\", \"a_hp\": 4141, \"d_hp\": 1227}, {\"round\": 10, \"action\": \"『MOJIE』的神·青龙攻击『龙宫城』的小龙女，气血-90\", \"a_hp\": 1227, \"d_hp\": 4051}, {\"round\": 11, \"action\": \"『MOJIE』的神·青龙触发高级闪避，躲开了『龙宫城』的小龙女的攻击\", \"a_hp\": 4051, \"d_hp\": 1227}, {\"round\": 12, \"action\": \"『MOJIE』的神·青龙使用高级必杀攻击『龙宫城』的小龙女，气血-215\", \"a_hp\": 1227, \"d_hp\": 3836}, {\"round\": 13, \"action\": \"『龙宫城』的小龙女攻击『MOJIE』的神·青龙，气血-570\", \"a_hp\": 3836, \"d_hp\": 657}, {\"round\": 14, \"action\": \"『MOJIE』的神·青龙攻击『龙宫城』的小龙女，气血-84\", \"a_hp\": 657, \"d_hp\": 3752}, {\"round\": 15, \"action\": \"『龙宫城』的小龙女攻击『MOJIE』的神·青龙，气血-580\", \"a_hp\": 3752, \"d_hp\": 77}], \"result\": \"『龙宫城』的小龙女阵亡，『MOJIE』的神·青龙获胜\"}]}', null, '0', '0', null, null, '0', '2026-01-10 11:34:14');
INSERT INTO `dragonpalace_daily_state` VALUES ('4053', '2026-01-11', '0', 'failed', '1', '0', '{\"battles\": [{\"battle_num\": 1, \"winner\": \"\", \"rounds\": [{\"round\": 1, \"action\": \"『海龙门』的龙虾化石攻击『123』的血螳螂，气血-501\", \"a_hp\": 2612, \"d_hp\": 0}], \"result\": \"『123』的血螳螂阵亡，『海龙门』的龙虾化石获胜\"}]}', null, '0', '0', null, null, '0', '0', null, null, '0', '2026-01-11 09:26:31');
INSERT INTO `dragonpalace_daily_state` VALUES ('4054', '2026-01-10', '0', 'completed', '4', '1', '{\"battles\": [{\"battle_num\": 1, \"winner\": \"\", \"rounds\": [{\"round\": 1, \"action\": \"『MOJIE』的神·朱雀攻击『海龙门』的海龙门守卫，气血-298\", \"a_hp\": 3204, \"d_hp\": 552}, {\"round\": 2, \"action\": \"『海龙门』的海龙门守卫攻击『MOJIE』的神·朱雀，气血-62\", \"a_hp\": 552, \"d_hp\": 3142}, {\"round\": 3, \"action\": \"『MOJIE』的神·朱雀攻击『海龙门』的海龙门守卫，气血-291\", \"a_hp\": 3142, \"d_hp\": 261}, {\"round\": 4, \"action\": \"『海龙门』的海龙门守卫攻击『MOJIE』的神·朱雀，气血-61\", \"a_hp\": 261, \"d_hp\": 3081}, {\"round\": 5, \"action\": \"『MOJIE』的神·朱雀攻击『海龙门』的海龙门守卫，气血-294\", \"a_hp\": 3081, \"d_hp\": 0}], \"result\": \"『海龙门』的海龙门守卫阵亡，『MOJIE』的神·朱雀获胜\"}]}', '3013', '1', '1', '{\"battles\": [{\"battle_num\": 1, \"winner\": \"\", \"rounds\": [{\"round\": 1, \"action\": \"『MOJIE』的神·朱雀攻击『龙宫城』的龙宫城守将，气血-259\", \"a_hp\": 3204, \"d_hp\": 1341}, {\"round\": 2, \"action\": \"『龙宫城』的龙宫城守将攻击『MOJIE』的神·朱雀，气血-299\", \"a_hp\": 1341, \"d_hp\": 2905}, {\"round\": 3, \"action\": \"『MOJIE』的神·朱雀攻击『龙宫城』的龙宫城守将，气血-300\", \"a_hp\": 2905, \"d_hp\": 1041}, {\"round\": 4, \"action\": \"『龙宫城』的龙宫城守将攻击『MOJIE』的神·朱雀，气血-281\", \"a_hp\": 1041, \"d_hp\": 2624}, {\"round\": 5, \"action\": \"『MOJIE』的神·朱雀攻击『龙宫城』的龙宫城守将，气血-252\", \"a_hp\": 2624, \"d_hp\": 789}, {\"round\": 6, \"action\": \"『龙宫城』的龙宫城守将攻击『MOJIE』的神·朱雀，气血-258\", \"a_hp\": 789, \"d_hp\": 2366}, {\"round\": 7, \"action\": \"『MOJIE』的神·朱雀攻击『龙宫城』的龙宫城守将，气血-259\", \"a_hp\": 2366, \"d_hp\": 530}, {\"round\": 8, \"action\": \"『龙宫城』的龙宫城守将攻击『MOJIE』的神·朱雀，气血-289\", \"a_hp\": 530, \"d_hp\": 2077}, {\"round\": 9, \"action\": \"『MOJIE』的神·朱雀攻击『龙宫城』的龙宫城守将，气血-272\", \"a_hp\": 2077, \"d_hp\": 258}, {\"round\": 10, \"action\": \"『龙宫城』的龙宫城守将攻击『MOJIE』的神·朱雀，气血-276\", \"a_hp\": 258, \"d_hp\": 1801}, {\"round\": 11, \"action\": \"『MOJIE』的神·朱雀攻击『龙宫城』的龙宫城守将，气血-293\", \"a_hp\": 1801, \"d_hp\": 0}], \"result\": \"『龙宫城』的龙宫城守将阵亡，『MOJIE』的神·朱雀获胜\"}]}', '3013', '1', '1', '{\"battles\": [{\"battle_num\": 1, \"winner\": \"\", \"rounds\": [{\"round\": 1, \"action\": \"『MOJIE』的神·朱雀攻击『龙殿』的龙殿守护者，气血-259\", \"a_hp\": 3204, \"d_hp\": 2341}, {\"round\": 2, \"action\": \"『龙殿』的龙殿守护者攻击『MOJIE』的神·朱雀，气血-184\", \"a_hp\": 2341, \"d_hp\": 3020}, {\"round\": 3, \"action\": \"『MOJIE』的神·朱雀使用高级必杀攻击『龙殿』的龙殿守护者，气血-732\", \"a_hp\": 3020, \"d_hp\": 1609}, {\"round\": 4, \"action\": \"『龙殿』的龙殿守护者攻击『MOJIE』的神·朱雀，气血-192\", \"a_hp\": 1609, \"d_hp\": 2828}, {\"round\": 5, \"action\": \"『MOJIE』的神·朱雀攻击『龙殿』的龙殿守护者，气血-293\", \"a_hp\": 2828, \"d_hp\": 1316}, {\"round\": 6, \"action\": \"『龙殿』的龙殿守护者攻击『MOJIE』的神·朱雀，气血-175\", \"a_hp\": 1316, \"d_hp\": 2653}, {\"round\": 7, \"action\": \"『MOJIE』的神·朱雀攻击『龙殿』的龙殿守护者，气血-250\", \"a_hp\": 2653, \"d_hp\": 1066}, {\"round\": 8, \"action\": \"『龙殿』的龙殿守护者攻击『MOJIE』的神·朱雀，气血-192\", \"a_hp\": 1066, \"d_hp\": 2461}, {\"round\": 9, \"action\": \"『MOJIE』的神·朱雀攻击『龙殿』的龙殿守护者，气血-251\", \"a_hp\": 2461, \"d_hp\": 815}, {\"round\": 10, \"action\": \"『龙殿』的龙殿守护者攻击『MOJIE』的神·朱雀，气血-175\", \"a_hp\": 815, \"d_hp\": 2286}, {\"round\": 11, \"action\": \"『MOJIE』的神·朱雀使用高级必杀攻击『龙殿』的龙殿守护者，气血-682\", \"a_hp\": 2286, \"d_hp\": 133}, {\"round\": 12, \"action\": \"『龙殿』的龙殿守护者攻击『MOJIE』的神·朱雀，气血-203\", \"a_hp\": 133, \"d_hp\": 2083}, {\"round\": 13, \"action\": \"『MOJIE』的神·朱雀攻击『龙殿』的龙殿守护者，气血-260\", \"a_hp\": 2083, \"d_hp\": 0}], \"result\": \"『龙殿』的龙殿守护者阵亡，『MOJIE』的神·朱雀获胜\"}]}', '3013', '1', '2026-01-10 10:55:07');
INSERT INTO `dragonpalace_daily_state` VALUES ('4055', '2026-01-11', '1', 'failed', '1', '0', '{\"battles\": [{\"battle_num\": 1, \"winner\": \"\", \"rounds\": [{\"round\": 1, \"action\": \"『海龙门』的龙虾化石攻击『789』的血螳螂，气血-504\", \"a_hp\": 2612, \"d_hp\": 0}], \"result\": \"『789』的血螳螂阵亡，『海龙门』的龙虾化石获胜\"}, {\"battle_num\": 2, \"winner\": \"\", \"rounds\": [{\"round\": 1, \"action\": \"『海龙门』的龙虾化石攻击『789』的追风狼，气血-502\", \"a_hp\": 2612, \"d_hp\": 0}], \"result\": \"『789』的追风狼阵亡，『海龙门』的龙虾化石获胜\"}]}', null, '0', '0', null, null, '0', '0', null, null, '0', '2026-01-11 09:43:05');

-- ----------------------------
-- Table structure for friend_relation
-- ----------------------------
DROP TABLE IF EXISTS `friend_relation`;
CREATE TABLE `friend_relation` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `friend_id` int NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_friendship` (`user_id`,`friend_id`),
  KEY `idx_user` (`user_id`),
  KEY `idx_friend` (`friend_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of friend_relation
-- ----------------------------
INSERT INTO `friend_relation` VALUES ('1', '4053', '4055', '2026-01-10 09:09:23');
INSERT INTO `friend_relation` VALUES ('2', '4055', '4053', '2026-01-10 09:09:23');

-- ----------------------------
-- Table structure for friend_request
-- ----------------------------
DROP TABLE IF EXISTS `friend_request`;
CREATE TABLE `friend_request` (
  `id` int NOT NULL AUTO_INCREMENT,
  `requester_id` int NOT NULL,
  `requester_name` varchar(50) NOT NULL,
  `receiver_id` int NOT NULL,
  `receiver_name` varchar(50) NOT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'pending',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_request` (`requester_id`,`receiver_id`),
  KEY `idx_requester` (`requester_id`),
  KEY `idx_receiver` (`receiver_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of friend_request
-- ----------------------------
INSERT INTO `friend_request` VALUES ('1', '4054', 'abc', '4053', '123', 'pending', '2026-01-11 07:09:16', '2026-01-11 09:09:16');
INSERT INTO `friend_request` VALUES ('2', '4055', '789', '4053', '123', 'accepted', '2026-01-10 09:09:16', '2026-01-11 09:09:16');
INSERT INTO `friend_request` VALUES ('3', '4056', '456', '4054', 'abc', 'pending', '2026-01-11 08:39:16', '2026-01-11 09:09:16');
INSERT INTO `friend_request` VALUES ('4', '4055', '789', '4054', 'abc', 'pending', '2026-01-11 09:43:56', '2026-01-11 09:43:56');

-- ----------------------------
-- Table structure for king_challenge_logs
-- ----------------------------
DROP TABLE IF EXISTS `king_challenge_logs`;
CREATE TABLE `king_challenge_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `challenger_id` int NOT NULL,
  `challenger_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `defender_id` int NOT NULL,
  `defender_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `challenger_wins` tinyint(1) NOT NULL,
  `challenger_rank_before` int NOT NULL,
  `challenger_rank_after` int NOT NULL,
  `defender_rank_before` int NOT NULL,
  `defender_rank_after` int NOT NULL,
  `area_index` int NOT NULL,
  `battle_report` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '战报数据(JSON格式)',
  `challenge_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_area_time` (`area_index`,`challenge_time`) USING BTREE,
  KEY `idx_challenger` (`challenger_id`,`challenge_time`) USING BTREE,
  KEY `idx_defender` (`defender_id`,`challenge_time`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Records of king_challenge_logs
-- ----------------------------
INSERT INTO `king_challenge_logs` VALUES ('1', '4055', '789', '4056', '456', '0', '2', '2', '1', '1', '1', null, '2026-01-10 14:53:24');
INSERT INTO `king_challenge_logs` VALUES ('2', '4055', '789', '4056', '456', '0', '2', '2', '1', '1', '1', null, '2026-01-10 14:57:38');
INSERT INTO `king_challenge_logs` VALUES ('3', '4055', '789', '4056', '456', '0', '2', '2', '1', '1', '1', '{\"attackerName\": \"789\", \"defenderName\": \"456\", \"victory\": false, \"battleLogs\": [\"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\"], \"detailLogs\": [\"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂使用高级吸血攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\"]}', '2026-01-10 15:09:21');
INSERT INTO `king_challenge_logs` VALUES ('4', '4055', '789', '4056', '456', '0', '2', '2', '1', '1', '1', '{\"attackerName\": \"789\", \"defenderName\": \"456\", \"victory\": false, \"battleLogs\": [\"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂使用高级吸血攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\"], \"detailLogs\": [\"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂使用高级吸血攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂使用高级吸血攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂使用高级吸血攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\"]}', '2026-01-10 15:23:11');
INSERT INTO `king_challenge_logs` VALUES ('5', '4055', '789', '4056', '456', '0', '2', '2', '1', '1', '1', '{\"attackerName\": \"789\", \"defenderName\": \"456\", \"victory\": false, \"battleLogs\": [\"『789』的血螳螂使用高级吸血攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\"], \"detailLogs\": [\"『789』的血螳螂使用高级吸血攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂使用高级吸血攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂使用高级吸血攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂使用高级吸血攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\"]}', '2026-01-10 15:30:30');
INSERT INTO `king_challenge_logs` VALUES ('6', '4055', '789', '4056', '456', '0', '2', '2', '1', '1', '1', '{\"attackerName\": \"789\", \"defenderName\": \"456\", \"victory\": false, \"battleLogs\": [\"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂使用高级吸血攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\"], \"detailLogs\": [\"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂使用高级吸血攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\"]}', '2026-01-10 15:51:01');
INSERT INTO `king_challenge_logs` VALUES ('7', '4055', '789', '4056', '456', '0', '2', '2', '1', '1', '1', '{\"attackerName\": \"789\", \"defenderName\": \"456\", \"victory\": false, \"battleLogs\": [\"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂使用高级吸血攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\"], \"detailLogs\": [\"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂使用高级吸血攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\"]}', '2026-01-10 15:58:43');
INSERT INTO `king_challenge_logs` VALUES ('8', '4055', '789', '4056', '456', '0', '2', '2', '1', '1', '1', '{\"attackerName\": \"789\", \"defenderName\": \"456\", \"victory\": false, \"battleLogs\": [\"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\"], \"detailLogs\": [\"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂使用高级吸血攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂使用高级吸血攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\"]}', '2026-01-10 19:07:12');
INSERT INTO `king_challenge_logs` VALUES ('9', '4055', '789', '4056', '456', '0', '2', '2', '1', '1', '1', '{\"attackerName\": \"789\", \"defenderName\": \"456\", \"victory\": false, \"battleLogs\": [\"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\"], \"detailLogs\": [\"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂使用高级吸血攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\"]}', '2026-01-10 19:35:37');
INSERT INTO `king_challenge_logs` VALUES ('10', '4055', '789', '4056', '456', '0', '2', '2', '1', '1', '1', '{\"attackerName\": \"789\", \"defenderName\": \"456\", \"victory\": false, \"battleLogs\": [\"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\"], \"detailLogs\": [\"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂使用高级吸血攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂使用高级吸血攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\"]}', '2026-01-10 19:47:11');
INSERT INTO `king_challenge_logs` VALUES ('11', '4055', '789', '4056', '456', '0', '2', '2', '1', '1', '1', '{\"attackerName\": \"789\", \"defenderName\": \"456\", \"victory\": false, \"battleLogs\": [\"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂使用高级吸血攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\"], \"detailLogs\": [\"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂使用高级吸血攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂使用高级吸血攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂使用高级吸血攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂使用高级吸血攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂使用高级吸血攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂使用高级吸血攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\"]}', '2026-01-10 19:51:39');
INSERT INTO `king_challenge_logs` VALUES ('12', '4055', '789', '4056', '456', '0', '2', '2', '1', '1', '1', '{\"attackerName\": \"789\", \"defenderName\": \"456\", \"victory\": false, \"battleLogs\": [\"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂使用高级吸血攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\"], \"detailLogs\": [\"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂使用高级吸血攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂使用高级吸血攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂使用高级吸血攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"『456』的羽精灵攻击『789』的血螳螂，气血-1\"]}', '2026-01-10 19:53:48');
INSERT INTO `king_challenge_logs` VALUES ('13', '4055', '789', '4056', '456', '0', '2', '2', '1', '1', '1', '{\"is_victory\": false, \"result\": \"失败(:×)\", \"attacker_id\": 4055, \"attacker_name\": \"789\", \"defender_id\": 4056, \"defender_name\": \"456\", \"total_turns\": 28, \"battles\": [{\"battle_num\": 1, \"attacker_beast\": \"\", \"defender_beast\": \"\", \"winner\": \"defender\", \"rounds\": [{\"round\": 1, \"action\": \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"a_hp\": 14, \"d_hp\": 21}, {\"round\": 2, \"action\": \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"a_hp\": 21, \"d_hp\": 13}, {\"round\": 3, \"action\": \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"a_hp\": 13, \"d_hp\": 20}, {\"round\": 4, \"action\": \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"a_hp\": 20, \"d_hp\": 12}, {\"round\": 5, \"action\": \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"a_hp\": 12, \"d_hp\": 19}, {\"round\": 6, \"action\": \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"a_hp\": 19, \"d_hp\": 11}, {\"round\": 7, \"action\": \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"a_hp\": 11, \"d_hp\": 18}, {\"round\": 8, \"action\": \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"a_hp\": 18, \"d_hp\": 10}, {\"round\": 9, \"action\": \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"a_hp\": 10, \"d_hp\": 17}, {\"round\": 10, \"action\": \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"a_hp\": 17, \"d_hp\": 9}, {\"round\": 11, \"action\": \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"a_hp\": 9, \"d_hp\": 16}, {\"round\": 12, \"action\": \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"a_hp\": 16, \"d_hp\": 8}, {\"round\": 13, \"action\": \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"a_hp\": 8, \"d_hp\": 15}, {\"round\": 14, \"action\": \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"a_hp\": 15, \"d_hp\": 7}, {\"round\": 15, \"action\": \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"a_hp\": 7, \"d_hp\": 14}, {\"round\": 16, \"action\": \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"a_hp\": 14, \"d_hp\": 6}, {\"round\": 17, \"action\": \"『789』的血螳螂使用高级吸血攻击『456』的羽精灵，气血-1\", \"a_hp\": 6, \"d_hp\": 13}, {\"round\": 18, \"action\": \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"a_hp\": 13, \"d_hp\": 5}, {\"round\": 19, \"action\": \"『789』的血螳螂使用高级吸血攻击『456』的羽精灵，气血-1\", \"a_hp\": 5, \"d_hp\": 12}, {\"round\": 20, \"action\": \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"a_hp\": 12, \"d_hp\": 4}, {\"round\": 21, \"action\": \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"a_hp\": 4, \"d_hp\": 11}, {\"round\": 22, \"action\": \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"a_hp\": 11, \"d_hp\": 3}, {\"round\": 23, \"action\": \"『789』的血螳螂使用高级吸血攻击『456』的羽精灵，气血-1\", \"a_hp\": 3, \"d_hp\": 10}, {\"round\": 24, \"action\": \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"a_hp\": 10, \"d_hp\": 2}, {\"round\": 25, \"action\": \"『789』的血螳螂攻击『456』的羽精灵，气血-1\", \"a_hp\": 2, \"d_hp\": 9}, {\"round\": 26, \"action\": \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"a_hp\": 9, \"d_hp\": 1}, {\"round\": 27, \"action\": \"『789』的血螳螂使用高级吸血攻击『456』的羽精灵，气血-1\", \"a_hp\": 1, \"d_hp\": 8}, {\"round\": 28, \"action\": \"『456』的羽精灵攻击『789』的血螳螂，气血-1\", \"a_hp\": 8, \"d_hp\": 0}], \"result\": \"『456』的羽精灵获胜，剩余气血8\", \"summary\": \"『789』的血螳螂攻击『456』的羽精灵，气血-1\"}], \"attacker_beasts\": [{\"name\": \"血螳螂\", \"realm\": \"地界\", \"exp_gain\": 0, \"template_id\": 3}], \"defender_beasts\": [{\"name\": \"羽精灵\", \"realm\": \"地界\", \"template_id\": 9}], \"incense_bonus\": \"无\", \"energy_cost\": 15, \"current_streak\": 0}', '2026-01-10 19:56:09');

-- ----------------------------
-- Table structure for king_challenge_rank
-- ----------------------------
DROP TABLE IF EXISTS `king_challenge_rank`;
CREATE TABLE `king_challenge_rank` (
  `user_id` int NOT NULL,
  `area_index` int NOT NULL DEFAULT '1' COMMENT '赛区编号（1=一赛区，2=二赛区）',
  `rank_position` int NOT NULL COMMENT '在赛区内的排名（1起）',
  `win_streak` int NOT NULL DEFAULT '0' COMMENT '连胜场次',
  `total_wins` int NOT NULL DEFAULT '0' COMMENT '总胜场',
  `total_losses` int NOT NULL DEFAULT '0' COMMENT '总负场',
  `today_challenges` int NOT NULL DEFAULT '0' COMMENT '今日挑战次数',
  `last_challenge_date` date DEFAULT NULL COMMENT '上次挑战日期',
  `last_challenge_time` datetime DEFAULT NULL COMMENT '最后挑战时间（用于冷却）',
  `is_registered` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否已报名本周',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`) USING BTREE,
  KEY `idx_area_rank` (`area_index`,`rank_position`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='召唤之王挑战赛排名表';

-- ----------------------------
-- Records of king_challenge_rank
-- ----------------------------
INSERT INTO `king_challenge_rank` VALUES ('4053', '2', '2', '0', '0', '0', '0', '2026-01-10', null, '0', '2026-01-10 14:38:53');
INSERT INTO `king_challenge_rank` VALUES ('4054', '2', '1', '0', '0', '0', '0', '2026-01-09', null, '0', '2026-01-09 19:48:40');
INSERT INTO `king_challenge_rank` VALUES ('4055', '1', '1', '1', '1', '14', '1', '2026-01-11', '2026-01-10 19:56:09', '0', '2026-01-11 09:44:32');
INSERT INTO `king_challenge_rank` VALUES ('4056', '1', '2', '0', '14', '1', '1', '2026-01-10', '2026-01-10 14:00:58', '0', '2026-01-11 09:44:32');

-- ----------------------------
-- Table structure for king_final_stage
-- ----------------------------
DROP TABLE IF EXISTS `king_final_stage`;
CREATE TABLE `king_final_stage` (
  `id` int NOT NULL AUTO_INCREMENT,
  `season` int NOT NULL COMMENT '赛季编号',
  `user_id` int NOT NULL COMMENT '玩家ID',
  `stage` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '阶段：32/16/8/4/2/champion',
  `match_id` int DEFAULT NULL COMMENT '对战ID',
  `opponent_id` int DEFAULT NULL COMMENT '对手ID',
  `is_bye` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否轮空',
  `is_winner` tinyint(1) DEFAULT NULL COMMENT '是否胜利（NULL=未比赛）',
  `battle_time` datetime DEFAULT NULL COMMENT '战斗时间',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_season_stage` (`season`,`stage`) USING BTREE,
  KEY `idx_user` (`user_id`) USING BTREE,
  KEY `idx_match` (`match_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='召唤之王正赛阶段表';

-- ----------------------------
-- Records of king_final_stage
-- ----------------------------

-- ----------------------------
-- Table structure for king_reward_claimed
-- ----------------------------
DROP TABLE IF EXISTS `king_reward_claimed`;
CREATE TABLE `king_reward_claimed` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `season` int NOT NULL DEFAULT '1' COMMENT '赛季编号',
  `reward_tier` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '奖励档位（冠军/亚军/四强等）',
  `claimed_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_user_season` (`user_id`,`season`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='召唤之王奖励领取记录';

-- ----------------------------
-- Records of king_reward_claimed
-- ----------------------------
INSERT INTO `king_reward_claimed` VALUES ('3', '4054', '202602', '冠军', '2026-01-09 22:04:34');
INSERT INTO `king_reward_claimed` VALUES ('4', '4055', '202602', '亚军', '2026-01-10 15:59:11');

-- ----------------------------
-- Table structure for king_season_config
-- ----------------------------
DROP TABLE IF EXISTS `king_season_config`;
CREATE TABLE `king_season_config` (
  `season` int NOT NULL COMMENT '赛季编号',
  `start_date` date NOT NULL COMMENT '赛季开始日期（周一）',
  `end_date` date NOT NULL COMMENT '赛季结束日期（周日）',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'registration' COMMENT '状态：registration/preliminary/final/finished',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`season`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='召唤之王赛季配置表';

-- ----------------------------
-- Records of king_season_config
-- ----------------------------

-- ----------------------------
-- Table structure for level_config
-- ----------------------------
DROP TABLE IF EXISTS `level_config`;
CREATE TABLE `level_config` (
  `level` int NOT NULL COMMENT '等级',
  `prestige_required` int NOT NULL COMMENT '晋级所需声望',
  `rank_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '阶位名称',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`level`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='等级配置表';

-- ----------------------------
-- Records of level_config
-- ----------------------------

-- ----------------------------
-- Table structure for manor_land
-- ----------------------------
DROP TABLE IF EXISTS `manor_land`;
CREATE TABLE `manor_land` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `land_index` int NOT NULL COMMENT '0-9:普通土地, 10:黄土地, 11:银土地, 12:金土地',
  `status` tinyint NOT NULL DEFAULT '0' COMMENT '0:未开启, 1:空闲, 2:种植中',
  `tree_type` int DEFAULT '0' COMMENT '种植的种类：1, 2, 4, 6, 8株',
  `plant_time` datetime DEFAULT NULL COMMENT '种植开始时间',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_user_land` (`user_id`,`land_index`) USING BTREE,
  KEY `idx_user_id` (`user_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='庄园土地表';

-- ----------------------------
-- Records of manor_land
-- ----------------------------

-- ----------------------------
-- Table structure for mosoul_global_pity
-- ----------------------------
DROP TABLE IF EXISTS `mosoul_global_pity`;
CREATE TABLE `mosoul_global_pity` (
  `counter_key` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `count` int NOT NULL DEFAULT '0',
  `pity_threshold` int NOT NULL DEFAULT '0',
  `soul_charm_consumed_global` int NOT NULL DEFAULT '0',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `copper_consumed_global` bigint unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`counter_key`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Records of mosoul_global_pity
-- ----------------------------

-- ----------------------------
-- Table structure for mosoul_hunting_state
-- ----------------------------
DROP TABLE IF EXISTS `mosoul_hunting_state`;
CREATE TABLE `mosoul_hunting_state` (
  `user_id` int NOT NULL,
  `field_type` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'normal',
  `normal_available_npcs` json NOT NULL,
  `advanced_available_npcs` json NOT NULL,
  `soul_charm_consumed` int NOT NULL DEFAULT '0',
  `copper_consumed` int NOT NULL DEFAULT '0',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Records of mosoul_hunting_state
-- ----------------------------

-- ----------------------------
-- Table structure for player
-- ----------------------------
DROP TABLE IF EXISTS `player`;
CREATE TABLE `player` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '账号',
  `password` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '密码',
  `nickname` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '昵称',
  `level` int NOT NULL DEFAULT '1' COMMENT '玩家等级(1-100)',
  `exp` int NOT NULL DEFAULT '0' COMMENT '当前经验值',
  `gold` int NOT NULL DEFAULT '0' COMMENT '金币',
  `yuanbao` int NOT NULL DEFAULT '0' COMMENT '元宝',
  `silver_diamond` int NOT NULL DEFAULT '0' COMMENT '宝石',
  `dice` int NOT NULL DEFAULT '0' COMMENT '骰子数量',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `prestige` int NOT NULL DEFAULT '0' COMMENT '当前声望',
  `cultivation_start` datetime DEFAULT NULL COMMENT '修行开始时间',
  `cultivation_duration` int DEFAULT '0' COMMENT '修行时长(秒)',
  `cultivation_reward` int DEFAULT '0' COMMENT '修行预计奖励声望',
  `location` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT '落龙镇',
  `last_signin_date` date DEFAULT NULL COMMENT '上次签到日期',
  `consecutive_signin_days` int NOT NULL DEFAULT '0' COMMENT '连续签到天数',
  `last_map_move_at` datetime DEFAULT NULL,
  `moving_to` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `is_summon_king` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否是召唤之王（1=是）',
  `enhancement_stone` int NOT NULL DEFAULT '0' COMMENT 'enhancement stone',
  `vip_level` int DEFAULT '0',
  `vip_exp` int DEFAULT '0',
  `crystal_tower` int DEFAULT '0' COMMENT '水晶塔活力值',
  `charm` int DEFAULT '0' COMMENT '魅力值',
  `energy` int DEFAULT '100' COMMENT '活力值',
  `last_energy_recovery_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '上次体力恢复时间',
  `cultivation_start_time` datetime DEFAULT NULL,
  `cultivation_area` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `cultivation_dungeon` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `last_dice_grant_date` date DEFAULT NULL,
  `inspire_expire_time` datetime DEFAULT NULL,
  `first_recharge_claimed` tinyint DEFAULT '0' COMMENT '首充是否已领取',
  PRIMARY KEY (`user_id`) USING BTREE,
  UNIQUE KEY `uk_username` (`username`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=4057 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='玩家基础信息表';

-- ----------------------------
-- Records of player
-- ----------------------------
INSERT INTO `player` VALUES ('4053', '123', '1234', '123', '22', '0', '1524', '0', '0', '0', '2026-01-09 14:47:08', '2026-01-11 09:40:25', '0', null, '0', '0', '林中空地', '2026-01-09', '1', null, null, '0', '0', '0', '0', '0', '0', '100', '2026-01-11 17:35:48', null, null, null, null, null, '0');
INSERT INTO `player` VALUES ('4054', 'abc', 'acbd', 'abc', '1', '0', '450000', '0', '0', '0', '2026-01-09 15:21:40', '2026-01-11 09:43:53', '0', null, '0', '0', '林中空地', null, '0', null, null, '0', '0', '0', '0', '0', '0', '100', '2026-01-11 17:43:53', null, null, null, null, null, '0');
INSERT INTO `player` VALUES ('4055', '789', '7890', '789', '25', '0', '1249724', '3688', '0', '12', '2026-01-10 12:44:54', '2026-01-11 09:44:32', '0', null, '0', '0', '林中空地', '2026-01-10', '1', null, null, '0', '0', '0', '0', '0', '0', '100', '2026-01-11 17:42:24', null, null, null, '2026-01-10', null, '0');
INSERT INTO `player` VALUES ('4056', '456', '4567', '456', '35', '0', '20100', '0', '0', '0', '2026-01-10 13:56:20', '2026-01-11 09:36:02', '0', null, '0', '0', '林中空地', null, '0', null, null, '0', '0', '0', '0', '0', '0', '100', '2026-01-11 17:36:02', null, null, null, null, null, '0');

-- ----------------------------
-- Table structure for player_bag
-- ----------------------------
DROP TABLE IF EXISTS `player_bag`;
CREATE TABLE `player_bag` (
  `user_id` int NOT NULL,
  `bag_level` int NOT NULL DEFAULT '1' COMMENT '背包等级 1-10',
  `capacity` int NOT NULL DEFAULT '50' COMMENT '背包容量（格子数）',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='玩家背包信息表';

-- ----------------------------
-- Records of player_bag
-- ----------------------------
INSERT INTO `player_bag` VALUES ('4053', '1', '100', '2026-01-09 14:47:08', '2026-01-09 14:47:08');
INSERT INTO `player_bag` VALUES ('4054', '1', '100', '2026-01-09 15:21:40', '2026-01-09 15:21:40');
INSERT INTO `player_bag` VALUES ('4055', '1', '100', '2026-01-10 12:44:55', '2026-01-10 12:44:55');
INSERT INTO `player_bag` VALUES ('4056', '1', '100', '2026-01-10 13:56:21', '2026-01-10 13:56:21');

-- ----------------------------
-- Table structure for player_beast
-- ----------------------------
DROP TABLE IF EXISTS `player_beast`;
CREATE TABLE `player_beast` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `template_id` int NOT NULL DEFAULT '0',
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '幻兽名称',
  `nickname` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '幻兽昵称（可自定义）',
  `realm` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '境界(神界/天界等)',
  `race` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT '' COMMENT '种族(虫族/龙族等)',
  `level` int NOT NULL DEFAULT '1' COMMENT '等级',
  `exp` int NOT NULL DEFAULT '0' COMMENT '当前经验',
  `nature` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '物系' COMMENT '特性(法系普攻/物系普攻等)',
  `personality` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT '' COMMENT '性格',
  `hp` int NOT NULL COMMENT '气血',
  `physical_attack` int NOT NULL COMMENT '物攻',
  `magic_attack` int NOT NULL COMMENT '法攻',
  `physical_defense` int NOT NULL COMMENT '物防',
  `magic_defense` int NOT NULL COMMENT '法防',
  `speed` int NOT NULL COMMENT '速度',
  `combat_power` int DEFAULT '0' COMMENT '综合战力',
  `growth_rate` int DEFAULT '0' COMMENT '成长率',
  `hp_aptitude` int DEFAULT '0' COMMENT '气血资质',
  `speed_aptitude` int DEFAULT '0' COMMENT '速度资质',
  `physical_attack_aptitude` int DEFAULT '0' COMMENT '物攻资质',
  `magic_attack_aptitude` int DEFAULT '0' COMMENT '法攻资质',
  `physical_defense_aptitude` int DEFAULT '0' COMMENT '物防资质',
  `magic_defense_aptitude` int DEFAULT '0' COMMENT '法防资质',
  `lifespan` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT '10000/10000' COMMENT '寿命',
  `skills` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '技能列表(JSON格式)',
  `counters` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT '' COMMENT '克制',
  `countered_by` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT '' COMMENT '被克',
  `attack_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'physical' COMMENT '攻击类型（physical/magic）',
  `is_in_team` tinyint(1) DEFAULT '0' COMMENT '是否在战斗队',
  `team_position` int DEFAULT '0' COMMENT '战斗队位置',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_user_team` (`user_id`,`is_in_team`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=752 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='玩家幻兽表';

-- ----------------------------
-- Records of player_beast
-- ----------------------------
INSERT INTO `player_beast` VALUES ('747', '4055', '3', '血螳螂', '血螳螂', '地界', '', '1', '0', '物系', '勇敢', '14', '11', '0', '10', '10', '1', '8', '860', '497', '580', '761', '0', '431', '394', '10000/10000', '[\"高级吸血\"]', '', '', 'physical', '1', '1', '2026-01-10 13:43:07', '2026-01-11 09:43:16');
INSERT INTO `player_beast` VALUES ('748', '4053', '3', '血螳螂', '血螳螂', '地界', '', '1', '0', '物系', '胆小', '15', '11', '0', '10', '10', '1', '8', '860', '520', '657', '739', '0', '586', '398', '10000/10000', '[\"幸运\"]', '', '', 'physical', '1', '0', '2026-01-10 13:43:43', '2026-01-10 13:43:45');
INSERT INTO `player_beast` VALUES ('749', '4056', '9', '羽精灵', '羽精灵', '地界', '', '1', '0', '物系', '勇敢', '22', '0', '10', '10', '11', '1', '8', '860', '744', '842', '0', '451', '171', '841', '10000/10000', '[]', '', '', 'magic', '1', '0', '2026-01-10 14:00:50', '2026-01-10 14:00:53');
INSERT INTO `player_beast` VALUES ('750', '4055', '9', '羽精灵', '羽精灵', '地界', '', '1', '0', '物系', '精明', '26', '0', '10', '10', '14', '1', '10', '860', '882', '527', '0', '636', '153', '1043', '10000/10000', '[]', '', '', 'magic', '0', '0', '2026-01-10 19:56:29', '2026-01-10 19:56:38');
INSERT INTO `player_beast` VALUES ('751', '4055', '6', '追风狼', '追风狼', '地界', '', '1', '0', '物系', '胆小', '15', '10', '0', '11', '10', '1', '8', '860', '529', '729', '592', '0', '844', '731', '10000/10000', '[]', '', '', 'physical', '1', '0', '2026-01-10 19:56:33', '2026-01-11 09:43:16');

-- ----------------------------
-- Table structure for player_daily_activity
-- ----------------------------
DROP TABLE IF EXISTS `player_daily_activity`;
CREATE TABLE `player_daily_activity` (
  `user_id` int NOT NULL,
  `activity_value` int DEFAULT '0',
  `last_updated_date` date DEFAULT NULL,
  `completed_tasks` json DEFAULT NULL,
  PRIMARY KEY (`user_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Records of player_daily_activity
-- ----------------------------
INSERT INTO `player_daily_activity` VALUES ('4055', '10', '2026-01-10',null);

-- ----------------------------
-- Table structure for player_dungeon_progress
-- ----------------------------
DROP TABLE IF EXISTS `player_dungeon_progress`;
CREATE TABLE `player_dungeon_progress` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `dungeon_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `current_floor` int DEFAULT '1',
  `total_floors` int DEFAULT '35',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `floor_cleared` tinyint(1) DEFAULT '1',
  `floor_event_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT 'beast',
  `loot_claimed` tinyint(1) DEFAULT '1',
  `resets_today` int DEFAULT '0',
  `last_reset_date` date DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_user_dungeon` (`user_id`,`dungeon_name`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=115 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Records of player_dungeon_progress
-- ----------------------------
INSERT INTO `player_dungeon_progress` VALUES ('113', '4055', '森林入口', '9', '35', '2026-01-10 13:08:05', '2026-01-10 13:08:23', '0', 'beast', '1', '0', null);

-- ----------------------------
-- Table structure for player_effect
-- ----------------------------
DROP TABLE IF EXISTS `player_effect`;
CREATE TABLE `player_effect` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `effect_key` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `end_time` datetime NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_user_effect` (`user_id`,`effect_key`) USING BTREE,
  KEY `idx_end_time` (`end_time`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Records of player_effect
-- ----------------------------

-- ----------------------------
-- Table structure for player_gift_claim
-- ----------------------------
DROP TABLE IF EXISTS `player_gift_claim`;
CREATE TABLE `player_gift_claim` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `gift_key` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `claimed_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_user_gift` (`user_id`,`gift_key`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Records of player_gift_claim
-- ----------------------------
INSERT INTO `player_gift_claim` VALUES ('1', '4055', 'beta_luxury', '2026-01-10 13:09:18');
INSERT INTO `player_gift_claim` VALUES ('2', '4055', 'dragon_palace_compensation', '2026-01-10 13:09:22');

-- ----------------------------
-- Table structure for player_immortalize_pool
-- ----------------------------
DROP TABLE IF EXISTS `player_immortalize_pool`;
CREATE TABLE `player_immortalize_pool` (
  `user_id` int NOT NULL COMMENT '玩家ID',
  `pool_level` tinyint NOT NULL DEFAULT '1' COMMENT '化仙池等级',
  `current_exp` bigint NOT NULL DEFAULT '0' COMMENT '化仙池当前可用经验',
  `formation_level` tinyint NOT NULL DEFAULT '0' COMMENT '化仙阵等级',
  `formation_started_at` datetime DEFAULT NULL COMMENT '化仙阵开始时间',
  `formation_ends_at` datetime DEFAULT NULL COMMENT '化仙阵结束时间',
  `formation_last_grant_at` datetime DEFAULT NULL COMMENT '化仙阵最近一次结算时间',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='玩家化仙池状态';

-- ----------------------------
-- Records of player_immortalize_pool
-- ----------------------------
INSERT INTO `player_immortalize_pool` VALUES ('4053', '1', '0', '0', null, null, null, '2026-01-09 22:12:23', '2026-01-09 22:12:23');
INSERT INTO `player_immortalize_pool` VALUES ('4055', '1', '0', '0', null, null, null, '2026-01-10 12:51:18', '2026-01-10 12:51:18');

-- ----------------------------
-- Table structure for player_inventory
-- ----------------------------
DROP TABLE IF EXISTS `player_inventory`;
CREATE TABLE `player_inventory` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `item_id` int NOT NULL COMMENT '物品ID',
  `quantity` int NOT NULL DEFAULT '1' COMMENT '数量',
  `is_temporary` tinyint NOT NULL DEFAULT '0' COMMENT '是否临时存放（0=正式，1=临时）',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_user_item_temp` (`user_id`,`item_id`,`is_temporary`) USING BTREE,
  KEY `idx_user_id` (`user_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=2584 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='玩家背包表';

-- ----------------------------
-- Records of player_inventory
-- ----------------------------
INSERT INTO `player_inventory` VALUES ('2544', '4053', '20006', '1', '0', '2026-01-09 14:47:08', '2026-01-09 14:47:08');
INSERT INTO `player_inventory` VALUES ('2545', '4053', '20009', '1', '0', '2026-01-09 14:47:08', '2026-01-09 14:47:08');
INSERT INTO `player_inventory` VALUES ('2546', '4054', '20003', '1', '0', '2026-01-09 15:21:40', '2026-01-09 15:21:40');
INSERT INTO `player_inventory` VALUES ('2547', '4054', '20006', '1', '0', '2026-01-09 15:21:40', '2026-01-09 15:21:40');
INSERT INTO `player_inventory` VALUES ('2548', '4054', '20009', '1', '0', '2026-01-09 15:21:40', '2026-01-09 15:21:40');
INSERT INTO `player_inventory` VALUES ('2549', '4053', '4002', '1', '0', '2026-01-10 12:27:06', '2026-01-11 09:40:25');
INSERT INTO `player_inventory` VALUES ('2553', '4055', '4002', '13', '0', '2026-01-10 12:45:17', '2026-01-10 19:46:21');
INSERT INTO `player_inventory` VALUES ('2554', '4055', '91001', '1', '0', '2026-01-10 13:09:04', '2026-01-10 13:09:04');
INSERT INTO `player_inventory` VALUES ('2555', '4055', '4001', '1', '0', '2026-01-10 13:09:15', '2026-01-10 13:09:15');
INSERT INTO `player_inventory` VALUES ('2556', '4055', '4003', '4', '0', '2026-01-10 13:09:15', '2026-01-10 13:09:17');
INSERT INTO `player_inventory` VALUES ('2557', '4055', '6010', '3', '0', '2026-01-10 13:09:15', '2026-01-10 13:09:17');
INSERT INTO `player_inventory` VALUES ('2558', '4055', '6015', '1', '0', '2026-01-10 13:09:15', '2026-01-10 13:09:15');
INSERT INTO `player_inventory` VALUES ('2559', '4055', '3011', '99', '0', '2026-01-10 13:09:17', '2026-01-10 13:09:20');
INSERT INTO `player_inventory` VALUES ('2560', '4055', '1005', '2', '0', '2026-01-10 13:09:18', '2026-01-10 13:09:17');
INSERT INTO `player_inventory` VALUES ('2561', '4055', '1002', '4', '0', '2026-01-10 13:09:18', '2026-01-10 13:09:17');
INSERT INTO `player_inventory` VALUES ('2562', '4055', '1006', '3', '0', '2026-01-10 13:09:18', '2026-01-10 13:09:17');
INSERT INTO `player_inventory` VALUES ('2563', '4055', '1001', '1', '0', '2026-01-10 13:09:18', '2026-01-10 13:09:17');
INSERT INTO `player_inventory` VALUES ('2564', '4055', '6033', '1', '0', '2026-01-10 13:09:18', '2026-01-10 13:09:17');
INSERT INTO `player_inventory` VALUES ('2565', '4055', '6001', '2', '0', '2026-01-10 13:09:18', '2026-01-10 13:09:18');
INSERT INTO `player_inventory` VALUES ('2566', '4055', '6007', '1', '0', '2026-01-10 13:09:18', '2026-01-10 13:09:18');
INSERT INTO `player_inventory` VALUES ('2567', '4055', '6003', '5', '0', '2026-01-10 13:09:21', '2026-01-10 13:09:20');
INSERT INTO `player_inventory` VALUES ('2569', '4055', '3012', '7', '0', '2026-01-10 13:09:23', '2026-01-10 13:09:22');
INSERT INTO `player_inventory` VALUES ('2570', '4055', '3014', '3', '0', '2026-01-10 13:09:23', '2026-01-10 13:09:22');
INSERT INTO `player_inventory` VALUES ('2572', '4056', '20003', '1', '0', '2026-01-10 13:56:21', '2026-01-10 13:56:21');
INSERT INTO `player_inventory` VALUES ('2573', '4056', '20006', '1', '0', '2026-01-10 13:56:21', '2026-01-10 13:56:21');
INSERT INTO `player_inventory` VALUES ('2575', '4055', '5001', '40', '0', '2026-01-10 15:59:11', '2026-01-10 15:59:10');
INSERT INTO `player_inventory` VALUES ('2576', '4055', '5002', '25', '0', '2026-01-10 15:59:11', '2026-01-10 15:59:11');

-- ----------------------------
-- Table structure for player_manor
-- ----------------------------
DROP TABLE IF EXISTS `player_manor`;
CREATE TABLE `player_manor` (
  `user_id` int NOT NULL,
  `total_harvest_count` int DEFAULT '0' COMMENT '累计收获次数',
  `total_gold_earned` bigint DEFAULT '0' COMMENT '累计获得铜钱',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='玩家庄园扩展表';

-- ----------------------------
-- Records of player_manor
-- ----------------------------

-- ----------------------------
-- Table structure for player_month_card
-- ----------------------------
DROP TABLE IF EXISTS `player_month_card`;
CREATE TABLE `player_month_card` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `month` tinyint unsigned NOT NULL,
  `start_date` datetime NOT NULL,
  `end_date` datetime NOT NULL,
  `days_total` smallint unsigned NOT NULL DEFAULT '30',
  `days_claimed` smallint unsigned NOT NULL DEFAULT '0',
  `last_claim_date` date DEFAULT NULL,
  `status` enum('pending','active','expired') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'active',
  `initial_reward` int NOT NULL DEFAULT '1000',
  `daily_reward` int NOT NULL DEFAULT '200',
  `initial_reward_claimed` tinyint(1) NOT NULL DEFAULT '0',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uniq_user_month` (`user_id`,`month`) USING BTREE,
  KEY `idx_user_status` (`user_id`,`status`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Records of player_month_card
-- ----------------------------

-- ----------------------------
-- Table structure for player_mosoul
-- ----------------------------
DROP TABLE IF EXISTS `player_mosoul`;
CREATE TABLE `player_mosoul` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `template_id` int NOT NULL,
  `level` int NOT NULL DEFAULT '1',
  `exp` int NOT NULL DEFAULT '0',
  `beast_id` int DEFAULT NULL,
  `slot_index` tinyint unsigned DEFAULT NULL COMMENT '槽位索引（1-8）',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_beast_slot` (`beast_id`,`slot_index`) USING BTREE,
  KEY `idx_user_id` (`user_id`) USING BTREE,
  KEY `idx_beast_id` (`beast_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=596 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Records of player_mosoul
-- ----------------------------

-- ----------------------------
-- Table structure for player_spirit
-- ----------------------------
DROP TABLE IF EXISTS `player_spirit`;
CREATE TABLE `player_spirit` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL COMMENT '玩家ID',
  `beast_id` int DEFAULT NULL COMMENT '装备到的幻兽ID（未装备时为NULL）',
  `element` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '元素：earth/fire/water/wood/metal/god',
  `race` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '种族：兽族/龙族/虫族/飞禽/神兽等',
  `line1_attr` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `line1_value_bp` int NOT NULL DEFAULT '0',
  `line1_unlocked` tinyint NOT NULL DEFAULT '0',
  `line1_locked` tinyint NOT NULL DEFAULT '0',
  `line2_attr` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `line2_value_bp` int NOT NULL DEFAULT '0',
  `line2_unlocked` tinyint NOT NULL DEFAULT '0',
  `line2_locked` tinyint NOT NULL DEFAULT '0',
  `line3_attr` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `line3_value_bp` int NOT NULL DEFAULT '0',
  `line3_unlocked` tinyint NOT NULL DEFAULT '0',
  `line3_locked` tinyint NOT NULL DEFAULT '0',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_user_id` (`user_id`) USING BTREE,
  KEY `idx_beast_id` (`beast_id`) USING BTREE,
  KEY `idx_user_beast` (`user_id`,`beast_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=172 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='玩家战灵';

-- ----------------------------
-- Records of player_spirit
-- ----------------------------

-- ----------------------------
-- Table structure for player_talent_levels
-- ----------------------------
DROP TABLE IF EXISTS `player_talent_levels`;
CREATE TABLE `player_talent_levels` (
  `user_id` int NOT NULL,
  `talent_key` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `level` int DEFAULT '0',
  PRIMARY KEY (`user_id`,`talent_key`) USING BTREE,
  CONSTRAINT `player_talent_levels_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `player` (`user_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Records of player_talent_levels
-- ----------------------------

-- ----------------------------
-- Table structure for private_message
-- ----------------------------
DROP TABLE IF EXISTS `private_message`;
CREATE TABLE `private_message` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sender_id` int NOT NULL,
  `sender_name` varchar(50) NOT NULL,
  `receiver_id` int NOT NULL,
  `receiver_name` varchar(50) NOT NULL,
  `content` varchar(200) NOT NULL,
  `is_read` tinyint(1) NOT NULL DEFAULT '0',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_sender` (`sender_id`),
  KEY `idx_receiver` (`receiver_id`),
  KEY `idx_receiver_created` (`receiver_id`,`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of private_message
-- ----------------------------
INSERT INTO `private_message` VALUES ('1', '4054', 'abc', '4053', '123', '你好，能带我打副本吗？', '0', '2026-01-11 08:09:09');
INSERT INTO `private_message` VALUES ('2', '4053', '123', '4054', 'abc', '可以啊，等我一下', '1', '2026-01-11 08:14:09');
INSERT INTO `private_message` VALUES ('3', '4054', 'abc', '4053', '123', '好的，谢谢！', '0', '2026-01-11 08:19:09');
INSERT INTO `private_message` VALUES ('4', '4055', '789', '4053', '123', '大佬，求指导！', '1', '2026-01-11 08:39:09');
INSERT INTO `private_message` VALUES ('5', '4056', '456', '4054', 'abc', '组队吗？', '0', '2026-01-11 08:49:09');

-- ----------------------------
-- Table structure for recharge_order
-- ----------------------------
DROP TABLE IF EXISTS `recharge_order`;
CREATE TABLE `recharge_order` (
  `id` int NOT NULL AUTO_INCREMENT,
  `out_trade_no` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '商户订单号',
  `trade_no` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '支付宝交易号',
  `user_id` int NOT NULL COMMENT '用户ID',
  `product_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '商品ID',
  `amount` decimal(10,2) NOT NULL COMMENT '支付金额(元)',
  `status` enum('pending','paid','failed','refunded') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT 'pending' COMMENT '订单状态',
  `yuanbao_granted` int DEFAULT '0' COMMENT '发放的宝石数量',
  `bonus_granted` int DEFAULT '0' COMMENT '首充奖励宝石',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `paid_at` datetime DEFAULT NULL COMMENT '支付时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `out_trade_no` (`out_trade_no`) USING BTREE,
  KEY `idx_user_id` (`user_id`) USING BTREE,
  KEY `idx_status` (`status`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='充值订单表';

-- ----------------------------
-- Records of recharge_order
-- ----------------------------

-- ----------------------------
-- Table structure for refine_pot_log
-- ----------------------------
DROP TABLE IF EXISTS `refine_pot_log`;
CREATE TABLE `refine_pot_log` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT '记录ID',
  `user_id` bigint unsigned NOT NULL COMMENT '玩家ID',
  `main_beast_id` bigint unsigned NOT NULL COMMENT '主幻兽ID',
  `material_beast_id` bigint unsigned NOT NULL COMMENT '副幻兽ID',
  `attr_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性类型',
  `before_value` int NOT NULL COMMENT '炼妖前属性值',
  `after_value` int NOT NULL COMMENT '炼妖后属性值',
  `delta` int NOT NULL COMMENT '属性变化值',
  `diff_x` int NOT NULL COMMENT '属性差值',
  `cost_gold` int unsigned NOT NULL DEFAULT '0' COMMENT '消耗铜钱',
  `cost_pill` int unsigned NOT NULL DEFAULT '0' COMMENT '消耗炼魂丹',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_user_id` (`user_id`) USING BTREE,
  KEY `idx_main_beast_id` (`main_beast_id`) USING BTREE,
  KEY `idx_created_at` (`created_at`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='炼妖日志表';

-- ----------------------------
-- Records of refine_pot_log
-- ----------------------------

-- ----------------------------
-- Table structure for spar_battle_log
-- ----------------------------
DROP TABLE IF EXISTS `spar_battle_log`;
CREATE TABLE `spar_battle_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `attacker_id` int NOT NULL,
  `attacker_name` varchar(50) NOT NULL,
  `defender_id` int NOT NULL,
  `defender_name` varchar(50) NOT NULL,
  `is_attacker_win` tinyint NOT NULL DEFAULT '0',
  `battle_data` text,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_attacker` (`attacker_id`),
  KEY `idx_defender` (`defender_id`),
  KEY `idx_created` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of spar_battle_log
-- ----------------------------
INSERT INTO `spar_battle_log` VALUES ('1', '4053', '123', '4054', 'abc', '1', '{\"rounds\": 3, \"winner_hp\": 500}', '2026-01-11 06:09:33');
INSERT INTO `spar_battle_log` VALUES ('2', '4055', '789', '4053', '123', '0', '{\"rounds\": 5, \"winner_hp\": 200}', '2026-01-11 07:09:33');
INSERT INTO `spar_battle_log` VALUES ('3', '4054', 'abc', '4056', '456', '1', '{\"rounds\": 2, \"winner_hp\": 800}', '2026-01-11 08:09:33');

-- ----------------------------
-- Table structure for spar_records
-- ----------------------------
DROP TABLE IF EXISTS `spar_records`;
CREATE TABLE `spar_records` (
  `id` int NOT NULL AUTO_INCREMENT,
  `attacker_id` int NOT NULL COMMENT '发起切磋的玩家ID',
  `defender_id` int NOT NULL COMMENT '被切磋的玩家ID',
  `is_victory` tinyint(1) NOT NULL DEFAULT '0' COMMENT '发起者是否胜利',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '切磋时间',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_attacker` (`attacker_id`) USING BTREE,
  KEY `idx_defender` (`defender_id`) USING BTREE,
  KEY `idx_created` (`created_at`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='切磋战绩记录';

-- ----------------------------
-- Records of spar_records
-- ----------------------------
INSERT INTO `spar_records` VALUES ('1', '4055', '4053', '0', '2026-01-10 19:01:35');
INSERT INTO `spar_records` VALUES ('2', '4055', '4053', '0', '2026-01-10 19:05:16');
INSERT INTO `spar_records` VALUES ('3', '4055', '4056', '0', '2026-01-10 19:16:34');
INSERT INTO `spar_records` VALUES ('4', '4055', '4053', '0', '2026-01-10 19:25:06');
INSERT INTO `spar_records` VALUES ('5', '4055', '4053', '0', '2026-01-10 19:33:49');
INSERT INTO `spar_records` VALUES ('6', '4055', '4053', '1', '2026-01-10 19:56:54');

-- ----------------------------
-- Table structure for spirit_account
-- ----------------------------
DROP TABLE IF EXISTS `spirit_account`;
CREATE TABLE `spirit_account` (
  `user_id` int NOT NULL,
  `spirit_power` int NOT NULL DEFAULT '0' COMMENT '灵力',
  `unlocked_elements` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '已解锁元素列表(JSON)',
  `free_refine_date` date DEFAULT NULL COMMENT '当日免费洗练计数对应日期',
  `free_refine_used` int NOT NULL DEFAULT '0' COMMENT '当日已使用免费洗练次数',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='战灵账户';

-- ----------------------------
-- Records of spirit_account
-- ----------------------------
INSERT INTO `spirit_account` VALUES ('4054', '0', '[]', null, '0', '2026-01-09 20:32:01', '2026-01-09 20:32:01');

-- ----------------------------
-- Table structure for task_reward_claims
-- ----------------------------
DROP TABLE IF EXISTS `task_reward_claims`;
CREATE TABLE `task_reward_claims` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int unsigned NOT NULL,
  `reward_key` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `claimed_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uniq_user_reward` (`user_id`,`reward_key`) USING BTREE,
  KEY `idx_reward_key` (`reward_key`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='任务奖励领取记录';

-- ----------------------------
-- Records of task_reward_claims
-- ----------------------------

-- ----------------------------
-- Table structure for tower_state
-- ----------------------------
DROP TABLE IF EXISTS `tower_state`;
CREATE TABLE `tower_state` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `tower_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'tongtian',
  `current_floor` int NOT NULL DEFAULT '1',
  `max_floor_record` int NOT NULL DEFAULT '1',
  `today_count` int NOT NULL DEFAULT '0',
  `last_challenge_date` date DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_user_tower` (`user_id`,`tower_type`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=374 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='闯塔状态表';

-- ----------------------------
-- Records of tower_state
-- ----------------------------
INSERT INTO `tower_state` VALUES ('371', '4054', 'tongtian', '1', '1', '0', null, '2026-01-09 19:48:21', '2026-01-09 19:48:21');
INSERT INTO `tower_state` VALUES ('372', '4053', 'tongtian', '1', '1', '0', null, '2026-01-09 22:12:08', '2026-01-09 22:12:08');
INSERT INTO `tower_state` VALUES ('373', '4055', 'tongtian', '1', '1', '0', null, '2026-01-10 13:08:33', '2026-01-10 13:08:33');

-- ----------------------------
-- Table structure for tree_player_week
-- ----------------------------
DROP TABLE IF EXISTS `tree_player_week`;
CREATE TABLE `tree_player_week` (
  `user_id` int NOT NULL,
  `week_start` date NOT NULL COMMENT '周一日期（与 tree_week.week_start 对齐）',
  `my_numbers_json` text COMMENT '玩家本周数字 JSON 数组（最多7个）',
  `last_draw_date` date DEFAULT NULL COMMENT '上次领取数字日期（用于每日一次）',
  `claimed_at` datetime DEFAULT NULL COMMENT '领奖时间（周日一次）',
  `claim_star` int NOT NULL DEFAULT '0' COMMENT '领奖星级（1~5；未领奖为0）',
  `match_count` int NOT NULL DEFAULT '0' COMMENT '命中数量（0~7）',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `red_numbers_json` text COMMENT '本周红果实数字 JSON 数组（最多6个）',
  `blue_number` int DEFAULT NULL COMMENT '本周蓝果实数字（周日领取）',
  PRIMARY KEY (`user_id`,`week_start`),
  KEY `idx_tree_player_week_week` (`week_start`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='古树玩家每周记录';

-- ----------------------------
-- Records of tree_player_week
-- ----------------------------
INSERT INTO `tree_player_week` VALUES ('4053', '2026-01-05', '[67]', '2026-01-11', null, '0', '0', '2026-01-11 09:16:54', '[]', '67');
INSERT INTO `tree_player_week` VALUES ('4054', '2026-01-05', '[78]', '2026-01-09', null, '0', '0', '2026-01-09 23:02:00', '[78]', null);
INSERT INTO `tree_player_week` VALUES ('4055', '2026-01-05', '[25]', '2026-01-11', null, '0', '0', '2026-01-11 09:44:59', '[]', '25');

-- ----------------------------
-- Table structure for tree_week
-- ----------------------------
DROP TABLE IF EXISTS `tree_week`;
CREATE TABLE `tree_week` (
  `week_start` date NOT NULL COMMENT '周一日期（该周的 week_start）',
  `winning_numbers_json` text COMMENT '开奖数字 JSON 数组（7个，0~100）',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `announce_date` date DEFAULT NULL COMMENT '公布日期（下周一）',
  `winning_red_numbers_json` text COMMENT '当周幸运红果实数字 JSON 数组（6个）',
  `winning_blue_number` int DEFAULT NULL COMMENT '当周幸运蓝果实数字（01~100）',
  PRIMARY KEY (`week_start`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='古树每周开奖信息';

-- ----------------------------
-- Records of tree_week
-- ----------------------------
INSERT INTO `tree_week` VALUES ('2025-12-29', '[87, 68, 9, 99, 91, 1, 65]', '2026-01-09 22:59:56', '2026-01-05', '[87, 68, 9, 99, 91, 1]', '65');

-- ----------------------------
-- Table structure for world_chat_message
-- ----------------------------
DROP TABLE IF EXISTS `world_chat_message`;
CREATE TABLE `world_chat_message` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `nickname` varchar(50) NOT NULL,
  `message_type` varchar(20) NOT NULL DEFAULT 'normal',
  `content` varchar(200) NOT NULL,
  `is_pinned` tinyint(1) NOT NULL DEFAULT '0',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user` (`user_id`),
  KEY `idx_type_created` (`message_type`,`created_at`),
  KEY `idx_pinned` (`is_pinned`,`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of world_chat_message
-- ----------------------------
INSERT INTO `world_chat_message` VALUES ('1', '4053', '123', 'normal', '大家好，我是新来的召唤师！', '0', '2026-01-11 07:08:59');
INSERT INTO `world_chat_message` VALUES ('2', '4054', 'abc', 'normal', '有没有人组队打副本？', '0', '2026-01-11 08:08:59');
INSERT INTO `world_chat_message` VALUES ('3', '4055', '789', 'normal', '今天运气不错，抽到了稀有幻兽！', '0', '2026-01-11 08:38:59');
INSERT INTO `world_chat_message` VALUES ('4', '4056', '456', 'normal', '求带新手过塔！', '0', '2026-01-11 08:53:59');
INSERT INTO `world_chat_message` VALUES ('5', '4053', '123', 'summon_king', '我是召唤之王，欢迎挑战！', '1', '2026-01-11 09:08:59');

-- ----------------------------
-- Table structure for zhenyao_battle_log
-- ----------------------------
DROP TABLE IF EXISTS `zhenyao_battle_log`;
CREATE TABLE `zhenyao_battle_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `floor` int NOT NULL COMMENT '层数',
  `attacker_id` int NOT NULL COMMENT '挑战者ID',
  `attacker_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '挑战者昵称',
  `defender_id` int NOT NULL COMMENT '被挑战者ID',
  `defender_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '被挑战者昵称',
  `is_success` tinyint NOT NULL DEFAULT '0' COMMENT '是否成功(1=成功,0=失败)',
  `remaining_seconds` int NOT NULL DEFAULT '0' COMMENT '剩余秒数(挑战时)',
  `battle_data` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '战斗详情(JSON)',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_floor` (`floor`) USING BTREE,
  KEY `idx_attacker` (`attacker_id`) USING BTREE,
  KEY `idx_defender` (`defender_id`) USING BTREE,
  KEY `idx_created` (`created_at`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=67 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='镇妖挑战记录表';

-- ----------------------------
-- Records of zhenyao_battle_log
-- ----------------------------

-- ----------------------------
-- Table structure for zhenyao_daily_count
-- ----------------------------
DROP TABLE IF EXISTS `zhenyao_daily_count`;
CREATE TABLE `zhenyao_daily_count` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `trial_count` int NOT NULL DEFAULT '0' COMMENT '试炼层已用次数',
  `hell_count` int NOT NULL DEFAULT '0' COMMENT '炼狱层已用次数',
  `count_date` date NOT NULL COMMENT '统计日期',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_user_date` (`user_id`,`count_date`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='镇妖每日次数表';

-- ----------------------------
-- Records of zhenyao_daily_count
-- ----------------------------

-- ----------------------------
-- Table structure for zhenyao_floor
-- ----------------------------
DROP TABLE IF EXISTS `zhenyao_floor`;
CREATE TABLE `zhenyao_floor` (
  `id` int NOT NULL AUTO_INCREMENT,
  `floor` int NOT NULL COMMENT '层数(1-120)',
  `occupant_id` int DEFAULT NULL COMMENT '占领者ID',
  `occupant_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT '' COMMENT '占领者昵称',
  `occupy_time` datetime DEFAULT NULL COMMENT '占领时间',
  `expire_time` datetime DEFAULT NULL COMMENT '到期时间',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `rewarded` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_floor` (`floor`) USING BTREE,
  KEY `idx_occupant` (`occupant_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=481 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='镇妖占领表';

-- ----------------------------
-- Records of zhenyao_floor
-- ----------------------------
