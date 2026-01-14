import sys
sys.path.insert(0, r'D:\project\plublic-work\December\game')
from infrastructure.db.connection import execute_query
rows = execute_query('DESCRIBE player')
for r in rows:
    print(r['Field'], r['Type'])
