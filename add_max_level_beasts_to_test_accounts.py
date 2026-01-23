#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
给测试账号添加满级幻兽
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.db.connection import execute_update, execute_query

def add_beasts_to_account(user_id, username):
    """给指定账号添加3只满级幻兽"""
    
    print(f"\n{'='*60}")
    print(f"为账号 {username} (ID: {user_id}) 添加满级幻兽")
    print('='*60)
    
    # 先检查是否已有幻兽
    existing_beasts = execute_query(
        "SELECT id, name, level FROM player_beast WHERE user_id = %s",
        (user_id,)
    )
    
    if existing_beasts:
        print(f"\n⚠️  该账号已有 {len(existing_beasts)} 只幻兽：")
        for beast in existing_beasts:
            beast_id = beast['id'] if isinstance(beast, dict) else beast[0]
            beast_name = beast['name'] if isinstance(beast, dict) else beast[1]
            beast_level = beast['level'] if isinstance(beast, dict) else beast[2]
            print(f"  - ID:{beast_id} {beast_name} (等级{beast_level})")
        
        # 删除现有幻兽
        print(f"\n🗑️  删除现有幻兽...")
        execute_update("DELETE FROM player_beast WHERE user_id = %s", (user_id,))
        print("  ✅ 已删除")
    
    # 创建3只满级（80级）天阶幻兽
    # 满级属性参考：80级天阶幻兽的属性应该很强
    beasts = [
        {
            "name": "烈焰神龙",
            "level": 80,
            "realm": "天阶",
            "nature": "物攻型",
            "hp": 8000,
            "physical_attack": 1200,
            "magic_attack": 600,
            "physical_defense": 800,
            "magic_defense": 700,
            "speed": 650
        },
        {
            "name": "冰霜凤凰",
            "level": 80,
            "realm": "天阶",
            "nature": "法攻型",
            "hp": 7500,
            "physical_attack": 500,
            "magic_attack": 1300,
            "physical_defense": 750,
            "magic_defense": 850,
            "speed": 680
        },
        {
            "name": "雷霆麒麟",
            "level": 80,
            "realm": "天阶",
            "nature": "速攻型",
            "hp": 7000,
            "physical_attack": 1000,
            "magic_attack": 800,
            "physical_defense": 700,
            "magic_defense": 700,
            "speed": 900
        }
    ]
    
    print(f"\n📦 创建3只80级天阶幻兽...")
    
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
                1, i + 1  # 设置为出战幻兽，位置1-3
            )
        )
        print(f"  ✅ {beast['name']} (等级{beast['level']}, {beast['nature']}, {beast['realm']})")
        print(f"     HP:{beast['hp']} 物攻:{beast['physical_attack']} 法攻:{beast['magic_attack']} 速度:{beast['speed']}")
    
    # 验证创建结果
    new_beasts = execute_query(
        "SELECT id, name, level, is_in_team FROM player_beast WHERE user_id = %s ORDER BY team_position",
        (user_id,)
    )
    
    print(f"\n✅ 成功创建 {len(new_beasts)} 只幻兽，已设置为出战状态")

def main():
    print("="*60)
    print("给测试账号添加满级幻兽")
    print("="*60)
    
    # 测试账号信息
    test_accounts = [
        {"user_id": 100006, "username": "test50_97355", "nickname": "测试50级A"},
        {"user_id": 100007, "username": "test50_46367", "nickname": "测试50级B"}
    ]
    
    for account in test_accounts:
        add_beasts_to_account(account["user_id"], account["nickname"])
    
    print("\n" + "="*60)
    print("所有账号处理完成")
    print("="*60)
    
    print("\n📋 测试账号信息：")
    print("-"*60)
    for account in test_accounts:
        print(f"账号：{account['nickname']}")
        print(f"  用户名：{account['username']}")
        print(f"  密码：123456")
        print(f"  user_id：{account['user_id']}")
        print(f"  幻兽：3只80级天阶幻兽（已出战）")
        print()
    
    print("💡 提示：")
    print("  - 每个账号有3只80级天阶幻兽")
    print("  - 幻兽已设置为出战状态")
    print("  - 属性强大，可以轻松应对各种战斗")
    print("  - 包含物攻型、法攻型、速攻型各一只")

if __name__ == '__main__':
    main()
