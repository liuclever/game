"""测试特定用户的 API 返回数据"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from application.services.alliance_service import AllianceService
from infrastructure.db.alliance_repo_mysql import MySQLAllianceRepo
from infrastructure.db.player_repo_mysql import MySQLPlayerRepo
from infrastructure.db.beast_repo_mysql import MySQLBeastRepo
from infrastructure.db.inventory_repo_mysql import MySQLInventoryRepo
from infrastructure.config.item_repo_from_config import ConfigItemRepo
from infrastructure.db.player_effect_repo_mysql import MySQLPlayerEffectRepo
from application.services.inventory_service import InventoryService
from application.services.beast_service import BeastService

def test_user_api(user_id):
    """测试特定用户的 API 返回"""
    print("=" * 80)
    print(f"测试用户 ID: {user_id} 的 API 返回数据")
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
        print(f"[ERROR] 获取联盟信息失败: {result.get('error')}")
        return
    
    member_info = result["member_info"]
    
    print(f"\n[Service 层返回的数据]")
    print(f"  现有贡献点 (contribution): {member_info.contribution}")
    print(f"  历史总贡献点 (total_contribution): {getattr(member_info, 'total_contribution', None)}")
    print(f"  total_contribution 类型: {type(getattr(member_info, 'total_contribution', None)).__name__}")
    
    # 模拟路由层的转换
    from interfaces.routes.alliance_routes import get_my_alliance
    from flask import Flask, jsonify
    from unittest.mock import patch
    
    # 直接检查路由层的逻辑
    print(f"\n[路由层转换后的数据（模拟）]")
    contribution = member_info.contribution or 0
    total_contribution = getattr(member_info, 'total_contribution', None) or (member_info.contribution or 0)
    
    print(f"  contribution: {contribution}")
    print(f"  total_contribution: {total_contribution}")
    print(f"  显示格式: {contribution}/{total_contribution}")
    
    # 检查问题
    if getattr(member_info, 'total_contribution', None) is None:
        print(f"\n[WARNING] total_contribution 为 None，路由层会使用 contribution 的值")
        print(f"  这会导致显示为: {contribution}/{contribution}")
    elif getattr(member_info, 'total_contribution', None) == member_info.contribution:
        print(f"\n[INFO] total_contribution 等于 contribution")
        print(f"  显示为: {contribution}/{contribution}")
    else:
        print(f"\n[OK] total_contribution 正确")
        print(f"  显示为: {contribution}/{getattr(member_info, 'total_contribution', None)}")

if __name__ == "__main__":
    # 测试用户"盟主2"（根据截图，贡献点是 627/632）
    test_user_api(20002)
    print("\n" + "=" * 80)
