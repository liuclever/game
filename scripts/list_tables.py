import sys
import os
sys.path.append(os.getcwd())
from infrastructure.db.connection import execute_query

try:
    tables = execute_query("SHOW TABLES")
    print("Tables in database:")
    for table in tables:
        print(list(table.values())[0])
except Exception as e:
    print(f"Error: {e}")
