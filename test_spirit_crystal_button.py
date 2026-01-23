#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试灵力水晶使用按钮是否正常显示
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.db.connection import execute_update, execute_query

def main():
    print("=" * 60)
    print("测试灵力水晶使用按钮")
    print("=" * 60)
    
    # 测试账号
    test_users = [
        {"user_id": 100006, "name": "测试50级A"},
        {"user_id": 100007, "name": "测试50级B"}
    ]
    
    for user in test_users:
        user_id = user["user_id"]
        name = user["name"]
        
        print(f"\n[{name}] (ID: {user_id})")
        print("-" * 60)
        
        # 检查是否有灵力水晶
        result = execute_query("""
            SELECT item_id, quantity 
            FROM player_inventory 
            WHERE user_id = %s AND item_id = 6101
        """, (user_id,))
        
        if not result:
            print("  ⚠️  背包中没有灵力水晶")
            # 添加一个用于测试
            print("  📦 添加1个灵力水晶用于测试...")
            execute_update("""
                INSERT INTO player_inventory (user_id, item_id, quantity, is_temporary)
                VALUES (%s, 6101, 1, 0)
            """, (user_id,))
            print("  ✅ 已添加")
        else:
            quantity = result[0]['quantity'] if isinstance(result[0], dict) else result[0][1]
            print(f"  ✅ 背包中有灵力水晶 x{quantity}")
    
    print("\n" + "=" * 60)
    print("代码修改验证")
    print("=" * 60)
    
    # 验证代码修改
    print("\n检查 inventory_service.py 中的修改...")
    with open('application/services/inventory_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if '6101' in content and '灵力水晶' in content:
            print("  ✅ 代码中已添加灵力水晶（6101）支持")
            # 找到相关行
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if '6101' in line:
                    print(f"\n  第 {i+1} 行: {line.strip()}")
                    if i+1 < len(lines):
                        print(f"  第 {i+2} 行: {lines[i+1].strip()}")
        else:
            print("  ❌ 代码中未找到灵力水晶支持")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    print("\n💡 下一步：")
    print("  1. 重启后端服务（运行 restart_flask.bat）")
    print("  2. 刷新浏览器（Ctrl+F5 强制刷新）")
    print("  3. 登录测试账号，打开背包查看灵力水晶")
    print("  4. 确认灵力水晶有【使用】按钮")

if __name__ == '__main__':
    main()
