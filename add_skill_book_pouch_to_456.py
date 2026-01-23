"""给用户名为456的玩家添加技能书口袋"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.db.connection import execute_query, execute_update

def add_skill_book_pouch():
    """给用户名为456的玩家添加1个技能书口袋"""
    
    print("=" * 60)
    print("给用户名为456的玩家添加技能书口袋")
    print("=" * 60)
    print()
    
    # 1. 查找玩家
    print("【1. 查找玩家】")
    players = execute_query(
        "SELECT user_id, nickname, level FROM player WHERE nickname = %s",
        ('456',)
    )
    
    if not players:
        print("✗ 未找到用户名为'456'的玩家")
        return
    
    player = players[0]
    user_id = player['user_id']
    nickname = player['nickname']
    level = player['level']
    
    print(f"✓ 找到玩家：{nickname} (ID: {user_id}, 等级: {level})")
    print()
    
    # 2. 检查当前技能书口袋数量
    print("【2. 检查当前技能书口袋数量】")
    current = execute_query(
        "SELECT quantity FROM player_inventory WHERE user_id = %s AND item_id = %s",
        (user_id, 6007)
    )
    
    current_quantity = current[0]['quantity'] if current else 0
    print(f"当前技能书口袋数量：{current_quantity}")
    print()
    
    # 3. 添加技能书口袋
    print("【3. 添加技能书口袋】")
    execute_update(
        """INSERT INTO player_inventory (user_id, item_id, quantity) 
           VALUES (%s, %s, %s) 
           ON DUPLICATE KEY UPDATE quantity = quantity + %s""",
        (user_id, 6007, 1, 1)
    )
    
    # 4. 验证结果
    print("【4. 验证结果】")
    result = execute_query(
        "SELECT quantity FROM player_inventory WHERE user_id = %s AND item_id = %s",
        (user_id, 6007)
    )
    
    new_quantity = result[0]['quantity'] if result else 0
    print(f"添加后技能书口袋数量：{new_quantity}")
    print()
    
    if new_quantity == current_quantity + 1:
        print("✓ 添加成功！")
    else:
        print("✗ 添加失败！")
    
    print()
    print("=" * 60)
    print("操作完成")
    print("=" * 60)


if __name__ == "__main__":
    add_skill_book_pouch()
