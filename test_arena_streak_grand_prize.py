"""
测试连胜竞技场大奖功能

使用方法：
python test_arena_streak_grand_prize.py
"""

import requests
import json
from datetime import datetime

# 配置
BASE_URL = "http://localhost:5000"
TEST_USER_ID = 1  # 修改为你的测试用户ID

def login(user_id):
    """登录测试用户"""
    session = requests.Session()
    # 这里需要根据实际的登录接口进行调整
    # 假设有一个测试登录接口
    response = session.post(f"{BASE_URL}/api/auth/test-login", json={"user_id": user_id})
    if response.status_code == 200:
        print(f"✅ 登录成功: 用户ID {user_id}")
        return session
    else:
        print(f"❌ 登录失败: {response.text}")
        return None

def get_arena_streak_info(session):
    """获取连胜竞技场信息"""
    response = session.get(f"{BASE_URL}/api/arena-streak/info")
    if response.status_code == 200:
        data = response.json()
        if data.get("ok"):
            print("\n📊 连胜竞技场信息:")
            print(f"  当前连胜: {data.get('current_streak')}次")
            print(f"  今日最高: {data.get('max_streak_today')}次")
            print(f"  连胜王: {data.get('streak_king', {}).get('nickname')} ({data.get('streak_king', {}).get('streak')}连胜)")
            print(f"  已领取大奖: {'是' if data.get('claimed_grand_prize') else '否'}")
            return data
        else:
            print(f"❌ 获取信息失败: {data.get('error')}")
            return None
    else:
        print(f"❌ 请求失败: {response.status_code}")
        return None

def claim_grand_prize(session):
    """领取连胜大奖"""
    print("\n🎁 尝试领取连胜大奖...")
    response = session.post(f"{BASE_URL}/api/arena-streak/claim-grand-prize")
    if response.status_code == 200:
        data = response.json()
        if data.get("ok"):
            print("✅ 领取成功!")
            print(f"  消息: {data.get('message')}")
            if "rewards" in data:
                print("  奖励:")
                for item, qty in data["rewards"].items():
                    print(f"    - {item}: {qty}")
            return True
        else:
            print(f"❌ 领取失败: {data.get('error')}")
            return False
    else:
        print(f"❌ 请求失败: {response.status_code}")
        return False

def check_inventory(session):
    """检查背包中的道具"""
    print("\n🎒 检查背包...")
    response = session.get(f"{BASE_URL}/api/inventory")
    if response.status_code == 200:
        data = response.json()
        if data.get("ok"):
            items = data.get("items", [])
            print(f"  背包物品数量: {len(items)}")
            
            # 查找大奖相关道具
            target_items = {
                6019: "追魂法宝",
                6005: "金袋",
                6004: "招财神符"
            }
            
            for item in items:
                item_id = item.get("item_info", {}).get("id")
                if item_id in target_items:
                    quantity = item.get("inv_item", {}).get("quantity", 0)
                    print(f"  ✅ {target_items[item_id]}: {quantity}个")
            return True
        else:
            print(f"❌ 获取背包失败: {data.get('error')}")
            return False
    else:
        print(f"❌ 请求失败: {response.status_code}")
        return False

def main():
    """主测试流程"""
    print("=" * 60)
    print("连胜竞技场大奖功能测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试用户ID: {TEST_USER_ID}")
    print("=" * 60)
    
    # 1. 登录
    session = login(TEST_USER_ID)
    if not session:
        print("\n❌ 测试终止: 登录失败")
        return
    
    # 2. 获取竞技场信息
    info = get_arena_streak_info(session)
    if not info:
        print("\n❌ 测试终止: 无法获取竞技场信息")
        return
    
    # 3. 检查是否是连胜王
    streak_king = info.get("streak_king", {})
    is_king = streak_king.get("user_id") == TEST_USER_ID
    
    if not is_king:
        print(f"\n⚠️  当前用户不是连胜王，无法领取大奖")
        print(f"   连胜王: {streak_king.get('nickname')} (ID: {streak_king.get('user_id')})")
        print(f"   你的连胜: {info.get('max_streak_today')}次")
        print(f"   连胜王连胜: {streak_king.get('streak')}次")
        print("\n💡 提示: 需要成为连胜王才能测试领取功能")
        return
    
    print(f"\n✅ 你是连胜王! 连胜次数: {info.get('max_streak_today')}")
    
    # 4. 检查是否已领取
    if info.get("claimed_grand_prize"):
        print("\n⚠️  今日已领取过大奖")
        print("💡 提示: 每日只能领取一次，请明天再试")
        return
    
    # 5. 领取大奖
    if claim_grand_prize(session):
        # 6. 验证背包
        check_inventory(session)
        
        # 7. 再次获取信息验证状态
        print("\n🔄 验证领取状态...")
        info2 = get_arena_streak_info(session)
        if info2 and info2.get("claimed_grand_prize"):
            print("✅ 领取状态已更新")
        else:
            print("⚠️  领取状态未更新（可能需要刷新）")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
