import pymysql
import sys

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '12345',
    'database': 'game_tower',
    'charset': 'utf8mb4',
}

def run_sql(sql):
    try:
        conn = pymysql.connect(**DB_CONFIG)
        with conn.cursor() as cursor:
            cursor.execute(sql)
            if sql.strip().upper().startswith('SELECT') or sql.strip().upper().startswith('SHOW'):
                return cursor.fetchall()
            conn.commit()
            return cursor.rowcount
    except Exception as e:
        return str(e)
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(run_sql(sys.argv[1]))
