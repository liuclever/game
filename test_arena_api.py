"""测试擂台API"""
from infrastructure.db.connection import execute_query
from interfaces.routes.arena_routes import get_player_rank

# 测试玩家等级和阶段
print("=== 测试玩家信息 ===")
players = execute_query("SELECT user_id, nickname, level FROM player LIMIT 5")
for p in players:
    user_id = p['user_id']
    nickname = p['nickname']
    level = p['level']
    rank_name, can_arena = get_player_rank(level)
    print(f"玩家ID: {user_id}, 昵称: {nickname}, 等级: {level}, 阶段: {rank_name}, 可参与擂台: {can_arena}")

# 模拟API调用逻辑
print("\n=== 模拟API调用 ===")
test_user_id = 4053
player_rows = execute_query("SELECT level, nickname FROM player WHERE user_id = %s", (test_user_id,))
if player_rows:
    player_level = player_rows[0].get('level', 1)
    player_nickname = player_rows[0].get('nickname', '未知')
    rank_name, can_arena = get_player_rank(player_level)
    
    print(f"测试玩家: {player_nickname} (ID: {test_user_id})")
    print(f"等级: {player_level}, 阶段: {rank_name}, 可参与: {can_arena}")
    
    if can_arena:
        arena_type = 'normal'
        arena_rows = execute_query(
            "SELECT * FROM arena WHERE rank_name = %s AND arena_type = %s",
            (rank_name, arena_type)
        )
        
        if arena_rows:
            arena_info = arena_rows[0]
            print(f"\n擂台信息:")
            print(f"  champion_user_id: {arena_info.get('champion_user_id')}")
            print(f"  champion_nickname: {arena_info.get('champion_nickname')}")
            print(f"  consecutive_wins: {arena_info.get('consecutive_wins')}")
            print(f"  prize_pool: {arena_info.get('prize_pool')}")
            
            is_empty = arena_info is None or arena_info.get('champion_user_id') is None
            is_champion = arena_info and arena_info.get('champion_user_id') == test_user_id
            
            print(f"\n判断结果:")
            print(f"  is_empty: {is_empty}")
            print(f"  is_champion: {is_champion}")
            
            # 构建返回数据
            arena_data = {
                "champion": arena_info['champion_nickname'] if arena_info and arena_info.get('champion_user_id') else None,
                "championUserId": arena_info['champion_user_id'] if arena_info else None,
                "consecutiveWins": arena_info['consecutive_wins'] if arena_info else 0,
                "prizePool": arena_info['prize_pool'] if arena_info else 0,
                "isChampion": is_champion,
                "isEmpty": is_empty,
            }
            print(f"\n返回的arena数据:")
            print(arena_data)
