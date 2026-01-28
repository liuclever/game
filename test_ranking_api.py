"""
测试排行榜 API 返回的数据格式
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from infrastructure.db.connection import execute_query
from infrastructure.db.player_beast_repo_mysql import MySQLPlayerBeastRepo
from interfaces.routes.beast_routes import _calc_total_combat_power_with_equipment


def test_power_ranking_total():
    """测试战力总排行 API 返回格式"""
    
    print(f"\n{'='*60}")
    print("测试战力总排行 API 返回格式")
    print(f"{'='*60}\n")
    
    # 模拟 API 调用逻辑
    ranking_type = 'power'
    page = 1
    size = 10
    offset = (page - 1) * size
    
    # 没有 filter_rank，即总排行
    where_parts = []
    params = []
    where_sql = ""
    
    # 查询所有玩家
    sql = f"""
        SELECT p.user_id as userId, p.nickname, p.level, p.vip_level as vipLevel
        FROM player p
        {where_sql}
        ORDER BY p.user_id
    """
    players = execute_query(sql) if not params else execute_query(sql, tuple(params))
    
    # 计算每个玩家的总战力
    beast_repo = MySQLPlayerBeastRepo()
    player_powers = []
    
    for player in (players or []):
        player_user_id = player['userId']
        team_beasts = beast_repo.get_team_beasts(player_user_id)
        
        if not team_beasts:
            continue
        
        total_power = 0
        for beast in team_beasts:
            power = _calc_total_combat_power_with_equipment(beast)
            total_power += power
        
        if total_power > 0:
            player_powers.append({
                "userId": player_user_id,
                "nickname": player['nickname'],
                "level": player['level'],
                "vipLevel": player['vipLevel'],
                "power": total_power
            })
    
    # 按战力排序
    player_powers.sort(key=lambda x: (-x['power'], -x['level']))
    
    # 分页
    total = len(player_powers)
    paginated = player_powers[offset:offset + size]
    rows = paginated
    
    # 补充 rank 字段（修复后的逻辑）
    rankings = []
    for idx, r in enumerate(rows or []):
        # 如果 r 已经是字典（如 power 类型），直接使用；否则转换
        if isinstance(r, dict):
            obj = r.copy()  # 使用 copy() 而不是 dict()
        else:
            obj = dict(r)
        obj["rank"] = int(offset + idx + 1)
        rankings.append(obj)
    
    print(f"总玩家数: {len(players)}")
    print(f"有效玩家数: {total}")
    print(f"当前页玩家数: {len(rankings)}")
    print()
    
    # 显示前10名
    print("排名 | 昵称 | 等级 | 战力")
    print("-" * 60)
    for p in rankings[:10]:
        print(f"{p['rank']:2d}   | {p['nickname']:15s} | Lv.{p['level']:2d} | {p['power']:5d}")
    
    print(f"\n{'='*60}")
    
    # 检查数据完整性
    all_have_power = all('power' in p and p['power'] > 0 for p in rankings)
    all_have_rank = all('rank' in p for p in rankings)
    
    if all_have_power and all_have_rank:
        print("✅ 数据格式正确，所有玩家都有 power 和 rank 字段")
        print(f"✅ 所有战力都大于 0")
    else:
        print("❌ 数据格式错误")
        if not all_have_power:
            print("  - 部分玩家缺少 power 字段或战力为 0")
        if not all_have_rank:
            print("  - 部分玩家缺少 rank 字段")
    
    print(f"{'='*60}\n")
    
    return rankings


def test_power_ranking_with_filter():
    """测试战力分段排行 API 返回格式"""
    
    print(f"\n{'='*60}")
    print("测试战力分段排行（黄阶）API 返回格式")
    print(f"{'='*60}\n")
    
    # 模拟 API 调用逻辑
    ranking_type = 'power'
    page = 1
    size = 10
    offset = (page - 1) * size
    filter_rank = "黄阶"
    
    # 有 filter_rank
    tier = (20, 29)
    where_parts = ["p.level BETWEEN %s AND %s"]
    params = [20, 29]
    where_sql = "WHERE " + " AND ".join(where_parts)
    
    # 查询该段位玩家
    sql = f"""
        SELECT p.user_id as userId, p.nickname, p.level, p.vip_level as vipLevel
        FROM player p
        {where_sql}
        ORDER BY p.user_id
    """
    players = execute_query(sql, tuple(params))
    
    # 计算每个玩家的总战力
    beast_repo = MySQLPlayerBeastRepo()
    player_powers = []
    
    for player in (players or []):
        player_user_id = player['userId']
        team_beasts = beast_repo.get_team_beasts(player_user_id)
        
        if not team_beasts:
            continue
        
        total_power = 0
        for beast in team_beasts:
            power = _calc_total_combat_power_with_equipment(beast)
            total_power += power
        
        if total_power > 0:
            player_powers.append({
                "userId": player_user_id,
                "nickname": player['nickname'],
                "level": player['level'],
                "vipLevel": player['vipLevel'],
                "power": total_power
            })
    
    # 按战力排序
    player_powers.sort(key=lambda x: (-x['power'], -x['level']))
    
    # 分页
    total = len(player_powers)
    paginated = player_powers[offset:offset + size]
    rows = paginated
    
    # 补充 rank 字段（修复后的逻辑）
    rankings = []
    for idx, r in enumerate(rows or []):
        if isinstance(r, dict):
            obj = r.copy()
        else:
            obj = dict(r)
        obj["rank"] = int(offset + idx + 1)
        rankings.append(obj)
    
    print(f"黄阶玩家数: {len(players)}")
    print(f"有效玩家数: {total}")
    print(f"当前页玩家数: {len(rankings)}")
    print()
    
    # 显示前10名
    print("排名 | 昵称 | 等级 | 战力")
    print("-" * 60)
    for p in rankings[:10]:
        print(f"{p['rank']:2d}   | {p['nickname']:15s} | Lv.{p['level']:2d} | {p['power']:5d}")
    
    print(f"\n{'='*60}")
    
    # 检查数据完整性
    all_have_power = all('power' in p and p['power'] > 0 for p in rankings)
    all_have_rank = all('rank' in p for p in rankings)
    
    if all_have_power and all_have_rank:
        print("✅ 数据格式正确，所有玩家都有 power 和 rank 字段")
        print(f"✅ 所有战力都大于 0")
    else:
        print("❌ 数据格式错误")
    
    print(f"{'='*60}\n")


if __name__ == "__main__":
    test_power_ranking_total()
    test_power_ranking_with_filter()
