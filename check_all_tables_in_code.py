#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查代码中所有涉及的表，确保清除脚本的完整性
"""
import os
import re
from pathlib import Path

# 已知要清除的表
cleared_tables = set("""
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

# 系统配置表（不应该清除）
system_tables = {'blacklist', 'lands', 'level_config'}

def find_table_references():
    """在代码中查找所有表引用"""
    table_patterns = [
        # SQL 语句中的表名
        r'FROM\s+`?(\w+)`?',
        r'INSERT\s+INTO\s+`?(\w+)`?',
        r'UPDATE\s+`?(\w+)`?',
        r'DELETE\s+FROM\s+`?(\w+)`?',
        r'TRUNCATE\s+TABLE\s+`?(\w+)`?',
        r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?(\w+)`?',
        r'DROP\s+TABLE\s+(?:IF\s+EXISTS\s+)?`?(\w+)`?',
        r'ALTER\s+TABLE\s+`?(\w+)`?',
        r'JOIN\s+`?(\w+)`?',
        # Python 代码中的表名
        r'TABLE\s*=\s*["\'](\w+)["\']',
        r'table_name\s*=\s*["\'](\w+)["\']',
        r'__tablename__\s*=\s*["\'](\w+)["\']',
    ]
    
    tables_found = set()
    file_table_map = {}
    
    # 搜索所有 Python 和 SQL 文件
    for ext in ['*.py', '*.sql']:
        for filepath in Path('.').rglob(ext):
            # 跳过虚拟环境和缓存目录
            if '.venv' in str(filepath) or '__pycache__' in str(filepath) or '.pytest_cache' in str(filepath):
                continue
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    for pattern in table_patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            table_name = match.group(1).lower()
                            # 过滤掉一些明显不是表名的词
                            if table_name not in ['select', 'where', 'and', 'or', 'not', 'null', 'true', 'false', 
                                                   'exists', 'values', 'set', 'key', 'index', 'primary', 'foreign',
                                                   'unique', 'default', 'auto_increment', 'comment', 'engine',
                                                   'charset', 'collate', 'unsigned', 'zerofill', 'binary']:
                                tables_found.add(table_name)
                                if table_name not in file_table_map:
                                    file_table_map[table_name] = []
                                file_table_map[table_name].append(str(filepath))
            except Exception as e:
                pass
    
    return tables_found, file_table_map

def main():
    print("=" * 80)
    print("代码中表引用完整性检查")
    print("=" * 80)
    print()
    
    print("正在扫描代码中的表引用...")
    tables_in_code, file_table_map = find_table_references()
    
    # 过滤掉一些已知的非表名
    non_tables = {'user', 'users', 'data', 'result', 'results', 'row', 'rows', 'temp', 
                  'tmp', 'test', 'example', 'sample', 'dual', 'information_schema',
                  'mysql', 'performance_schema', 'sys', '__future__', 'abc', 'alliance',
                  'annotations', 'typing', 'datetime', 'json', 'os', 'sys', 'time',
                  'random', 'math', 'string', 'collections', 'itertools', 'functools',
                  'pathlib', 'logging', 'unittest', 'pytest', 'flask', 'sqlalchemy',
                  'dict', 'list', 'tuple', 'set', 'str', 'int', 'float', 'bool',
                  'none', 'type', 'object', 'class', 'def', 'return', 'import',
                  'beast', 'item', 'skill', 'monster', 'map', 'config', 'service',
                  'repository', 'entity', 'model', 'schema', 'route', 'controller'}
    tables_in_code = tables_in_code - non_tables
    
    print(f"在代码中发现 {len(tables_in_code)} 个可能的表引用")
    print()
    
    # 分类表
    player_alliance_tables = tables_in_code - system_tables
    
    # 检查1：代码中的表是否都在清除列表或系统表中
    uncategorized_tables = player_alliance_tables - cleared_tables
    
    if uncategorized_tables:
        print("[警告] 发现代码中引用但未分类的表：")
        print("-" * 80)
        for table in sorted(uncategorized_tables):
            files = file_table_map.get(table, [])
            unique_files = list(set(files))
            print(f"\n  表名: {table}")
            print(f"  引用文件数: {len(unique_files)}")
            if len(unique_files) <= 3:
                for f in unique_files[:3]:
                    print(f"    - {f}")
        print()
    else:
        print("[OK] 所有代码中的表都已正确分类")
        print()
    
    # 检查2：清除列表中的表是否在代码中被引用
    unused_tables = cleared_tables - tables_in_code
    
    if unused_tables:
        print("[警告] 清除列表中有表在代码中未找到引用：")
        print("-" * 80)
        for table in sorted(unused_tables):
            print(f"  - {table}")
        print("  （这些表可能在数据库中存在但代码中未使用，或者是历史遗留表）")
        print()
    
    # 检查3：系统表的引用情况
    print("=" * 80)
    print("系统配置表引用情况：")
    print("=" * 80)
    for table in sorted(system_tables):
        if table in tables_in_code:
            files = set(file_table_map.get(table, []))
            print(f"\n[OK] {table}")
            print(f"   引用文件数: {len(files)}")
            if len(files) <= 5:
                for f in list(files)[:5]:
                    print(f"   - {f}")
        else:
            print(f"\n[警告] {table} - 在代码中未找到引用")
    print()
    
    # 检查4：特殊表的分析
    print("=" * 80)
    print("特殊表分析：")
    print("=" * 80)
    
    # 检查可能是配置表但被标记为清除的表
    potential_config_tables = []
    for table in cleared_tables:
        if any(keyword in table for keyword in ['config', 'template', 'setting']):
            potential_config_tables.append(table)
    
    if potential_config_tables:
        print("\n[警告] 以下表名包含配置相关关键词，请确认是否应该清除：")
        for table in sorted(potential_config_tables):
            files = set(file_table_map.get(table, []))
            print(f"  - {table} (引用于 {len(files)} 个文件)")
    
    # 检查可能遗漏的玩家数据表
    potential_player_tables = []
    for table in tables_in_code:
        if table.startswith('player_') and table not in cleared_tables and table not in system_tables:
            potential_player_tables.append(table)
    
    if potential_player_tables:
        print("\n[警告] 发现可能遗漏的玩家数据表：")
        for table in sorted(potential_player_tables):
            files = set(file_table_map.get(table, []))
            print(f"  - {table} (引用于 {len(files)} 个文件)")
    
    print()
    print("=" * 80)
    print("总结：")
    print("=" * 80)
    print(f"代码中引用的表总数: {len(tables_in_code)}")
    print(f"清除脚本覆盖的表: {len(cleared_tables)}")
    print(f"系统配置表: {len(system_tables)}")
    print(f"未分类的表: {len(uncategorized_tables)}")
    print()
    
    if not uncategorized_tables and not potential_player_tables:
        print("[OK] 清除脚本覆盖完整，没有遗漏的玩家/联盟数据表")
    else:
        print("[警告] 建议检查上述未分类的表，确认是否需要添加到清除脚本")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
