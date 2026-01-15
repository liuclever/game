import sys
import os
sys.path.append(os.getcwd())
from infrastructure.db.connection import execute_update

sql = """
-- 联盟动态表
CREATE TABLE IF NOT EXISTS alliance_activities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    alliance_id INT NOT NULL,
    event_type VARCHAR(16) NOT NULL,
    actor_user_id INT DEFAULT NULL,
    actor_name VARCHAR(32) DEFAULT NULL,
    target_user_id INT DEFAULT NULL,
    target_name VARCHAR(32) DEFAULT NULL,
    item_name VARCHAR(32) DEFAULT NULL,
    item_quantity INT DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_alliance_activity (alliance_id, created_at),
    FOREIGN KEY (alliance_id) REFERENCES alliances(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

try:
    execute_update(sql)
    print("Successfully created alliance_activities table")
except Exception as e:
    print(f"Error: {e}")
