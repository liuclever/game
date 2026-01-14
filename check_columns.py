from infrastructure.db.connection import execute_query

cols = execute_query("SHOW COLUMNS FROM player LIKE 'signin%'")
print("签到相关字段:")
for c in cols:
    print(f"  {c['Field']}: {c['Type']}")
