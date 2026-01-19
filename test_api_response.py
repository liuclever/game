"""测试API返回的数据"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from infrastructure.db.alliance_repo_mysql import MySQLAllianceRepo
from application.services.alliance_service import AllianceService
from infrastructure.db.player_repo_mysql import MySQLPlayerRepo
from application.services.inventory_service import InventoryService
from infrastructure.db.inventory_repo_mysql import MySQLInventoryRepo
from domain.repositories.item_repo import IItemRepo

# 简化版本，直接测试 get_member 方法
def test_get_member():
    """测试 get_member 方法返回的数据"""
    print("=" * 80)
    print("测试 get_member 方法返回的数据")
    print("=" * 80)
    
    # 找一个测试用户
    from infrastructure.db.connection import execute_query
    sql = """
        SELECT am.user_id, am.contribution, am.total_contribution
        FROM alliance_members am
        WHERE am.contribution >= 5
        LIMIT 1
    """
    rows = execute_query(sql)
    if not rows:
        print("[ERROR] 未找到测试用户")
        return False
    
    user_id = rows[0]['user_id']
    db_contribution = rows[0]['contribution'] or 0
    db_total = rows[0].get('total_contribution') or 0
    
    print(f"\n测试用户 ID: {user_id}")
    print(f"数据库直接查询:")
    print(f"  现有贡献点: {db_contribution}")
    print(f"  历史总贡献点: {db_total}")
    
    # 使用 get_member 方法
    repo = MySQLAllianceRepo()
    member = repo.get_member(user_id)
    
    if not member:
        print("[ERROR] get_member 返回 None")
        return False
    
    api_contribution = member.contribution or 0
    api_total = getattr(member, 'total_contribution', 0) or 0
    
    print(f"\nget_member 方法返回:")
    print(f"  现有贡献点: {api_contribution}")
    print(f"  历史总贡献点: {api_total}")
    
    # 验证
    success = True
    if api_contribution != db_contribution:
        print(f"  [ERROR] 现有贡献点不一致!")
        success = False
    else:
        print(f"  [OK] 现有贡献点一致")
    
    if api_total != db_total:
        print(f"  [ERROR] 历史总贡献点不一致!")
        print(f"  [ERROR] 数据库: {db_total}, API: {api_total}")
        success = False
    else:
        print(f"  [OK] 历史总贡献点一致")
    
    # 测试减少贡献点后的情况
    print(f"\n[测试] 减少贡献点后")
    repo.update_member_contribution(user_id, -5)
    
    # 重新查询
    member_after = repo.get_member(user_id)
    api_contribution_after = member_after.contribution or 0
    api_total_after = getattr(member_after, 'total_contribution', 0) or 0
    
    sql_after = """
        SELECT am.user_id, am.contribution, am.total_contribution
        FROM alliance_members am
        WHERE am.user_id = %s
    """
    db_rows_after = execute_query(sql_after, (user_id,))
    db_contribution_after = db_rows_after[0]['contribution'] or 0
    db_total_after = db_rows_after[0].get('total_contribution') or 0
    
    print(f"  数据库: 现有贡献点={db_contribution_after}, 历史总贡献点={db_total_after}")
    print(f"  API: 现有贡献点={api_contribution_after}, 历史总贡献点={api_total_after}")
    
    if api_total_after != db_total_after:
        print(f"  [ERROR] 减少贡献点后，历史总贡献点不一致!")
        success = False
    elif api_total_after != api_total:
        print(f"  [ERROR] 历史总贡献点被减少了!")
        success = False
    else:
        print(f"  [OK] 历史总贡献点保持不变")
    
    return success

if __name__ == "__main__":
    result = test_get_member()
    print("\n" + "=" * 80)
    if result:
        print("[SUCCESS] 所有测试通过！")
    else:
        print("[FAILED] 测试失败！")
    print("=" * 80)
