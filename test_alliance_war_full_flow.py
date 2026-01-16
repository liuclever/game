#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
完整测试盟战流程
1. 设置测试环境（分配战灵、签到）
2. 执行对战
3. 验证最终结果
"""
import sys
import os
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 设置输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from interfaces.web_api.bootstrap import services
from domain.entities.alliance_registration import STATUS_REGISTERED, STATUS_CONFIRMED, STATUS_CANCELLED
from infrastructure.db.connection import execute_query, execute_update

def main():
    """测试完整的盟战流程"""
    land_id = 1
    
    print("="*60)
    print("盟战完整流程测试")
    print("="*60)
    
    # 1. 运行设置脚本
    print("\n步骤1: 设置测试环境...")
    import subprocess
    result = subprocess.run(
        [sys.executable, "setup_alliance_war_test.py", str(land_id), "setup_only"],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    if result.returncode != 0:
        print("设置失败:")
        print(result.stderr)
        return False
    
    # 2. 执行对战
    print("\n步骤2: 执行对战...")
    from interfaces.routes.alliance_routes import run_land_battle
    from flask import Flask, request
    from unittest.mock import patch
    
    app = Flask(__name__)
    with app.test_request_context(f'/api/alliance/war/run-battle/{land_id}', 
                                  method='POST',
                                  json={'test_mode': True}):
        with patch('interfaces.routes.alliance_routes.get_current_user_id', return_value=1):
            from interfaces.routes import alliance_routes as routes_module
            routes_module.get_current_user_id = lambda: 1
            
            response = run_land_battle(land_id)
            
            if hasattr(response, 'get_json'):
                result = response.get_json()
            else:
                result = response[0].get_json() if response else {}
            
            if result.get('ok'):
                print(f"\n[成功] {result.get('message')}")
                occupation = result.get('occupation', {})
                if occupation:
                    print(f"  联盟 {occupation.get('alliance_id')} 占领了土地 {land_id}")
                return True
            else:
                print(f"\n[失败] {result.get('error')}")
                return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
