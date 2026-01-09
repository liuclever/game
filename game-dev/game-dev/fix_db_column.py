import sys
sys.path.append('.')
from infrastructure.db.connection import get_connection

def check_and_fix():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Check player_beast
            try:
                cursor.execute("DESCRIBE player_beast")
                columns = [row['Field'] for row in cursor.fetchall()]
                print(f"player_beast columns: {columns}")
                if 'template_id' not in columns:
                    print("Adding template_id to player_beast...")
                    cursor.execute("ALTER TABLE player_beast ADD COLUMN template_id INT NOT NULL DEFAULT 0 AFTER user_id")
                    print("Added template_id to player_beast")
            except Exception as e:
                print(f"Error checking player_beast: {e}")

            # Check user_beast
            try:
                cursor.execute("DESCRIBE user_beast")
                columns = [row['Field'] for row in cursor.fetchall()]
                print(f"user_beast columns: {columns}")
                if 'template_id' not in columns:
                    print("Adding template_id to user_beast...")
                    cursor.execute("ALTER TABLE user_beast ADD COLUMN template_id INT NOT NULL DEFAULT 0 AFTER user_id")
                    print("Added template_id to user_beast")
            except Exception as e:
                print(f"Error checking user_beast: {e}")
        conn.commit()
    finally:
        conn.close()

if __name__ == "__main__":
    check_and_fix()
