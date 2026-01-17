from infrastructure.db.connection import execute_query, execute_update
try:
    cols = execute_query("DESC player_dungeon_progress")
    names = [c['Field'] for c in cols]
    if 'resets_today' not in names:
        execute_update("ALTER TABLE player_dungeon_progress ADD COLUMN resets_today INT DEFAULT 0")
    if 'last_reset_date' not in names:
        execute_update("ALTER TABLE player_dungeon_progress ADD COLUMN last_reset_date DATE")
    print("Columns checked/added")
except Exception as e:
    print(f"Error: {e}")
