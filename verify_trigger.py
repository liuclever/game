"""验证数据库触发器是否生效"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from infrastructure.db.connection import execute_query, execute_update, get_connection

def check_trigger():
    """检查触发器是否存在"""
    print("检查数据库触发器...")
    
    sql = """
        SELECT TRIGGER_NAME, EVENT_MANIPULATION, EVENT_OBJECT_TABLE, ACTION_STATEMENT
        FROM information_schema.TRIGGERS
        WHERE TRIGGER_SCHEMA = 'game_tower'
          AND TRIGGER_NAME = 'protect_total_contribution'
    """
    rows = execute_query(sql)
    
    if not rows:
        print("[ERROR] 触发器不存在！")
        print("请运行: python create_trigger.py")
        return False
    
    trigger = rows[0]
    print(f"[OK] 触发器存在: {trigger['TRIGGER_NAME']}")
    print(f"  事件: {trigger['EVENT_MANIPULATION']}")
    print(f"  表: {trigger['EVENT_OBJECT_TABLE']}")
    return True

def test_trigger_protection():
    """测试触发器保护功能"""
    print("\n测试触发器保护功能...")
    
    # 找一个测试用户
    sql = """
        SELECT am.user_id, am.contribution, am.total_contribution
        FROM alliance_members am
        WHERE am.contribution >= 5
        LIMIT 1
    """
    rows = execute_query(sql)
    if not rows:
        print("[ERROR] 未找到测试用户")
        return False
    
    user = rows[0]
    user_id = user['user_id']
    before_contribution = user['contribution'] or 0
    before_total = user.get('total_contribution') or 0
    
    print(f"\n测试用户 ID: {user_id}")
    print(f"初始状态: 现有贡献点={before_contribution}, 历史总贡献点={before_total}")
    
    # 尝试直接更新 total_contribution 为更小的值（触发器应该阻止）
    print(f"\n尝试将历史总贡献点减少到 {before_total - 10}...")
    
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # 尝试减少 total_contribution
            sql = """
                UPDATE alliance_members 
                SET total_contribution = %s
                WHERE user_id = %s
            """
            cursor.execute(sql, (before_total - 10, user_id))
            conn.commit()
            
            # 检查结果
            check_sql = """
                SELECT contribution, total_contribution
                FROM alliance_members
                WHERE user_id = %s
            """
            cursor.execute(check_sql, (user_id,))
            result = cursor.fetchone()
            
            after_total = result.get('total_contribution') or 0
            
            print(f"  更新后: 历史总贡献点={after_total}")
            
            if after_total == before_total - 10:
                print(f"  [ERROR] 触发器没有生效！历史总贡献点被减少了！")
                # 恢复数据
                cursor.execute("UPDATE alliance_members SET total_contribution = %s WHERE user_id = %s", 
                             (before_total, user_id))
                conn.commit()
                return False
            elif after_total == before_total:
                print(f"  [OK] 触发器生效！历史总贡献点没有被减少")
                return True
            else:
                print(f"  [WARN] 历史总贡献点变成了 {after_total}，可能是触发器修改了值")
                return True
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 测试失败: {str(e)}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 80)
    print("验证数据库触发器")
    print("=" * 80)
    
    if not check_trigger():
        exit(1)
    
    if test_trigger_protection():
        print("\n" + "=" * 80)
        print("[SUCCESS] 触发器正常工作！")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("[FAILED] 触发器没有正常工作！")
        print("=" * 80)
