
import pymysql
from pymysql.cursors import DictCursor
import json

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'game_tower',
    'charset': 'utf8mb4',
    'cursorclass': DictCursor,
}

def check_beasts():
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            # Get all beasts
            cursor.execute("SELECT id, name, nickname, template_id, level, nature, physical_attack, physical_attack_aptitude, magic_attack_aptitude, attack_type FROM player_beast")
            rows = cursor.fetchall()
            print(f"{'ID':<5} {'Name':<15} {'Lv':<3} {'Type':<10} {'P-Atk':<6} {'P-Apt':<6} {'M-Apt':<6} {'AtkType':<10}")
            print("-" * 80)
            for row in rows:
                print(f"{row['id']:<5} {row['nickname'] or row['name']:<15} {row['level']:<3} {row['nature']:<10} {row['physical_attack']:<6} {row['physical_attack_aptitude']:<6} {row['magic_attack_aptitude']:<6} {row['attack_type']:<10}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_beasts()
