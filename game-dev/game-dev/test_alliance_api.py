"""
完整测试联盟系统API功能
包括联盟基础功能和盟战功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_alliance_api():
    """测试联盟系统API"""
    print("=" * 60)
    print("测试联盟系统API功能")
    print("=" * 60)
    
    # 创建两个session
    session1 = requests.Session()  # test1
    session2 = requests.Session()  # test2
    
    # 1. 登录test1
    print("\n1. 登录test1账号...")
    login1_res = session1.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "test1", "password": "123456"}
    )
    if login1_res.status_code != 200:
        print(f"[FAIL] test1登录失败: {login1_res.text}")
        return False
    print("[OK] test1登录成功")
    
    # 2. 登录test2
    print("\n2. 登录test2账号...")
    login2_res = session2.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "test2", "password": "123456"}
    )
    if login2_res.status_code != 200:
        print(f"[FAIL] test2登录失败: {login2_res.text}")
        return False
    print("[OK] test2登录成功")
    
    # 3. test1获取我的联盟信息
    print("\n3. test1获取我的联盟信息...")
    my_alliance_res = session1.get(f"{BASE_URL}/api/alliance/my")
    if my_alliance_res.status_code == 200:
        data = my_alliance_res.json()
        if data.get('ok'):
            alliance = data.get('alliance', {})
            print(f"[OK] 联盟名称: {alliance.get('name')}")
            print(f"    联盟等级: {alliance.get('level')}")
            print(f"    联盟资金: {alliance.get('funds')}")
            print(f"    成员数: {data.get('member_count', 0)}")
        else:
            print(f"[WARN] 未加入联盟: {data.get('error')}")
    else:
        print(f"[FAIL] API错误: {my_alliance_res.status_code}")
    
    # 4. test1获取联盟建筑信息
    print("\n4. test1获取联盟建筑信息...")
    buildings_res = session1.get(f"{BASE_URL}/api/alliance/buildings")
    if buildings_res.status_code == 200:
        data = buildings_res.json()
        if data.get('ok'):
            buildings = data.get('buildings', {})
            print(f"[OK] 获取到 {len(buildings)} 个建筑")
            for key, info in buildings.items():
                print(f"    - {key}: {info.get('level', 1)}级")
        else:
            print(f"[WARN] 获取失败: {data.get('error')}")
    
    # 5. test1获取联盟战信息
    print("\n5. test1获取联盟战信息...")
    war_info_res = session1.get(f"{BASE_URL}/api/alliance/war/info")
    if war_info_res.status_code == 200:
        data = war_info_res.json()
        if data.get('ok'):
            war_data = data.get('data', {})
            print(f"[OK] 获取联盟战信息成功")
            if war_data.get('personal'):
                personal = war_data['personal']
                print(f"    个人状态: 已报名={personal.get('signed_up', False)}")
            if war_data.get('statistics'):
                stats = war_data['statistics']
                print(f"    飞龙军: {stats.get('dragon_count', 0)}人")
                print(f"    伏虎军: {stats.get('tiger_count', 0)}人")
        else:
            print(f"[WARN] 获取失败: {data.get('error')}")
    
    # 6. test1报名联盟战
    print("\n6. test1报名联盟战...")
    signup_res = session1.post(f"{BASE_URL}/api/alliance/war/signup")
    if signup_res.status_code == 200:
        data = signup_res.json()
        if data.get('ok'):
            signup_data = data.get('data', {})
            print(f"[OK] 报名成功: {signup_data.get('army_label')}")
        else:
            print(f"[WARN] 报名失败: {data.get('error')}")
    else:
        print(f"[FAIL] API错误: {signup_res.status_code}")
    
    # 7. test1获取联盟兵营信息
    print("\n7. test1获取联盟兵营信息...")
    barracks_res = session1.get(f"{BASE_URL}/api/alliance/barracks")
    if barracks_res.status_code == 200:
        data = barracks_res.json()
        if data.get('ok'):
            barracks_data = data.get('data', {})
            print(f"[OK] 获取兵营信息成功")
            if barracks_data.get('dragon'):
                print(f"    飞龙军: {len(barracks_data['dragon'])}人")
            if barracks_data.get('tiger'):
                print(f"    伏虎军: {len(barracks_data['tiger'])}人")
        else:
            print(f"[WARN] 获取失败: {data.get('error')}")
    
    # 8. test1获取联盟战功状态
    print("\n8. test1获取联盟战功状态...")
    honor_res = session1.get(f"{BASE_URL}/api/alliance/war/honor")
    if honor_res.status_code == 200:
        data = honor_res.json()
        if data.get('ok'):
            honor_data = data.get('data', {})
            print(f"[OK] 当前战功: {honor_data.get('current_honor', 0)}")
            print(f"    历史战功: {honor_data.get('history_honor', 0)}")
            effects = honor_data.get('active_effects', [])
            print(f"    生效效果: {len(effects)}个")
        else:
            print(f"[WARN] 获取失败: {data.get('error')}")
    
    # 9. test1获取联盟战排行榜
    print("\n9. test1获取联盟战排行榜...")
    ranking_res = session1.get(f"{BASE_URL}/api/alliance/war/ranking", params={"page": 1, "size": 10})
    if ranking_res.status_code == 200:
        data = ranking_res.json()
        if data.get('ok'):
            ranking_data = data.get('data', {})
            rankings = ranking_data.get('rankings', [])
            print(f"[OK] 获取到 {len(rankings)} 条排名")
            for i, r in enumerate(rankings[:5], 1):
                print(f"    {i}. {r.get('alliance_name')}: {r.get('score', 0)}分")
        else:
            print(f"[WARN] 获取失败: {data.get('error')}")
    
    # 10. test1获取联盟聊天消息
    print("\n10. test1获取联盟聊天消息...")
    chat_res = session1.get(f"{BASE_URL}/api/alliance/chat/messages")
    if chat_res.status_code == 200:
        data = chat_res.json()
        if data.get('ok'):
            messages = data.get('messages', [])
            print(f"[OK] 获取到 {len(messages)} 条消息")
            for msg in messages[:3]:
                print(f"    {msg.get('sender_name')}: {msg.get('content')[:30]}")
        else:
            print(f"[WARN] 获取失败: {data.get('error')}")
    
    # 11. test1发送联盟聊天消息
    print("\n11. test1发送联盟聊天消息...")
    send_chat_res = session1.post(
        f"{BASE_URL}/api/alliance/chat/send",
        json={"content": "测试联盟聊天消息"}
    )
    if send_chat_res.status_code == 200:
        data = send_chat_res.json()
        if data.get('ok'):
            print("[OK] 发送消息成功")
        else:
            print(f"[WARN] 发送失败: {data.get('error')}")
    
    # 12. test1获取联盟动态
    print("\n12. test1获取联盟动态...")
    activities_res = session1.get(f"{BASE_URL}/api/alliance/activities", params={"limit": 10})
    if activities_res.status_code == 200:
        data = activities_res.json()
        if data.get('ok'):
            activities = data.get('activities', [])
            print(f"[OK] 获取到 {len(activities)} 条动态")
            for act in activities[:3]:
                print(f"    {act.get('event_type')}: {act.get('actor_name')}")
        else:
            print(f"[WARN] 获取失败: {data.get('error')}")
    
    print("\n" + "=" * 60)
    print("[PASS] 联盟系统API测试通过")
    print("=" * 60)
    return True

if __name__ == '__main__':
    try:
        success = test_alliance_api()
        if not success:
            print("\n[FAIL] 测试失败")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("\n[WARN] 无法连接到后端服务 (http://127.0.0.1:5000)")
        print("请确保后端服务已启动")
        sys.exit(1)
    except Exception as e:
        print(f"\n[FAIL] 测试异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
