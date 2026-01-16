"""
删除测试账号脚本
删除所有 test_lv50_* 开头的测试账号及其相关数据
"""
import sys
from pathlib import Path

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

def delete_test_accounts():
    """删除所有测试账号"""
    
    print("\n" + "=" * 60)
    print("  删除测试账号工具")
    print("=" * 60)
    
    # 测试数据库连接
    print("\n[1/4] 测试数据库连接...")
    try:
        result = execute_query("SELECT 1 as test")
        print("✅ 数据库连接正常")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 查询要删除的账号
    print("\n[2/4] 查询测试账号...")
    try:
        test_accounts = execute_query(
            "SELECT user_id, username, nickname FROM player WHERE username LIKE 'test_lv50_%'"
        )
        
        if not test_accounts:
            print("⚠️  没有找到测试账号")
            return
        
        print(f"✅ 找到 {len(test_accounts)} 个测试账号:")
        for acc in test_accounts:
            print(f"   - {acc['username']} (ID: {acc['user_id']}, 昵称: {acc['nickname']})")
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 确认删除
    print(f"\n⚠️  警告：即将删除 {len(test_accounts)} 个测试账号及其所有相关数据！")
    print("   包括：玩家信息、幻兽、背包物品等")
    confirm = input("\n确认删除？(输入 yes 确认): ")
    
    if confirm.lower() != 'yes':
        print("\n❌ 已取消删除操作")
        return
    
    # 开始删除
    print(f"\n[3/4] 开始删除测试账号...")
    
    deleted_count = 0
    user_ids = [acc['user_id'] for acc in test_accounts]
    
    try:
        # 删除相关数据
        tables_to_clean = [
            ('player_beast', '幻兽'),
            ('player_inventory', '背包物品'),
            ('player_bag', '背包信息'),
            ('player_spirit', '战灵'),
            ('player_mosoul', '魔魂'),
            ('player_effect', '效果'),
            ('player_dungeon_progress', '副本进度'),
            ('player_daily_activity', '每日活动'),
            ('player_gift_claim', '礼包领取'),
            ('player_immortalize_pool', '化仙池'),
            ('player_manor', '庄园'),
            ('player_month_card', '月卡'),
            ('player_talent_levels', '天赋'),
            ('arena_streak', '连胜竞技场记录'),
        ]
        
        print("\n   删除关联数据:")
        for table, desc in tables_to_clean:
            try:
                # 构建 IN 子句
                placeholders = ','.join(['%s'] * len(user_ids))
                sql = f"DELETE FROM {table} WHERE user_id IN ({placeholders})"
                affected = execute_update(sql, tuple(user_ids))
                if affected > 0:
                    print(f"   ✅ {desc}: 删除 {affected} 条记录")
            except Exception as e:
                # 某些表可能不存在或没有数据，忽略错误
                if "doesn't exist" not in str(e) and "Unknown column" not in str(e):
                    print(f"   ⚠️  {desc}: {e}")
        
        # 最后删除玩家主表
        print("\n   删除玩家账号:")
        placeholders = ','.join(['%s'] * len(user_ids))
        sql = f"DELETE FROM player WHERE user_id IN ({placeholders})"
        affected = execute_update(sql, tuple(user_ids))
        deleted_count = affected
        print(f"   ✅ 玩家账号: 删除 {affected} 个")
        
    except Exception as e:
        print(f"\n❌ 删除失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 60)
    print(f"[4/4] 完成！成功删除 {deleted_count} 个测试账号")
    print("=" * 60)
    print()

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  删除测试账号工具")
    print("=" * 60 + "\n")
    
    try:
        delete_test_accounts()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
    except Exception as e:
        print(f"\n\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n按任意键退出...")
    input()
