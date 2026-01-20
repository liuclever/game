"""检查Flask是否重新加载了代码"""
import requests
import json
import time

def check_api():
    """检查API响应"""
    url = "http://localhost:5000/api/alliance/my"
    cookies = {
        'session': 'eyJuaWNrbmFtZSI6IjEyMzQ1NiIsInVzZXJfaWQiOjIwMDU3fQ.aW8dSw.yk5ioKnAzrlyt_saggu8XYgzcBg'
    }
    
    try:
        response = requests.get(url, cookies=cookies, timeout=5)
        if response.status_code == 200:
            data = response.json()
            member_info = data.get('member_info', {})
            
            print("API响应中的member_info字段:")
            print(f"  可用字段: {list(member_info.keys())}")
            
            if '_debug_version' in member_info:
                print(f"  ✅ 看到_debug_version字段！说明代码已重新加载")
                print(f"  版本: {member_info['_debug_version']}")
            else:
                print(f"  ❌ 没有_debug_version字段！说明代码没有重新加载")
            
            if 'total_contribution' in member_info:
                print(f"  ✅ total_contribution字段存在！")
                print(f"  值: {member_info['total_contribution']}")
            else:
                print(f"  ❌ total_contribution字段不存在！")
            
            return member_info
        else:
            print(f"HTTP错误: {response.status_code}")
            return None
    except Exception as e:
        print(f"请求失败: {e}")
        return None

if __name__ == "__main__":
    print("=" * 80)
    print("检查Flask是否重新加载了代码")
    print("=" * 80)
    print("\n请确保:")
    print("1. Flask服务正在运行")
    print("2. 已保存 interfaces/routes/alliance_routes.py 文件")
    print("3. Flask应该检测到文件变化并自动重载")
    print("\n等待3秒后测试...")
    time.sleep(3)
    
    member_info = check_api()
    
    if member_info:
        print("\n" + "=" * 80)
        if '_debug_version' not in member_info:
            print("结论: Flask没有重新加载代码！")
            print("\n解决方案:")
            print("1. 完全停止Flask服务（Ctrl+C）")
            print("2. 重新启动: python -m interfaces.web_api.app")
            print("3. 等待服务完全启动后再测试")
        else:
            print("结论: Flask已重新加载代码！")
    print("=" * 80)
