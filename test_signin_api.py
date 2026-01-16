"""测试签到API"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from interfaces.web_api.app import app
import json

print("=" * 60)
print("测试签到API")
print("=" * 60)
print()

# 创建测试客户端
client = app.test_client()

# 模拟登录
print("【步骤1】登录")
print("-" * 60)
# 使用session模拟登录
with client.session_transaction() as sess:
    sess['user_id'] = 4053

print("✅ 已设置session (user_id=4053)")
print()

# 测试获取签到信息
print("【步骤2】获取签到信息")
print("-" * 60)
response = client.get('/api/signin/info')
data = response.get_json()
print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
print()

# 测试获取补签信息
print("【步骤3】获取补签信息")
print("-" * 60)
response = client.get('/api/signin/makeup/info')
data = response.get_json()
print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")

if data.get('ok'):
    print(f"\n已签到的日期: {data.get('signedDays')}")
    print(f"未签到的日期: {data.get('missedDays')}")
    print(f"补签卡数量: {data.get('currentCards')}")
    print(f"可补签次数: {data.get('availableMakeups')}")

print()
print("=" * 60)
print("测试完成")
print("=" * 60)
