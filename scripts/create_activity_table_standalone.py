import pymysql

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '12345',
    'database': 'game_tower',
    'charset': 'utf8mb4',
}

def run_sql():
    sql = """
    CREATE TABLE IF NOT EXISTS player_daily_activity (
        user_id INT PRIMARY KEY,
        activity_value INT DEFAULT 0,
        last_updated_date DATE,
        completed_tasks JSON
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            conn.commit()
            print("Table created successfully")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run_sql()
