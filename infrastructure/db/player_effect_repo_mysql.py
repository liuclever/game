from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from infrastructure.db.connection import execute_query, execute_update


@dataclass
class PlayerEffect:
    id: Optional[int]
    user_id: int
    effect_key: str
    end_time: datetime


class MySQLPlayerEffectRepo:
    TABLE = "player_effect"

    def __init__(self):
        self._ensure_table()

    def _ensure_table(self) -> None:
        execute_update(
            f"""
            CREATE TABLE IF NOT EXISTS {self.TABLE} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                effect_key VARCHAR(64) NOT NULL,
                end_time DATETIME NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY uk_user_effect (user_id, effect_key),
                INDEX idx_end_time (end_time)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )

    def get_end_time(self, user_id: int, effect_key: str) -> Optional[datetime]:
        rows = execute_query(
            f"SELECT end_time FROM {self.TABLE} WHERE user_id = %s AND effect_key = %s LIMIT 1",
            (user_id, effect_key),
        )
        if not rows:
            return None
        return rows[0].get("end_time")

    def add_duration_seconds(
        self,
        user_id: int,
        effect_key: str,
        duration_seconds: int,
        now: Optional[datetime] = None,
    ) -> datetime:
        if now is None:
            now = datetime.now()

        current_end = self.get_end_time(user_id, effect_key)
        base = current_end if current_end and current_end > now else now
        new_end = base + timedelta(seconds=int(duration_seconds or 0))

        execute_update(
            f"""
            INSERT INTO {self.TABLE} (user_id, effect_key, end_time)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE end_time = VALUES(end_time)
            """,
            (user_id, effect_key, new_end),
        )
        return new_end

    def is_active(self, user_id: int, effect_key: str, now: Optional[datetime] = None) -> bool:
        if now is None:
            now = datetime.now()
        end_time = self.get_end_time(user_id, effect_key)
        return bool(end_time and end_time > now)
