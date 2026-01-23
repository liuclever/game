"""测试镇妖宝箱结晶显示"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.db.connection import execute_query, execute_update
from application.services.inventory_service import InventoryService
from infrastructure.db.inventory_repo_mysql import MySQLInventoryRepo
from infrastructure.config.item_repo_from_config import ConfigItemRepo
from infrastructure.db.player_repo_mysql import MySQLPlayerRepo

def test_chest_crystal_display():
    """测试打开宝箱时结晶的显示"""
    
    print("=" * 80)
    print("测试镇妖宝箱结晶显示")
    print("=" * 80)
    print()
    
    inventory_service = InventoryService(
        inventory_repo=MySQLInventoryRepo(),
        item_repo=ConfigItemRepo(),
        player_repo=MySQLPlayerRepo()
    )
    
    # 结晶ID和名称映射
    crystal_names = {
        1001: "金之结晶",
        1002: "木之结晶",
        1003: "水之结晶",
        1004: "火之结晶",
        1005: "土之结晶",
        1006: "风之结晶",
        1007: "电之结晶"
    }
    
    # 测试场景
    test_cases = [
        {"level": 35, "chest_id": 92001, "chest_name": "三星试炼宝箱", "expected_crystals": 3},
        {"level": 45, "chest_id": 92001, "chest_name": "四星试炼宝箱", "expected_crystals": 4},
        {"level": 55, "chest_id": 92002, "chest_name": "五星炼狱宝箱", "expected_crystals": 5},
        {"level": 75, "chest_id": 92002, "chest_name": "七星炼狱宝箱", "expected_crystals": 7},
    ]
    
    for test_case in test_cases:
        level = test_case["level"]
        chest_id = test_case["chest_id"]
        chest_name = test_case["chest_name"]
        expected_crystals = test_case["expected_crystals"]
        
        print(f"{'='*80}")
        print(f"测试场景：{level}级玩家打开{chest_name}")
        print(f"预期获得：{expected_crystals}种不同的结晶")
        print(f"{'='*80}")
        
        # 查找该等级的测试账号
        players = execute_query(
            "SELECT user_id, nickname, level FROM player WHERE level = %s LIMIT 1",
            (level,)
        )
        
        if not players:
            print(f"⚠️  没有找到{level}级的玩家，跳过")
            print()
            continue
        
        user_id = players[0]['user_id']
        nickname = players[0]['nickname']
        
        print(f"玩家：{nickname} (ID: {user_id}, 等级: {level})")
        print()
        
        # 清空该玩家的背包
        execute_update("DELETE FROM player_inventory WHERE user_id = %s", (user_id,))
        
        # 添加宝箱
        inventory_service.add_item(user_id, chest_id, 1)
        
        # 获取背包中的宝箱
        items = inventory_service.get_inventory(user_id, include_temp=False)
        chest_inv_item = None
        for item in items:
            if item.item_info.id == chest_id:
                chest_inv_item = item.inv_item
                break
        
        if not chest_inv_item:
            print(f"✗ 未找到宝箱")
            print()
            continue
        
        # 打开宝箱
        try:
            result = inventory_service.use_item(user_id, chest_inv_item.id, 1)
            
            print(f"打开结果：")
            print(f"  消息：{result.get('message', '')}")
            print()
            
            # 检查获得的奖励
            rewards = result.get('rewards', {})
            
            # 统计结晶
            crystals_obtained = []
            for item_name, qty in rewards.items():
                if item_name in crystal_names.values():
                    crystals_obtained.append(f"{item_name}×{qty}")
            
            print(f"获得的结晶：")
            if crystals_obtained:
                for crystal in crystals_obtained:
                    print(f"  - {crystal}")
                
                # 验证
                if len(crystals_obtained) == expected_crystals:
                    print(f"\n✓ 正确：获得了{len(crystals_obtained)}种不同的结晶")
                else:
                    print(f"\n✗ 错误：预期{expected_crystals}种，实际{len(crystals_obtained)}种")
            else:
                print(f"  ✗ 未获得结晶")
            
            # 检查消息中是否包含"七类结晶"
            message = result.get('message', '')
            if "七类结晶" in message:
                print(f"\n✗ 错误：消息中仍然包含'七类结晶'字样")
                print(f"   消息：{message}")
            else:
                print(f"\n✓ 正确：消息中不包含'七类结晶'字样，直接显示具体结晶")
            
        except Exception as e:
            print(f"✗ 打开宝箱失败：{e}")
        
        # 清理测试数据
        execute_update("DELETE FROM player_inventory WHERE user_id = %s", (user_id,))
        
        print()
    
    print(f"{'='*80}")
    print("测试完成")
    print(f"{'='*80}")
    print()
    
    # 显示预期效果
    print(f"{'='*80}")
    print("预期显示效果")
    print(f"{'='*80}")
    print()
    print("修改前：")
    print("  成功开启三星试炼宝箱×1，获得：活力草×1、七类结晶×3、铜钱×100000")
    print()
    print("修改后：")
    print("  成功开启三星试炼宝箱×1，获得：活力草×1、金之结晶×1、木之结晶×1、水之结晶×1、铜钱×100000")
    print()
    print(f"{'='*80}")


if __name__ == "__main__":
    test_chest_crystal_display()
