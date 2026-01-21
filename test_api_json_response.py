"""测试 API 返回的 JSON 数据格式"""
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

def simulate_api_json(user_id):
    """模拟 API 返回的 JSON 数据"""
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
            "total_contribution": (member_info.total_contribution if hasattr(member_info, 'total_contribution') and member_info.total_contribution is not None else (member_info.contribution or 0)),
        }
    }
    
    return api_response

def test_api_json():
    """测试 API JSON 响应"""
    print("=" * 80)
    print("测试 API 返回的 JSON 数据格式")
    print("=" * 80)
    
    # 找一个测试用户（根据截图，用户ID可能是20003，贡献是109/109）
    sql = """
        SELECT am.user_id, am.contribution, am.total_contribution,
               COALESCE(p.nickname, CONCAT('玩家', am.user_id)) as nickname
        FROM alliance_members am
        LEFT JOIN player p ON am.user_id = p.user_id
        WHERE am.contribution >= 100 AND am.contribution <= 120
        ORDER BY am.contribution DESC
        LIMIT 5
    """
    rows = execute_query(sql)
    
    if not rows:
        print("[ERROR] 未找到合适的测试用户")
        return
    
    for row in rows:
        user_id = row['user_id']
        nickname = row['nickname'] or f"玩家{user_id}"
        db_contribution = row['contribution'] or 0
        db_total = row.get('total_contribution')
        
        print(f"\n用户: {nickname} (ID: {user_id})")
        print(f"  数据库: 现有贡献点={db_contribution}, 历史总贡献点={db_total}")
        
        # 获取 API 返回的数据
        api_response = simulate_api_json(user_id)
        if api_response:
            api_contribution = api_response['member_info']['contribution']
            api_total = api_response['member_info']['total_contribution']
            
            print(f"  API返回: 现有贡献点={api_contribution}, 历史总贡献点={api_total}")
            
            # 检查是否一致
            if api_contribution != db_contribution:
                print(f"  [ERROR] 现有贡献点不一致！数据库: {db_contribution}, API: {api_contribution}")
            
            if api_total != db_total:
                print(f"  [ERROR] 历史总贡献点不一致！数据库: {db_total}, API: {api_total}")
            else:
                print(f"  [OK] 数据一致")
            
            # 打印 JSON 格式
            print(f"  JSON格式: {json.dumps(api_response['member_info'], ensure_ascii=False, indent=2)}")

if __name__ == "__main__":
    test_api_json()
    print("\n" + "=" * 80)
