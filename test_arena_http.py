"""测试擂台HTTP API"""
import requests

# 测试URL
BASE_URL = "http://127.0.0.1:5000"

# 创建session以保持登录状态
session = requests.Session()

# 1. 先登录
print("=== 步骤1: 登录 ===")
login_data = {
    "username": "123",
    "password": "123"
}
response = session.post(f"{BASE_URL}/api/auth/login", json=login_data)
print(f"登录响应: {response.status_code}")
print(f"登录结果: {response.json()}")
print()

# 2. 获取擂台信息
print("=== 步骤2: 获取擂台信息 ===")
response = session.get(f"{BASE_URL}/api/arena/info?type=normal")
print(f"响应状态码: {response.status_code}")
data = response.json()
print(f"响应数据: {data}")
print()

if data.get('ok'):
    arena = data.get('arena', {})
    print(f"擂台信息:")
    print(f"  champion: {arena.get('champion')}")
    print(f"  championUserId: {arena.get('championUserId')}")
    print(f"  consecutiveWins: {arena.get('consecutiveWins')}")
    print(f"  prizePool: {arena.get('prizePool')}")
    print(f"  isChampion: {arena.get('isChampion')}")
    print(f"  isEmpty: {arena.get('isEmpty')}")
