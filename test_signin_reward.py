"""
测试签到累计奖励功能
"""
import requests
from infrastructure.db.connection import execute_query, execute_update

BASE_URL = "http://localhost:5000"

def login(username, password):
    """登录并返回session"""
    session = requests.Session()
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "username": username,
        "password": password
    })
    if response.status_code == 200:
        print(f"✅ 登录成功: {username}")
        return session
    else:
        print(f"❌ 登录失败: {response.text}")
        return None

def set_consecutive_days(user_id, days):
    """设置连续签到天数"""
    execute_update(
        "UPDATE player SET consecutive_signin_days = %s WHERE user_id = %s",
        (days, user_id)
    )
    print(f"✅ 已设置连续签到天数为 {days} 天")

def test_get_reward_info(session, days):
    """测试获取奖励信息"""
    print(f"\n--- 测试获取{days}天奖励信息 ---")
    response = session.get(f"{BASE_URL}/api/signin/reward/{days}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 获取成功")
        print(f"   连续签到天数: {data.get('consecutiveDays')}")
        print(f"   是否已领取: {data.get('claimed')}")
        print(f"   是否可领取: {data.get('canClaim')}")
        return data
    else:
        print(f"❌ 获取失败: {response.text}")
        return None

def test_claim_reward(session, days):
    """测试领取奖励"""
    print(f"\n--- 测试领取{days}天奖励 ---")
    response = session.post(f"{BASE_URL}/api/signin/reward/{days}/claim")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 领取成功: {data.get('message')}")
        return True
    else:
        error = response.json().get('error', '未知错误')
        print(f"❌ 领取失败: {error}")
        return False

def check_inventory(user_id):
    """检查背包物品"""
    print(f"\n--- 检查背包物品 ---")
    items = execute_query(
        """SELECT i.item_id, i.quantity, it.name 
           FROM player_inventory i
           LEFT JOIN items it ON i.item_id = it.id
           WHERE i.user_id = %s AND i.quantity > 0
           ORDER BY i.item_id""",
        (user_id,)
    )
    
    if items:
        print("背包物品:")
        for item in items:
            item_name = item.get('name', f"物品{item['item_id']}")
            print(f"  - {item_name} x{item['quantity']}")
    else:
        print("背包为空")

def check_copper(user_id):
    """检查铜钱"""
    player = execute_query(
        "SELECT gold FROM player WHERE user_id = %s",
        (user_id,)
    )
    if player:
        print(f"当前铜钱: {player[0]['gold']}")

if __name__ == "__main__":
    print("=" * 60)
    print("签到累计奖励功能测试")
    print("=" * 60)
    
    # 登录测试账号
    session = login("test1", "123456")
    if not session:
        print("❌ 无法登录，测试终止")
        exit(1)
    
    # 获取用户ID
    user_info = execute_query("SELECT user_id FROM user WHERE username = 'test1'")
    if not user_info:
        print("❌ 找不到用户，测试终止")
        exit(1)
    
    user_id = user_info[0]['user_id']
    print(f"用户ID: {user_id}")
    
    # 清空已领取记录
    execute_update(
        "UPDATE player SET signin_rewards_claimed = '' WHERE user_id = %s",
        (user_id,)
    )
    print("✅ 已清空领取记录")
    
    # 测试场景1: 连续签到不足7天
    print("\n【场景1】连续签到不足7天")
    print("-" * 60)
    set_consecutive_days(user_id, 5)
    info = test_get_reward_info(session, 7)
    if info and not info.get('canClaim'):
        test_claim_reward(session, 7)  # 应该失败
    
    # 测试场景2: 连续签到满7天
    print("\n【场景2】连续签到满7天")
    print("-" * 60)
    set_consecutive_days(user_id, 7)
    test_get_reward_info(session, 7)
    check_inventory(user_id)
    check_copper(user_id)
    test_claim_reward(session, 7)
    check_inventory(user_id)
    check_copper(user_id)
    
    # 测试场景3: 重复领取
    print("\n【场景3】重复领取7天奖励")
    print("-" * 60)
    test_claim_reward(session, 7)  # 应该失败
    
    # 测试场景4: 15天奖励
    print("\n【场景4】15天奖励")
    print("-" * 60)
    set_consecutive_days(user_id, 15)
    test_get_reward_info(session, 15)
    test_claim_reward(session, 15)
    check_inventory(user_id)
    
    # 测试场景5: 30天奖励
    print("\n【场景5】30天奖励")
    print("-" * 60)
    set_consecutive_days(user_id, 30)
    test_get_reward_info(session, 30)
    test_claim_reward(session, 30)
    check_inventory(user_id)
    check_copper(user_id)
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
