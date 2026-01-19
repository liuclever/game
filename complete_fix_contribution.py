"""完整修复历史总贡献点功能"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from infrastructure.db.connection import execute_query, execute_update, get_connection

def ensure_trigger():
    """确保触发器存在"""
    print("=" * 80)
    print("步骤1: 确保数据库触发器存在")
    print("=" * 80)
    
    sql = """
        SELECT TRIGGER_NAME
        FROM information_schema.TRIGGERS
        WHERE TRIGGER_SCHEMA = 'game_tower'
          AND TRIGGER_NAME = 'protect_total_contribution'
    """
    rows = execute_query(sql)
    
    if not rows:
        print("[ERROR] 触发器不存在，正在创建...")
        from create_trigger import create_trigger
        if not create_trigger():
            print("[ERROR] 创建触发器失败！")
            return False
    else:
        print("[OK] 触发器已存在")
    
    return True

def fix_all_data():
    """修复所有数据"""
    print("\n" + "=" * 80)
    print("步骤2: 修复所有数据")
    print("=" * 80)
    
    # 确保 total_contribution 至少等于 contribution
    sql = """
        UPDATE alliance_members
        SET total_contribution = GREATEST(COALESCE(total_contribution, 0), contribution)
        WHERE total_contribution IS NULL OR total_contribution < contribution
    """
    
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            affected = cursor.rowcount
            conn.commit()
            print(f"[OK] 修复了 {affected} 条记录")
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 修复失败: {str(e)}")
        return False
    finally:
        conn.close()
    
    return True

def verify_fix():
    """验证修复结果"""
    print("\n" + "=" * 80)
    print("步骤3: 验证修复结果")
    print("=" * 80)
    
    sql = """
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN total_contribution > contribution THEN 1 ELSE 0 END) as correct,
            SUM(CASE WHEN total_contribution = contribution THEN 1 ELSE 0 END) as equal,
            SUM(CASE WHEN total_contribution < contribution THEN 1 ELSE 0 END) as wrong
        FROM alliance_members
    """
    
    rows = execute_query(sql)
    if rows:
        stats = rows[0]
        total = stats['total'] or 0
        correct = stats['correct'] or 0
        equal = stats['equal'] or 0
        wrong = stats['wrong'] or 0
        
        print(f"总成员数: {total}")
        print(f"  历史总贡献点 > 现有贡献点: {correct} (正常，消耗过贡献点)")
        print(f"  历史总贡献点 = 现有贡献点: {equal} (可能未消耗过)")
        print(f"  历史总贡献点 < 现有贡献点: {wrong} (异常)")
        
        if wrong > 0:
            print(f"\n[ERROR] 仍有 {wrong} 条异常数据！")
            return False
        else:
            print(f"\n[OK] 所有数据正常")
            return True
    
    return False

def test_update_logic():
    """测试更新逻辑"""
    print("\n" + "=" * 80)
    print("步骤4: 测试更新逻辑")
    print("=" * 80)
    
    from infrastructure.db.alliance_repo_mysql import MySQLAllianceRepo
    
    # 找一个测试用户
    sql = """
        SELECT am.user_id, am.contribution, am.total_contribution
        FROM alliance_members am
        WHERE am.contribution >= 10
        LIMIT 1
    """
    rows = execute_query(sql)
    if not rows:
        print("[ERROR] 未找到测试用户")
        return False
    
    user_id = rows[0]['user_id']
    before_contribution = rows[0]['contribution'] or 0
    before_total = rows[0].get('total_contribution') or 0
    
    print(f"测试用户 ID: {user_id}")
    print(f"初始: 现有贡献点={before_contribution}, 历史总贡献点={before_total}")
    
    repo = MySQLAllianceRepo()
    
    # 测试减少
    print(f"\n测试减少 5 点贡献...")
    repo.update_member_contribution(user_id, -5)
    
    rows_after = execute_query("SELECT contribution, total_contribution FROM alliance_members WHERE user_id = %s", (user_id,))
    after_contribution = rows_after[0]['contribution'] or 0
    after_total = rows_after[0].get('total_contribution') or 0
    
    print(f"结果: 现有贡献点={after_contribution}, 历史总贡献点={after_total}")
    
    if after_total != before_total:
        print(f"[ERROR] 历史总贡献点被减少了！")
        return False
    else:
        print(f"[OK] 历史总贡献点保持不变")
    
    # 恢复数据
    repo.update_member_contribution(user_id, 5)
    
    return True

def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("历史总贡献点功能完整修复")
    print("=" * 80)
    
    results = []
    
    # 步骤1: 确保触发器存在
    results.append(("触发器检查", ensure_trigger()))
    
    # 步骤2: 修复数据
    results.append(("数据修复", fix_all_data()))
    
    # 步骤3: 验证修复
    results.append(("数据验证", verify_fix()))
    
    # 步骤4: 测试更新逻辑
    results.append(("更新逻辑测试", test_update_logic()))
    
    # 汇总
    print("\n" + "=" * 80)
    print("修复结果汇总")
    print("=" * 80)
    
    all_passed = True
    for step_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{step_name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 80)
    if all_passed:
        print("[SUCCESS] 所有步骤完成！历史总贡献点功能已完全修复！")
        print("\n现在:")
        print("1. 数据库触发器会保护历史总贡献点不被减少")
        print("2. 代码逻辑确保只增不减")
        print("3. 所有数据已修复")
        print("\n请测试实际使用情况，如果还有问题，请提供具体操作步骤。")
    else:
        print("[FAILED] 部分步骤失败，请检查错误信息")
    print("=" * 80)

if __name__ == "__main__":
    main()
