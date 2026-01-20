"""测试镇妖动态功能"""
import requests

BASE_URL = "http://localhost:5000"

def login(username, password):
    """登录并返回 token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": username,
        "password": password
    })
    if response.status_code == 200:
        data = response.json()
        if data.get("ok"):
            return data.get("token")
    return None

def get_zhenyao_info(token):
    """获取镇妖信息"""
    response = requests.get(
        f"{BASE_URL}/api/zhenyao/info",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()

def get_dynamics(token, dynamic_type="all"):
    """获取动态"""
    response = requests.get(
        f"{BASE_URL}/api/zhenyao/dynamics?type={dynamic_type}",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()

def occupy_floor(token, floor):
    """占领层"""
    response = requests.post(
        f"{BASE_URL}/api/zhenyao/occupy",
        headers={"Authorization": f"Bearer {token}"},
        json={"floor": floor}
    )
    return response.json()

def challenge_floor(token, floor):
    """挑战层"""
    response = requests.post(
        f"{BASE_URL}/api/zhenyao/challenge",
        headers={"Authorization": f"Bearer {token}"},
        json={"floor": floor}
    )
    return response.json()

def test_dynamics_display():
    """测试动态显示"""
    print("=== 测试镇妖动态显示 ===\n")
    
    # 登录
    token = login("789", "123456")
    if not token:
        print("❌ 登录失败")
        return
    
    print("✓ 登录成功\n")
    
    # 获取镇妖信息
    print("1. 获取镇妖信息")
    info = get_zhenyao_info(token)
    if not info.get("can_zhenyao"):
        print(f"⚠ 无法镇妖: {info.get('error')}")
        return
    
    print(f"✓ 可以镇妖")
    print(f"  - 等级: {info['player_level']}")
    print(f"  - 阶位: {info['rank_name']}")
    print(f"  - 试炼层: {len(info.get('trial_floors', []))} 层")
    print(f"  - 炼狱层: {len(info.get('hell_floors', []))} 层")
    
    # 获取全服动态
    print("\n2. 获取全服动态")
    all_dynamics = get_dynamics(token, "all")
    if all_dynamics.get("ok"):
        dynamics = all_dynamics.get("dynamics", [])
        print(f"✓ 找到 {len(dynamics)} 条全服动态")
        
        if dynamics:
            print("\n最近的动态:")
            for i, d in enumerate(dynamics[:5], 1):
                print(f"\n  {i}. {d['text']}")
                print(f"     时间: {d['time']}")
                print(f"     层数: {d['floor']}")
                print(f"     结果: {'成功' if d['success'] else '失败'}")
        else:
            print("  暂无动态")
    else:
        print(f"❌ 获取失败: {all_dynamics.get('error')}")
    
    # 获取个人动态
    print("\n3. 获取个人动态")
    personal_dynamics = get_dynamics(token, "personal")
    if personal_dynamics.get("ok"):
        dynamics = personal_dynamics.get("dynamics", [])
        print(f"✓ 找到 {len(dynamics)} 条个人动态")
        
        if dynamics:
            print("\n我的动态:")
            for i, d in enumerate(dynamics[:5], 1):
                print(f"\n  {i}. {d['text']}")
                print(f"     时间: {d['time']}")
                print(f"     层数: {d['floor']}")
                print(f"     结果: {'成功' if d['success'] else '失败'}")
        else:
            print("  暂无个人动态")
    else:
        print(f"❌ 获取失败: {personal_dynamics.get('error')}")

def test_dynamic_text_format():
    """测试动态文本格式"""
    print("\n=== 测试动态文本格式 ===\n")
    
    # 模拟不同类型的动态
    test_cases = [
        {
            "type": "占领",
            "attacker": "张三",
            "defender": "",
            "floor": 31,
            "success": True,
            "expected": "【张三】成功占领第31层聚魂阵"
        },
        {
            "type": "挑战成功",
            "attacker": "李四",
            "defender": "王五",
            "floor": 35,
            "success": True,
            "expected": "【李四】挑战【王五】占领的第35层聚魂阵，挑战成功！"
        },
        {
            "type": "挑战失败",
            "attacker": "赵六",
            "defender": "孙七",
            "floor": 40,
            "success": False,
            "expected": "【赵六】挑战【孙七】占领的第40层聚魂阵，挑战失败"
        },
    ]
    
    print("预期的动态文本格式:\n")
    for case in test_cases:
        print(f"{case['type']:8s}: {case['expected']}")

def test_occupy_and_check_dynamic():
    """测试占领并检查动态"""
    print("\n=== 测试占领并检查动态 ===\n")
    
    token = login("789", "123456")
    if not token:
        print("❌ 登录失败")
        return
    
    print("✓ 登录成功\n")
    
    # 获取镇妖信息
    info = get_zhenyao_info(token)
    if not info.get("can_zhenyao"):
        print(f"⚠ 无法镇妖: {info.get('error')}")
        return
    
    trial_floors = info.get('trial_floors', [])
    if not trial_floors:
        print("⚠ 没有可用的试炼层")
        return
    
    # 尝试占领第一个试炼层
    target_floor = trial_floors[0]
    print(f"尝试占领第 {target_floor} 层...")
    
    result = occupy_floor(token, target_floor)
    if result.get("ok"):
        print(f"✓ {result['message']}")
        
        # 等待一下，然后检查动态
        import time
        time.sleep(1)
        
        print("\n检查动态是否更新...")
        dynamics = get_dynamics(token, "all")
        if dynamics.get("ok"):
            recent = dynamics.get("dynamics", [])
            if recent:
                latest = recent[0]
                print(f"✓ 最新动态: {latest['text']}")
                if str(target_floor) in latest['text']:
                    print(f"✓ 动态包含正确的层数")
            else:
                print("⚠ 没有找到动态")
    else:
        print(f"⚠ 占领失败: {result.get('error')}")
        print("  (可能已经占领了其他层，或该层已被占领)")

if __name__ == "__main__":
    print("镇妖动态功能测试")
    print("=" * 60)
    
    try:
        test_dynamics_display()
        test_dynamic_text_format()
        # test_occupy_and_check_dynamic()  # 可选：实际测试占领
        
        print("\n" + "=" * 60)
        print("测试完成")
        print("\n动态文本格式:")
        print("- 占领: 【玩家】成功占领第X层聚魂阵")
        print("- 挑战成功: 【挑战者】挑战【防守者】占领的第X层聚魂阵，挑战成功！")
        print("- 挑战失败: 【挑战者】挑战【防守者】占领的第X层聚魂阵，挑战失败")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到服务器，请确保后端服务正在运行")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
