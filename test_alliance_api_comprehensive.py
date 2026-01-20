"""
全面测试联盟API，确保 total_contribution 字段正确返回
"""
import sys
import os
import json
import io

# 设置输出编码为UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from infrastructure.db.alliance_repo_mysql import MySQLAllianceRepo
from infrastructure.db.player_repo_mysql import MySQLPlayerRepo
from infrastructure.db.beast_repo_mysql import MySQLBeastRepo
from infrastructure.db.inventory_repo_mysql import MySQLInventoryRepo
from infrastructure.db.connection import execute_query
from infrastructure.config.item_repo_from_config import ConfigItemRepo
from infrastructure.db.player_effect_repo_mysql import MySQLPlayerEffectRepo
from application.services.alliance_service import AllianceService
from application.services.beast_service import BeastService
from application.services.inventory_service import InventoryService

def test_database_query(user_id: int):
    """测试数据库查询"""
    print("=" * 80)
    print("测试1: 数据库查询")
    print("=" * 80)
    
    sql = """
        SELECT m.*, p.nickname, p.level
        FROM alliance_members m
        LEFT JOIN player p ON m.user_id = p.user_id
        WHERE m.user_id = %s
    """
    rows = execute_query(sql, (user_id,))
    
    if not rows:
        print(f"[ERROR] 用户 {user_id} 不在联盟中")
        return None
    
    row = rows[0]
    print(f"[OK] 数据库查询成功")
    print(f"   contribution: {row.get('contribution')}")
    print(f"   total_contribution: {row.get('total_contribution')}")
    print(f"   role: {row.get('role')}")
    
    # 检查字段是否存在
    if 'total_contribution' not in row:
        print("[ERROR] 数据库字段 total_contribution 不存在！")
        return None
    
    if row.get('total_contribution') is None:
        print("[WARNING] 数据库 total_contribution 为 NULL")
    
    return row

def test_repo_layer(user_id: int):
    """测试仓库层"""
    print("\n" + "=" * 80)
    print("测试2: 仓库层 (AllianceRepo)")
    print("=" * 80)
    
    repo = MySQLAllianceRepo()
    member = repo.get_member(user_id)
    
    if not member:
        print(f"[ERROR] 用户 {user_id} 不在联盟中")
        return None
    
    print(f"[OK] 仓库层返回 AllianceMember 对象")
    print(f"   contribution: {member.contribution}")
    print(f"   total_contribution: {getattr(member, 'total_contribution', 'NOT_FOUND')}")
    print(f"   role: {member.role}")
    
    # 检查是否有 total_contribution 属性
    if not hasattr(member, 'total_contribution'):
        print("[ERROR] AllianceMember 对象没有 total_contribution 属性！")
        return None
    
    if member.total_contribution is None:
        print("[WARNING] AllianceMember.total_contribution 为 None")
    
    return member

def test_service_layer(user_id: int):
    """测试服务层"""
    print("\n" + "=" * 80)
    print("测试3: 服务层 (AllianceService)")
    print("=" * 80)
    
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
    
    result = alliance_service.get_my_alliance(user_id)
    
    if not result.get("ok"):
        print(f"[ERROR] 服务层返回错误: {result.get('error')}")
        return None
    
    print(f"[OK] 服务层返回成功")
    member_info = result["member_info"]
    
    # 检查 member_info 的类型
    print(f"   member_info 类型: {type(member_info)}")
    
    if isinstance(member_info, dict):
        print(f"   contribution: {member_info.get('contribution')}")
        print(f"   total_contribution: {member_info.get('total_contribution', 'NOT_FOUND')}")
        print(f"   role: {member_info.get('role')}")
        
        if 'total_contribution' not in member_info:
            print("[ERROR] 服务层返回的 member_info 字典中没有 total_contribution 字段！")
            return None
    else:
        print(f"   contribution: {member_info.contribution}")
        print(f"   total_contribution: {getattr(member_info, 'total_contribution', 'NOT_FOUND')}")
        print(f"   role: {member_info.role}")
        
        if not hasattr(member_info, 'total_contribution'):
            print("[ERROR] 服务层返回的 member_info 对象没有 total_contribution 属性！")
            return None
    
    return result

