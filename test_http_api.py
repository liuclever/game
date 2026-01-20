"""通过HTTP请求测试API"""
import requests
import json

def test_http_api():
    """通过HTTP请求测试API"""
    print("=" * 80)
    print("通过HTTP请求测试 /api/alliance/my API")
    print("=" * 80)
    
    # 使用session来保持cookie
    session = requests.Session()
    
    # 首先登录（如果需要）
    # 这里假设你已经登录了，直接使用cookie
    # 或者你需要先登录获取session
    
    url = "http://localhost:5000/api/alliance/my"
    
    # 从你之前提供的cookie中提取session
    cookies = {
        'session': 'eyJuaWNrbmFtZSI6IjEyMzQ1NiIsInVzZXJfaWQiOjIwMDU3fQ.aW8dSw.yk5ioKnAzrlyt_saggu8XYgzcBg'
    }
    
    print(f"\n[发送HTTP请求]")
    print(f"  URL: {url}")
    
    try:
        response = session.get(url, cookies=cookies)
        
        print(f"\n[HTTP响应]")
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n[响应JSON]")
            print(json.dumps(data, ensure_ascii=False, indent=2))
            
            # 检查member_info
            if 'member_info' in data:
                member_info = data['member_info']
                print(f"\n[member_info检查]")
                print(f"  可用字段: {list(member_info.keys())}")
                print(f"  role: {member_info.get('role')}")
                print(f"  contribution: {member_info.get('contribution')}")
                print(f"  total_contribution: {member_info.get('total_contribution', '字段不存在')}")
                
                if 'total_contribution' in member_info:
                    print(f"\n  ✅ total_contribution 字段存在！")
                    print(f"  值: {member_info['total_contribution']}")
                    print(f"  前端应显示: {member_info['contribution']}/{member_info['total_contribution']}")
                else:
                    print(f"\n  ❌ total_contribution 字段不存在！")
                    print(f"  这是问题所在！")
            else:
                print(f"\n  ❌ member_info 不存在！")
        else:
            print(f"\n[ERROR] HTTP错误: {response.status_code}")
            print(f"  响应内容: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"\n[ERROR] 无法连接到服务器")
        print(f"  请确保Flask服务正在运行在 http://localhost:5000")
    except Exception as e:
        print(f"\n[ERROR] 请求失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_http_api()
    print("\n" + "=" * 80)
