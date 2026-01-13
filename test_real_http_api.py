"""测试实际的HTTP API响应"""
import sys
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# 使用Flask测试客户端
from interfaces.web_api.app import app

print("=" * 60)
print("测试实际HTTP API响应")
print("=" * 60)
print()

# 创建测试客户端
client = app.test_client()

# 测试两个玩家
test_users = [
    ('123', '123', 4053),  # 玩家A
    ('789', '789', 4055),  # 玩家B
]

for username, password, expected_user_id in test_users:
    print(f"【测试玩家: {username}】")
    print("-" * 60)
    
    # 1. 登录
    response = client.post('/api/auth/login', 
                          json={'username': username, 'password': password})
    login_data = response.get_json()
    
    if not login_data.get('ok'):
        print(f"❌ 登录失败: {login_data.get('error')}")
        continue
    
    print(f"✅ 登录成功")
    
    # 2. 获取擂台信息
    response = client.get('/api/arena/info?type=normal')
    arena_data = response.get_json()
    
    print(f"\nHTTP响应状态码: {response.status_code}")
    print(f"响应数据:")
    print(json.dumps(arena_data, indent=2, ensure_ascii=False))
    
    if arena_data.get('ok'):
        arena = arena_data.get('arena', {})
        print(f"\n解析后的擂台信息:")
        print(f"  champion: {arena.get('champion')}")
        print(f"  championUserId: {arena.get('championUserId')}")
        print(f"  isEmpty: {arena.get('isEmpty')}")
        print(f"  isChampion: {arena.get('isChampion')}")
        print(f"  consecutiveWins: {arena.get('consecutiveWins')}")
        print(f"  prizePool: {arena.get('prizePool')}")
        
        # 判断
        if arena.get('isEmpty'):
            print(f"\n⚠️ 玩家 {username} 看到擂台为空")
        elif arena.get('champion'):
            print(f"\n✅ 玩家 {username} 看到擂主: {arena.get('champion')}")
        else:
            print(f"\n❌ 异常：isEmpty=False但champion为空")
    else:
        print(f"\n❌ API返回错误: {arena_data.get('error')}")
    
    print()

print("=" * 60)
