"""测试同一阶段的两个玩家能否看到同一个擂台"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from infrastructure.db.connection import execute_query, execute_update
from interfaces.routes.arena_routes import get_player_rank

print("=" * 60)
print("测试同一阶段玩家的擂台视图")
print("=" * 60)
print()

# 找出所有黄阶玩家
print("【步骤1】查找所有黄阶玩家（20-29级）")
print("-" * 60)
players = execute_query(
    "SELECT user_id, nickname, level FROM player WHERE level >= 20 AND level <= 29 ORDER BY user_id"
)

if len(players) < 2:
    print("❌ 黄阶玩家不足2个，无法测试")
    exit(1)

print(f"找到 {len(players)} 个黄阶玩家:")
for p in players[:5]:  # 只显示前5个
    rank_name, _ = get_player_rank(p['level'])
    print(f"  - {p['nickname']} (ID: {p['user_id']}, 等级: {p['level']}, 阶段: {rank_name})")
print()

# 选择两个玩家
player_a = players[0]
player_b = players[1] if len(players) > 1 else players[0]

print("【步骤2】玩家A占领擂台")
print("-" * 60)
print(f"玩家A: {player_a['nickname']} (ID: {player_a['user_id']})")

# 先清空黄阶擂台
execute_update(
    """UPDATE arena SET champion_user_id = NULL, champion_nickname = NULL, 
       consecutive_wins = 0, prize_pool = 0
       WHERE rank_name = '黄阶' AND arena_type = 'normal'"""
)
print("✅ 黄阶擂台已清空")

# 玩家A占领
execute_update(
    """UPDATE arena SET champion_user_id = %s, champion_nickname = %s, 
       consecutive_wins = 0, prize_pool = 1, last_battle_time = NOW()
       WHERE rank_name = '黄阶' AND arena_type = 'normal'""",
    (player_a['user_id'], player_a['nickname'])
)
print(f"✅ 玩家A {player_a['nickname']} 已占领黄阶擂台")
print()

# 玩家A查询
print("【步骤3】玩家A查询擂台（应该看到自己）")
print("-" * 60)
arena_rows = execute_query(
    "SELECT * FROM arena WHERE rank_name = '黄阶' AND arena_type = 'normal'"
)
if arena_rows:
    arena = arena_rows[0]
    print(f"玩家A看到的擂台:")
    print(f"  champion_user_id: {arena['champion_user_id']}")
    print(f"  champion_nickname: {arena['champion_nickname']}")
    print(f"  isEmpty: {arena['champion_user_id'] is None}")
    
    if arena['champion_user_id'] == player_a['user_id']:
        print(f"✅ 正确：玩家A看到自己是擂主")
    else:
        print(f"❌ 错误：玩家A看不到自己是擂主")
print()

# 玩家B查询
print("【步骤4】玩家B查询擂台（应该看到玩家A）")
print("-" * 60)
print(f"玩家B: {player_b['nickname']} (ID: {player_b['user_id']})")

arena_rows = execute_query(
    "SELECT * FROM arena WHERE rank_name = '黄阶' AND arena_type = 'normal'"
)
if arena_rows:
    arena = arena_rows[0]
    print(f"玩家B看到的擂台:")
    print(f"  champion_user_id: {arena['champion_user_id']}")
    print(f"  champion_nickname: {arena['champion_nickname']}")
    print(f"  isEmpty: {arena['champion_user_id'] is None}")
    
    if arena['champion_user_id'] == player_a['user_id']:
        print(f"✅ 正确：玩家B看到玩家A是擂主")
    elif arena['champion_user_id'] is None:
        print(f"❌ 错误：玩家B看到擂台为空！")
    else:
        print(f"❌ 错误：玩家B看到的擂主不对")
print()

# 模拟API返回
print("【步骤5】模拟API返回给玩家B的数据")
print("-" * 60)
if arena_rows:
    arena_info = arena_rows[0]
    is_empty = arena_info is None or arena_info.get('champion_user_id') is None
    is_champion = arena_info and arena_info.get('champion_user_id') == player_b['user_id']
    
    api_response = {
        "champion": arena_info['champion_nickname'] if arena_info and arena_info.get('champion_user_id') else None,
        "championUserId": arena_info['champion_user_id'] if arena_info else None,
        "consecutiveWins": arena_info['consecutive_wins'] if arena_info else 0,
        "prizePool": arena_info['prize_pool'] if arena_info else 0,
        "isChampion": is_champion,
        "isEmpty": is_empty,
    }
    
    print("API返回的arena对象:")
    for key, value in api_response.items():
        print(f"  {key}: {value}")
    
    if api_response['isEmpty']:
        print("\n❌ 问题确认：API返回isEmpty=True，但数据库中有擂主！")
    else:
        print(f"\n✅ 正常：API返回isEmpty=False，擂主是 {api_response['champion']}")

print()
print("=" * 60)
