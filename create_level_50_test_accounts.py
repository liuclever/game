"""创建2个50级的测试账号"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.db.connection import execute_query, execute_update
import random

def create_test_account(nickname, level=50):
    """创建一个测试账号"""
    
    print(f"\n{'='*60}")
    print(f"创建测试账号：{nickname}")
    print(f"{'='*60}")
    
    # 1. 检查账号是否已存在
    existing = execute_query(
        "SELECT user_id FROM player WHERE nickname = %s",
        (nickname,)
    )
    
    if existing:
        user_id = existing[0]['user_id']
        print(f"✓ 账号已存在，user_id: {user_id}")
        
        # 更新等级
        execute_update(
            "UPDATE player SET level = %s WHERE user_id = %s",
            (level, user_id)
        )
        print(f"✓ 更新等级为 {level}")
        
        return user_id
    
    # 2. 创建玩家账号
    # 生成唯一的username
    username = f"test50_{random.randint(10000, 99999)}"
    
    execute_update(
        """INSERT INTO player (
            username, nickname, level, exp, gold, yuanbao, energy,
            location, vip_level, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())""",
        (username, nickname, level, 0, 500000, 10000, 100, '落龙镇', 0)
    )
    
    # 获取新创建的user_id
    result = execute_query(
        "SELECT user_id FROM player WHERE nickname = %s",
        (nickname,)
    )
    user_id = result[0]['user_id']
    
    print(f"✓ 创建玩家账号成功")
    print(f"  - user_id: {user_id}")
    print(f"  - 等级: {level}")
    print(f"  - 铜钱: 500,000")
    print(f"  - 元宝: 10,000")
    print(f"  - 活力: 100")
    
    # 3. 创建背包
    execute_update(
        """INSERT INTO player_bag (user_id, capacity, created_at)
           VALUES (%s, %s, NOW())
           ON DUPLICATE KEY UPDATE capacity = %s""",
        (user_id, 100, 100)
    )
    print(f"✓ 创建背包（容量: 100）")
    
    # 4. 创建幻兽（3只50级幻兽）
    beasts = [
        {
            "name": "火焰狮",
            "level": level,
            "realm": "天阶",
            "nature": "物攻型",
            "hp": 3500,
            "physical_attack": 450,
            "magic_attack": 200,
            "physical_defense": 350,
            "magic_defense": 300,
            "speed": 280
        },
        {
            "name": "冰霜龙",
            "level": level,
            "realm": "天阶",
            "nature": "法攻型",
            "hp": 3200,
            "physical_attack": 200,
            "magic_attack": 480,
            "physical_defense": 320,
            "magic_defense": 380,
            "speed": 260
        },
        {
            "name": "雷电虎",
            "level": level,
            "realm": "天阶",
            "nature": "速攻型",
            "hp": 3000,
            "physical_attack": 420,
            "magic_attack": 220,
            "physical_defense": 300,
            "magic_defense": 280,
            "speed": 350
        }
    ]
    
    for i, beast in enumerate(beasts):
        execute_update(
            """INSERT INTO player_beast (
                user_id, name, level, exp, realm, nature,
                hp, physical_attack, magic_attack,
                physical_defense, magic_defense, speed,
                is_in_team, team_position, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())""",
            (
                user_id, beast["name"], beast["level"], 0, beast["realm"], beast["nature"],
                beast["hp"], beast["physical_attack"], beast["magic_attack"],
                beast["physical_defense"], beast["magic_defense"], beast["speed"],
                1, i + 1  # 设置为出战幻兽
            )
        )
    
    print(f"✓ 创建3只{level}级幻兽（已设置为出战）")
    for beast in beasts:
        print(f"  - {beast['name']} ({beast['nature']}, {beast['realm']})")
    
    # 5. 添加一些基础道具
    items = [
        (4001, 50, "活力草"),
        (4002, 20, "捕捉球"),
        (4003, 10, "强力捕捉球"),
        (6001, 5, "镇妖符"),
        (6010, 10, "骰子包"),
        (6024, 5, "双倍卡"),
    ]
    
    for item_id, quantity, name in items:
        execute_update(
            """INSERT INTO player_inventory (user_id, item_id, quantity)
               VALUES (%s, %s, %s)
               ON DUPLICATE KEY UPDATE quantity = quantity + %s""",
            (user_id, item_id, quantity, quantity)
        )
    
    print(f"✓ 添加基础道具")
    for _, quantity, name in items:
        print(f"  - {name} × {quantity}")
    
    return user_id


def main():
    """主函数"""
    
    print("=" * 60)
    print("创建50级测试账号")
    print("=" * 60)
    
    # 创建2个测试账号
    test_accounts = [
        "测试50级A",
        "测试50级B"
    ]
    
    created_accounts = []
    
    for nickname in test_accounts:
        user_id = create_test_account(nickname, level=50)
        created_accounts.append({
            "user_id": user_id,
            "nickname": nickname
        })
    
    # 显示总结
    print(f"\n{'='*60}")
    print("创建完成")
    print(f"{'='*60}")
    print()
    print("测试账号列表：")
    for account in created_accounts:
        print(f"  - {account['nickname']} (ID: {account['user_id']})")
    
    print()
    print("账号配置：")
    print("  - 等级: 50")
    print("  - 铜钱: 500,000")
    print("  - 元宝: 10,000")
    print("  - 活力: 100")
    print("  - 幻兽: 3只50级天阶幻兽（已出战）")
    print("  - 背包: 容量100，包含基础道具")
    
    print()
    print("登录信息：")
    print("  - 用户名: 测试50级A 或 测试50级B")
    print("  - 密码: (根据你的系统设置)")
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
