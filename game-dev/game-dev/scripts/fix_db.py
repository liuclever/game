import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from infrastructure.db.connection import get_connection

def execute_sql_file(file_path):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            with open(file_path, 'r', encoding='utf-8') as f:
                sql = f.read()
                # Split by semicolon and execute each statement
                statements = sql.split(';')
                for statement in statements:
                    if statement.strip():
                        print(f"Executing: {statement[:50]}...")
                        cursor.execute(statement)
            conn.commit()
            print("Successfully executed SQL file.")
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    sql_file = os.path.join('sql', '028_alliance_system.sql')
    execute_sql_file(sql_file)
