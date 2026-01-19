"""执行数据库迁移脚本"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from infrastructure.db.connection import get_connection

def run_sql_file(file_path):
    """执行SQL文件"""
    print(f"执行迁移脚本: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"[ERROR] 文件不存在: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # 分割SQL语句（按分号分割，但要注意存储过程等）
    statements = []
    current_statement = ""
    
    for line in sql_content.split('\n'):
        line = line.strip()
        if not line or line.startswith('--'):
            continue
        
        current_statement += line + '\n'
        
        if line.endswith(';'):
            statements.append(current_statement.strip())
            current_statement = ""
    
    if current_statement.strip():
        statements.append(current_statement.strip())
    
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            for i, statement in enumerate(statements, 1):
                if not statement:
                    continue
                try:
                    print(f"  执行语句 {i}/{len(statements)}...")
                    cursor.execute(statement)
                except Exception as e:
                    # 如果是字段已存在的错误，可以忽略
                    if 'Duplicate column name' in str(e) or 'already exists' in str(e).lower():
                        print(f"  [SKIP] 字段已存在，跳过: {str(e)[:50]}")
                    else:
                        print(f"  [ERROR] 执行失败: {str(e)[:100]}")
                        raise
            
            conn.commit()
            print(f"[SUCCESS] 迁移完成！")
            return True
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 迁移失败: {str(e)}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    migration_file = "sql/042_add_total_contribution_to_alliance_members.sql"
    if len(sys.argv) > 1:
        migration_file = sys.argv[1]
    
    run_sql_file(migration_file)
