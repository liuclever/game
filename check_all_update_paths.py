"""检查所有可能更新贡献点的代码路径"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from infrastructure.db.connection import execute_query

def check_all_update_paths():
    """检查所有更新路径"""
    print("=" * 80)
    print("检查所有可能更新贡献点的代码路径")
    print("=" * 80)
    
    # 检查是否有直接更新 total_contribution 的 SQL
    print("\n[检查1] 搜索代码中所有可能更新 total_contribution 的地方")
    
    import os
    import re
    
    code_files = []
    for root, dirs, files in os.walk('.'):
        # 跳过一些目录
        if 'node_modules' in root or '__pycache__' in root or '.git' in root:
            continue
        for file in files:
            if file.endswith(('.py', '.sql')):
                code_files.append(os.path.join(root, file))
    
    suspicious_patterns = [
        (r'UPDATE.*alliance_members.*SET.*total_contribution\s*=', '直接更新 total_contribution'),
        (r'SET.*total_contribution\s*=\s*contribution', '将 total_contribution 设置为 contribution'),
        (r'total_contribution\s*=\s*contribution', 'total_contribution = contribution'),
    ]
    
    found_issues = []
    
    for file_path in code_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    for pattern, description in suspicious_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            # 排除我们自己的修复代码
                            if 'GREATEST' in line or 'protect_total_contribution' in line:
                                continue
                            found_issues.append({
                                'file': file_path,
                                'line': line_num,
                                'pattern': description,
                                'content': line.strip()
                            })
        except Exception as e:
            pass
    
    if found_issues:
        print(f"\n[WARN] 发现 {len(found_issues)} 个可疑的更新:")
        for issue in found_issues[:10]:  # 只显示前10个
            print(f"  {issue['file']}:{issue['line']}")
            print(f"    {issue['pattern']}")
            print(f"    {issue['content'][:80]}")
    else:
        print("[OK] 没有发现可疑的直接更新")
    
    # 检查数据库触发器
    print("\n[检查2] 检查数据库触发器")
    sql = """
        SELECT TRIGGER_NAME, EVENT_MANIPULATION, ACTION_STATEMENT
        FROM information_schema.TRIGGERS
        WHERE TRIGGER_SCHEMA = 'game_tower'
          AND TRIGGER_NAME = 'protect_total_contribution'
    """
    rows = execute_query(sql)
    
    if rows:
        print("[OK] 触发器存在")
        print(f"  事件: {rows[0]['EVENT_MANIPULATION']}")
        statement = rows[0]['ACTION_STATEMENT'] or ''
        if 'NEW.total_contribution < OLD.total_contribution' in statement:
            print("[OK] 触发器包含保护逻辑")
        else:
            print("[WARN] 触发器可能没有正确的保护逻辑")
    else:
        print("[ERROR] 触发器不存在！")
    
    # 检查实际数据
    print("\n[检查3] 检查实际数据")
    sql = """
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN total_contribution < contribution THEN 1 ELSE 0 END) as wrong
        FROM alliance_members
    """
    rows = execute_query(sql)
    if rows:
        stats = rows[0]
        total = stats['total'] or 0
        wrong = stats['wrong'] or 0
        
        print(f"总成员数: {total}")
        print(f"异常数据: {wrong}")
        
        if wrong > 0:
            print("[ERROR] 发现异常数据！")
            # 显示异常数据
            sql = """
                SELECT user_id, contribution, total_contribution
                FROM alliance_members
                WHERE total_contribution < contribution
                LIMIT 5
            """
            wrong_rows = execute_query(sql)
            for row in wrong_rows:
                print(f"  用户 {row['user_id']}: 现有={row['contribution']}, 历史={row.get('total_contribution')}")
        else:
            print("[OK] 所有数据正常")
    
    return len(found_issues) == 0 and wrong == 0

if __name__ == "__main__":
    result = check_all_update_paths()
    print("\n" + "=" * 80)
    if result:
        print("[SUCCESS] 所有检查通过！")
    else:
        print("[WARN] 发现一些问题，请检查")
    print("=" * 80)
