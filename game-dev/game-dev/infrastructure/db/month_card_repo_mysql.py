"""
MySQL 仓储：玩家月卡
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import List, Optional

from infrastructure.db.connection import execute_query, execute_insert, execute_update


@dataclass
class PlayerMonthCard:
    id: Optional[int]
    user_id: int
    month: int
    start_date: datetime
    end_date: datetime
    days_total: int = 30
    days_claimed: int = 0
    last_claim_date: Optional[date] = None
    status: str = "active"
    initial_reward: int = 1000
    daily_reward: int = 200
    initial_reward_claimed: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row: dict) -> "PlayerMonthCard":
        return cls(
            id=row.get("id"),
            user_id=row.get("user_id"),
            month=row.get("month"),
            start_date=row.get("start_date"),
            end_date=row.get("end_date"),
            days_total=row.get("days_total", 30),
            days_claimed=row.get("days_claimed", 0),
            last_claim_date=row.get("last_claim_date"),
            status=row.get("status", "active"),
            initial_reward=row.get("initial_reward", 1000),
            daily_reward=row.get("daily_reward", 200),
            initial_reward_claimed=bool(row.get("initial_reward_claimed")),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )


class MySQLMonthCardRepo:
    TABLE = "player_month_card"

    def get_by_user_and_month(self, user_id: int, month: int) -> Optional[PlayerMonthCard]:
        sql = f"SELECT * FROM {self.TABLE} WHERE user_id = %s AND month = %s LIMIT 1"
        rows = execute_query(sql, (user_id, month))
        if rows:
            return PlayerMonthCard.from_row(rows[0])
        return None

    def list_by_user(self, user_id: int) -> List[PlayerMonthCard]:
        sql = f"SELECT * FROM {self.TABLE} WHERE user_id = %s ORDER BY month"
        rows = execute_query(sql, (user_id,))
        return [PlayerMonthCard.from_row(row) for row in rows]

    def create_or_update(self, record: PlayerMonthCard) -> int:
        if record.id:
            return self._update(record)
        return self._insert(record)

    def _insert(self, record: PlayerMonthCard) -> int:
        sql = f"""
            INSERT INTO {self.TABLE} (
                user_id, month, start_date, end_date,
                days_total, days_claimed, last_claim_date,
                status, initial_reward, daily_reward, initial_reward_claimed
            ) VALUES (
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s
            )
        """
        new_id = execute_insert(
            sql,
            (
                record.user_id,
                record.month,
                record.start_date,
                record.end_date,
                record.days_total,
                record.days_claimed,
                record.last_claim_date,
                record.status,
                record.initial_reward,
                record.daily_reward,
                int(record.initial_reward_claimed),
            ),
        )
        record.id = new_id
        return new_id

    def _update(self, record: PlayerMonthCard) -> int:
        sql = f"""
            UPDATE {self.TABLE}
            SET
                start_date = %s,
                end_date = %s,
                days_total = %s,
                days_claimed = %s,
                last_claim_date = %s,
                status = %s,
                initial_reward = %s,
                daily_reward = %s,
                initial_reward_claimed = %s
            WHERE id = %s
        """
        return execute_update(
            sql,
            (
                record.start_date,
                record.end_date,
                record.days_total,
                record.days_claimed,
                record.last_claim_date,
                record.status,
                record.initial_reward,
                record.daily_reward,
                int(record.initial_reward_claimed),
                record.id,
            ),
        )

    def update_claim(
        self,
        user_id: int,
        month: int,
        last_claim_date: date,
        days_claimed: int,
        status: str,
    ) -> int:
        sql = f"""
            UPDATE {self.TABLE}
            SET
                last_claim_date = %s,
                days_claimed = %s,
                status = %s
            WHERE user_id = %s AND month = %s
        """
        return execute_update(sql, (last_claim_date, days_claimed, status, user_id, month))

    def update_status(
        self,
        user_id: int,
        month: int,
        status: str,
        initial_reward_claimed: Optional[bool] = None,
    ) -> int:
        if initial_reward_claimed is None:
            sql = f"""
                UPDATE {self.TABLE}
                SET status = %s
                WHERE user_id = %s AND month = %s
            """
            params = (status, user_id, month)
        else:
            sql = f"""
                UPDATE {self.TABLE}
                SET status = %s,
                    initial_reward_claimed = %s
                WHERE user_id = %s AND month = %s
            """
            params = (status, int(initial_reward_claimed), user_id, month)
        return execute_update(sql, params)
