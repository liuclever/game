"""检查测试账号的背包物品"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.db.connection import execute_query

# 测试账号
test_accounts = [100006, 100007]

print("检查测试账号背包...")
print("="*80)

for user_id in test_accounts:
    # 获取玩家信息
    player = execute_query(
        "SELECT nickname FROM player WHERE user_id = %s",
        (user_id,)
    )
    
    if not player:
        print(f"未找到 user_id: {user_id}")
        continue
    
    nickname = player[0]['nickname']
    print(f"\n{nickname} (ID: {user_id})")
    print("-"*80)
    
    # 获取背包物品
    items = execute_query(
        """SELECT item_id, quantity, is_temporary
           FROM player_inventory
           WHERE user_id = %s
           ORDER BY item_id""",
        (user_id,)
    )
    
    if items:
        print(f"背包物品数量: {len(items)}")
        for item in items:
            temp_flag = " [临时]" if item.get('is_temporary') else ""
            print(f"  - 物品ID: {item['item_id']} × {item['quantity']}{temp_flag}")
    else:
        print("背包为空")

print("\n" + "="*80)
print("\n检查技能书口袋 (ID: 6007)...")

for user_id in test_accounts:
    result = execute_query(
        "SELECT quantity FROM player_inventory WHERE user_id = %s AND item_id = 6007",
        (user_id,)
    )
    
    player = execute_query("SELECT nickname FROM player WHERE user_id = %s", (user_id,))
    nickname = player[0]['nickname'] if player else f"用户{user_id}"
    
    if result:
        print(f"✓ {nickname}: 有技能书口袋 × {result[0]['quantity']}")
    else:
        print(f"✗ {nickname}: 没有技能书口袋")
