import sys
sys.path.insert(0, r'D:\project\plublic-work\December\game')
from infrastructure.db.connection import execute_update, execute_query

sqls = [
    "ALTER TABLE player ADD COLUMN crystal_tower INT DEFAULT 0 COMMENT '水晶塔活力值'",
    "ALTER TABLE player ADD COLUMN charm INT DEFAULT 0 COMMENT '魅力值'",
    "ALTER TABLE player ADD COLUMN energy INT DEFAULT 100 COMMENT '活力值'",
]

for sql in sqls:
    try:
        execute_update(sql)
        print(f"OK: {sql[:50]}...")
    except Exception as e:
        if 'Duplicate column' in str(e):
            print(f"SKIP (already exists): {sql[:50]}...")
        else:
            print(f"ERROR: {e}")

rows = execute_query('DESCRIBE player')
print("\nFinal table structure:")
for r in rows:
    print(r['Field'], r['Type'])
