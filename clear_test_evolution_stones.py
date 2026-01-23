#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清空测试账号的进化石
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.db.connection import execute_update

def main():
    user_id = 100006
    
    print("清空测试账号的进化石...")
    
    # 删除所有进化石
    execute_update(
        "DELETE FROM player_inventory WHERE user_id = %s AND item_id BETWEEN 3001 AND 3007",
        (user_id,)
    )
    
    print("✅ 已清空")

if __name__ == '__main__':
    main()
