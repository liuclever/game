"""为测试账号设置密码"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.db.connection import execute_update, execute_query

# 为测试账号设置简单密码
test_accounts = [
    ("测试50级A", "123456"),
    ("测试50级B", "123456")
]

print("为测试账号设置密码...")
print("="*60)

for nickname, password in test_accounts:
    # 更新密码
    execute_update(
        "UPDATE player SET password = %s WHERE nickname = %s",
        (password, nickname)
    )
    
    # 验证
    result = execute_query(
        "SELECT user_id, username, nickname, password FROM player WHERE nickname = %s",
        (nickname,)
    )
    
    if result:
        acc = result[0]
        print(f"✓ {nickname}")
        print(f"  用户名: {acc['username']}")
        print(f"  密码: {password}")
        print(f"  user_id: {acc['user_id']}")
        print()

print("="*60)
print("密码设置完成！")
print()
print("登录信息：")
print("  账号1: 测试50级A / 密码: 123456")
print("  账号2: 测试50级B / 密码: 123456")
