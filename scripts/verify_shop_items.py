#!/usr/bin/env python3
"""验证商城配置中的所有商品item_id是否在items.json中存在"""

import json
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_json_file(filepath):
    """加载JSON文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def verify_shop_items():
    """验证商城商品配置"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    shop_config_path = os.path.join(base_dir, 'configs', 'shop.json')
    items_config_path = os.path.join(base_dir, 'configs', 'items.json')
    
    # 加载配置
    shop_config = load_json_file(shop_config_path)
    items_config = load_json_file(items_config_path)
    
    # 构建item_id集合
    item_ids = set()
    for item in items_config:
        item_ids.add(item.get('id'))
    
    # 检查商城商品
    shop_items = shop_config.get('items', [])
    errors = []
    warnings = []
    
    print("=" * 60)
    print("商城商品配置验证")
    print("=" * 60)
    print(f"\n物品配置总数: {len(item_ids)}")
    print(f"商城商品总数: {len(shop_items)}\n")
    
    for shop_item in shop_items:
        shop_item_id = shop_item.get('id')
        item_id = shop_item.get('item_id')
        name = shop_item.get('name', '未知')
        
        if not item_id:
            errors.append({
                'shop_item_id': shop_item_id,
                'name': name,
                'error': '缺少item_id字段'
            })
        elif item_id not in item_ids:
            errors.append({
                'shop_item_id': shop_item_id,
                'item_id': item_id,
                'name': name,
                'error': f'item_id {item_id} 在items.json中不存在'
            })
        else:
            # 验证物品模板信息
            item_template = None
            for item in items_config:
                if item.get('id') == item_id:
                    item_template = item
                    break
            
            if item_template:
                print(f"[OK] 商品ID {shop_item_id}: {name} (item_id: {item_id})")
    
    # 输出错误
    if errors:
        print("\n" + "=" * 60)
        print("发现的问题:")
        print("=" * 60)
        for error in errors:
            print(f"\n[ERROR] 商品ID {error['shop_item_id']}: {error['name']}")
            print(f"   错误: {error['error']}")
            if 'item_id' in error:
                print(f"   item_id: {error['item_id']}")
        return False
    else:
        print("\n" + "=" * 60)
        print("[OK] 所有商城商品配置正确！")
        print("=" * 60)
        return True

if __name__ == '__main__':
    success = verify_shop_items()
    sys.exit(0 if success else 1)
