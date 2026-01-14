"""给测试联盟的所有成员设置贡献点到满值

运行示例（项目根目录）：
    python scripts/set_alliance_contribution.py
    python scripts/set_alliance_contribution.py --alliance_name "测试联盟" --contribution 57
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.db.connection import execute_query, execute_update

def set_alliance_contribution(alliance_name="测试联盟", contribution=57):
    """设置指定联盟所有成员的贡献点"""
    
    # 查找联盟
    sql = "SELECT id, name FROM alliances WHERE name = %s"
    rows = execute_query(sql, (alliance_name,))
    
    if not rows:
        print(f"错误: 未找到名为 '{alliance_name}' 的联盟")
        return
    
    alliance = rows[0]
    alliance_id = alliance['id']
    print(f"找到联盟: {alliance['name']} (ID: {alliance_id})")
    
    # 查找联盟的所有成员
    sql = """
        SELECT am.user_id, am.contribution, p.nickname 
        FROM alliance_members am
        LEFT JOIN player p ON am.user_id = p.user_id
        WHERE am.alliance_id = %s
    """
    members = execute_query(sql, (alliance_id,))
    
    if not members:
        print(f"错误: 联盟 '{alliance_name}' 没有成员")
        return
    
    print(f"\n找到 {len(members)} 个成员:")
    print("-" * 60)
    
    # 更新每个成员的贡献点
    updated_count = 0
    for member in members:
        user_id = member['user_id']
        current_contribution = member.get('contribution', 0) or 0
        nickname = member.get('nickname') or f"玩家{user_id}"
        
        # 直接设置为目标贡献值
        sql = "UPDATE alliance_members SET contribution = %s WHERE user_id = %s AND alliance_id = %s"
        execute_update(sql, (contribution, user_id, alliance_id))
        
        print(f"  用户 {nickname} (ID: {user_id}): {current_contribution} -> {contribution}")
        updated_count += 1
    
    print("-" * 60)
    print(f"完成! 已更新 {updated_count} 个成员的贡献点为 {contribution}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="设置联盟成员贡献点")
    parser.add_argument("--alliance_name", type=str, default="测试联盟", help="联盟名称（默认：测试联盟）")
    parser.add_argument("--contribution", type=int, default=57, help="贡献点数值（默认：57）")
    
    args = parser.parse_args()
    
    set_alliance_contribution(args.alliance_name, args.contribution)
