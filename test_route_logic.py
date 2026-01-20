"""直接测试路由逻辑，不依赖Flask session"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unittest.mock import MagicMock, patch
from application.services.alliance_service import AllianceService
from infrastructure.db.alliance_repo_mysql import MySQLAllianceRepo
from infrastructure.db.player_repo_mysql import MySQLPlayerRepo
from infrastructure.db.beast_repo_mysql import MySQLBeastRepo
from infrastructure.db.inventory_repo_mysql import MySQLInventoryRepo
from infrastructure.config.item_repo_from_config import ConfigItemRepo
from infrastructure.db.player_effect_repo_mysql import MySQLPlayerEffectRepo
from application.services.inventory_service import InventoryService
from application.services.beast_service import BeastService

def test_route_logic():
    """测试路由逻辑（模拟get_my_alliance函数的核心逻辑）"""
    print("=" * 80)
    print("测试路由逻辑（模拟 get_my_alliance 函数）")
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
    
    # 模拟路由函数的核心逻辑
    print(f"\n[步骤1] 调用 alliance_service.get_my_alliance({user_id})")
    result = alliance_service.get_my_alliance(user_id)
    
    if not result.get("ok"):
        print(f"[ERROR] 获取联盟信息失败: {result.get('error')}")
        return
    
    print(f"[OK] 获取成功")
    
    alliance = result["alliance"]
    member_info = result["member_info"]
    
    print(f"\n[步骤2] 检查 member_info 对象")
    print(f"  类型: {type(member_info)}")
    print(f"  contribution: {member_info.contribution}")
    print(f"  hasattr total_contribution: {hasattr(member_info, 'total_contribution')}")
    
    if hasattr(member_info, 'total_contribution'):
        total_contrib = getattr(member_info, 'total_contribution')
        print(f"  total_contribution 值: {total_contrib} (类型: {type(total_contrib).__name__})")
    else:
        print(f"  [ERROR] member_info 没有 total_contribution 属性！")
        return
    
    print(f"\n[步骤3] 模拟路由层的转换逻辑")
    # 使用和路由层完全相同的逻辑
    total_contribution_value = getattr(member_info, 'total_contribution', None) if getattr(member_info, 'total_contribution', None) is not None else (member_info.contribution or 0)
    
    print(f"  计算结果: {total_contribution_value}")
    
    # 构建响应（完全模拟路由层）
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
        "member_info": {
            "role": member_info.role,
            "contribution": member_info.contribution or 0,
            "total_contribution": total_contribution_value,
        },
        "member_count": result["member_count"],
        "member_capacity": result.get("member_capacity"),
        "fire_ore_claimed_today": bool(result.get("fire_ore_claimed_today", False)),
    }
    
    print(f"\n[步骤4] 最终响应数据")
    print(json.dumps(response_data, ensure_ascii=False, indent=2))
    
    print(f"\n[步骤5] 验证 member_info")
    member_info_dict = response_data["member_info"]
    print(f"  role: {member_info_dict.get('role')}")
    print(f"  contribution: {member_info_dict.get('contribution')}")
    print(f"  total_contribution: {member_info_dict.get('total_contribution')}")
    
    if 'total_contribution' in member_info_dict:
        print(f"\n  ✅ total_contribution 字段存在！")
        print(f"  值: {member_info_dict['total_contribution']}")
        print(f"  前端应显示: {member_info_dict['contribution']}/{member_info_dict['total_contribution']}")
    else:
        print(f"\n  ❌ total_contribution 字段不存在！")
        print(f"  可用字段: {list(member_info_dict.keys())}")

if __name__ == "__main__":
    test_route_logic()
    print("\n" + "=" * 80)
    print("如果测试显示 total_contribution 字段存在且正确，")
    print("但实际API响应中没有，说明Flask没有重新加载代码。")
    print("请完全停止并重新启动Flask服务。")
    print("=" * 80)
