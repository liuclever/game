"""检查实际的API响应数据"""
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

def get_full_api_response(user_id):
    """获取完整的API响应（完全模拟路由层）"""
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
    
    # 完全模拟路由层的转换（这是关键！）
    # 使用和 routes/alliance_routes.py 完全相同的逻辑
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

def check_user_api(user_id):
    """检查用户的API响应"""
    print("=" * 80)
    print(f"检查用户 ID: {user_id} 的实际API响应")
    print("=" * 80)
    
    # 从数据库获取原始数据
    sql = """
        SELECT am.user_id, am.contribution, am.total_contribution,
               COALESCE(p.nickname, CONCAT('玩家', am.user_id)) as nickname
        FROM alliance_members am
        LEFT JOIN player p ON am.user_id = p.user_id
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
    print(f"\n[数据库原始数据]")
    print(f"  contribution: {db_contribution}")
    print(f"  total_contribution: {db_total}")
    
    # 获取API响应
    api_response = get_full_api_response(user_id)
    
    if not api_response:
        print(f"\n[ERROR] 无法获取API响应")
        return
    
    api_contribution = api_response['member_info']['contribution']
    api_total = api_response['member_info']['total_contribution']
    
    print(f"\n[API返回数据]")
    print(f"  contribution: {api_contribution}")
    print(f"  total_contribution: {api_total}")
    
    # 打印完整的JSON响应（格式化，模拟实际HTTP响应）
    print(f"\n[完整API响应JSON（模拟HTTP响应）]")
    json_str = json.dumps(api_response, ensure_ascii=False, indent=2)
    print(json_str)
    
    # 计算content-length（模拟HTTP响应头）
    content_length = len(json_str.encode('utf-8'))
    print(f"\n[HTTP响应信息]")
    print(f"  Content-Type: application/json")
    print(f"  Content-Length: {content_length}")
    
    # 检查member_info部分
    print(f"\n[member_info详细分析]")
    member_info = api_response['member_info']
    print(f"  role: {member_info['role']} (类型: {type(member_info['role']).__name__})")
    print(f"  contribution: {member_info['contribution']} (类型: {type(member_info['contribution']).__name__})")
    print(f"  total_contribution: {member_info['total_contribution']} (类型: {type(member_info['total_contribution']).__name__})")
    
    # 前端显示格式
    display_format = f"{member_info['contribution']}/{member_info['total_contribution']}"
    print(f"\n[前端应显示]")
    print(f"  贡献: {display_format}")
    
    # 验证
    print(f"\n[数据验证]")
    if api_contribution == db_contribution:
        print(f"  ✅ contribution 一致")
    else:
        print(f"  ❌ contribution 不一致: DB={db_contribution}, API={api_contribution}")
    
    if api_total == db_total:
        print(f"  ✅ total_contribution 一致")
    else:
        print(f"  ❌ total_contribution 不一致: DB={db_total}, API={api_total}")
        if db_total and api_total:
            print(f"     差异: {db_total - api_total}")
    
    # 特别检查：如果两个值相同，但数据库中不同
    if member_info['contribution'] == member_info['total_contribution']:
        if db_total and db_total > db_contribution:
            print(f"\n  ⚠️  警告：前端会显示两个相同的数字，但数据库中历史总贡献点更大！")
            print(f"     这可能是路由层逻辑的问题")
            print(f"     数据库: {db_contribution}/{db_total}")
            print(f"     API返回: {api_contribution}/{api_total}")
            print(f"     前端显示: {display_format}")

if __name__ == "__main__":
    # 用户ID 20057（从session cookie中解析）
    check_user_api(20057)
    print("\n" + "=" * 80)
    print("如果API返回的数据正确，但前端显示错误，请检查：")
    print("1. 前端代码是否已重新编译")
    print("2. 浏览器缓存是否已清除")
    print("3. 前端 getContributionDisplay() 函数是否正确")
    print("=" * 80)
