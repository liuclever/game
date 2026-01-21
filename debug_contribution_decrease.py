"""调试贡献点减少问题：检查领取火能原石后历史总贡献点是否被错误减少"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from infrastructure.db.connection import execute_query, execute_update, get_connection

def check_user_contribution(user_id):
    """检查用户的贡献点数据"""
    sql = """
        SELECT am.user_id, am.contribution, am.total_contribution,
               COALESCE(p.nickname, CONCAT('玩家', am.user_id)) as nickname,
               am.alliance_id
        FROM alliance_members am
        LEFT JOIN player p ON am.user_id = p.user_id
        WHERE am.user_id = %s
    """
    rows = execute_query(sql, (user_id,))
    if not rows:
        return None
    return rows[0]

def check_trigger():
    """检查数据库触发器是否存在"""
    sql = "SHOW TRIGGERS LIKE 'alliance_members'"
    rows = execute_query(sql)
    triggers = [row['Trigger'] for row in rows]
    return 'protect_total_contribution' in triggers

def test_update():
    """测试更新操作"""
    print("=" * 80)
    print("调试：检查领取火能原石后历史总贡献点是否被错误减少")
    print("=" * 80)
    
    # 检查触发器
    has_trigger = check_trigger()
    print(f"\n[检查触发器]")
    if has_trigger:
        print(f"  [OK] 触发器 protect_total_contribution 存在")
    else:
        print(f"  [ERROR] 触发器 protect_total_contribution 不存在！")
        print(f"  [建议] 运行 sql/044_protect_total_contribution.sql 创建触发器")
    
    # 找一个贡献点接近 632 的用户（根据截图）
    sql = """
        SELECT am.user_id, am.contribution, am.total_contribution,
               COALESCE(p.nickname, CONCAT('玩家', am.user_id)) as nickname
        FROM alliance_members am
        LEFT JOIN player p ON am.user_id = p.user_id
        WHERE am.contribution >= 600 AND am.contribution <= 650
        ORDER BY am.contribution DESC
        LIMIT 5
    """
    rows = execute_query(sql)
    
    if not rows:
        print("\n[ERROR] 未找到贡献点在 600-650 范围内的用户")
        return
    
    print(f"\n[找到的用户]")
    for row in rows:
        user_id = row['user_id']
        nickname = row['nickname'] or f"玩家{user_id}"
        contribution = row['contribution'] or 0
        total_contribution = row.get('total_contribution')
        
        print(f"  用户ID: {user_id}, 昵称: {nickname}")
        print(f"    现有贡献点: {contribution}")
        print(f"    历史总贡献点: {total_contribution}")
        
        # 检查数据一致性
        if total_contribution is None:
            print(f"    [WARNING] 历史总贡献点为 NULL！")
        elif total_contribution < contribution:
            print(f"    [ERROR] 历史总贡献点小于现有贡献点！数据异常！")
        elif total_contribution == contribution:
            print(f"    [INFO] 历史总贡献点等于现有贡献点（可能从未消耗过贡献点）")
        else:
            print(f"    [OK] 历史总贡献点大于现有贡献点（正常）")
        print()

def check_recent_claims():
    """检查最近的领取记录"""
    print("\n[检查最近的领取记录]")
    sql = """
        SELECT am.user_id, am.contribution, am.total_contribution,
               COALESCE(p.nickname, CONCAT('玩家', am.user_id)) as nickname,
               p.last_fire_ore_claim_date
        FROM alliance_members am
        LEFT JOIN player p ON am.user_id = p.user_id
        WHERE p.last_fire_ore_claim_date >= DATE_SUB(CURDATE(), INTERVAL 1 DAY)
        ORDER BY p.last_fire_ore_claim_date DESC
        LIMIT 10
    """
    rows = execute_query(sql)
    
    if not rows:
        print("  没有找到最近的领取记录")
        return
    
    print(f"  找到 {len(rows)} 条最近的领取记录：")
    for row in rows:
        user_id = row['user_id']
        nickname = row['nickname'] or f"玩家{user_id}"
        contribution = row['contribution'] or 0
        total_contribution = row.get('total_contribution')
        claim_date = row.get('last_fire_ore_claim_date')
        
        print(f"    用户: {nickname} (ID: {user_id})")
        print(f"      领取时间: {claim_date}")
        print(f"      现有贡献点: {contribution}")
        print(f"      历史总贡献点: {total_contribution}")
        
        # 检查是否异常
        if total_contribution is not None and total_contribution < contribution:
            print(f"      [ERROR] 历史总贡献点小于现有贡献点！数据异常！")
        print()

if __name__ == "__main__":
    test_update()
    check_recent_claims()
    print("\n" + "=" * 80)
    print("如果发现历史总贡献点被错误减少，可能的原因：")
    print("1. 数据库触发器没有正确创建或工作")
    print("2. 有其他地方直接更新了 total_contribution 字段")
    print("3. update_member_contribution 方法的逻辑有问题")
    print("=" * 80)
