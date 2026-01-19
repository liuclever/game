"""测试联盟成员历史总贡献点功能

测试场景：
1. 检查数据库字段是否存在
2. 测试增加贡献点（捐赠）时，两个值都增加
3. 测试减少贡献点（消耗）时，只有现有贡献点减少，历史总贡献点不变
4. 验证历史总贡献点只增不减
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from infrastructure.db.connection import execute_query, execute_update
from infrastructure.db.alliance_repo_mysql import MySQLAllianceRepo
from domain.entities.alliance import AllianceMember

def check_database_field():
    """检查数据库字段是否存在"""
    print("=" * 60)
    print("【测试1】检查数据库字段")
    print("=" * 60)
    
    sql = """
        SELECT COUNT(*) as cnt
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = 'game_tower'
          AND TABLE_NAME = 'alliance_members'
          AND COLUMN_NAME = 'total_contribution'
    """
    rows = execute_query(sql)
    exists = rows[0]['cnt'] > 0 if rows else False
    
    if exists:
        print("[OK] total_contribution 字段存在")
    else:
        print("[ERROR] total_contribution 字段不存在，请先执行迁移脚本：")
        print("  source sql/042_add_total_contribution_to_alliance_members.sql")
        return False
    
    return True

def get_member_contribution(user_id: int):
    """获取成员的贡献点信息"""
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

def test_increase_contribution():
    """测试增加贡献点"""
    print("\n" + "=" * 60)
    print("【测试2】测试增加贡献点（捐赠）")
    print("=" * 60)
    
    # 查找一个联盟成员
    sql = """
        SELECT am.user_id, am.contribution, am.total_contribution,
               COALESCE(p.nickname, CONCAT('玩家', am.user_id)) as nickname
        FROM alliance_members am
        LEFT JOIN player p ON am.user_id = p.user_id
        LIMIT 1
    """
    rows = execute_query(sql)
    if not rows:
        print("[ERROR] 未找到联盟成员，无法测试")
        return False
    
    member = rows[0]
    user_id = member['user_id']
    old_contribution = member['contribution'] or 0
    old_total = member.get('total_contribution') or old_contribution
    
    print(f"测试用户: {member['nickname']} (ID: {user_id})")
    print(f"初始状态: 现有贡献点={old_contribution}, 历史总贡献点={old_total}")
    
    # 使用仓储方法增加贡献点（模拟捐赠）
    repo = MySQLAllianceRepo()
    increase_amount = 10
    repo.update_member_contribution(user_id, increase_amount)
    
    # 检查结果
    new_data = get_member_contribution(user_id)
    new_contribution = new_data['contribution'] or 0
    new_total = new_data.get('total_contribution') or new_contribution
    
    print(f"增加 {increase_amount} 点贡献后:")
    print(f"  现有贡献点: {old_contribution} -> {new_contribution}")
    print(f"  历史总贡献点: {old_total} -> {new_total}")
    
    # 验证
    success = True
    if new_contribution != old_contribution + increase_amount:
        print(f"[ERROR] 现有贡献点错误: 期望 {old_contribution + increase_amount}, 实际 {new_contribution}")
        success = False
    else:
        print(f"[OK] 现有贡献点正确: {new_contribution}")
    
    if new_total != old_total + increase_amount:
        print(f"[ERROR] 历史总贡献点错误: 期望 {old_total + increase_amount}, 实际 {new_total}")
        success = False
    else:
        print(f"[OK] 历史总贡献点正确: {new_total}")
    
    if new_total < new_contribution:
        print(f"[ERROR] 历史总贡献点不应小于现有贡献点")
        success = False
    else:
        print(f"[OK] 历史总贡献点 >= 现有贡献点")
    
    return success

def test_decrease_contribution():
    """测试减少贡献点"""
    print("\n" + "=" * 60)
    print("【测试3】测试减少贡献点（消耗）")
    print("=" * 60)
    
    # 查找一个联盟成员
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
        print("✗ 未找到有足够贡献点的联盟成员，无法测试")
        return False
    
    member = rows[0]
    user_id = member['user_id']
    old_contribution = member['contribution'] or 0
    old_total = member.get('total_contribution') or old_contribution
    
    print(f"测试用户: {member['nickname']} (ID: {user_id})")
    print(f"初始状态: 现有贡献点={old_contribution}, 历史总贡献点={old_total}")
    
    # 使用仓储方法减少贡献点（模拟消耗）
    repo = MySQLAllianceRepo()
    decrease_amount = 5
    repo.update_member_contribution(user_id, -decrease_amount)
    
    # 检查结果
    new_data = get_member_contribution(user_id)
    new_contribution = new_data['contribution'] or 0
    new_total = new_data.get('total_contribution') or new_contribution
    
    print(f"减少 {decrease_amount} 点贡献后:")
    print(f"  现有贡献点: {old_contribution} -> {new_contribution}")
    print(f"  历史总贡献点: {old_total} -> {new_total}")
    
    # 验证
    success = True
    expected_contribution = max(0, old_contribution - decrease_amount)
    if new_contribution != expected_contribution:
        print(f"[ERROR] 现有贡献点错误: 期望 {expected_contribution}, 实际 {new_contribution}")
        success = False
    else:
        print(f"[OK] 现有贡献点正确: {new_contribution}")
    
    if new_total != old_total:
        print(f"[ERROR] 历史总贡献点不应改变: 期望 {old_total}, 实际 {new_total}")
        success = False
    else:
        print(f"[OK] 历史总贡献点保持不变: {new_total}")
    
    if new_total < new_contribution:
        print(f"[ERROR] 历史总贡献点不应小于现有贡献点")
        success = False
    else:
        print(f"[OK] 历史总贡献点 >= 现有贡献点")
    
    return success

def test_multiple_operations():
    """测试多次操作"""
    print("\n" + "=" * 60)
    print("【测试4】测试多次操作（增加->减少->增加）")
    print("=" * 60)
    
    # 查找一个联盟成员
    sql = """
        SELECT am.user_id, am.contribution, am.total_contribution,
               COALESCE(p.nickname, CONCAT('玩家', am.user_id)) as nickname
        FROM alliance_members am
        LEFT JOIN player p ON am.user_id = p.user_id
        LIMIT 1
    """
    rows = execute_query(sql)
    if not rows:
        print("[ERROR] 未找到联盟成员，无法测试")
        return False
    
    member = rows[0]
    user_id = member['user_id']
    initial_contribution = member['contribution'] or 0
    initial_total = member.get('total_contribution') or initial_contribution
    
    print(f"测试用户: {member['nickname']} (ID: {user_id})")
    print(f"初始状态: 现有贡献点={initial_contribution}, 历史总贡献点={initial_total}")
    
    repo = MySQLAllianceRepo()
    
    # 操作1: 增加 20 点
    print("\n操作1: 增加 20 点贡献")
    repo.update_member_contribution(user_id, 20)
    data1 = get_member_contribution(user_id)
    print(f"  现有贡献点: {data1['contribution']}, 历史总贡献点: {data1.get('total_contribution')}")
    
    # 操作2: 减少 10 点
    print("\n操作2: 减少 10 点贡献")
    repo.update_member_contribution(user_id, -10)
    data2 = get_member_contribution(user_id)
    print(f"  现有贡献点: {data2['contribution']}, 历史总贡献点: {data2.get('total_contribution')}")
    
    # 操作3: 再增加 15 点
    print("\n操作3: 再增加 15 点贡献")
    repo.update_member_contribution(user_id, 15)
    data3 = get_member_contribution(user_id)
    print(f"  现有贡献点: {data3['contribution']}, 历史总贡献点: {data3.get('total_contribution')}")
    
    # 验证最终结果
    final_contribution = data3['contribution'] or 0
    final_total = data3.get('total_contribution') or final_contribution
    
    expected_contribution = initial_contribution + 20 - 10 + 15
    expected_total = initial_total + 20 + 15  # 只累加增加的部分
    
    print(f"\n最终状态:")
    print(f"  现有贡献点: {final_contribution} (期望: {expected_contribution})")
    print(f"  历史总贡献点: {final_total} (期望: {expected_total})")
    
    success = True
    if final_contribution != expected_contribution:
        print(f"[ERROR] 现有贡献点错误")
        success = False
    else:
        print(f"[OK] 现有贡献点正确")
    
    if final_total != expected_total:
        print(f"[ERROR] 历史总贡献点错误")
        success = False
    else:
        print(f"[OK] 历史总贡献点正确")
    
    if final_total < final_contribution:
        print(f"[ERROR] 历史总贡献点不应小于现有贡献点")
        success = False
    else:
        print(f"[OK] 历史总贡献点 >= 现有贡献点")
    
    return success

def show_all_members():
    """显示所有成员的贡献点信息"""
    print("\n" + "=" * 60)
    print("【当前所有联盟成员的贡献点信息】")
    print("=" * 60)
    
    sql = """
        SELECT am.user_id, am.contribution, am.total_contribution,
               COALESCE(p.nickname, CONCAT('玩家', am.user_id)) as nickname,
               a.name as alliance_name
        FROM alliance_members am
        LEFT JOIN player p ON am.user_id = p.user_id
        LEFT JOIN alliances a ON am.alliance_id = a.id
        ORDER BY am.alliance_id, am.user_id
        LIMIT 20
    """
    rows = execute_query(sql)
    
    if not rows:
        print("没有找到联盟成员")
        return
    
    print(f"{'用户ID':<8} {'昵称':<15} {'联盟':<15} {'现有贡献':<10} {'历史总贡献':<12} {'状态':<8}")
    print("-" * 80)
    
    for row in rows:
        user_id = row['user_id']
        nickname = row['nickname'] or f"玩家{user_id}"
        alliance = row['alliance_name'] or "未知"
        contribution = row['contribution'] or 0
        total = row.get('total_contribution') or contribution
        
        status = "[OK]" if total >= contribution else "[ERR]"
        
        print(f"{user_id:<8} {nickname:<15} {alliance:<15} {contribution:<10} {total:<12} {status:<8}")

def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("联盟成员历史总贡献点功能测试")
    print("=" * 60)
    
    results = []
    
    # 测试1: 检查数据库字段
    if check_database_field():
        results.append(("字段检查", True))
        
        # 显示当前所有成员信息
        show_all_members()
        
        # 测试2: 增加贡献点
        results.append(("增加贡献点", test_increase_contribution()))
        
        # 测试3: 减少贡献点
        results.append(("减少贡献点", test_decrease_contribution()))
        
        # 测试4: 多次操作
        results.append(("多次操作", test_multiple_operations()))
        
        # 再次显示所有成员信息
        show_all_members()
    else:
        results.append(("字段检查", False))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("【测试结果汇总】")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "[PASS] 通过" if passed else "[FAIL] 失败"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("[SUCCESS] 所有测试通过！")
    else:
        print("[FAILED] 部分测试失败，请检查")
    print("=" * 60)

if __name__ == "__main__":
    main()
