"""检查用户20057的实际API响应数据"""
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

def get_api_response(user_id):
    """获取完整的API响应数据（模拟路由层）"""
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
    
    alliance = result["alliance"]
    member_info = result["member_info"]
    
    # 模拟路由层的完整转换（这是关键！）
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
    
    return api_response

def check_user(user_id):
    """检查特定用户的数据"""
    print("=" * 80)
    print(f"检查用户 ID: {user_id} 的API响应数据")
    print("=" * 80)
    
    # 从数据库获取原始数据
    sql = """
        SELECT am.user_id, am.contribution, am.total_contribution,
               COALESCE(p.nickname, CONCAT('玩家', am.user_id)) as nickname,
               a.name as alliance_name
        FROM alliance_members am
        LEFT JOIN player p ON am.user_id = p.user_id
        LEFT JOIN alliances a ON am.alliance_id = a.id
        WHERE am.user_id = %s
    """
    rows = execute_query(sql, (user_id,))
    
    if not rows:
        print(f"[ERROR] 用户 {user_id} 不存在或未加入联盟")
        return
    
    db_data = rows[0]
    db_contribution = db_data['contribution'] or 0
    db_total = db_data.get('total_contribution')
    
    print(f"\n用户: {db_data['nickname']} (ID: {user_id})")
    print(f"联盟: {db_data['alliance_name']}")
    print(f"\n[数据库原始数据]")
    print(f"  现有贡献点 (contribution): {db_contribution}")
    print(f"  历史总贡献点 (total_contribution): {db_total} (类型: {type(db_total).__name__})")
    
    # 获取API响应
    api_response = get_api_response(user_id)
    
    if not api_response:
        print(f"\n[ERROR] 无法获取API响应")
        return
    
    api_contribution = api_response['member_info']['contribution']
    api_total = api_response['member_info']['total_contribution']
    
    print(f"\n[API返回数据]")
    print(f"  现有贡献点 (contribution): {api_contribution}")
    print(f"  历史总贡献点 (total_contribution): {api_total} (类型: {type(api_total).__name__})")
    
    # 检查一致性
    print(f"\n[数据一致性检查]")
    if api_contribution != db_contribution:
        print(f"  [ERROR] 现有贡献点不一致！")
        print(f"    数据库: {db_contribution}, API: {api_contribution}")
    else:
        print(f"  [OK] 现有贡献点一致: {api_contribution}")
    
    if api_total != db_total:
        print(f"  [ERROR] 历史总贡献点不一致！")
        print(f"    数据库: {db_total}, API: {api_total}")
        print(f"    差异: {db_total - api_total if db_total and api_total else 'N/A'}")
    else:
        print(f"  [OK] 历史总贡献点一致: {api_total}")
    
    # 打印完整的JSON响应（格式化）
    print(f"\n[完整API响应JSON]")
    print(json.dumps(api_response, ensure_ascii=False, indent=2))
    
    # 特别检查member_info部分
    print(f"\n[member_info详细检查]")
    member_info = api_response['member_info']
    print(f"  role: {member_info['role']}")
    print(f"  contribution: {member_info['contribution']} (类型: {type(member_info['contribution']).__name__})")
    print(f"  total_contribution: {member_info['total_contribution']} (类型: {type(member_info['total_contribution']).__name__})")
    
    # 检查前端显示格式
    display_format = f"{member_info['contribution']}/{member_info['total_contribution']}"
    print(f"\n[前端显示格式]")
    print(f"  贡献: {display_format}")
    
    if member_info['contribution'] == member_info['total_contribution']:
        if db_total and db_total > db_contribution:
            print(f"  [WARNING] 前端会显示两个相同的数字，但数据库中历史总贡献点应该更大！")
            print(f"    这可能是路由层逻辑的问题")
        else:
            print(f"  [INFO] 两个数字相同（用户可能从未消耗过贡献点）")

if __name__ == "__main__":
    # 从请求头中解析的用户ID是20057
    check_user(20057)
    print("\n" + "=" * 80)
