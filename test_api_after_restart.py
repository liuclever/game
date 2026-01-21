"""测试重启后的API响应"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from infrastructure.db.connection import execute_query
from application.services.alliance_service import AllianceService
from infrastructure.db.alliance_repo_mysql import MySQLAllianceRepo
from infrastructure.db.player_repo_mysql import MySQLPlayerRepo
from infrastructure.db.beast_repo_mysql import MySQLBeastRepo
from infrastructure.db.inventory_repo_mysql import MySQLInventoryRepo
from infrastructure.config.item_repo_from_config import ConfigItemRepo
from infrastructure.db.player_effect_repo_mysql import MySQLPlayerEffectRepo
from application.services.inventory_service import InventoryService
from application.services.beast_service import BeastService

def test_api_response(user_id):
    """测试API响应（完全模拟路由层）"""
    print("=" * 80)
    print(f"测试用户 ID: {user_id} 的API响应（模拟重启后的路由层）")
    print("=" * 80)
    
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
        print(f"[ERROR] 无法获取联盟信息: {result.get('error')}")
        return
    
    alliance = result["alliance"]
    member_info = result["member_info"]
    
    # 完全模拟路由层的转换（使用和 routes/alliance_routes.py 完全相同的代码）
    api_response = {
        "ok": True,
        "alliance": {
            "id": alliance.id,
            "name": alliance.name,
            "leader_id": alliance.leader_id,
            "level": alliance.level,
            "exp": alliance.exp,
            "funds": alliance.funds,
            "crystals": alliance.crystals,
            "prosperity": alliance.prosperity,
            "notice": alliance.notice,
        },
        "member_info": {
            "role": member_info.role,
            "contribution": member_info.contribution or 0,
            "total_contribution": (member_info.total_contribution if hasattr(member_info, 'total_contribution') and member_info.total_contribution is not None else (member_info.contribution or 0)),
        },
        "member_count": result["member_count"],
        "member_capacity": result.get("member_capacity"),
        "fire_ore_claimed_today": bool(result.get("fire_ore_claimed_today", False)),
    }
    
    print(f"\n[API响应JSON]")
    json_str = json.dumps(api_response, ensure_ascii=False, indent=2)
    print(json_str)
    
    # 检查member_info
    print(f"\n[member_info检查]")
    member_info_dict = api_response["member_info"]
    print(f"  role: {member_info_dict.get('role')}")
    print(f"  contribution: {member_info_dict.get('contribution')}")
    print(f"  total_contribution: {member_info_dict.get('total_contribution')}")
    
    # 验证
    if 'total_contribution' in member_info_dict:
        print(f"\n  ✅ total_contribution 字段存在！")
        print(f"  值: {member_info_dict['total_contribution']}")
    else:
        print(f"\n  ❌ total_contribution 字段不存在！")
        print(f"  这是问题所在！")
    
    # 检查值是否正确
    db_sql = """
        SELECT am.contribution, am.total_contribution
        FROM alliance_members am
        WHERE am.user_id = %s
    """
    db_rows = execute_query(db_sql, (user_id,))
    if db_rows:
        db_contribution = db_rows[0]['contribution'] or 0
        db_total = db_rows[0].get('total_contribution')
        
        print(f"\n[数据库对比]")
        print(f"  数据库: contribution={db_contribution}, total_contribution={db_total}")
        print(f"  API返回: contribution={member_info_dict.get('contribution')}, total_contribution={member_info_dict.get('total_contribution')}")
        
        if member_info_dict.get('total_contribution') == db_total:
            print(f"  ✅ total_contribution 值正确！")
        else:
            print(f"  ❌ total_contribution 值不正确！")

if __name__ == "__main__":
    test_api_response(20057)
    print("\n" + "=" * 80)
    print("如果测试显示 total_contribution 字段存在且正确，")
    print("但实际API响应中没有，请检查：")
    print("1. 后端服务是否真的重启了（可能需要完全停止再启动）")
    print("2. 是否有其他路由文件覆盖了这个路由")
    print("3. 浏览器是否缓存了旧的响应")
    print("=" * 80)
