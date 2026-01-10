
import pymysql
import sys
import os

# Add parent directory to sys.path to import from infrastructure
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.db.connection import DB_CONFIG

def fix_db():
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            # Check columns in player_dungeon_progress
            cursor.execute("DESCRIBE player_dungeon_progress")
            columns = [row['Field'] for row in cursor.fetchall()]
            
            print(f"Current columns in player_dungeon_progress: {columns}")
            
            # Columns to add
            to_add = {
                'total_floors': "INT DEFAULT 35",
                'floor_event_type': "VARCHAR(50) DEFAULT 'beast'",
                'resets_today': "INT DEFAULT 0",
                'last_reset_date': "DATE",
                'loot_claimed': "TINYINT(1) DEFAULT 1",
                'updated_at': "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
            }
            
            for col, definition in to_add.items():
                if col not in columns:
                    print(f"Adding column {col}...")
                    cursor.execute(f"ALTER TABLE player_dungeon_progress ADD COLUMN {col} {definition}")
            
            conn.commit()
            print("Database fix completed successfully.")
    except Exception as e:
        print(f"Error fixing database: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_db()
