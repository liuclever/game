"""擂台问题诊断脚本"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from infrastructure.db.connection import execute_query
from interfaces.routes.arena_routes import get_player_rank

print("=" * 60)
print("擂台功能诊断报告")
print("=" * 60)
print()

# 1. 检查数据库中的擂台数据
print("【1】数据库擂台数据检查")
print("-" * 60)
arenas = execute_query("SELECT * FROM arena WHERE champion_user_id IS NOT NULL")
if arenas:
    print(f"找到 {len(arenas)} 个有擂主的擂台:")
    for arena in arenas:
        print(f"  - {arena['rank_name']} {arena['arena_type']}场")
        print(f"    擂主: {arena['champion_nickname']} (ID: {arena['champion_user_id']})")
        print(f"    连胜: {arena['consecutive_wins']}, 奖池: {arena['prize_pool']}")
else:
    print("❌ 没有找到任何有擂主的擂台！")
print()

# 2. 检查玩家数据
print("【2】玩家数据检查")
print("-" * 60)
players = execute_query("SELECT user_id, nickname, level FROM player WHERE level >= 20 LIMIT 5")
print(f"找到 {len(players)} 个20级以上的玩家:")
for p in players:
    rank_name, can_arena = get_player_rank(p['level'])
    print(f"  - {p['nickname']} (ID: {p['user_id']}, 等级: {p['level']}, 阶段: {rank_name})")
print()

# 3. 模拟API调用
print("【3】模拟API调用测试")
print("-" * 60)
test_user_id = 4055  # 使用一个非擂主的玩家
player_rows = execute_query("SELECT level, nickname FROM player WHERE user_id = %s", (test_user_id,))
if player_rows:
    player_level = player_rows[0].get('level', 1)
    player_nickname = player_rows[0].get('nickname', '未知')
    rank_name, can_arena = get_player_rank(player_level)
    
    print(f"测试玩家: {player_nickname} (ID: {test_user_id})")
    print(f"等级: {player_level}, 阶段: {rank_name}")
    
    if can_arena:
        arena_type = 'normal'
        arena_rows = execute_query(
            "SELECT * FROM arena WHERE rank_name = %s AND arena_type = %s",
            (rank_name, arena_type)
        )
        
        if arena_rows:
            arena_info = arena_rows[0]
            is_empty = arena_info is None or arena_info.get('champion_user_id') is None
            
            print(f"\n查询到的擂台信息:")
            print(f"  champion_user_id: {arena_info.get('champion_user_id')}")
            print(f"  champion_nickname: {arena_info.get('champion_nickname')}")
            print(f"  is_empty判断结果: {is_empty}")
            
            # 构建API返回数据
            arena_data = {
                "champion": arena_info['champion_nickname'] if arena_info and arena_info.get('champion_user_id') else None,
                "championUserId": arena_info['champion_user_id'] if arena_info else None,
                "consecutiveWins": arena_info['consecutive_wins'] if arena_info else 0,
                "prizePool": arena_info['prize_pool'] if arena_info else 0,
                "isChampion": arena_info and arena_info.get('champion_user_id') == test_user_id,
                "isEmpty": is_empty,
            }
            
            print(f"\nAPI应该返回的arena数据:")
            for key, value in arena_data.items():
                print(f"  {key}: {value}")
            
            if arena_data['isEmpty']:
                print("\n❌ 问题确认: isEmpty为True，但数据库中有擂主！")
            else:
                print("\n✅ 数据正常: isEmpty为False，擂主信息正确")
print()

# 4. 诊断建议
print("【4】诊断建议")
print("-" * 60)
print("如果上面显示数据正常，但前端仍然看不到擂主，可能的原因:")
print("  1. 后端服务需要重启（代码更新未生效）")
print("  2. 前端浏览器缓存（需要清除缓存或硬刷新）")
print("  3. 前端和后端版本不一致")
print()
print("建议操作:")
print("  1. 重启后端服务")
print("  2. 清除浏览器缓存（Ctrl+Shift+Delete）或硬刷新（Ctrl+F5）")
print("  3. 检查浏览器开发者工具的Network标签，查看API返回的实际数据")
print("=" * 60)
