"""测试擂台数据查询"""
from infrastructure.db.connection import execute_query

# 查询所有擂台数据
print("=== 查询所有擂台数据 ===")
arenas = execute_query("SELECT * FROM arena")
for arena in arenas:
    print(f"ID: {arena['id']}, 阶段: {arena['rank_name']}, 类型: {arena['arena_type']}")
    print(f"  擂主ID: {arena['champion_user_id']} (类型: {type(arena['champion_user_id'])})")
    print(f"  擂主昵称: {arena['champion_nickname']}")
    print(f"  连胜: {arena['consecutive_wins']}, 奖池: {arena['prize_pool']}")
    print()

# 测试查询黄阶普通场
print("=== 查询黄阶普通场 ===")
result = execute_query(
    "SELECT * FROM arena WHERE rank_name = %s AND arena_type = %s",
    ('黄阶', 'normal')
)
if result:
    arena = result[0]
    print(f"找到擂台: {arena}")
    print(f"champion_user_id: {arena.get('champion_user_id')} (类型: {type(arena.get('champion_user_id'))})")
    print(f"champion_nickname: {arena.get('champion_nickname')}")
    print(f"is None? {arena.get('champion_user_id') is None}")
else:
    print("未找到擂台")
