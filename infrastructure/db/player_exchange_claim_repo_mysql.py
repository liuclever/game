from dataclasses import dataclass
from datetime import datetime
from typing import List

from infrastructure.db.connection import execute_query, execute_update


@dataclass
class PlayerExchangeClaim:
    user_id: int
    exchange_key: str
    claimed_at: datetime


class MySQLPlayerExchangeClaimRepo:
    """玩家兑换领取记录（用于“限一次”类兑换的服务端强校验）。"""

    TABLE = "player_exchange_claim"

    def __init__(self):
        self._ensure_table()

    def _ensure_table(self) -> None:
        execute_update(
            f"""
            CREATE TABLE IF NOT EXISTS {self.TABLE} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                exchange_key VARCHAR(128) NOT NULL,
                claimed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY uk_user_exchange (user_id, exchange_key)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )

    def get_claimed_keys(self, user_id: int) -> List[str]:
        rows = execute_query(
            f"SELECT exchange_key FROM {self.TABLE} WHERE user_id = %s",
            (user_id,),
        )
        return [r.get("exchange_key") for r in rows if r.get("exchange_key")]

    def mark_claimed(self, user_id: int, exchange_key: str) -> None:
        execute_update(
            f"""
            INSERT INTO {self.TABLE} (user_id, exchange_key, claimed_at)
            VALUES (%s, %s, CURRENT_TIMESTAMP)
            ON DUPLICATE KEY UPDATE claimed_at = claimed_at
            """,
            (user_id, exchange_key),
        )

    def is_claimed(self, user_id: int, exchange_key: str) -> bool:
        rows = execute_query(
            f"SELECT 1 FROM {self.TABLE} WHERE user_id = %s AND exchange_key = %s LIMIT 1",
            (user_id, exchange_key),
        )
        return bool(rows)


