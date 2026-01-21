"""调试member_info对象，检查是否有total_contribution属性"""
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

def debug_member_info(user_id):
    """调试member_info对象"""
    print("=" * 80)
    print(f"调试用户 ID: {user_id} 的 member_info 对象")
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
    
    member_info = result["member_info"]
    
    print(f"\n[member_info 对象信息]")
    print(f"  类型: {type(member_info)}")
    print(f"  所有属性: {dir(member_info)}")
    
    # 检查是否有 total_contribution 属性
    print(f"\n[检查 total_contribution 属性]")
    has_attr = hasattr(member_info, 'total_contribution')
    print(f"  hasattr(member_info, 'total_contribution'): {has_attr}")
    
    if has_attr:
        total_value = getattr(member_info, 'total_contribution', None)
        print(f"  getattr(member_info, 'total_contribution'): {total_value} (类型: {type(total_value).__name__})")
        
        # 检查是否为 None
        if total_value is None:
            print(f"  [WARNING] total_contribution 是 None")
        else:
            print(f"  [OK] total_contribution 有值: {total_value}")
    else:
        print(f"  [ERROR] member_info 对象没有 total_contribution 属性！")
        print(f"  这可能是 AllianceMember 实体类的问题")
    
    # 尝试直接访问
    try:
        direct_access = member_info.total_contribution
        print(f"\n  直接访问 member_info.total_contribution: {direct_access}")
    except AttributeError as e:
        print(f"\n  [ERROR] 直接访问失败: {e}")
    
    # 打印所有属性值
    print(f"\n[所有属性值]")
    for attr in dir(member_info):
        if not attr.startswith('_'):
            try:
                value = getattr(member_info, attr)
                if not callable(value):
                    print(f"  {attr}: {value} (类型: {type(value).__name__})")
            except:
                pass
    
    # 模拟路由层的转换
    print(f"\n[模拟路由层转换]")
    try:
        # 使用和路由层完全相同的逻辑
        total_contribution_value = (member_info.total_contribution if hasattr(member_info, 'total_contribution') and member_info.total_contribution is not None else (member_info.contribution or 0))
        print(f"  计算结果: {total_contribution_value}")
        
        member_info_dict = {
            "role": member_info.role,
            "contribution": member_info.contribution or 0,
            "total_contribution": total_contribution_value,
        }
        print(f"\n[转换后的字典]")
        print(f"  {member_info_dict}")
    except Exception as e:
        print(f"  [ERROR] 转换失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_member_info(20057)
    print("\n" + "=" * 80)
