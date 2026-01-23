#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证测试账号的幻兽配置
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.db.connection import execute_query

def verify_account(user_id, nickname):
    """验证账号的幻兽配置"""
    print(f"\n{'='*60}")
    print(f"验证账号：{nickname} (ID: {user_id})")
    print('='*60)
    
    # 查询幻兽信息
    beasts = execute_query("""
        SELECT id, name, level, realm, nature, 
               hp, physical_attack, magic_attack, 
               physical_defense, magic_defense, speed,
               is_in_team, team_position
        FROM player_beast 
        WHERE user_id = %s 
        ORDER BY team_position
    """, (user_id,))
    
    if not beasts:
        print("❌ 该账号没有幻兽！")
        return False
    
    print(f"\n✅ 找到 {len(beasts)} 只幻兽：\n")
    
    all_valid = True
    for beast in beasts:
        # 处理字典或元组格式
        if isinstance(beast, dict):
            beast_id = beast['id']
            name = beast['name']
            level = beast['level']
            realm = beast['realm']
            nature = beast['nature']
            hp = beast['hp']
            p_atk = beast['physical_attack']
            m_atk = beast['magic_attack']
            p_def = beast['physical_defense']
            m_def = beast['magic_defense']
            speed = beast['speed']
            in_team = beast['is_in_team']
            position = beast['team_position']
        else:
            beast_id, name, level, realm, nature, hp, p_atk, m_atk, p_def, m_def, speed, in_team, position = beast
        
        print(f"【{name}】")
        print(f"  ID: {beast_id}")
        print(f"  等级: {level} | 阶位: {realm} | 性格: {nature}")
        print(f"  HP: {hp}")
        print(f"  物攻: {p_atk} | 法攻: {m_atk}")
        print(f"  物防: {p_def} | 法防: {m_def}")
        print(f"  速度: {speed}")
        print(f"  出战状态: {'✅ 已出战' if in_team else '❌ 未出战'} | 位置: {position if position else 'N/A'}")
        
        # 验证是否满足要求
        if level != 80:
            print(f"  ⚠️  等级不是80级")
            all_valid = False
        if realm != "天阶":
            print(f"  ⚠️  不是天阶幻兽")
            all_valid = False
        if not in_team:
            print(f"  ⚠️  未设置为出战")
            all_valid = False
        
        print()
    
    if all_valid:
        print("✅ 所有幻兽配置正确！")
    else:
        print("⚠️  部分幻兽配置有问题")
    
    return all_valid

def main():
    print("="*60)
    print("验证测试账号幻兽配置")
    print("="*60)
    
    test_accounts = [
        {"user_id": 100006, "nickname": "测试50级A"},
        {"user_id": 100007, "nickname": "测试50级B"}
    ]
    
    results = []
    for account in test_accounts:
        result = verify_account(account["user_id"], account["nickname"])
        results.append((account["nickname"], result))
    
    print("\n" + "="*60)
    print("验证结果汇总")
    print("="*60)
    
    for nickname, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{nickname}: {status}")
    
    if all(r[1] for r in results):
        print("\n🎉 所有账号验证通过！可以开始测试了！")
    else:
        print("\n⚠️  部分账号验证失败，请检查")

if __name__ == '__main__':
    main()
