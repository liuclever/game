"""测试真实的贡献点流程：模拟用户操作"""
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

def simulate_user_flow():
    """模拟用户操作流程"""
    print("=" * 80)
    print("模拟用户操作流程测试")
    print("=" * 80)
    
    # 找一个测试用户
    sql = """
        SELECT am.user_id, am.contribution, am.total_contribution,
               COALESCE(p.nickname, CONCAT('玩家', am.user_id)) as nickname
        FROM alliance_members am
        LEFT JOIN player p ON am.user_id = p.user_id
        WHERE am.contribution >= 10
        LIMIT 1
    """
    rows = execute_query(sql)
    if not rows:
        print("[ERROR] 未找到有足够贡献点的用户")
        return
    
    user = rows[0]
    user_id = user['user_id']
    initial_contribution = user['contribution'] or 0
    initial_total = user.get('total_contribution') or initial_contribution
    
    print(f"\n测试用户: {user['nickname']} (ID: {user_id})")
    print(f"初始状态: 现有贡献点={initial_contribution}, 历史总贡献点={initial_total}")
    
    repo = MySQLAllianceRepo()
    
    # 步骤1: 增加贡献点（模拟捐赠）
    print("\n[步骤1] 增加 20 点贡献（模拟捐赠）")
    repo.update_member_contribution(user_id, 20)
    data1 = get_member_data(user_id)
    print(f"  结果: 现有贡献点={data1['contribution']}, 历史总贡献点={data1.get('total_contribution')}")
    
    expected_contribution1 = initial_contribution + 20
    expected_total1 = initial_total + 20
    
    if data1['contribution'] != expected_contribution1:
        print(f"  [ERROR] 现有贡献点错误: 期望 {expected_contribution1}, 实际 {data1['contribution']}")
        return False
    if data1.get('total_contribution') != expected_total1:
        print(f"  [ERROR] 历史总贡献点错误: 期望 {expected_total1}, 实际 {data1.get('total_contribution')}")
        return False
    print(f"  [OK] 增加贡献点成功")
    
    # 步骤2: 减少贡献点（模拟消耗）
    print("\n[步骤2] 减少 10 点贡献（模拟消耗）")
    repo.update_member_contribution(user_id, -10)
    data2 = get_member_data(user_id)
    print(f"  结果: 现有贡献点={data2['contribution']}, 历史总贡献点={data2.get('total_contribution')}")
    
    expected_contribution2 = expected_contribution1 - 10
    expected_total2 = expected_total1  # 历史总贡献点不应该减少
    
    if data2['contribution'] != expected_contribution2:
        print(f"  [ERROR] 现有贡献点错误: 期望 {expected_contribution2}, 实际 {data2['contribution']}")
        return False
    if data2.get('total_contribution') != expected_total2:
        print(f"  [ERROR] 历史总贡献点被错误减少: 期望 {expected_total2}, 实际 {data2.get('total_contribution')}")
        print(f"  [ERROR] 这就是问题所在！历史总贡献点不应该减少！")
        return False
    print(f"  [OK] 减少贡献点成功，历史总贡献点保持不变")
    
    # 步骤3: 再次减少贡献点
    print("\n[步骤3] 再次减少 5 点贡献（模拟消耗）")
    repo.update_member_contribution(user_id, -5)
    data3 = get_member_data(user_id)
    print(f"  结果: 现有贡献点={data3['contribution']}, 历史总贡献点={data3.get('total_contribution')}")
    
    expected_contribution3 = expected_contribution2 - 5
    expected_total3 = expected_total2  # 历史总贡献点不应该减少
    
    if data3['contribution'] != expected_contribution3:
        print(f"  [ERROR] 现有贡献点错误: 期望 {expected_contribution3}, 实际 {data3['contribution']}")
        return False
    if data3.get('total_contribution') != expected_total3:
        print(f"  [ERROR] 历史总贡献点被错误减少: 期望 {expected_total3}, 实际 {data3.get('total_contribution')}")
        print(f"  [ERROR] 这就是问题所在！历史总贡献点不应该减少！")
        return False
    print(f"  [OK] 再次减少贡献点成功，历史总贡献点保持不变")
    
    # 最终验证
    print("\n[最终验证]")
    print(f"  现有贡献点: {data3['contribution']}")
    print(f"  历史总贡献点: {data3.get('total_contribution')}")
    
    if data3.get('total_contribution') < data3['contribution']:
        print(f"  [ERROR] 历史总贡献点小于现有贡献点，数据异常！")
        return False
    
    if data3.get('total_contribution') == data3['contribution']:
        print(f"  [WARN] 历史总贡献点等于现有贡献点")
        print(f"  [WARN] 这可能是因为用户从未消耗过贡献点，或者数据被错误初始化")
        print(f"  [WARN] 如果用户消耗过贡献点，这两个数字应该不同")
    
    print(f"\n[SUCCESS] 测试完成！")
    print(f"  如果历史总贡献点保持不变，说明功能正常")
    print(f"  如果历史总贡献点减少了，说明有问题需要修复")
    
    return True

if __name__ == "__main__":
    simulate_user_flow()
