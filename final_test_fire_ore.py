"""最终测试：模拟完整的领取火能原石流程"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from infrastructure.db.connection import execute_query, execute_update
from infrastructure.db.alliance_repo_mysql import MySQLAllianceRepo
from application.services.alliance_service import AllianceService
from infrastructure.db.player_repo_mysql import MySQLPlayerRepo
from application.services.inventory_service import InventoryService
from infrastructure.db.inventory_repo_mysql import MySQLInventoryRepo
from domain.repositories.item_repo import IItemRepo

# 创建一个简单的 ItemRepo 实现
class SimpleItemRepo(IItemRepo):
    def get_by_id(self, item_id: int):
        return {"id": item_id, "name": "测试物品"}

def get_member_from_db(user_id):
    """直接从数据库获取成员数据"""
    sql = """
        SELECT am.user_id, am.contribution, am.total_contribution
        FROM alliance_members am
        WHERE am.user_id = %s
    """
    rows = execute_query(sql, (user_id,))
    if not rows:
        return None
    return rows[0]

def test_complete_flow():
    """完整测试流程"""
    print("=" * 80)
    print("完整测试：领取火能原石的完整流程")
    print("=" * 80)
    
    # 找一个测试用户
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
        print("[ERROR] 未找到测试用户")
        return False
    
    user_id = rows[0]['user_id']
    nickname = rows[0]['nickname']
    
    print(f"\n测试用户: {nickname} (ID: {user_id})")
    
    # 清除今日领取记录
    sql = """
        UPDATE player 
        SET last_fire_ore_claim_date = DATE_SUB(CURDATE(), INTERVAL 1 DAY)
        WHERE user_id = %s
    """
    execute_update(sql, (user_id,))
    
    # 获取初始数据（从数据库）
    db_before = get_member_from_db(user_id)
    before_contribution = db_before['contribution'] or 0
    before_total = db_before.get('total_contribution') or 0
    
    print(f"\n[初始状态 - 数据库]")
    print(f"  现有贡献点: {before_contribution}")
    print(f"  历史总贡献点: {before_total}")
    
    # 获取初始数据（通过 get_member）
    repo = MySQLAllianceRepo()
    member_before = repo.get_member(user_id)
    api_before_contribution = member_before.contribution or 0
    api_before_total = getattr(member_before, 'total_contribution', 0) or 0
    
    print(f"\n[初始状态 - API]")
    print(f"  现有贡献点: {api_before_contribution}")
    print(f"  历史总贡献点: {api_before_total}")
    
    if api_before_contribution != before_contribution or api_before_total != before_total:
        print(f"[ERROR] 数据库和API数据不一致！")
        return False
    
    # 模拟领取火能原石（只测试贡献点更新部分）
    print(f"\n[步骤1] 模拟消耗 5 点贡献（领取火能原石）")
    print(f"  调用: update_member_contribution({user_id}, -5)")
    
    repo.update_member_contribution(user_id, -5)
    
    # 检查数据库中的数据
    db_after = get_member_from_db(user_id)
    after_contribution = db_after['contribution'] or 0
    after_total = db_after.get('total_contribution') or 0
    
    print(f"\n[更新后 - 数据库]")
    print(f"  现有贡献点: {after_contribution}")
    print(f"  历史总贡献点: {after_total}")
    
    # 检查API返回的数据
    member_after = repo.get_member(user_id)
    api_after_contribution = member_after.contribution or 0
    api_after_total = getattr(member_after, 'total_contribution', 0) or 0
    
    print(f"\n[更新后 - API]")
    print(f"  现有贡献点: {api_after_contribution}")
    print(f"  历史总贡献点: {api_after_total}")
    
    # 验证
    expected_contribution = max(0, before_contribution - 5)
    expected_total = before_total  # 不应该改变
    
    print(f"\n[验证]")
    print(f"  期望: 现有贡献点={expected_contribution}, 历史总贡献点={expected_total}")
    
    success = True
    
    # 验证数据库数据
    if after_contribution != expected_contribution:
        print(f"  [ERROR] 数据库现有贡献点错误!")
        success = False
    else:
        print(f"  [OK] 数据库现有贡献点正确")
    
    if after_total != expected_total:
        print(f"  [ERROR] 数据库历史总贡献点被错误减少!")
        print(f"  [ERROR] 从 {before_total} 减少到 {after_total}")
        success = False
    else:
        print(f"  [OK] 数据库历史总贡献点保持不变")
    
    # 验证API数据
    if api_after_contribution != after_contribution:
        print(f"  [ERROR] API现有贡献点与数据库不一致!")
        success = False
    else:
        print(f"  [OK] API现有贡献点与数据库一致")
    
    if api_after_total != after_total:
        print(f"  [ERROR] API历史总贡献点与数据库不一致!")
        success = False
    else:
        print(f"  [OK] API历史总贡献点与数据库一致")
    
    # 模拟前端显示
    print(f"\n[前端显示模拟]")
    frontend_contribution = api_after_contribution
    frontend_total = api_after_total or api_after_contribution  # 前端回退逻辑
    print(f"  显示: 贡献: {frontend_contribution}/{frontend_total}")
    
    if frontend_total != expected_total:
        print(f"  [ERROR] 前端显示的历史总贡献点错误!")
        print(f"  [ERROR] 期望: {expected_total}, 实际: {frontend_total}")
        if frontend_total == frontend_contribution:
            print(f"  [ERROR] 前端使用了回退逻辑，说明 total_contribution 为 0 或不存在")
        success = False
    else:
        print(f"  [OK] 前端显示正确")
    
    return success

if __name__ == "__main__":
    result = test_complete_flow()
    print("\n" + "=" * 80)
    if result:
        print("[SUCCESS] 所有测试通过！")
        print("\n如果实际使用时还有问题，请:")
        print("1. 检查浏览器控制台是否有错误")
        print("2. 检查网络请求返回的数据")
        print("3. 提供具体的操作步骤和截图")
    else:
        print("[FAILED] 测试失败！请检查错误信息")
    print("=" * 80)
