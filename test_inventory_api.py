"""测试背包API"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from interfaces.web_api.bootstrap import services

# 测试账号
test_user_id = 100006

print(f"测试背包API - 用户ID: {test_user_id}")
print("="*80)

# 1. 获取背包信息
print("\n1. 获取背包信息...")
bag_info = services.inventory_service.get_bag_info(test_user_id)
print(f"背包等级: {bag_info['bag_level']}")
print(f"背包容量: {bag_info['capacity']}")
print(f"已用格子: {bag_info['used_slots']}")
print(f"临时格子: {bag_info['temp_slots']}")

# 2. 获取背包物品列表
print("\n2. 获取背包物品列表...")
items = services.inventory_service.get_inventory(test_user_id, include_temp=False)
print(f"物品数量: {len(items)}")

if items:
    print("\n物品详情:")
    for item in items:
        print(f"  - {item.item_info.name} (ID: {item.item_info.id}) × {item.inv_item.quantity}")
        print(f"    类型: {item.item_info.type}")
        print(f"    描述: {item.item_info.description}")
        can_use, action = services.inventory_service.can_use_or_open_item(item.item_info)
        if can_use:
            print(f"    可{action}")
else:
    print("背包为空")

# 3. 检查技能书口袋
print("\n3. 检查技能书口袋...")
pouch_count = services.inventory_service.get_item_count(test_user_id, 6007)
print(f"技能书口袋数量: {pouch_count}")

# 4. 获取临时背包
print("\n4. 获取临时背包...")
temp_items = services.inventory_service.get_temp_items(test_user_id)
print(f"临时物品数量: {len(temp_items)}")

print("\n" + "="*80)
print("测试完成")
