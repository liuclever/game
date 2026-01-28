#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析清除脚本，找出哪些表不应该被清除
"""

# 数据库备份中的所有表
all_tables = """
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
""".strip().split('\n')

# 清除脚本中要清除的表
cleared_tables = """
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
alliance_season_rewards
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
player_dungeon_progress
cultivation_config
manor_land
player_manor
player_beast
beast_bone
player_mosoul
player_spirit
player_inventory
player_bag
player_effect
player_immortalize_pool
player_month_card
player_talent_levels
recharge_order
player
king_season_config
tree_week
""".strip().split('\n')

# 找出不在清除列表中的表（这些表应该被保留）
all_tables_set = set(all_tables)
cleared_tables_set = set(cleared_tables)

preserved_tables = sorted(all_tables_set - cleared_tables_set)
missing_in_backup = sorted(cleared_tables_set - all_tables_set)

print("=" * 80)
print("数据库清除脚本分析报告")
print("=" * 80)
print()

print(f"数据库备份中的表总数: {len(all_tables)}")
print(f"清除脚本中要清除的表数: {len(cleared_tables)}")
print()

if preserved_tables:
    print("【重要】以下表在数据库中存在，但不会被清除脚本清除：")
    print("-" * 80)
    for table in preserved_tables:
        # 判断表的类型
        if table.startswith('activity_'):
            table_type = "活动数据表（包含玩家活动记录）"
        elif table == 'blacklist':
            table_type = "系统配置表（黑名单）"
        elif table == 'lands':
            table_type = "系统配置表（土地配置）"
        elif table == 'level_config':
            table_type = "系统配置表（等级配置）"
        elif table == 'spirit_account':
            table_type = "玩家数据表（战灵账户）"
        elif table.startswith('player_'):
            table_type = "玩家数据表"
        elif table.startswith('fortune_'):
            table_type = "玩家数据表（福缘符）"
        elif table.startswith('zhenyao_'):
            table_type = "玩家数据表（镇妖）"
        elif table.startswith('tower_'):
            table_type = "玩家数据表（通天塔）"
        elif table.startswith('refine_'):
            table_type = "玩家数据表（炼妖壶）"
        elif table.startswith('task_'):
            table_type = "玩家数据表（任务奖励）"
        else:
            table_type = "未分类"
        
        print(f"  - {table:40s} [{table_type}]")
    print()

if missing_in_backup:
    print("【注意】以下表在清除脚本中，但在数据库备份中不存在：")
    print("-" * 80)
    for table in missing_in_backup:
        print(f"  - {table}")
    print()

print("=" * 80)
print("建议：")
print("=" * 80)

# 分类建议
system_config_tables = [t for t in preserved_tables if t in ['blacklist', 'lands', 'level_config']]
activity_tables = [t for t in preserved_tables if t.startswith('activity_')]
player_data_tables = [t for t in preserved_tables if t.startswith('player_') or t.startswith('zhenyao_') or t.startswith('tower_') or t.startswith('fortune_') or t.startswith('refine_') or t.startswith('task_') or t == 'spirit_account']

if system_config_tables:
    print("\n1. 系统配置表（建议保留，不要清除）：")
    for table in system_config_tables:
        print(f"   - {table}")

if activity_tables:
    print("\n2. 活动数据表（包含玩家活动记录，建议添加到清除脚本）：")
    for table in activity_tables:
        print(f"   - {table}")

if player_data_tables:
    print("\n3. 玩家数据表（建议添加到清除脚本）：")
    for table in player_data_tables:
        print(f"   - {table}")

print("\n" + "=" * 80)
