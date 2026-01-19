"""测试火能原石领取时贡献点的变化（验证历史总贡献点不会被减少）"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from infrastructure.db.connection import execute_query, execute_update
from infrastructure.db.alliance_repo_mysql import MySQLAllianceRepo

def get_member_data(user_id):
    """获取成员数据"""
    sql = """
        SELECT contribution, total_contribution
        FROM alliance_members
        WHERE user_id = %s
    """
    rows = execute_query(sql, (user_id,))
    if rows:
        return rows[0]
    return None

def test_fire_ore_contribution():
    """测试领取火能原石时贡献点的变化"""
    print("=" * 60)
    print("测试：领取火能原石时贡献点的变化")
    print("=" * 60)
    
    # 请替换为你的测试用户ID
    test_user_id = int(input("请输入测试用户ID: "))
    
    # 获取初始数据
    initial_data = get_member_data(test_user_id)
    if not initial_data:
        print(f"[错误] 找不到用户 {test_user_id} 的联盟成员数据")
        return
    
    initial_contribution = initial_data.get('contribution', 0) or 0
    initial_total = initial_data.get('total_contribution', 0) or 0
    
    print(f"\n[初始状态]")
    print(f"  现有贡献点: {initial_contribution}")
    print(f"  历史总贡献点: {initial_total}")
    
    if initial_contribution < 5:
        print(f"\n[警告] 现有贡献点不足 5，无法领取火能原石")
        print(f"  请先增加贡献点（可以通过捐赠等方式）")
        return
    
    # 模拟领取火能原石（消耗 5 点贡献）
    print(f"\n[模拟领取火能原石]")
    print(f"  消耗贡献点: 5")
    
    repo = MySQLAllianceRepo()
    repo.update_member_contribution(test_user_id, -5)
    
    # 获取更新后的数据
    after_data = get_member_data(test_user_id)
    after_contribution = after_data.get('contribution', 0) or 0
    after_total = after_data.get('total_contribution', 0) or 0
    
    print(f"\n[更新后状态]")
    print(f"  现有贡献点: {after_contribution}")
    print(f"  历史总贡献点: {after_total}")
    
    # 验证结果
    print(f"\n[验证结果]")
    expected_contribution = max(0, initial_contribution - 5)
    expected_total = initial_total  # 历史总贡献点应该不变
    
    contribution_ok = (after_contribution == expected_contribution)
    total_ok = (after_total == expected_total)
    
    if contribution_ok:
        print(f"  ✓ 现有贡献点正确: {initial_contribution} -> {after_contribution} (预期: {expected_contribution})")
    else:
        print(f"  ✗ 现有贡献点错误: {initial_contribution} -> {after_contribution} (预期: {expected_contribution})")
    
    if total_ok:
        print(f"  ✓ 历史总贡献点正确: {initial_total} -> {after_total} (预期: {expected_total})")
    else:
        print(f"  ✗ 历史总贡献点错误: {initial_total} -> {after_total} (预期: {expected_total})")
        print(f"    历史总贡献点被错误地减少了！")
    
    if contribution_ok and total_ok:
        print(f"\n[SUCCESS] 测试通过！历史总贡献点保持不变。")
    else:
        print(f"\n[FAILED] 测试失败！请检查代码实现。")
    
    # 恢复数据（可选）
    restore = input("\n是否恢复贡献点？(y/n): ").strip().lower()
    if restore == 'y':
        repo.update_member_contribution(test_user_id, 5)
        restored_data = get_member_data(test_user_id)
        print(f"  已恢复: 现有贡献点 = {restored_data.get('contribution', 0)}")

if __name__ == "__main__":
    test_fire_ore_contribution()
