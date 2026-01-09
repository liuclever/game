import pymysql
from infrastructure.db.connection import DB_CONFIG

try:
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cursor:
        # Check if columns exist
        cursor.execute("SHOW COLUMNS FROM players LIKE 'cultivation_start_time'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE players ADD COLUMN cultivation_start_time DATETIME DEFAULT NULL")
            print("Added cultivation_start_time")
        
        cursor.execute("SHOW COLUMNS FROM players LIKE 'cultivation_area'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE players ADD COLUMN cultivation_area VARCHAR(50) DEFAULT NULL")
            print("Added cultivation_area")
            
        cursor.execute("SHOW COLUMNS FROM players LIKE 'cultivation_dungeon'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE players ADD COLUMN cultivation_dungeon VARCHAR(50) DEFAULT NULL")
            print("Added cultivation_dungeon")
            
    conn.commit()
    conn.close()
    print("Success")
except Exception as e:
    print(f"Error: {e}")
