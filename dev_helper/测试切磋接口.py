"""测试连胜竞技场切磋接口"""
import requests
import json

# 测试配置
BASE_URL = "http://localhost:5000"
session = requests.Session()

def test_login():
    """测试登录"""
    print("1. 测试登录...")
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "username": "test",
        "password": "test123"
    })
    print(f"   状态码: {response.status_code}")
    print(f"   响应: {response.json()}")
    return response.json().get('ok', False)

def test_arena_streak_info():
    """测试获取竞技场信息"""
    print("\n2. 测试获取竞技场信息...")
    response = session.get(f"{BASE_URL}/api/arena-streak/info")
    print(f"   状态码: {response.status_code}")
    data = response.json()
    print(f"   响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
    return data

def test_battle(opponent_id):
    """测试切磋"""
    print(f"\n3. 测试切磋 (对手ID: {opponent_id})...")
    try:
        response = session.post(f"{BASE_URL}/api/arena-streak/battle", json={
            "opponent_id": opponent_id
        })
        print(f"   状态码: {response.status_code}")
        data = response.json()
        print(f"   响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        return data
    except Exception as e:
        print(f"   错误: {e}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("测试连胜竞技场切磋接口")
    print("=" * 60)
    
    # 登录
    if not test_login():
        print("\n❌ 登录失败，无法继续测试")
        exit(1)
    
    # 获取竞技场信息
    info = test_arena_streak_info()
    if not info.get('ok'):
        print("\n❌ 获取竞技场信息失败")
        exit(1)
    
    # 获取对手
    opponents = info.get('opponents', [])
    if not opponents:
        print("\n❌ 没有可切磋的对手")
        exit(1)
    
    opponent_id = opponents[0]['user_id']
    print(f"\n选择对手: {opponents[0]['nickname']} (ID: {opponent_id})")
    
    # 测试切磋
    battle_result = test_battle(opponent_id)
    
    if battle_result and battle_result.get('ok'):
        print("\n✅ 切磋成功！")
        print(f"   胜负: {'胜利' if battle_result.get('victory') else '失败'}")
        print(f"   连胜: {battle_result.get('current_streak')}次")
        print(f"   战报条数: {len(battle_result.get('battle_logs', []))}")
    else:
        print("\n❌ 切磋失败")
        if battle_result:
            print(f"   错误: {battle_result.get('error', '未知错误')}")
    
    print("\n" + "=" * 60)
