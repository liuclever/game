"""测试完整的 API 流程：领取火能原石后检查贡献点变化"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from infrastructure.db.connection import execute_query, execute_update
from application.services.alliance_service import AllianceService
from infrastructure.db.alliance_repo_mysql import MySQLAllianceRepo
from infrastructure.db.player_repo_mysql import MySQLPlayerRepo
from infrastructure.db.beast_repo_mysql import MySQLBeastRepo
from infrastructure.db.inventory_repo_mysql import MySQLInventoryRepo
from infrastructure.config.item_repo_from_config import ConfigItemRepo
from infrastructure.db.player_effect_repo_mysql import MySQLPlayerEffectRepo
from application.services.inventory_service import InventoryService
from application.services.beast_service import BeastService

def get_member_data(user_id):
    """获取成员数据（直接从数据库）"""
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

def test_api_flow():
    """测试完整的 API 流程"""
    print("=" * 80)
    print("完整测试：通过 API 领取火能原石后检查贡献点变化")
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
    
    # 确保 total_contribution 有值
    if user.get('total_contribution') is None:
        print("\n[警告] total_contribution 为 NULL，设置为 contribution 的值")
        sql_update = """
            UPDATE alliance_members 
            SET total_contribution = contribution
            WHERE user_id = %s AND total_contribution IS NULL
        """
        execute_update(sql_update, (user_id,))
        rows = execute_query(sql)
        user = rows[0]
    
    initial_contribution = user['contribution'] or 0
    initial_total = user.get('total_contribution') or 0
    
    print(f"\n[初始状态 - 数据库]")
    print(f"  现有贡献点: {initial_contribution}")
    print(f"  历史总贡献点: {initial_total}")
    
    # 清除今日领取记录
    sql = """
        UPDATE player 
        SET last_fire_ore_claim_date = DATE_SUB(CURDATE(), INTERVAL 1 DAY)
        WHERE user_id = %s
    """
    execute_update(sql, (user_id,))
    
    # 初始化服务（模拟真实的 API 调用）
    alliance_repo = MySQLAllianceRepo()
    player_repo = MySQLPlayerRepo()
    beast_repo = MySQLBeastRepo()
    inventory_repo = MySQLInventoryRepo()
    item_repo = ConfigItemRepo()
    player_effect_repo = MySQLPlayerEffectRepo()
    
    beast_service = BeastService(
        template_repo=None,  # 不需要
        beast_repo=beast_repo,
        player_repo=player_repo,
    )
    
    inventory_service = InventoryService(
        item_repo=item_repo,
        inventory_repo=inventory_repo,
        player_repo=player_repo,
        beast_service=beast_service,
        player_effect_repo=player_effect_repo,
    )
    
    alliance_service = AllianceService(
        alliance_repo=alliance_repo,
        player_repo=player_repo,
        inventory_service=inventory_service,
        beast_repo=beast_repo
    )
    
    # 获取初始的联盟信息（模拟 get_my_alliance API）
    result_before = alliance_service.get_my_alliance(user_id)
    if result_before.get("ok"):
        member_info_before = result_before["member_info"]
        api_contribution_before = member_info_before.contribution or 0
        api_total_before = getattr(member_info_before, 'total_contribution', None) or 0
        print(f"\n[初始状态 - API (get_my_alliance)]")
        print(f"  现有贡献点: {api_contribution_before}")
        print(f"  历史总贡献点: {api_total_before}")
    
    # 调用 claim_fire_ore（模拟真实的 API 调用）
    print(f"\n[步骤1] 调用 claim_fire_ore API")
    result = alliance_service.claim_fire_ore(user_id)
    
    if not result.get("ok"):
        print(f"  [ERROR] API 返回失败: {result.get('error')}")
        return False
    
    print(f"  [OK] API 返回成功")
    
    # 检查数据库中的数据
    db_after = get_member_data(user_id)
    db_contribution_after = db_after['contribution'] or 0
    db_total_after = db_after.get('total_contribution')
    
    print(f"\n[更新后 - 数据库]")
    print(f"  现有贡献点: {db_contribution_after}")
    print(f"  历史总贡献点: {db_total_after}")
    
    # 再次调用 get_my_alliance（模拟前端刷新数据）
    result_after = alliance_service.get_my_alliance(user_id)
    if result_after.get("ok"):
        member_info_after = result_after["member_info"]
        api_contribution_after = member_info_after.contribution or 0
        api_total_after = getattr(member_info_after, 'total_contribution', None)
        print(f"\n[更新后 - API (get_my_alliance)]")
        print(f"  现有贡献点: {api_contribution_after}")
        print(f"  历史总贡献点: {api_total_after} (类型: {type(api_total_after).__name__})")
    
    # 验证结果
    expected_contribution = max(0, initial_contribution - 5)
    expected_total = initial_total  # 不应该改变
    
    print(f"\n[验证结果]")
    print(f"  期望: 现有贡献点={expected_contribution}, 历史总贡献点={expected_total}")
    
    success = True
    
    # 检查数据库数据
    if db_contribution_after != expected_contribution:
        print(f"  [ERROR] 数据库现有贡献点错误!")
        success = False
    else:
        print(f"  [OK] 数据库现有贡献点正确")
    
    if db_total_after is None:
        print(f"  [ERROR] 数据库历史总贡献点为 NULL!")
        success = False
    elif db_total_after != expected_total:
        print(f"  [ERROR] 数据库历史总贡献点被错误减少!")
        print(f"  [ERROR] 从 {initial_total} 减少到 {db_total_after}")
        success = False
    else:
        print(f"  [OK] 数据库历史总贡献点保持不变")
    
    # 检查 API 返回的数据
    if result_after.get("ok"):
        if api_total_after is None:
            print(f"  [WARNING] API 返回的历史总贡献点为 None!")
            print(f"  [WARNING] 前端会使用 contribution 作为默认值，导致显示错误")
            success = False
        elif api_total_after != expected_total:
            print(f"  [ERROR] API 返回的历史总贡献点错误!")
            print(f"  [ERROR] 期望: {expected_total}, 实际: {api_total_after}")
            success = False
        else:
            print(f"  [OK] API 返回的历史总贡献点正确")
    
    return success

if __name__ == "__main__":
    result = test_api_flow()
    print("\n" + "=" * 80)
    if result:
        print("[SUCCESS] 测试通过！")
    else:
        print("[FAILED] 测试失败！")
        print("\n可能的问题:")
        print("1. total_contribution 字段为 NULL，导致读取时使用 contribution 的值")
        print("2. API 返回的数据格式有问题")
        print("3. 前端显示逻辑有问题")
    print("=" * 80)
