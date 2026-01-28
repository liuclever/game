"""测试副本战斗完整流程"""
import sys
sys.path.insert(0, '.')

import requests
import json

BASE_URL = "http://localhost:5000"

def test_dungeon_battle():
    """测试副本战斗流程"""
    
    # 使用测试账号登录
    session = requests.Session()
    
    print("=" * 70)
    print("测试副本战斗流程")
    print("=" * 70)
    
    # 1. 登录
    print("\n1. 登录测试账号...")
    login_data = {
        "username": "秦王",
        "password": "123456"
    }
    resp = session.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if resp.status_code == 200:
        result = resp.json()
        if result.get('ok'):
            print(f"   ✓ 登录成功: {result.get('username')}")
        else:
            print(f"   ❌ 登录失败: {result.get('error')}")
            return
    else:
        print(f"   ❌ 登录请求失败: {resp.status_code}")
        return
    
    # 2. 获取副本进度
    print("\n2. 获取副本进度...")
    dungeon_name = "森林入口"
    resp = session.get(f"{BASE_URL}/api/dungeon/progress?dungeon_name={dungeon_name}")
    if resp.status_code == 200:
        progress = resp.json()
        if progress.get('ok'):
            current_floor = progress.get('current_floor', 1)
            print(f"   ✓ 当前楼层: {current_floor}")
        else:
            print(f"   ❌ 获取进度失败: {progress.get('error')}")
            return
    else:
        print(f"   ❌ 请求失败: {resp.status_code}")
        return
    
    # 3. 获取当前层幻兽
    print(f"\n3. 获取第{current_floor}层幻兽...")
    resp = session.get(f"{BASE_URL}/api/dungeon/floor/beasts?dungeon_name={dungeon_name}&floor={current_floor}")
    if resp.status_code == 200:
        floor_data = resp.json()
        if floor_data.get('ok'):
            beasts = floor_data.get('beasts', [])
            floor_type = floor_data.get('floor_event_type', 'unknown')
            print(f"   ✓ 楼层类型: {floor_type}")
            print(f"   ✓ 幻兽数量: {len(beasts)}")
            
            if beasts:
                for i, beast in enumerate(beasts, 1):
                    print(f"   {i}. {beast.get('name')} (Lv.{beast.get('level')})")
                    stats = beast.get('stats', {})
                    print(f"      HP:{stats.get('hp')} 物攻:{stats.get('atk')} "
                          f"法攻:{stats.get('matk', 0)} 速度:{stats.get('speed')}")
            else:
                print(f"   ⚠️  当前层没有幻兽（可能是随机事件层）")
                return
        else:
            print(f"   ❌ 获取幻兽失败: {floor_data.get('error')}")
            return
    else:
        print(f"   ❌ 请求失败: {resp.status_code}")
        return
    
    # 4. 挑战幻兽
    print(f"\n4. 挑战幻兽...")
    challenge_data = {
        "dungeon_name": dungeon_name,
        "floor": current_floor,
        "beasts": beasts
    }
    
    resp = session.post(f"{BASE_URL}/api/dungeon/challenge", json=challenge_data)
    if resp.status_code == 200:
        result = resp.json()
        if result.get('ok'):
            battle_data = result.get('battle_data', {})
            is_victory = battle_data.get('is_victory', False)
            rating = battle_data.get('rating', 'N/A')
            battles = battle_data.get('battles', [])
            
            print(f"   ✓ 战斗完成")
            print(f"   结果: {'胜利' if is_victory else '失败'}")
            print(f"   评级: {rating}")
            print(f"   战斗回合数: {len(battles)}")
            
            if battles:
                print(f"\n   战斗详情:")
                for i, battle in enumerate(battles, 1):
                    rounds = battle.get('rounds', [])
                    winner = battle.get('winner', 'unknown')
                    print(f"   第{i}场: {len(rounds)}回合, 胜者: {winner}")
                    
                    # 显示前3回合
                    for j, round_data in enumerate(rounds[:3], 1):
                        action = round_data.get('action', '')
                        print(f"      回合{j}: {action}")
            else:
                print(f"   ❌ 没有战斗数据！")
        else:
            print(f"   ❌ 挑战失败: {result.get('error')}")
    else:
        print(f"   ❌ 请求失败: {resp.status_code}")
        print(f"   响应内容: {resp.text}")
    
    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70)

if __name__ == '__main__':
    test_dungeon_battle()
