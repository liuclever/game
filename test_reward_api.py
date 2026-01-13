"""
快速测试签到奖励API
"""
import requests

BASE_URL = "http://localhost:5000"

# 登录
session = requests.Session()
print("正在登录...")
response = session.post(f"{BASE_URL}/api/auth/login", json={
    "username": "test1",
    "password": "123456"
})

if response.status_code != 200:
    print(f"❌ 登录失败: {response.text}")
    exit(1)

print("✅ 登录成功")
print()

# 获取签到信息
print("获取签到信息...")
response = session.get(f"{BASE_URL}/api/signin/info")
if response.status_code == 200:
    data = response.json()
    print(f"✅ 签到信息:")
    print(f"   连续签到天数: {data.get('consecutiveDays')}")
    print(f"   今日已签到: {data.get('hasSigned')}")
else:
    print(f"❌ 获取失败: {response.text}")

print()

# 测试7天奖励接口
for days in [7, 15, 30]:
    print(f"测试{days}天奖励接口...")
    response = session.get(f"{BASE_URL}/api/signin/reward/{days}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {days}天奖励状态:")
        print(f"   ok: {data.get('ok')}")
        print(f"   consecutiveDays: {data.get('consecutiveDays')}")
        print(f"   claimed: {data.get('claimed')}")
        print(f"   canClaim: {data.get('canClaim')}")
    else:
        print(f"❌ 获取失败: {response.status_code} - {response.text}")
    
    print()
