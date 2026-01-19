"""调试API返回的数据，模拟前端请求"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from infrastructure.db.alliance_repo_mysql import MySQLAllianceRepo
from application.services.alliance_service import AllianceService
from infrastructure.db.player_repo_mysql import MySQLPlayerRepo
from application.services.inventory_service import InventoryService
from infrastructure.db.inventory_repo_mysql import MySQLInventoryRepo
from domain.repositories.item_repo import IItemRepo

# 简化版本，直接模拟API返回
def simulate_api_response(user_id):
    """模拟API返回的数据"""
    print(f"\n模拟API返回数据（用户ID: {user_id}）")
    print("-" * 60)
    
    # 1. 数据库直接查询
    from infrastructure.db.connection import execute_query
    sql = """
        SELECT am.user_id, am.contribution, am.total_contribution
        FROM alliance_members am
        WHERE am.user_id = %s
    """
    db_rows = execute_query(sql, (user_id,))
    if not db_rows:
        print("[ERROR] 用户不存在")
        return None
    
    db_data = db_rows[0]
    db_contribution = db_data['contribution'] or 0
    db_total = db_data.get('total_contribution') or 0
    
    print(f"数据库数据:")
    print(f"  contribution: {db_contribution}")
    print(f"  total_contribution: {db_total}")
    
    # 2. 通过 get_member 获取
    repo = MySQLAllianceRepo()
    member = repo.get_member(user_id)
    if not member:
        print("[ERROR] get_member 返回 None")
        return None
    
    member_contribution = member.contribution or 0
    member_total = getattr(member, 'total_contribution', 0) or 0
    
    print(f"\nget_member 返回:")
    print(f"  contribution: {member_contribution}")
    print(f"  total_contribution: {member_total}")
    
    # 3. 模拟后端路由返回
    route_response = {
        "contribution": member_contribution,
        "total_contribution": member_total or 0,
    }
    
    print(f"\n后端路由返回:")
    print(f"  contribution: {route_response['contribution']}")
    print(f"  total_contribution: {route_response['total_contribution']}")
    
    # 4. 模拟前端显示
    frontend_display = {
        "contribution": route_response['contribution'],
        "total_contribution": route_response['total_contribution'] or route_response['contribution']
    }
    
    print(f"\n前端显示（使用回退逻辑）:")
    print(f"  贡献: {frontend_display['contribution']}/{frontend_display['total_contribution']}")
    
    # 检查问题
    print(f"\n[问题检查]")
    if db_total != member_total:
        print(f"  [ERROR] 数据库和 get_member 不一致!")
        print(f"    数据库: {db_total}, get_member: {member_total}")
    else:
        print(f"  [OK] 数据库和 get_member 一致")
    
    if member_total != route_response['total_contribution']:
        print(f"  [ERROR] get_member 和路由返回不一致!")
        print(f"    get_member: {member_total}, 路由: {route_response['total_contribution']}")
    else:
        print(f"  [OK] get_member 和路由返回一致")
    
    if frontend_display['total_contribution'] == frontend_display['contribution'] and db_total > db_contribution:
        print(f"  [WARN] 前端使用了回退逻辑!")
        print(f"    数据库历史总贡献点: {db_total}")
        print(f"    前端显示: {frontend_display['total_contribution']}")
        print(f"    这说明 total_contribution 为 0 或不存在")
    
    return {
        "db": {"contribution": db_contribution, "total": db_total},
        "member": {"contribution": member_contribution, "total": member_total},
        "route": route_response,
        "frontend": frontend_display
    }

if __name__ == "__main__":
    print("=" * 80)
    print("调试API返回数据")
    print("=" * 80)
    
    # 找一个测试用户
    from infrastructure.db.connection import execute_query
    sql = """
        SELECT am.user_id, am.contribution, am.total_contribution
        FROM alliance_members am
        WHERE am.contribution >= 5
        LIMIT 1
    """
    rows = execute_query(sql)
    if rows:
        user_id = rows[0]['user_id']
        
        print(f"\n[测试前]")
        simulate_api_response(user_id)
        
        # 减少贡献点
        print(f"\n" + "=" * 80)
        print("减少 5 点贡献后")
        print("=" * 80)
        
        repo = MySQLAllianceRepo()
        repo.update_member_contribution(user_id, -5)
        
        print(f"\n[测试后]")
        simulate_api_response(user_id)
