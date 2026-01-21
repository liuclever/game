"""
直接测试路由函数，模拟 Flask 请求
"""
import sys
import os
import json
import io

# 设置输出编码为UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 模拟 Flask session
class MockSession:
    def __init__(self, user_id):
        self._user_id = user_id
    
    def get(self, key, default=None):
        if key == 'user_id':
            return self._user_id
        return default

# 模拟 Flask request
class MockRequest:
    def __init__(self):
        self.method = 'GET'

# 模拟 Flask jsonify
def mock_jsonify(data):
    return json.dumps(data, ensure_ascii=False, indent=2)

# 导入路由函数需要的依赖
from interfaces.web_api.app import app
from interfaces.routes.alliance_routes import get_my_alliance

def test_route_function(user_id=20057):
    """直接测试路由函数"""
    print("=" * 80)
    print("直接测试路由函数 get_my_alliance")
    print("=" * 80)
    
    # 使用 Flask 应用上下文
    with app.app_context():
        # 模拟 session
        from flask import session
        session['user_id'] = user_id
        
        # 模拟 session
        import interfaces.routes.alliance_routes as alliance_routes_module
        original_get_current_user_id = alliance_routes_module.get_current_user_id
        
        def mock_get_current_user_id():
            return session.get('user_id', 0)
        
        # 替换函数
        alliance_routes_module.get_current_user_id = mock_get_current_user_id
        
        try:
            # 调用路由函数
            print(f"\n调用路由函数，user_id={user_id}...")
            result = get_my_alliance()
            
            # 解析 JSON 响应
            if hasattr(result, 'data'):
                # Flask Response 对象
                response_data = json.loads(result.data.decode('utf-8'))
            elif isinstance(result, tuple):
                # (response, status_code)
                response_data = json.loads(result[0].data.decode('utf-8'))
            else:
                response_data = result
            
            print("\n[OK] 路由函数执行成功")
            print("\n响应数据:")
            print(json.dumps(response_data, ensure_ascii=False, indent=2))
            
            # 检查 member_info
            if response_data.get('ok') and 'member_info' in response_data:
                member_info = response_data['member_info']
                print("\n" + "=" * 80)
                print("member_info 字段检查:")
                print("=" * 80)
                print(f"  role: {member_info.get('role')}")
                print(f"  contribution: {member_info.get('contribution')}")
                print(f"  total_contribution: {member_info.get('total_contribution', 'NOT_FOUND')}")
                
                if 'total_contribution' in member_info:
                    print("\n[OK] total_contribution 字段存在！")
                    print(f"  值: {member_info['total_contribution']}")
                    return True
                else:
                    print("\n[ERROR] total_contribution 字段不存在！")
                    print(f"  member_info 包含的字段: {list(member_info.keys())}")
                    return False
            else:
                print("\n[ERROR] 响应格式不正确")
                return False
                
        except Exception as e:
            print(f"\n[ERROR] 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # 恢复原函数
            alliance_routes_module.get_current_user_id = original_get_current_user_id

if __name__ == "__main__":
    success = test_route_function(20057)
    if success:
        print("\n" + "=" * 80)
        print("[OK] 所有测试通过！路由函数正确返回 total_contribution 字段")
        print("=" * 80)
        print("\n如果浏览器中仍然看不到 total_contribution，请:")
        print("1. 重启 Flask 服务（停止后重新启动）")
        print("2. 清除浏览器缓存（Ctrl+F5 强制刷新）")
        print("3. 检查浏览器 Network 标签中的实际响应")
    else:
        print("\n" + "=" * 80)
        print("[ERROR] 测试失败！需要检查代码")
        print("=" * 80)
