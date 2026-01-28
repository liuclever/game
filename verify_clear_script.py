#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证清除脚本的完整性
"""

# 数据库备份中的所有表
all_tables_in_db = set("""
activity_claims
activity_finalize_log
activity_power_ranking_reward
activity_wheel_lottery
alliance_activities
alliance_army_assignments
alliance_army_signups
alliance_beast_storage
alliance_buildings
alliance_chat_messages
alliance_competition_battles
alliance_competition_personal_battles
alliance_competition_personal_scores
alliance_competition_prestige
alliance_competition_registrations
alliance_competition_rewards
alliance_competition_scores
alliance_competition_sessions
alliance_competition_signups
alliance_competition_team_members
alliance_competition_teams
alliance_item_storage
alliance_land_battle
alliance_land_battle_duel
alliance_land_battle_round
alliance_land_occupation
alliance_land_registration
alliance_members
alliance_quit_records
alliance_talents
alliance_training_participants
alliance_training_rooms
alliance_war_battle_records
alliance_war_checkin
alliance_war_honor_effects
alliance_war_honor_exchange
alliance_war_scores
alliance_war_session_config
alliances
arena
arena_battle_log
arena_daily_challenge
arena_stats
arena_streak
arena_streak_history
battlefield_battle_log
battlefield_signup
beast_bone
blacklist
cultivation_config
dragonpalace_daily_state
fortune_talisman_daily
friend_relation
friend_request
king_challenge_logs
king_challenge_rank
king_final_stage
king_reward_claimed
king_season_config
lands
level_config
manor_land
mosoul_global_pity
mosoul_hunting_state
player
player_bag
player_beast
player_chest_counter
player_daily_activity
player_diamond_exchange_log
player_dungeon_progress
player_effect
player_exchange_claim
player_gift_claim
player_immortalize_pool
player_inventory
player_manor
player_month_card
player_mosoul
player_shop_daily_purchase
player_signin_records
player_spirit
player_talent_levels
private_message
recharge_order
refine_pot_log
spar_battle_log
spar_records
spirit_account
task_reward_claims
tower_state
tree_player_week
tree_week
world_chat_message
zhenyao_battle_log
zhenyao_daily_count
zhenyao_floor
""".strip().split('\n'))

# 更新后的清除脚本中要清除的表
cleared_tables_updated = set("""
alliance_competition_sessions
alliance_competition_registrations
alliance_competition_teams
alliance_competition_signups
alliance_competition_team_members
alliance_competition_battles
alliance_competition_personal_battles
alliance_competition_scores
alliance_competition_personal_scores
alliance_competition_prestige
alliance_competition_rewards
alliance_war_checkin
alliance_war_battle_records
alliance_war_honor_exchange
alliance_land_occupation
alliance_land_battle_duel
alliance_land_battle_round
alliance_land_battle
alliance_land_registration
alliance_army_signups
alliance_war_session_config
alliance_training_participants
alliance_training_rooms
alliance_item_storage
alliance_beast_storage
alliance_activities
alliance_chat_messages
alliance_war_honor_effects
alliance_war_scores
alliance_army_assignments
alliance_members
alliance_talents
alliance_buildings
alliance_quit_records
alliances
arena_battle_log
arena_daily_challenge
arena_streak_history
arena_streak
arena_stats
arena
battlefield_battle_log
battlefield_signup
spar_battle_log
spar_records
zhenyao_battle_log
zhenyao_daily_count
zhenyao_floor
king_challenge_logs
king_challenge_rank
king_final_stage
king_reward_claimed
friend_relation
friend_request
world_chat_message
private_message
player_daily_activity
player_gift_claim
dragonpalace_daily_state
mosoul_hunting_state
mosoul_global_pity
player_signin_records
tree_player_week
activity_claims
activity_finalize_log
activity_power_ranking_reward
activity_wheel_lottery
fortune_talisman_daily
player_chest_counter
player_diamond_exchange_log
player_exchange_claim
player_shop_daily_purchase
task_reward_claims
player_dungeon_progress
cultivation_config
manor_land
player_manor
player_beast
beast_bone
player_mosoul
player_spirit
spirit_account
refine_pot_log
player_inventory
player_bag
player_effect
player_immortalize_pool
player_month_card
player_talent_levels
tower_state
recharge_order
player
king_season_config
tree_week
""".strip().split('\n'))

# 应该保留的系统配置表
system_config_tables = {'blacklist', 'lands', 'level_config'}

print("=" * 80)
print("清除脚本验证报告")
print("=" * 80)
print()

# 验证1：检查是否有遗漏的玩家/联盟数据表
player_alliance_tables = all_tables_in_db - system_config_tables
missing_tables = player_alliance_tables - cleared_tables_updated

if missing_tables:
    print("❌ 错误：以下玩家/联盟数据表未被清除脚本覆盖：")
    for table in sorted(missing_tables):
        print(f"   - {table}")
    print()
else:
    print("✅ 所有玩家和联盟数据表都已包含在清除脚本中")
    print()

# 验证2：检查系统配置表是否被正确保留
preserved_tables = all_tables_in_db - cleared_tables_updated

if preserved_tables == system_config_tables:
    print("✅ 系统配置表被正确保留：")
    for table in sorted(preserved_tables):
        print(f"   - {table}")
    print()
else:
    print("⚠️  保留的表与预期不符：")
    print(f"   预期保留: {sorted(system_config_tables)}")
    print(f"   实际保留: {sorted(preserved_tables)}")
    print()

# 验证3：检查是否有不存在的表
non_existent_tables = cleared_tables_updated - all_tables_in_db

if non_existent_tables:
    print("⚠️  警告：清除脚本中包含数据库中不存在的表：")
    for table in sorted(non_existent_tables):
        print(f"   - {table}")
    print("   （这些表使用了 IF EXISTS，所以不会导致错误）")
    print()
else:
    print("✅ 清除脚本中的所有表都存在于数据库中")
    print()

# 统计信息
print("=" * 80)
print("统计信息：")
print("=" * 80)
print(f"数据库中的表总数: {len(all_tables_in_db)}")
print(f"要清除的表数量: {len(cleared_tables_updated)}")
print(f"保留的表数量: {len(preserved_tables)}")
print()

# 最终结论
print("=" * 80)
print("结论：")
print("=" * 80)

if not missing_tables and preserved_tables == system_config_tables:
    print("✅ 清除脚本已完善，可以安全使用！")
    print()
    print("清除脚本将：")
    print("  1. 清除所有玩家数据（包括活动记录、战斗记录、背包等）")
    print("  2. 清除所有联盟数据（包括联盟成员、盟战记录等）")
    print("  3. 保留系统配置表（blacklist, lands, level_config）")
    print()
    print("⚠️  执行前请务必备份数据库！")
else:
    print("⚠️  清除脚本需要进一步检查和修正")

print("=" * 80)
