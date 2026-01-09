import sys
import os
sys.path.append(os.getcwd())
from infrastructure.db.connection import execute_update

try:
    execute_update("ALTER TABLE alliances ADD COLUMN funds INT DEFAULT 0;")
    print("Added funds column")
except Exception as e:
    print(f"Funds column error: {e}")

try:
    execute_update("ALTER TABLE alliances ADD COLUMN crystals INT DEFAULT 0;")
    print("Added crystals column")
except Exception as e:
    print(f"Crystals column error: {e}")

try:
    execute_update("ALTER TABLE alliances ADD COLUMN prosperity INT DEFAULT 0;")
    print("Added prosperity column")
except Exception as e:
    print(f"Prosperity column error: {e}")
