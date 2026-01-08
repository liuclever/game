from infrastructure.db.connection import execute_update
try:
    execute_update("ALTER TABLE player_dungeon_progress ADD COLUMN resets_today INT DEFAULT 0;")
    execute_update("ALTER TABLE player_dungeon_progress ADD COLUMN last_reset_date DATE;")
    execute_update("UPDATE player_dungeon_progress SET last_reset_date = CURDATE();")
    print("Success")
except Exception as e:
    print(f"Error: {e}")
