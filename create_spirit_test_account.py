"""
创建或更新一个35级以上的测试账号，用于测试战灵功能
"""
import sys
from pathlib import Path

# 将项目根目录添加到 sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

print("正在导入模块...")
try:
    from infrastructure.db.connection import execute_query, execute_update
    print("✅ 数据库连接模块导入成功")
except Exception as e:
    print(f"❌ 导入数据库模块失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

def create_or_update_spirit_test_account():
    """创建或更新一个35级以上的测试账号"""
    
    print("=" * 60)
    print("创建/更新战灵测试账号")
    print("=" * 60)
    
    # 测试账号信息
    TEST_USER_ID = 99999
    TEST_USERNAME = "test_spirit"
    TEST_NICKNAME = "战灵测试号"
    TEST_PASSWORD = "test123"
    TEST_LEVEL = 35
    
    # 测试数据库连接
    print("\n[1/3] 测试数据库连接...")
    try:
        result = execute_query("SELECT 1 as test")
        print("✅ 数据库连接正常")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 检查账号是否存在
    print("\n[2/3] 检查账号是否存在...")
    existing = execute_query(
        "SELECT user_id, username, level FROM player WHERE user_id = %s OR username = %s",
        (TEST_USER_ID, TEST_USERNAME)
    )
    
    if existing:
        # 账号已存在，更新等级
        existing_user = existing[0]
        current_level = existing_user.get('level', 1) or 1
        current_level = int(current_level)
        
        if current_level >= TEST_LEVEL:
            print(f"✅ 账号已存在: {existing_user.get('username')} (ID: {existing_user.get('user_id')})")
            print(f"   当前等级: {current_level}级 (已达到35级要求)")
            print(f"\n📝 账号信息:")
            print(f"   用户名: {existing_user.get('username')}")
            print(f"   用户ID: {existing_user.get('user_id')}")
            print(f"   等级: {current_level}级")
            print(f"\n✅ 可以使用此账号测试战灵功能！")
        else:
            print(f"⚠️  账号已存在: {existing_user.get('username')} (ID: {existing_user.get('user_id')})")
            print(f"   当前等级: {current_level}级")
            print(f"   正在更新等级到 {TEST_LEVEL}级...")
            
            execute_update(
                "UPDATE player SET level = %s WHERE user_id = %s",
                (TEST_LEVEL, existing_user.get('user_id'))
            )
            
            print(f"✅ 等级已更新到 {TEST_LEVEL}级")
            print(f"\n📝 账号信息:")
            print(f"   用户名: {existing_user.get('username')}")
            print(f"   用户ID: {existing_user.get('user_id')}")
            print(f"   等级: {TEST_LEVEL}级")
            print(f"\n✅ 可以使用此账号测试战灵功能！")
    else:
        # 账号不存在，创建新账号
        print(f"📝 账号不存在，正在创建新账号...")
        
        try:
            # 创建玩家账号（35级）
            execute_update(
                """INSERT INTO player (
                    user_id, username, nickname, password, level, 
                    exp, gold, yuanbao, energy, prestige, 
                    enhancement_stone, vip_level, crystal_tower,
                    created_at
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    0, 1000000, 10000, 190, 0,
                    10000, 0, 0,
                    NOW()
                )""",
                (TEST_USER_ID, TEST_USERNAME, TEST_NICKNAME, TEST_PASSWORD, TEST_LEVEL)
            )
            
            print(f"✅ 账号创建成功！")
            print(f"\n📝 账号信息:")
            print(f"   用户名: {TEST_USERNAME}")
            print(f"   密码: {TEST_PASSWORD}")
            print(f"   用户ID: {TEST_USER_ID}")
            print(f"   等级: {TEST_LEVEL}级")
            print(f"   铜钱: 1,000,000")
            print(f"   元宝: 10,000")
            print(f"   强化石: 10,000")
            print(f"\n✅ 可以使用此账号测试战灵功能！")
            
        except Exception as e:
            print(f"❌ 创建账号失败: {e}")
            import traceback
            traceback.print_exc()
            return
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)
    print("\n💡 提示:")
    print("  1. 使用用户名和密码登录游戏")
    print("  2. 战灵功能需要35级才能解锁")
    print("  3. 如果遇到问题，可以运行此脚本更新账号等级")
    print()

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  创建/更新战灵测试账号工具")
    print("=" * 60 + "\n")
    
    try:
        create_or_update_spirit_test_account()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
    except Exception as e:
        print(f"\n\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n按任意键退出...")
    input()
