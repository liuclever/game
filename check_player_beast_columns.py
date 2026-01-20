#!/usr/bin/env python3
"""检查player_beast表结构"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from infrastructure.db.connection import execute_query

# 查询表结构
columns = execute_query("SHOW COLUMNS FROM player_beast")

print("player_beast 表结构:")
print()
for col in columns:
    print(f"  {col['Field']}: {col['Type']}")
