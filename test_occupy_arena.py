"""测试占领擂台功能"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from infrastructure.db.connection import execute_query, execute_update
from interfaces.routes.arena_routes import get_player_rank, get_arena_ball_id

print("=" * 60)
print("测试占领擂台功能")
print("=" * 60)
print()

# 测试玩家
test_user_id = 4055  # 玩家789
arena_type = 'normal'

# 1. 查看当前擂台状态
print("【步骤1】查看当前擂台状态")
print("-" * 60)
player_rows = execute_query("SELECT level, nickname FROM player WHERE user_id = %s", (test_user_id,))
if not player_rows:
    print("❌ 玩家不存在")
    exit(1)

player_level = player_rows[0].get('level', 1)
player_nickname = player_rows[0].get('nickname', '未知')
rank_name, can_arena = get_player_rank(player_level)

print(f"测试玩家: {player_nickname} (ID: {test_user_id})")
print(f"等级: {player_level}, 阶段: {rank_name}")

arena_rows = execute_query(
    "SELECT * FROM arena WHERE rank_name = %s AND arena_type = %s",
    (rank_name, arena_type)
)

if not arena_rows:
    print("❌ 擂台不存在")
    exit(1)

arena = arena_rows[0]
print(f"\n当前擂台状态:")
print(f"  champion_user_id: {arena['champion_user_id']}")
print(f"  champion_nickname: {arena['champion_nickname']}")
print(f"  consecutive_wins: {arena['consecutive_wins']}")
print(f"  prize_pool: {arena['prize_pool']}")
print()

# 2. 如果有擂主，先清空
if arena['champion_user_id']:
    print("【步骤2】清空擂台（为了测试）")
    print("-" * 60)
    execute_update(
        """UPDATE arena SET champion_user_id = NULL, champion_nickname = NULL, 
           consecutive_wins = 0, prize_pool = 0
           WHERE rank_name = %s AND arena_type = %s""",
        (rank_name, arena_type)
    )
    print("✅ 擂台已清空")
    print()

# 3. 模拟占领擂台
print("【步骤3】模拟玩家占领擂台")
print("-" * 60)

# 检查球数量
ball_id = get_arena_ball_id(arena_type)
ball_rows = execute_query(
    "SELECT quantity FROM player_inventory WHERE user_id = %s AND item_id = %s",
    (test_user_id, ball_id)
)
ball_count = ball_rows[0].get('quantity', 0) if ball_rows else 0
print(f"玩家拥有的球数量: {ball_count}")

if ball_count < 1:
    print("❌ 球不足，添加球...")
    execute_update(
        """INSERT INTO player_inventory (user_id, item_id, quantity, is_temporary)
           VALUES (%s, %s, 10, 0)
           ON DUPLICATE KEY UPDATE quantity = quantity + 10""",
        (test_user_id, ball_id)
    )
    print("✅ 已添加10个球")

# 消耗球
execute_update(
    "UPDATE player_inventory SET quantity = quantity - 1 WHERE user_id = %s AND item_id = %s",
    (test_user_id, ball_id)
)
print("✅ 消耗1个球")

# 占领擂台
affected_rows = execute_update(
    """UPDATE arena SET champion_user_id = %s, champion_nickname = %s, 
       consecutive_wins = 0, prize_pool = prize_pool + 1, last_battle_time = NOW()
       WHERE rank_name = %s AND arena_type = %s""",
    (test_user_id, player_nickname, rank_name, arena_type)
)
print(f"✅ 执行UPDATE语句，影响行数: {affected_rows}")
print()

# 4. 立即查询验证
print("【步骤4】立即查询验证")
print("-" * 60)
arena_rows = execute_query(
    "SELECT * FROM arena WHERE rank_name = %s AND arena_type = %s",
    (rank_name, arena_type)
)

if arena_rows:
    arena = arena_rows[0]
    print(f"查询结果:")
    print(f"  champion_user_id: {arena['champion_user_id']} (类型: {type(arena['champion_user_id'])})")
    print(f"  champion_nickname: {arena['champion_nickname']}")
    print(f"  consecutive_wins: {arena['consecutive_wins']}")
    print(f"  prize_pool: {arena['prize_pool']}")
    
    if arena['champion_user_id'] == test_user_id:
        print(f"\n✅ 成功！玩家 {player_nickname} 已占领擂台")
    else:
        print(f"\n❌ 失败！擂主不是 {player_nickname}")
        print(f"   期望: {test_user_id}, 实际: {arena['champion_user_id']}")
else:
    print("❌ 查询失败，未找到擂台")
print()

# 5. 模拟另一个玩家查询
print("【步骤5】模拟另一个玩家查询")
print("-" * 60)
other_user_id = 4056  # 玩家456
other_rows = execute_query("SELECT level, nickname FROM player WHERE user_id = %s", (other_user_id,))
if other_rows:
    other_nickname = other_rows[0].get('nickname', '未知')
    other_level = other_rows[0].get('level', 1)
    other_rank, _ = get_player_rank(other_level)
    
    print(f"另一个玩家: {other_nickname} (ID: {other_user_id})")
    print(f"等级: {other_level}, 阶段: {other_rank}")
    
    # 查询擂台
    arena_rows = execute_query(
        "SELECT * FROM arena WHERE rank_name = %s AND arena_type = %s",
        (other_rank, arena_type)
    )
    
    if arena_rows:
        arena = arena_rows[0]
        is_empty = arena is None or arena.get('champion_user_id') is None
        
        print(f"\n该玩家看到的擂台:")
        print(f"  champion_user_id: {arena['champion_user_id']}")
        print(f"  champion_nickname: {arena['champion_nickname']}")
        print(f"  isEmpty判断: {is_empty}")
        
        if other_rank == rank_name:
            if arena['champion_user_id'] == test_user_id:
                print(f"\n✅ 正确！玩家 {other_nickname} 能看到擂主 {player_nickname}")
            else:
                print(f"\n❌ 错误！玩家 {other_nickname} 看不到正确的擂主")
        else:
            print(f"\n⚠️ 注意：两个玩家不在同一阶段（{rank_name} vs {other_rank}）")

print()
print("=" * 60)
print("测试完成")
print("=" * 60)
