"""
战灵功能测试验证脚本
用于创建测试数据并验证战灵系统的各项功能
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

def setup_spirit_test_data(user_id):
    """为指定账号设置战灵测试数据"""
    
    print("=" * 60)
    print("战灵功能测试数据设置")
    print("=" * 60)
    
    # 检查账号是否存在
    print(f"\n[1/5] 检查账号 (user_id={user_id})...")
    player = execute_query("SELECT user_id, username, level FROM player WHERE user_id = %s", (user_id,))
    if not player:
        print(f"❌ 账号不存在，请先创建账号")
        return False
    
    player_info = player[0]
    current_level = player_info.get('level', 1) or 1
    current_level = int(current_level)
    
    print(f"✅ 账号存在: {player_info.get('username')} (等级: {current_level})")
    
    # 确保等级>=35
    if current_level < 35:
        print(f"⚠️  等级不足35级，正在更新到35级...")
        execute_update("UPDATE player SET level = 35 WHERE user_id = %s", (user_id,))
        print(f"✅ 等级已更新到35级")
    
    # 确保有足够的资源
    print(f"\n[2/5] 设置资源...")
    execute_update(
        """UPDATE player SET 
            gold = GREATEST(gold, 1000000),
            yuanbao = GREATEST(yuanbao, 5000)
        WHERE user_id = %s""",
        (user_id,)
    )
    print(f"✅ 资源已设置（铜钱>=100万，元宝>=5000）")
    
    # 添加灵石到背包（每种10个）
    print(f"\n[3/5] 添加灵石到背包...")
    stone_items = {
        7101: "土灵石",
        7102: "火灵石",
        7103: "水灵石",
        7104: "木灵石",
        7105: "金灵石",
        7106: "神灵石",
    }
    
    for item_id, name in stone_items.items():
        # 检查是否已有
        existing = execute_query(
            "SELECT quantity FROM player_inventory WHERE user_id = %s AND item_id = %s",
            (user_id, item_id)
        )
        if existing:
            current_qty = existing[0].get('quantity', 0) or 0
            if current_qty < 10:
                execute_update(
                    "UPDATE player_inventory SET quantity = 10 WHERE user_id = %s AND item_id = %s",
                    (user_id, item_id)
                )
                print(f"  ✅ {name}: 已更新到10个")
        else:
            execute_update(
                "INSERT INTO player_inventory (user_id, item_id, quantity, is_temporary) VALUES (%s, %s, 10, 0)",
                (user_id, item_id)
            )
            print(f"  ✅ {name}: 已添加10个")
    
    # 添加战灵钥匙和灵力水晶
    print(f"\n[4/5] 添加战灵钥匙和灵力水晶...")
    key_items = {
        6006: "战灵钥匙",
        6101: "灵力水晶",
    }
    
    for item_id, name in key_items.items():
        existing = execute_query(
            "SELECT quantity FROM player_inventory WHERE user_id = %s AND item_id = %s",
            (user_id, item_id)
        )
        if existing:
            current_qty = existing[0].get('quantity', 0) or 0
            if current_qty < 100:
                execute_update(
                    "UPDATE player_inventory SET quantity = 100 WHERE user_id = %s AND item_id = %s",
                    (user_id, item_id)
                )
                print(f"  ✅ {name}: 已更新到100个")
        else:
            execute_update(
                "INSERT INTO player_inventory (user_id, item_id, quantity, is_temporary) VALUES (%s, %s, 100, 0)",
                (user_id, item_id)
            )
            print(f"  ✅ {name}: 已添加100个")
    
    # 解锁所有元素（如果战灵账户存在）
    print(f"\n[5/6] 解锁元素孔位...")
    account = execute_query(
        "SELECT * FROM spirit_account WHERE user_id = %s",
        (user_id,)
    )
    
    if account:
        execute_update(
            """UPDATE spirit_account SET 
                unlocked_elements = '["earth","fire","water","wood","metal","god"]'
            WHERE user_id = %s""",
            (user_id,)
        )
        print(f"  ✅ 已解锁所有元素孔位")
    else:
        # 创建战灵账户
        execute_update(
            """INSERT INTO spirit_account (user_id, spirit_power, unlocked_elements)
            VALUES (%s, 0, '["earth","fire","water","wood","metal","god"]')""",
            (user_id,)
        )
        print(f"  ✅ 已创建战灵账户并解锁所有元素")
    
    # 检查是否有幻兽
    print(f"\n[6/6] 检查幻兽...")
    beasts = execute_query(
        "SELECT id, name FROM player_beast WHERE user_id = %s LIMIT 1",
        (user_id,)
    )
    
    if beasts:
        beast_info = beasts[0]
        print(f"  ✅ 账号已有幻兽: {beast_info.get('name')} (ID: {beast_info.get('id')})")
    else:
        print(f"  ⚠️  账号暂无幻兽")
        print(f"  💡 提示：可以通过以下方式获取幻兽：")
        print(f"     1. 使用API: POST /api/beast/obtain (见测试指南)")
        print(f"     2. 在游戏中通过召唤球或其他方式获得")
    
    print("\n" + "=" * 60)
    print("✅ 测试数据设置完成！")
    print("=" * 60)
    
    print("\n📝 测试步骤：")
    print("  1. 登录游戏，进入【背包】")
    print("  2. 找到【土灵石】等灵石，点击【打开】按钮")
    print("  3. 开启灵石后会获得战灵，战灵会存入【灵件室】")
    print("  4. 进入【战灵】页面")
    if not beasts:
        print("  5. 确保账号中有一只幻兽（如果没有，可通过API或游戏内获取）")
        print("  6. 选择一只幻兽")
        print("  7. 点击元素槽位（如【土位】），选择战灵进行装备")
    else:
        print("  5. 选择一只幻兽")
        print("  6. 点击元素槽位（如【土位】），选择战灵进行装备")
    print("  7. 装备后可以查看战灵详情，解锁词条，洗练等")
    print("\n💡 提示：")
    print("  - 背包中已有每种灵石10个")
    print("  - 已有战灵钥匙100个（用于解锁词条）")
    print("  - 已有灵力水晶100个（用于获得灵力）")
    print("  - 所有元素孔位已解锁")
    if not beasts:
        print("  - ⚠️  需要先获取一只幻兽才能测试装备功能")
    print()
    
    return True

def main():
    print("\n" + "=" * 60)
    print("  战灵功能测试验证工具")
    print("=" * 60 + "\n")
    
    # 获取用户ID
    user_id_input = input("请输入要测试的账号ID（直接回车使用99999）: ").strip()
    if user_id_input:
        try:
            user_id = int(user_id_input)
        except ValueError:
            print("❌ 无效的用户ID")
            return
    else:
        user_id = 99999
    
    try:
        success = setup_spirit_test_data(user_id)
        if success:
            print(f"\n✅ 可以使用账号ID {user_id} 进行测试了！")
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
    except Exception as e:
        print(f"\n\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n按任意键退出...")
    input()

if __name__ == '__main__':
    main()
