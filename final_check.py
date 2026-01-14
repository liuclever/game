"""最终检查 - 对比数据库和后端代码"""
from infrastructure.db.connection import execute_query
import os

print("=" * 70)
print("数据库与后端代码一致性检查")
print("=" * 70)

# 获取所有表
all_tables = execute_query("SHOW TABLES")
table_names = {list(t.values())[0] for t in all_tables}

issues = []

# 1. 检查签到系统
print("\n【签到系统】")
print("-" * 70)
if 'player_signin_records' in table_names:
    print("✅ player_signin_records 表存在")
    
    # 检查表结构
    cols = execute_query("DESCRIBE player_signin_records")
    required_cols = ['id', 'user_id', 'signin_date', 'is_makeup', 'reward_copper']
    for col in required_cols:
        if any(c['Field'] == col for c in cols):
            print(f"  ✅ {col} 字段存在")
        else:
            print(f"  ❌ {col} 字段缺失")
            issues.append(f"player_signin_records 表缺少 {col} 字段")
else:
    print("❌ player_signin_records 表不存在")
    issues.append("缺少 player_signin_records 表")

# 检查 player 表的签到字段
player_cols = execute_query("DESCRIBE player")
player_fields = {c['Field'] for c in player_cols}

signin_fields = ['last_signin_date', 'consecutive_signin_days', 'signin_rewards_claimed']
for field in signin_fields:
    if field in player_fields:
        print(f"  ✅ player.{field} 字段存在")
    else:
        print(f"  ❌ player.{field} 字段缺失")
        issues.append(f"player 表缺少 {field} 字段")

# 2. 检查擂台系统
print("\n【擂台系统】")
print("-" * 70)
arena_tables = {
    'arena': '擂台主表',
    'arena_battle_log': '擂台战斗记录',
    'arena_daily_challenge': '每日挑战次数',
    'arena_stats': '擂台统计',
    'arena_streak': '连胜记录',
    'arena_streak_history': '连胜历史'
}

for table, desc in arena_tables.items():
    if table in table_names:
        print(f"✅ {table} ({desc})")
    else:
        print(f"❌ {table} ({desc}) 不存在")
        issues.append(f"缺少 {table} 表")

# 3. 检查背包系统
print("\n【背包系统】")
print("-" * 70)
if 'player_inventory' in table_names:
    print("✅ player_inventory 表存在")
    inv_cols = execute_query("DESCRIBE player_inventory")
    inv_fields = {c['Field'] for c in inv_cols}
    required = ['user_id', 'item_id', 'quantity']
    for field in required:
        if field in inv_fields:
            print(f"  ✅ {field} 字段存在")
        else:
            print(f"  ❌ {field} 字段缺失")
            issues.append(f"player_inventory 表缺少 {field} 字段")
else:
    print("❌ player_inventory 表不存在")
    issues.append("缺少 player_inventory 表")

# 4. 检查 VIP 系统
print("\n【VIP 系统】")
print("-" * 70)
vip_fields = ['vip_level', 'vip_exp']
for field in vip_fields:
    if field in player_fields:
        print(f"✅ player.{field} 字段存在")
    else:
        print(f"❌ player.{field} 字段缺失")
        issues.append(f"player 表缺少 {field} 字段")

# 5. 检查活力系统
print("\n【活力系统】")
print("-" * 70)
energy_fields = ['energy', 'last_energy_recovery_time']
for field in energy_fields:
    if field in player_fields:
        print(f"✅ player.{field} 字段存在")
    else:
        print(f"❌ player.{field} 字段缺失")
        issues.append(f"player 表缺少 {field} 字段")

# 6. 检查货币系统
print("\n【货币系统】")
print("-" * 70)
currency_fields = ['gold', 'yuanbao', 'silver_diamond', 'dice', 'enhancement_stone', 'crystal_tower']
for field in currency_fields:
    if field in player_fields:
        print(f"✅ player.{field} 字段存在")
    else:
        print(f"❌ player.{field} 字段缺失")
        issues.append(f"player 表缺少 {field} 字段")

# 总结
print("\n" + "=" * 70)
print("检查总结")
print("=" * 70)

if issues:
    print(f"\n⚠️  发现 {len(issues)} 个问题:\n")
    for i, issue in enumerate(issues, 1):
        print(f"{i}. {issue}")
    print("\n建议: 运行数据库迁移脚本修复这些问题")
else:
    print("\n✅ 数据库结构与后端代码完全一致！")
    print("✅ 所有必需的表和字段都已存在")

print("\n" + "=" * 70)
