"""完整测试领取火能原石的流程，包括数据读取"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from infrastructure.db.connection import execute_query, execute_update
from infrastructure.db.alliance_repo_mysql import MySQLAllianceRepo

def get_member_data(user_id):
    """获取成员数据"""
    sql = """
        SELECT am.user_id, am.contribution, am.total_contribution,
               COALESCE(p.nickname, CONCAT('玩家', am.user_id)) as nickname
        FROM alliance_members am
        LEFT JOIN player p ON am.user_id = p.user_id
        WHERE am.user_id = %s
    """
    rows = execute_query(sql, (user_id,))
    if not rows:
        return None
    return rows[0]

def test_full_flow():
    """完整测试流程"""
    print("=" * 80)
    print("完整测试：领取火能原石后的数据变化")
    print("=" * 80)
    
    # 找一个有足够贡献点的用户
    sql = """
        SELECT am.user_id, am.contribution, am.total_contribution,
               COALESCE(p.nickname, CONCAT('玩家', am.user_id)) as nickname
        FROM alliance_members am
        LEFT JOIN player p ON am.user_id = p.user_id
        WHERE am.contribution >= 5
        LIMIT 1
    """
    rows = execute_query(sql)
    if not rows:
        print("[ERROR] 未找到有足够贡献点的用户")
        return False
    
    user = rows[0]
    user_id = user['user_id']
    
    print(f"\n测试用户: {user['nickname']} (ID: {user_id})")
    
    # 清除今日领取记录
    sql = """
        UPDATE player 
        SET last_fire_ore_claim_date = DATE_SUB(CURDATE(), INTERVAL 1 DAY)
        WHERE user_id = %s
    """
    execute_update(sql, (user_id,))
    
    # 获取初始数据
    repo = MySQLAllianceRepo()
    member_before = repo.get_member(user_id)
    if not member_before:
        print("[ERROR] 无法获取成员信息")
        return False
    
    before_contribution = member_before.contribution or 0
    before_total = getattr(member_before, 'total_contribution', 0) or 0
    
    print(f"\n[初始状态]")
    print(f"  现有贡献点: {before_contribution}")
    print(f"  历史总贡献点: {before_total}")
    
    # 模拟领取火能原石（只测试贡献点更新部分）
    print(f"\n[模拟领取火能原石]")
    print(f"  调用: update_member_contribution({user_id}, -5)")
    
    repo.update_member_contribution(user_id, -5)
    
    # 重新读取数据
    member_after = repo.get_member(user_id)
    after_contribution = member_after.contribution or 0
    after_total = getattr(member_after, 'total_contribution', 0) or 0
    
    print(f"\n[更新后状态]")
    print(f"  现有贡献点: {after_contribution}")
    print(f"  历史总贡献点: {after_total}")
    
    # 验证
    expected_contribution = max(0, before_contribution - 5)
    expected_total = before_total
    
    print(f"\n[验证]")
    print(f"  期望: 现有贡献点={expected_contribution}, 历史总贡献点={expected_total}")
    
    success = True
    if after_contribution != expected_contribution:
        print(f"  [ERROR] 现有贡献点错误!")
        success = False
    else:
        print(f"  [OK] 现有贡献点正确")
    
    if after_total != expected_total:
        print(f"  [ERROR] 历史总贡献点被错误减少!")
        print(f"  [ERROR] 从 {before_total} 减少到 {after_total}")
        success = False
    else:
        print(f"  [OK] 历史总贡献点保持不变")
    
    # 检查数据库中的实际 SQL 执行情况
    print(f"\n[检查] 查看数据库中的实际数据")
    db_data = get_member_data(user_id)
    db_contribution = db_data['contribution'] or 0
    db_total = db_data.get('total_contribution') or 0
    
    print(f"  数据库查询结果: 现有贡献点={db_contribution}, 历史总贡献点={db_total}")
    
    if db_contribution != after_contribution or db_total != after_total:
        print(f"  [ERROR] 数据不一致!")
        success = False
    else:
        print(f"  [OK] 数据一致")
    
    return success

if __name__ == "__main__":
    result = test_full_flow()
    print("\n" + "=" * 80)
    if result:
        print("[SUCCESS] 所有测试通过！")
    else:
        print("[FAILED] 测试失败！请检查代码逻辑")
    print("=" * 80)
