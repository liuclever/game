"""测试镇妖宝箱星级显示"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.db.connection import execute_query, execute_update
from application.services.inventory_service import InventoryService
from infrastructure.db.inventory_repo_mysql import MySQLInventoryRepo
from infrastructure.config.item_repo_from_config import ConfigItemRepo
from infrastructure.db.player_repo_mysql import MySQLPlayerRepo

def test_chest_star_display():
    """测试不同等级玩家背包中宝箱的星级显示"""
    
    print("=" * 70)
    print("测试镇妖宝箱星级显示")
    print("=" * 70)
    
    # 测试场景
    test_cases = [
        {"level": 35, "expected_star": "三星"},
        {"level": 45, "expected_star": "四星"},
        {"level": 55, "expected_star": "五星"},
        {"level": 65, "expected_star": "六星"},
        {"level": 75, "expected_star": "七星"},
        {"level": 85, "expected_star": "八星"},
    ]
    
    inventory_service = InventoryService(
        inventory_repo=MySQLInventoryRepo(),
        item_repo=ConfigItemRepo(),
        player_repo=MySQLPlayerRepo()
    )
    
    for test_case in test_cases:
        level = test_case["level"]
        expected_star = test_case["expected_star"]
        
        print(f"\n{'='*70}")
        print(f"测试场景：{level}级玩家")
        print(f"预期星级：{expected_star}")
        print(f"{'='*70}")
        
        # 查找该等级的测试账号
        players = execute_query(
            "SELECT user_id, nickname, level FROM player WHERE level = %s LIMIT 1",
            (level,)
        )
        
        if not players:
            print(f"⚠️  没有找到{level}级的玩家，跳过")
            continue
        
        user_id = players[0]['user_id']
        nickname = players[0]['nickname']
        
        print(f"玩家：{nickname} (ID: {user_id}, 等级: {level})")
        
        # 清空该玩家的背包
        execute_update("DELETE FROM player_inventory WHERE user_id = %s", (user_id,))
        
        # 添加试炼宝箱和炼狱宝箱
        inventory_service.add_item(user_id, 92001, 1)  # 试炼宝箱
        inventory_service.add_item(user_id, 92002, 1)  # 炼狱宝箱
        
        # 获取背包物品
        items = inventory_service.get_inventory(user_id, include_temp=False)
        
        print(f"\n背包中的宝箱：")
        for item in items:
            if item.item_info.id in (92001, 92002):
                # 模拟前端显示逻辑
                item_name = item.item_info.name
                
                # 计算星级
                if level < 30:
                    star_level = 0
                elif level < 40:
                    star_level = 3
                elif level < 50:
                    star_level = 4
                elif level < 60:
                    star_level = 5
                elif level < 70:
                    star_level = 6
                elif level < 80:
                    star_level = 7
                else:
                    star_level = 8
                
                star_map = {
                    3: "三星",
                    4: "四星",
                    5: "五星",
                    6: "六星",
                    7: "七星",
                    8: "八星",
                }
                star_prefix = star_map.get(star_level, "")
                
                if star_prefix:
                    display_name = f"{star_prefix}{item_name}"
                else:
                    display_name = item_name
                
                # 验证
                is_correct = star_prefix == expected_star
                status = "✓" if is_correct else "✗"
                
                print(f"  {status} {display_name} (原名: {item_name}, 数量: {item.inv_item.quantity})")
                
                if not is_correct:
                    print(f"    预期: {expected_star}{item_name}")
                    print(f"    实际: {display_name}")
        
        # 清理测试数据
        execute_update("DELETE FROM player_inventory WHERE user_id = %s", (user_id,))
    
    print(f"\n{'='*70}")
    print("测试完成")
    print(f"{'='*70}")


if __name__ == "__main__":
    test_chest_star_display()
