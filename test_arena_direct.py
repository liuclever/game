"""直接测试擂台API逻辑"""
import sys
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask
from interfaces.routes.arena_routes import arena_bp, get_player_rank
from infrastructure.db.connection import execute_query

# 创建测试Flask应用
app = Flask(__name__)
app.secret_key = 'test_key'
app.register_blueprint(arena_bp)

# 测试不同玩家看到的擂台信息
test_users = [
    (4053, '123'),  # 擂主本人
    (4055, '789'),  # 其他玩家
]

print("=== 测试擂台信息返回 ===\n")

for user_id, nickname in test_users:
    print(f"测试玩家: {nickname} (ID: {user_id})")
    
    # 获取玩家信息
    player_rows = execute_query("SELECT level, nickname FROM player WHERE user_id = %s", (user_id,))
    if not player_rows:
        print(f"  玩家不存在\n")
        continue
    
    player_level = player_rows[0].get('level', 1)
    rank_name, can_arena = get_player_rank(player_level)
    
    print(f"  等级: {player_level}, 阶段: {rank_name}")
    
    if not can_arena:
        print(f"  不能参与擂台\n")
        continue
    
    # 查询擂台信息
    arena_type = 'normal'
    arena_rows = execute_query(
        "SELECT * FROM arena WHERE rank_name = %s AND arena_type = %s",
        (rank_name, arena_type)
    )
    
    if not arena_rows:
        print(f"  擂台不存在\n")
        continue
    
    arena_info = arena_rows[0]
    
    # 判断逻辑
    is_empty = arena_info is None or arena_info.get('champion_user_id') is None
    is_champion = arena_info and arena_info.get('champion_user_id') == user_id
    
    # 构建返回数据（模拟API返回）
    arena_data = {
        "champion": arena_info['champion_nickname'] if arena_info and arena_info.get('champion_user_id') else None,
        "championUserId": arena_info['champion_user_id'] if arena_info else None,
        "consecutiveWins": arena_info['consecutive_wins'] if arena_info else 0,
        "prizePool": arena_info['prize_pool'] if arena_info else 0,
        "isChampion": is_champion,
        "isEmpty": is_empty,
    }
    
    print(f"  擂台数据:")
    print(f"    champion: {arena_data['champion']}")
    print(f"    championUserId: {arena_data['championUserId']}")
    print(f"    isEmpty: {arena_data['isEmpty']}")
    print(f"    isChampion: {arena_data['isChampion']}")
    print()
