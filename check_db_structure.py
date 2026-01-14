"""检查数据库结构"""
from infrastructure.db.connection import get_connection

def check_table_structure(table_name):
    """检查表结构"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f'DESCRIBE {table_name}')
            cols = cursor.fetchall()
            print(f"\n=== {table_name} 表结构 ===")
            for col in cols:
                print(f"{col['Field']:30} {col['Type']:20} NULL:{col['Null']:3} KEY:{col['Key']:3} DEFAULT:{col['Default']}")
    finally:
        conn.close()

# 检查关键表
tables = ['player', 'arena', 'arena_battle_log', 'arena_daily_challenge', 
          'player_daily_activity', 'world_chat_message']

for table in tables:
    try:
        check_table_structure(table)
    except Exception as e:
        print(f"检查 {table} 失败: {e}")
