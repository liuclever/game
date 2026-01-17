from dataclasses import dataclass
from datetime import datetime
from typing import List

from infrastructure.db.connection import execute_query, execute_update


@dataclass
class PlayerGiftClaim:
    user_id: int
    gift_key: str
    claimed_at: datetime


class MySQLPlayerGiftClaimRepo:
    TABLE = "player_gift_claim"

    def __init__(self):
        self._ensure_table()

    def _ensure_table(self) -> None:
        execute_update(
            f"""
            CREATE TABLE IF NOT EXISTS {self.TABLE} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                gift_key VARCHAR(64) NOT NULL,
                claimed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY uk_user_gift (user_id, gift_key)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )

    def get_claimed_keys(self, user_id: int) -> List[str]:
        rows = execute_query(
            f"SELECT gift_key FROM {self.TABLE} WHERE user_id = %s",
            (user_id,),
        )
        return [r.get("gift_key") for r in rows if r.get("gift_key")]

    def mark_claimed(self, user_id: int, gift_key: str) -> None:
        """标记礼包为已领取，如果已存在则抛出异常（防止并发重复领取）"""
        try:
            execute_update(
                f"""
                INSERT INTO {self.TABLE} (user_id, gift_key, claimed_at)
                VALUES (%s, %s, CURRENT_TIMESTAMP)
                """,
                (user_id, gift_key),
            )
        except Exception as e:
            # 如果是唯一键冲突（已领取），抛出异常
            error_msg = str(e).lower()
            if 'duplicate' in error_msg or 'unique' in error_msg or '1062' in error_msg:
                raise ValueError("该礼包已领取")
            # 其他错误重新抛出
            raise

    def is_claimed(self, user_id: int, gift_key: str) -> bool:
        rows = execute_query(
            f"SELECT 1 FROM {self.TABLE} WHERE user_id = %s AND gift_key = %s LIMIT 1",
            (user_id, gift_key),
        )
        return bool(rows)
