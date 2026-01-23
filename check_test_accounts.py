"""查询测试账号信息"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.db.connection import execute_query

# 查询测试账号信息
accounts = execute_query('''
    SELECT user_id, username, nickname, password, level, gold, yuanbao, energy
    FROM player 
    WHERE nickname IN ('测试50级A', '测试50级B')
    ORDER BY user_id
''')

if accounts:
    print('找到的测试账号：')
    print('='*80)
    for acc in accounts:
        password = acc.get("password", "") or "(未设置)"
        print(f'昵称: {acc["nickname"]}')
        print(f'用户名: {acc["username"]}')
        print(f'密码: {password}')
        print(f'user_id: {acc["user_id"]}')
        print(f'等级: {acc["level"]}')
        print(f'铜钱: {acc["gold"]:,}')
        print(f'元宝: {acc["yuanbao"]:,}')
        print(f'活力: {acc["energy"]}')
        print('-'*80)
else:
    print('未找到测试账号，可能还未创建')
    print('请先运行: python create_level_50_test_accounts.py')
