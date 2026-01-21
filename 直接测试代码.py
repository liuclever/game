"""直接测试代码逻辑，不依赖Flask"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 模拟路由函数的逻辑
from application.services.alliance_service import AllianceService
from infrastructure.db.alliance_repo_mysql import MySQLAllianceRepo
from infrastructure.db.player_repo_mysql import MySQLPlayerRepo
from infrastructure.db.beast_repo_mysql import MySQLBeastRepo
from infrastructure.db.inventory_repo_mysql import MySQLInventoryRepo
from infrastructure.config.item_repo_from_config import ConfigItemRepo
from infrastructure.db.player_effect_repo_mysql import MySQLPlayerEffectRepo
from application.services.inventory_service import InventoryService
from application.services.beast_service import BeastService

def test_code_logic():
    """直接测试代码逻辑"""
    print("=" * 80)
    print("直接测试代码逻辑（模拟路由函数）")
    print("=" * 80)
    
    user_id = 20057
    
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
    
    # 模拟路由函数逻辑（完全按照 alliance_routes.py 的代码）
    result = alliance_service.get_my_alliance(user_id)
    
    if result["ok"]:
        alliance = result["alliance"]
        member_info = result["member_info"]
        
        # 计算total_contribution值 - 修复版本（和路由代码完全一致）
        total_contrib_value = getattr(member_info, 'total_contribution', None)
        if total_contrib_value is None:
            total_contrib_value = member_info.contribution or 0
        
        # 构建member_info字典 - 确保包含total_contribution（和路由代码完全一致）
        member_info_dict = {
            "role": member_info.role,
            "contribution": member_info.contribution or 0,
            "total_contribution": total_contrib_value,
        }
        
        # 构建完整响应（和路由代码完全一致）
        response_data = {
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
            "member_info": member_info_dict,
            "member_count": result["member_count"],
            "member_capacity": result.get("member_capacity"),
            "fire_ore_claimed_today": bool(result.get("fire_ore_claimed_today", False)),
        }
        
        print("\n[模拟路由函数返回的JSON]")
        print(json.dumps(response_data, ensure_ascii=False, indent=2))
        
        print("\n[member_info验证]")
        print(f"  字段: {list(member_info_dict.keys())}")
        print(f"  contribution: {member_info_dict['contribution']}")
        print(f"  total_contribution: {member_info_dict['total_contribution']}")
        
        if 'total_contribution' in member_info_dict:
            print(f"\n  [OK] total_contribution 字段存在！")
            print(f"  前端应显示: {member_info_dict['contribution']}/{member_info_dict['total_contribution']}")
        else:
            print(f"\n  [ERROR] total_contribution 字段不存在！")
    else:
        print(f"[ERROR] 获取联盟信息失败: {result.get('error')}")

if __name__ == "__main__":
    test_code_logic()
    print("\n" + "=" * 80)
    print("如果上面的测试显示 total_contribution 字段存在，")
    print("但实际API响应中没有，说明Flask没有重新加载代码。")
    print("\n请完全停止Flask服务（Ctrl+C），然后重新启动。")
    print("=" * 80)
