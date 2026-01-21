"""全面测试贡献点问题：模拟真实的用户操作流程"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from infrastructure.db.connection import execute_query, execute_update
from infrastructure.db.alliance_repo_mysql import MySQLAllianceRepo
from infrastructure.db.player_repo_mysql import MySQLPlayerRepo
from infrastructure.db.beast_repo_mysql import MySQLBeastRepo
from infrastructure.db.inventory_repo_mysql import MySQLInventoryRepo
from infrastructure.config.item_repo_from_config import ConfigItemRepo
from infrastructure.db.player_effect_repo_mysql import MySQLPlayerEffectRepo
from application.services.alliance_service import AllianceService
from application.services.inventory_service import InventoryService
from application.services.beast_service import BeastService
from interfaces.routes.alliance_routes import get_my_alliance
from flask import Flask
from unittest.mock import patch, MagicMock

def get_member_data(user_id):
    """直接从数据库获取成员数据"""
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

def simulate_api_call(user_id):
    """模拟 API 调用，获取返回的 JSON 数据"""
    # 初始化服务
    alliance_repo = MySQLAllianceRepo()
    player_repo = MySQLPlayerRepo()
    beast_repo = MySQLBeastRepo()
    inventory_repo = MySQLInventoryRepo()
    item_repo = ConfigItemRepo()
    player_effect_repo = MySQLPlayerEffectRepo()
    
    beast_service = BeastService(
        template_repo=None,
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
    
    # 获取联盟信息
    result = alliance_service.get_my_alliance(user_id)
    
    if not result.get("ok"):
        return None
    
    member_info = result["member_info"]
    
    # 模拟路由层的转换（这是关键！）
    api_response = {
        "ok": True,
        "member_info": {
            "role": member_info.role,
            "contribution": member_info.contribution or 0,
            "total_contribution": getattr(member_info, 'total_contribution', None) if getattr(member_info, 'total_contribution', None) is not None else (member_info.contribution or 0),
        }
    }
    
    return api_response

def comprehensive_test():
    """全面测试"""
    print("=" * 80)
    print("全面测试：模拟真实的用户操作流程")
    print("=" * 80)
    
    # 找一个有足够贡献点的用户
    sql = """
        SELECT am.user_id, am.contribution, am.total_contribution,
               COALESCE(p.nickname, CONCAT('玩家', am.user_id)) as nickname
        FROM alliance_members am
        LEFT JOIN player p ON am.user_id = p.user_id
        WHERE am.contribution >= 10
        ORDER BY am.contribution DESC
        LIMIT 1
    """
    rows = execute_query(sql)
    
    if not rows:
        print("[ERROR] 未找到有足够贡献点的用户")
        return False
    
    user = rows[0]
    user_id = user['user_id']
    nickname = user['nickname'] or f"玩家{user_id}"
    
    print(f"\n测试用户: {nickname} (ID: {user_id})")
    
    # 确保 total_contribution 有值且大于 contribution
    if user.get('total_contribution') is None or user.get('total_contribution') <= user['contribution']:
        print(f"\n[设置测试数据] 确保 total_contribution > contribution")
        new_total = (user['contribution'] or 0) + 10
        sql_update = """
            UPDATE alliance_members 
            SET total_contribution = %s
            WHERE user_id = %s
        """
        execute_update(sql_update, (new_total, user_id))
        # 重新获取
        rows = execute_query(sql)
        user = rows[0]
    
    initial_contribution = user['contribution'] or 0
    initial_total = user.get('total_contribution') or 0
    
    print(f"\n[步骤1] 初始状态")
    print(f"  数据库: 现有贡献点={initial_contribution}, 历史总贡献点={initial_total}")
    
    # 模拟 API 调用
    api_before = simulate_api_call(user_id)
    if api_before:
        api_contribution_before = api_before['member_info']['contribution']
        api_total_before = api_before['member_info']['total_contribution']
        print(f"  API返回: 现有贡献点={api_contribution_before}, 历史总贡献点={api_total_before}")
        
        if api_total_before != initial_total:
            print(f"  [ERROR] API 返回的 total_contribution 与数据库不一致！")
            print(f"    数据库: {initial_total}, API: {api_total_before}")
            return False
    
    # 清除今日领取记录
    sql = """
        UPDATE player 
        SET last_fire_ore_claim_date = DATE_SUB(CURDATE(), INTERVAL 1 DAY)
        WHERE user_id = %s
    """
    execute_update(sql, (user_id,))
    
    # 初始化服务
    alliance_repo = MySQLAllianceRepo()
    player_repo = MySQLPlayerRepo()
    beast_repo = MySQLBeastRepo()
    inventory_repo = MySQLInventoryRepo()
    item_repo = ConfigItemRepo()
    player_effect_repo = MySQLPlayerEffectRepo()
    
    beast_service = BeastService(
        template_repo=None,
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
    
    # 执行领取火能原石
    print(f"\n[步骤2] 执行领取火能原石（消耗5点贡献）")
    result = alliance_service.claim_fire_ore(user_id)
    
    if not result.get("ok"):
        print(f"  [ERROR] 领取失败: {result.get('error')}")
        return False
    
    print(f"  [OK] 领取成功")
    
    # 检查数据库中的数据
    db_after = get_member_data(user_id)
    db_contribution_after = db_after['contribution'] or 0
    db_total_after = db_after.get('total_contribution')
    
    print(f"\n[步骤3] 领取后的状态")
    print(f"  数据库: 现有贡献点={db_contribution_after}, 历史总贡献点={db_total_after}")
    
    # 再次模拟 API 调用
    api_after = simulate_api_call(user_id)
    if api_after:
        api_contribution_after = api_after['member_info']['contribution']
        api_total_after = api_after['member_info']['total_contribution']
        print(f"  API返回: 现有贡献点={api_contribution_after}, 历史总贡献点={api_total_after}")
        
        # 这是关键检查！
        if api_total_after != initial_total:
            print(f"\n  [ERROR] API 返回的 total_contribution 被错误减少了！")
            print(f"    初始值: {initial_total}")
            print(f"    当前值: {api_total_after}")
            print(f"    减少了: {initial_total - api_total_after}")
            print(f"\n  [问题定位] 路由层的逻辑有问题！")
            return False
        else:
            print(f"  [OK] API 返回的 total_contribution 正确（保持不变）")
    
    # 验证结果
    expected_contribution = max(0, initial_contribution - 5)
    expected_total = initial_total
    
    print(f"\n[验证结果]")
    print(f"  期望: 现有贡献点={expected_contribution}, 历史总贡献点={expected_total}")
    
    success = True
    
    # 检查数据库
    if db_contribution_after != expected_contribution:
        print(f"  [ERROR] 数据库现有贡献点错误!")
        success = False
    else:
        print(f"  [OK] 数据库现有贡献点正确")
    
    if db_total_after != expected_total:
        print(f"  [ERROR] 数据库历史总贡献点被错误减少!")
        success = False
    else:
        print(f"  [OK] 数据库历史总贡献点保持不变")
    
    # 检查 API
    if api_after:
        if api_total_after != expected_total:
            print(f"  [ERROR] API 返回的历史总贡献点错误!")
            success = False
        else:
            print(f"  [OK] API 返回的历史总贡献点正确")
    
    return success

if __name__ == "__main__":
    result = comprehensive_test()
    print("\n" + "=" * 80)
    if result:
        print("[SUCCESS] 测试通过！所有数据都正确")
    else:
        print("[FAILED] 测试失败！发现了问题")
        print("\n请检查上面的错误信息，找到问题所在")
    print("=" * 80)
