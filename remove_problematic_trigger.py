"""删除可能有问题的触发器，让代码逻辑直接生效"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from infrastructure.db.connection import get_connection

def remove_trigger():
    """删除触发器"""
    print("删除可能有问题的触发器...")
    
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # 删除触发器
            cursor.execute("DROP TRIGGER IF EXISTS protect_total_contribution")
            conn.commit()
            print("[SUCCESS] 触发器已删除")
            print("现在代码逻辑会直接生效：")
            print("  - 增加贡献点时：contribution 和 total_contribution 都增加")
            print("  - 减少贡献点时：只减少 contribution，total_contribution 保持不变")
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 删除触发器失败: {str(e)}")
        return False
    finally:
        conn.close()
    
    return True

if __name__ == "__main__":
    remove_trigger()
