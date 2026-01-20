"""测试灵力水晶使用功能"""
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

def get_inventory(token):
    """获取背包物品"""
    response = requests.get(
        f"{BASE_URL}/api/inventory/list",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()

def get_spirit_account(token):
    """获取战灵账户信息"""
    response = requests.get(
        f"{BASE_URL}/api/spirit/account",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()

def consume_crystal(token, quantity=1):
    """使用灵力水晶"""
    response = requests.post(
        f"{BASE_URL}/api/spirit/consume-crystal",
        headers={"Authorization": f"Bearer {token}"},
        json={"quantity": quantity}
    )
    return response.json()

def test_crystal_usage():
    """测试灵力水晶使用功能"""
    print("=== 测试灵力水晶使用功能 ===\n")
    
    # 登录
    token = login("789", "123456")
    if not token:
        print("❌ 登录失败")
        return
    
    print("✓ 登录成功\n")
    
    # 获取背包信息
    print("1. 检查背包中的灵力水晶数量")
    inv_data = get_inventory(token)
    if not inv_data.get("ok"):
        print(f"❌ 获取背包失败: {inv_data.get('error')}")
        return
    
    crystal_item = None
    for item in inv_data.get("items", []):
        if item.get("item_id") == 6101:
            crystal_item = item
            break
    
    if crystal_item:
        print(f"✓ 拥有灵力水晶: {crystal_item['quantity']} 个")
    else:
        print("⚠ 背包中没有灵力水晶")
        print("提示: 可以通过镇妖宝箱或战灵塔获得灵力水晶")
        return
    
    # 获取当前灵力
    print("\n2. 检查当前灵力")
    spirit_data = get_spirit_account(token)
    if not spirit_data.get("ok"):
        print(f"❌ 获取战灵账户失败: {spirit_data.get('error')}")
        return
    
    before_power = spirit_data.get("account", {}).get("spirit_power", 0)
    print(f"✓ 当前灵力: {before_power}")
    
    # 使用灵力水晶
    print("\n3. 使用灵力水晶")
    use_qty = min(1, crystal_item['quantity'])
    print(f"尝试使用 {use_qty} 个灵力水晶...")
    
    result = consume_crystal(token, use_qty)
    if not result.get("ok"):
        print(f"❌ 使用失败: {result.get('error')}")
        return
    
    gained = result.get("gained_spirit_power", 0)
    used = result.get("used_crystals", 0)
    after_power = result.get("account", {}).get("spirit_power", 0)
    
    print(f"✓ 使用成功!")
    print(f"  - 使用数量: {used} 个")
    print(f"  - 获得灵力: {gained}")
    print(f"  - 灵力变化: {before_power} → {after_power}")
    
    # 验证
    print("\n4. 验证结果")
    expected_power = before_power + (use_qty * 10)
    if after_power == expected_power:
        print(f"✓ 灵力计算正确 (1个水晶 = 10灵力)")
    else:
        print(f"⚠ 灵力计算异常: 预期{expected_power}，实际{after_power}")
    
    # 再次检查背包
    print("\n5. 检查背包中的剩余数量")
    inv_data2 = get_inventory(token)
    if inv_data2.get("ok"):
        crystal_item2 = None
        for item in inv_data2.get("items", []):
            if item.get("item_id") == 6101:
                crystal_item2 = item
                break
        
        if crystal_item2:
            remaining = crystal_item2['quantity']
            expected_remaining = crystal_item['quantity'] - used
            print(f"✓ 剩余灵力水晶: {remaining} 个")
            if remaining == expected_remaining:
                print(f"✓ 数量扣除正确")
            else:
                print(f"⚠ 数量异常: 预期{expected_remaining}，实际{remaining}")
        else:
            print("✓ 灵力水晶已用完")

def test_batch_usage():
    """测试批量使用"""
    print("\n=== 测试批量使用灵力水晶 ===\n")
    
    token = login("789", "123456")
    if not token:
        print("❌ 登录失败")
        return
    
    # 获取当前状态
    inv_data = get_inventory(token)
    spirit_data = get_spirit_account(token)
    
    if not inv_data.get("ok") or not spirit_data.get("ok"):
        print("❌ 获取数据失败")
        return
    
    crystal_item = None
    for item in inv_data.get("items", []):
        if item.get("item_id") == 6101:
            crystal_item = item
            break
    
    if not crystal_item or crystal_item['quantity'] < 5:
        print("⚠ 灵力水晶数量不足5个，跳过批量测试")
        return
    
    before_power = spirit_data.get("account", {}).get("spirit_power", 0)
    before_qty = crystal_item['quantity']
    
    print(f"使用前: 灵力={before_power}, 水晶={before_qty}个")
    
    # 批量使用5个
    print("\n尝试使用 5 个灵力水晶...")
    result = consume_crystal(token, 5)
    
    if result.get("ok"):
        gained = result.get("gained_spirit_power", 0)
        after_power = result.get("account", {}).get("spirit_power", 0)
        
        print(f"✓ 批量使用成功!")
        print(f"  - 获得灵力: {gained}")
        print(f"  - 灵力变化: {before_power} → {after_power}")
        
        if gained == 50:
            print(f"✓ 批量计算正确 (5个水晶 = 50灵力)")
        else:
            print(f"⚠ 批量计算异常: 预期50，实际{gained}")
    else:
        print(f"❌ 批量使用失败: {result.get('error')}")

if __name__ == "__main__":
    print("灵力水晶使用功能测试")
    print("=" * 60)
    
    try:
        test_crystal_usage()
        test_batch_usage()
        
        print("\n" + "=" * 60)
        print("测试完成")
        print("\n功能说明:")
        print("- 1个灵力水晶 = 10灵力")
        print("- 灵力用于洗练战灵的属性条")
        print("- 可以在背包中点击灵力水晶使用")
        print("- 支持批量使用")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到服务器，请确保后端服务正在运行")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
