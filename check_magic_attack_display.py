"""检查法攻显示问题"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import json

print("="*80)
print("检查法攻显示问题")
print("="*80)

# 1. 检查配置文件
print("\n1. 检查副本配置文件...")
config_path = os.path.join(os.path.dirname(__file__), 'configs', 'dungeon_beasts.json')

with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# 找几个法攻型幻兽
magic_beasts = []
for dungeon_id, dungeon_data in config['dungeons'].items():
    dungeon_name = dungeon_data['name']
    
    # 检查普通幻兽
    for beast in dungeon_data['beasts'].get('normal', []):
        if beast.get('attack_type') == 'magical':
            magic_beasts.append({
                'dungeon': dungeon_name,
                'type': '普通',
                'name': beast['name'],
                'level': beast['level'],
                'matk': beast['stats'].get('matk', 0),
                'atk': beast['stats'].get('atk', 0)
            })
            if len(magic_beasts) >= 3:
                break
    
    if len(magic_beasts) >= 3:
        break

print(f"\n找到 {len(magic_beasts)} 个法攻型幻兽示例：")
for beast in magic_beasts:
    print(f"  - {beast['dungeon']}: {beast['name']} (等级{beast['level']})")
    print(f"    matk={beast['matk']}, atk={beast['atk']}")

# 2. 测试API
print("\n2. 测试副本API...")
try:
    from interfaces.routes.dungeon_routes import _to_pvp_beasts_from_config
    
    # 构造测试数据
    test_beast = {
        'name': '测试法攻幻兽',
        'level': 10,
        'count': 1,
        'stats': {
            'hp': 100,
            'matk': 50,  # 法攻值
            'def': 30,
            'mdef': 40,
            'speed': 20
        },
        'attack_type': 'magical',
        'skills': []
    }
    
    pvp_beasts = _to_pvp_beasts_from_config([test_beast])
    
    if pvp_beasts:
        beast = pvp_beasts[0]
        print(f"\n  测试幻兽: {beast.name}")
        print(f"  物攻: {beast.physical_attack}")
        print(f"  法攻: {beast.magic_attack}")
        
        if beast.magic_attack == 50:
            print("\n  ✅ 法攻显示正确！")
        else:
            print(f"\n  ✗ 法攻显示错误！期望50，实际{beast.magic_attack}")
    else:
        print("\n  ✗ 无法创建测试幻兽")
        
except Exception as e:
    print(f"\n  ✗ 测试失败: {e}")
    import traceback
    traceback.print_exc()

# 3. 检查代码
print("\n3. 检查代码修复...")
code_path = os.path.join(os.path.dirname(__file__), 'interfaces', 'routes', 'dungeon_routes.py')

with open(code_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 查找关键代码行
if "ma = stats.get('matk', 0) if attack_type == 'magic' else 0" in code:
    print("  ✅ 代码修复正确")
elif "ma = stats.get('atk', 0) if attack_type == 'magic'" in code:
    print("  ✗ 代码未修复（仍然是错误的版本）")
else:
    print("  ⚠ 无法确认代码状态")

print("\n" + "="*80)
print("\n如果法攻仍然显示0，请：")
print("1. 重启后端服务")
print("2. 强制刷新浏览器（Ctrl+F5）")
print("3. 确认查看的是法攻型幻兽（attack_type为magical）")
print("4. 检查浏览器控制台是否有错误")
