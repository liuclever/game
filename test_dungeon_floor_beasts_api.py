"""测试副本楼层幻兽API"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import requests

# 测试用户ID（需要先登录）
test_user_id = 100000  # 睡啥觉

print("=" * 60)
print("测试副本楼层幻兽API")
print("=" * 60)

# 测试不同的副本和楼层
test_cases = [
    ("宁静之森", 2),
    ("森林秘境", 2),
    ("森林入口", 2),
    ("森林入口", 5),  # 随机事件层
    ("森林入口", 10), # 随机事件层
]

for dungeon_name, floor in test_cases:
    print(f"\n【测试】{dungeon_name} - 第{floor}层")
    
    try:
        # 注意：这个测试需要后端服务正在运行
        url = f"http://localhost:5000/api/dungeon/floor/beasts?dungeon_name={dungeon_name}&floor={floor}"
        
        # 需要带上session cookie
        response = requests.get(url, cookies={'session': 'test_session'})
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                print(f"  ✅ API调用成功")
                print(f"     floor_event_type: {data.get('floor_event_type')}")
                print(f"     description: {data.get('description')}")
                print(f"     beasts数量: {len(data.get('beasts', []))}")
                
                if data.get('floor_event_type') in ['climb', 'vitality_spring', 'rps']:
                    print(f"     ✅ 随机事件信息完整")
                elif data.get('beasts'):
                    print(f"     ✅ 幻兽信息完整")
            else:
                print(f"  ❌ API返回错误: {data.get('error')}")
        else:
            print(f"  ❌ HTTP错误: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print(f"  ⚠️  无法连接到后端服务（请确保后端正在运行）")
        break
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)

print("\n【说明】")
print("如果看到'无法连接到后端服务'，说明后端没有运行")
print("如果API返回正确的description，说明后端接口正常")
print("如果前端仍然显示空白，可能是前端代码的问题")