def test_route_layer_simulation(user_id: int):
    """模拟路由层处理"""
    print("\n" + "=" * 80)
    print("测试4: 路由层模拟 (模拟 alliance_routes.py 的逻辑)")
    print("=" * 80)
    
    # 获取服务层结果
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
    
    result = alliance_service.get_my_alliance(user_id)
    
    if not result.get("ok"):
        print(f"[ERROR] 服务层返回错误: {result.get('error')}")
        return None
    
    alliance = result["alliance"]
    member_info = result["member_info"]
    
    # 模拟路由层的处理逻辑
    print("   模拟路由层处理...")
    
    if isinstance(member_info, dict):
        contribution = member_info.get("contribution", 0) or 0
        total_contrib_value = member_info.get("total_contribution")
        if total_contrib_value is None or total_contrib_value < contribution:
            total_contrib_value = contribution
        role = member_info.get("role", 0)
    else:
        contribution = member_info.contribution or 0
        total_contrib_value = getattr(member_info, 'total_contribution', None)
        if total_contrib_value is None or total_contrib_value < contribution:
            total_contrib_value = contribution
        role = member_info.role
    
    member_info_dict = {
        "role": role,
        "contribution": contribution,
        "total_contribution": int(total_contrib_value) if total_contrib_value is not None else contribution,
    }
    
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
        "member_info": member_info_dict,
        "member_count": result["member_count"],
        "member_capacity": result.get("member_capacity"),
        "fire_ore_claimed_today": bool(result.get("fire_ore_claimed_today", False)),
    }
    
    print(f"[OK] 路由层模拟成功")
    print(f"   member_info.contribution: {member_info_dict['contribution']}")
    print(f"   member_info.total_contribution: {member_info_dict.get('total_contribution', 'NOT_FOUND')}")
    
    if 'total_contribution' not in member_info_dict:
        print("[ERROR] 路由层返回的 member_info 字典中没有 total_contribution 字段！")
        return None
    
    print("\n   最终 API 响应 JSON:")
    print(json.dumps(api_response, ensure_ascii=False, indent=2))
    
    return api_response

def main():
    """主测试函数"""
    print("=" * 80)
    print("联盟API全面测试 - 验证 total_contribution 字段")
    print("=" * 80)
    
    # 测试用户ID（从你提供的响应中看到是 20057）
    test_user_id = 20057
    
    print(f"\n测试用户ID: {test_user_id}\n")
    
    # 测试1: 数据库查询
    db_result = test_database_query(test_user_id)
    if not db_result:
        print("\n❌ 数据库查询失败，停止测试")
        return
    
    # 测试2: 仓库层
    repo_result = test_repo_layer(test_user_id)
    if not repo_result:
        print("\n❌ 仓库层测试失败，停止测试")
        return
    
    # 测试3: 服务层
    service_result = test_service_layer(test_user_id)
    if not service_result:
        print("\n❌ 服务层测试失败，停止测试")
        return
    
    # 测试4: 路由层模拟
    route_result = test_route_layer_simulation(test_user_id)
    if not route_result:
        print("\n❌ 路由层模拟失败")
        return
    
    # 最终总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    
    if route_result and 'total_contribution' in route_result.get('member_info', {}):
        print("[OK] 所有测试通过！total_contribution 字段正确返回")
        print(f"\n最终响应中的 member_info:")
        print(f"  - contribution: {route_result['member_info']['contribution']}")
        print(f"  - total_contribution: {route_result['member_info']['total_contribution']}")
        print(f"  - role: {route_result['member_info']['role']}")
    else:
        print("[ERROR] 测试失败！total_contribution 字段未正确返回")
        print("\n请检查:")
        print("1. 数据库字段是否存在")
        print("2. AllianceMember 实体类是否有 total_contribution 属性")
        print("3. 路由层代码是否正确处理")

if __name__ == "__main__":
    main()
