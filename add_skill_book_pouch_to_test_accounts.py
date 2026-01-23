"""给测试账号添加技能书口袋"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.db.connection import execute_update, execute_query

# 技能书口袋的物品ID
SKILL_BOOK_POUCH_ITEM_ID = 6007

# 测试账号
test_accounts = [
    ("测试50级A", 100006),
    ("测试50级B", 100007)
]

print("给测试账号添加技能书口袋...")
print("="*60)

for nickname, user_id in test_accounts:
    # 检查是否已有技能书口袋
    existing = execute_query(
        "SELECT quantity FROM player_inventory WHERE user_id = %s AND item_id = %s",
        (user_id, SKILL_BOOK_POUCH_ITEM_ID)
    )
    
    if existing:
        # 已有，增加数量
        execute_update(
            "UPDATE player_inventory SET quantity = quantity + 1 WHERE user_id = %s AND item_id = %s",
            (user_id, SKILL_BOOK_POUCH_ITEM_ID)
        )
        new_quantity = existing[0]['quantity'] + 1
        print(f"✓ {nickname} (ID: {user_id})")
        print(f"  已有技能书口袋，数量增加: {existing[0]['quantity']} → {new_quantity}")
    else:
        # 没有，新增
        execute_update(
            "INSERT INTO player_inventory (user_id, item_id, quantity) VALUES (%s, %s, 1)",
            (user_id, SKILL_BOOK_POUCH_ITEM_ID)
        )
        print(f"✓ {nickname} (ID: {user_id})")
        print(f"  添加技能书口袋 × 1")
    
    print()

print("="*60)
print("添加完成！")
print()
print("技能书口袋说明：")
print("  - 物品ID: 6007")
print("  - 打开后可随机获得53种技能书中的一本")
print("  - 可在背包中直接打开使用")
