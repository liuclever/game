"""诊断背包显示问题"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.db.connection import execute_query

print("="*80)
print("诊断背包显示问题")
print("="*80)

# 测试账号
test_user_ids = [100006, 100007]

for user_id in test_user_ids:
    print(f"\n检查用户 ID: {user_id}")
    print("-"*80)
    
    # 1. 检查玩家是否存在
    player = execute_query(
        "SELECT user_id, username, nickname, level FROM player WHERE user_id = %s",
        (user_id,)
    )
    
    if not player:
        print(f"✗ 玩家不存在")
        continue
    
    print(f"✓ 玩家存在: {player[0]['nickname']} (用户名: {player[0]['username']})")
    
    # 2. 检查背包表是否存在
    bag = execute_query(
        "SELECT * FROM player_bag WHERE user_id = %s",
        (user_id,)
    )
    
    if bag:
        print(f"✓ 背包记录存在: 容量 {bag[0]['capacity']}")
    else:
        print(f"✗ 背包记录不存在")
    
    # 3. 检查背包物品
    items = execute_query(
        "SELECT * FROM player_inventory WHERE user_id = %s",
        (user_id,)
    )
    
    print(f"✓ 背包物品数量: {len(items)}")
    
    if items:
        print("\n  物品列表:")
        for item in items:
            temp = " [临时]" if item.get('is_temporary') else ""
            print(f"    - item_id: {item['item_id']}, quantity: {item['quantity']}{temp}")
    
    # 4. 检查物品是否有 quantity = 0 的情况
    zero_items = execute_query(
        "SELECT * FROM player_inventory WHERE user_id = %s AND quantity <= 0",
        (user_id,)
    )
    
    if zero_items:
        print(f"\n  ⚠ 发现 {len(zero_items)} 个数量为0的物品（这些会被过滤）")
        for item in zero_items:
            print(f"    - item_id: {item['item_id']}, quantity: {item['quantity']}")

print("\n" + "="*80)
print("\n检查物品配置文件...")

# 检查物品配置
try:
    from infrastructure.config.item_repo_from_config import ConfigItemRepo
    item_repo = ConfigItemRepo()
    
    # 检查技能书口袋配置
    skill_book_pouch = item_repo.get_by_id(6007)
    if skill_book_pouch:
        print(f"✓ 技能书口袋配置存在")
        print(f"  - ID: {skill_book_pouch.id}")
        print(f"  - 名称: {skill_book_pouch.name}")
        print(f"  - 类型: {skill_book_pouch.type}")
        print(f"  - 描述: {skill_book_pouch.description}")
    else:
        print(f"✗ 技能书口袋配置不存在")
    
    # 检查其他物品
    test_items = [4001, 4002, 4003, 6001, 6010, 6024]
    print(f"\n检查其他物品配置:")
    for item_id in test_items:
        item = item_repo.get_by_id(item_id)
        if item:
            print(f"  ✓ {item_id}: {item.name}")
        else:
            print(f"  ✗ {item_id}: 配置不存在")
            
except Exception as e:
    print(f"✗ 加载物品配置失败: {e}")

print("\n" + "="*80)
print("\n测试背包路由...")

# 模拟背包API调用
try:
    from flask import Flask
    from interfaces.routes.inventory_routes import inventory_bp
    
    app = Flask(__name__)
    app.register_blueprint(inventory_bp)
    app.secret_key = 'test_secret_key'
    
    with app.test_client() as client:
        # 设置session
        with client.session_transaction() as sess:
            sess['user_id'] = 100006
        
        # 调用背包API
        response = client.get('/api/inventory/list')
        
        print(f"API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.get_json()
            print(f"✓ API调用成功")
            print(f"  - ok: {data.get('ok')}")
            print(f"  - items数量: {len(data.get('items', []))}")
            
            if data.get('items'):
                print(f"\n  返回的物品:")
                for item in data.get('items', []):
                    print(f"    - {item.get('name')} (ID: {item.get('item_id')}) × {item.get('quantity')}")
            else:
                print(f"\n  ⚠ API返回的items为空")
                print(f"  完整响应: {data}")
        else:
            print(f"✗ API调用失败")
            print(f"  响应: {response.get_data(as_text=True)}")
            
except Exception as e:
    print(f"✗ 测试背包路由失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("诊断完成")
