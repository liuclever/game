"""测试召唤之王挑战赛报名要求和对手无幻兽挑战"""
import requests
import json

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

def get_king_info(token):
    """获取召唤之王信息"""
    response = requests.get(
        f"{BASE_URL}/api/king/info",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()

def register_king(token):
    """报名参加挑战赛"""
    response = requests.post(
        f"{BASE_URL}/api/king/register",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()

def challenge_king(token, target_user_id):
    """发起挑战"""
    response = requests.post(
        f"{BASE_URL}/api/king/challenge",
        headers={"Authorization": f"Bearer {token}"},
        json={"targetUserId": target_user_id}
    )
    return response.json()

def test_registration_requirement():
    """测试必须报名才能挑战"""
    print("\n=== 测试1: 未报名时尝试挑战 ===")
    
    # 使用测试账号登录
    token = login("test1", "123456")
    if not token:
        print("❌ 登录失败")
        return
    
    print("✓ 登录成功")
    
    # 获取挑战赛信息
    info = get_king_info(token)
    if not info.get("ok"):
        print(f"❌ 获取信息失败: {info.get('error')}")
        return
    
    print(f"✓ 当前排名: {info['myRank']}")
    print(f"✓ 是否已报名: {info['isRegistered']}")
    
    # 如果未报名，尝试挑战（应该失败）
    if not info['isRegistered']:
        challengers = info.get('challengers', [])
        if challengers:
            target_id = challengers[0]['userId']
            print(f"\n尝试挑战玩家 {target_id}（未报名状态）...")
            result = challenge_king(token, target_id)
            
            if not result.get("ok"):
                if "报名" in result.get("error", ""):
                    print(f"✓ 正确拒绝: {result['error']}")
                else:
                    print(f"⚠ 拒绝原因不符: {result['error']}")
            else:
                print(f"❌ 应该拒绝但允许了挑战")
        else:
            print("⚠ 没有可挑战的对手")
    else:
        print("⚠ 玩家已报名，无法测试未报名挑战")

def test_challenge_without_beasts():
    """测试挑战没有出战幻兽的对手"""
    print("\n=== 测试2: 挑战没有出战幻兽的对手 ===")
    
    # 这个测试需要手动设置一个没有出战幻兽的测试账号
    # 这里只是演示逻辑
    print("提示: 需要手动创建一个没有出战幻兽的测试账号来完整测试此功能")
    print("预期行为: 允许挑战，挑战者自动获胜")

def test_registration_and_challenge():
    """测试完整流程：报名 -> 挑战"""
    print("\n=== 测试3: 完整流程测试 ===")
    
    token = login("test1", "123456")
    if not token:
        print("❌ 登录失败")
        return
    
    print("✓ 登录成功")
    
    # 获取信息
    info = get_king_info(token)
    if not info.get("ok"):
        print(f"❌ 获取信息失败: {info.get('error')}")
        return
    
    print(f"✓ 当前排名: {info['myRank']}")
    print(f"✓ 是否已报名: {info['isRegistered']}")
    
    # 如果未报名，先报名
    if not info['isRegistered']:
        print("\n尝试报名...")
        reg_result = register_king(token)
        
        if reg_result.get("ok"):
            print(f"✓ 报名成功: {reg_result.get('message')}")
        else:
            error = reg_result.get('error', '')
            if "星期一" in error:
                print(f"⚠ 报名时间限制: {error}")
                print("提示: 报名功能仅在星期一开放")
                return
            elif "已报名" in error:
                print(f"✓ 已经报名过了")
            else:
                print(f"❌ 报名失败: {error}")
                return
    
    # 刷新信息
    info = get_king_info(token)
    if info.get('isRegistered'):
        print("\n✓ 已报名，可以进行挑战")
        
        challengers = info.get('challengers', [])
        if challengers:
            target = challengers[0]
            print(f"\n尝试挑战排名 {target['rank']} 的 {target['nickname']}...")
            
            result = challenge_king(token, target['userId'])
            
            if result.get("ok"):
                print(f"✓ 挑战成功!")
                print(f"  - 胜负: {'胜利' if result['win'] else '失败'}")
                print(f"  - 新排名: {result['newRank']}")
                print(f"  - 奖励: {result['reward']} 铜钱")
                print(f"  - 消息: {result['message']}")
            else:
                print(f"⚠ 挑战失败: {result.get('error')}")
        else:
            print("⚠ 没有可挑战的对手（已是第一名）")

if __name__ == "__main__":
    print("召唤之王挑战赛 - 报名要求和对手无幻兽测试")
    print("=" * 60)
    
    try:
        # 测试1: 未报名时不能挑战
        test_registration_requirement()
        
        # 测试2: 可以挑战没有幻兽的对手
        test_challenge_without_beasts()
        
        # 测试3: 完整流程
        test_registration_and_challenge()
        
        print("\n" + "=" * 60)
        print("测试完成")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到服务器，请确保后端服务正在运行")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
