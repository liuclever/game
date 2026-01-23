"""给测试账号添加镇妖宝箱"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.db.connection import execute_update, execute_query

# 宝箱物品ID
ZHENYAO_TRIAL_CHEST_ITEM_ID = 92001  # 试炼宝箱
ZHENYAO_HELL_CHEST_ITEM_ID = 92002   # 炼狱宝箱

# 测试账号
test_accounts = [
    ("测试50级A", 100006),
    ("测试50级B", 100007)
]

print("="*80)
print("给测试账号添加镇妖宝箱")
print("="*80)

for nickname, user_id in test_accounts:
    print(f"\n{nickname} (ID: {user_id})")
    print("-"*80)
    
    # 添加试炼宝箱
    print("  添加试炼宝箱...")
    existing_trial = execute_query(
        "SELECT quantity FROM player_inventory WHERE user_id = %s AND item_id = %s",
        (user_id, ZHENYAO_TRIAL_CHEST_ITEM_ID)
    )
    
    if existing_trial:
        execute_update(
            "UPDATE player_inventory SET quantity = quantity + 1 WHERE user_id = %s AND item_id = %s",
            (user_id, ZHENYAO_TRIAL_CHEST_ITEM_ID)
        )
        new_quantity = existing_trial[0]['quantity'] + 1
        print(f"    ✓ 试炼宝箱数量: {existing_trial[0]['quantity']} → {new_quantity}")
    else:
        execute_update(
            "INSERT INTO player_inventory (user_id, item_id, quantity) VALUES (%s, %s, 1)",
            (user_id, ZHENYAO_TRIAL_CHEST_ITEM_ID)
        )
        print(f"    ✓ 添加试炼宝箱 × 1")
    
    # 添加炼狱宝箱
    print("  添加炼狱宝箱...")
    existing_hell = execute_query(
        "SELECT quantity FROM player_inventory WHERE user_id = %s AND item_id = %s",
        (user_id, ZHENYAO_HELL_CHEST_ITEM_ID)
    )
    
    if existing_hell:
        execute_update(
            "UPDATE player_inventory SET quantity = quantity + 1 WHERE user_id = %s AND item_id = %s",
            (user_id, ZHENYAO_HELL_CHEST_ITEM_ID)
        )
        new_quantity = existing_hell[0]['quantity'] + 1
        print(f"    ✓ 炼狱宝箱数量: {existing_hell[0]['quantity']} → {new_quantity}")
    else:
        execute_update(
            "INSERT INTO player_inventory (user_id, item_id, quantity) VALUES (%s, %s, 1)",
            (user_id, ZHENYAO_HELL_CHEST_ITEM_ID)
        )
        print(f"    ✓ 添加炼狱宝箱 × 1")

print("\n" + "="*80)
print("添加完成！")
print("\n宝箱说明：")
print("  - 试炼宝箱 (ID: 92001): 打开后获得铜钱、活力草、结晶")
print("  - 炼狱宝箱 (ID: 92002): 打开后获得铜钱、活力草、结晶、强力捕捉球、追魂法宝、灵力水晶")
print("\n使用方法：")
print("  1. 登录游戏")
print("  2. 打开背包")
print("  3. 找到宝箱，点击'打开'")
print("  4. 根据等级获得相应奖励")
print("\n注意：")
print("  - 宝箱会根据玩家等级显示星级（50级显示为'五星'）")
print("  - 奖励内容根据玩家等级决定（50级获得140,000铜钱等）")
