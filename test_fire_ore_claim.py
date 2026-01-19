"""测试领取火能原石时贡献点的变化"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from infrastructure.db.connection import execute_query, execute_update
from infrastructure.db.alliance_repo_mysql import MySQLAllianceRepo
from application.services.alliance_service import AllianceService
from application.services.inventory_service import InventoryService
from infrastructure.db.player_repo_mysql import MySQLPlayerRepo

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

def test_fire_ore_claim():
    """测试领取火能原石"""
    print("=" * 80)
    print("测试领取火能原石时贡献点的变化")
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
    initial_contribution = user['contribution'] or 0
    initial_total = user.get('total_contribution') or initial_contribution
    
    print(f"\n测试用户: {user['nickname']} (ID: {user_id})")
    print(f"初始状态: 现有贡献点={initial_contribution}, 历史总贡献点={initial_total}")
    
    # 清除今日领取记录（确保可以领取）
    sql = """
        UPDATE player 
        SET last_fire_ore_claim_date = DATE_SUB(CURDATE(), INTERVAL 1 DAY)
        WHERE user_id = %s
    """
    execute_update(sql, (user_id,))
    print("\n[步骤1] 清除今日领取记录，确保可以领取")
    
    # 确保用户有火能原石物品槽位
    # 这里我们直接测试 update_member_contribution 方法
    repo = MySQLAllianceRepo()
    
    print("\n[步骤2] 模拟消耗 5 点贡献（领取火能原石）")
    print(f"  调用: update_member_contribution({user_id}, -5)")
    
    # 记录更新前的数据
    before_data = get_member_data(user_id)
    before_contribution = before_data['contribution'] or 0
    before_total = before_data.get('total_contribution') or before_contribution
    
    print(f"  更新前: 现有贡献点={before_contribution}, 历史总贡献点={before_total}")
    
    # 执行更新
    repo.update_member_contribution(user_id, -5)
    
    # 记录更新后的数据
    after_data = get_member_data(user_id)
    after_contribution = after_data['contribution'] or 0
    after_total = after_data.get('total_contribution') or after_contribution
    
    print(f"  更新后: 现有贡献点={after_contribution}, 历史总贡献点={after_total}")
    
    # 验证
    expected_contribution = max(0, before_contribution - 5)
    expected_total = before_total  # 历史总贡献点不应该改变
    
    print(f"\n[验证]")
    print(f"  期望: 现有贡献点={expected_contribution}, 历史总贡献点={expected_total}")
    
    success = True
    if after_contribution != expected_contribution:
        print(f"  [ERROR] 现有贡献点错误: 期望 {expected_contribution}, 实际 {after_contribution}")
        success = False
    else:
        print(f"  [OK] 现有贡献点正确: {after_contribution}")
    
    if after_total != expected_total:
        print(f"  [ERROR] 历史总贡献点被错误减少!")
        print(f"  [ERROR] 期望: {expected_total}, 实际: {after_total}")
        print(f"  [ERROR] 减少了: {expected_total - after_total} 点")
        success = False
    else:
        print(f"  [OK] 历史总贡献点保持不变: {after_total}")
    
    if after_total < after_contribution:
        print(f"  [ERROR] 历史总贡献点小于现有贡献点!")
        success = False
    else:
        print(f"  [OK] 历史总贡献点 >= 现有贡献点")
    
    # 检查数据库中的实际 SQL
    print(f"\n[检查] 查看实际执行的 SQL 逻辑")
    print(f"  减少贡献点时应该执行:")
    print(f"    UPDATE alliance_members")
    print(f"    SET contribution = GREATEST(0, contribution + (-5))")
    print(f"    WHERE user_id = {user_id}")
    print(f"  注意：不应该更新 total_contribution 字段")
    
    return success

if __name__ == "__main__":
    result = test_fire_ore_claim()
    print("\n" + "=" * 80)
    if result:
        print("[SUCCESS] 测试通过！历史总贡献点没有被减少")
    else:
        print("[FAILED] 测试失败！历史总贡献点被错误减少了")
        print("\n可能的原因:")
        print("1. 数据库触发器没有正确创建")
        print("2. 有其他地方在更新 total_contribution")
        print("3. SQL 执行有问题")
    print("=" * 80)
