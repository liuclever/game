"""MySQL版战灵账户仓库"""

from __future__ import annotations

from typing import Optional
from datetime import date
import json

from domain.entities.spirit import SpiritAccount
from domain.repositories.spirit_repo import ISpiritAccountRepo
from infrastructure.db.connection import execute_query, execute_update
from infrastructure.config.spirit_system_config import get_spirit_system_config


class MySQLSpiritAccountRepo(ISpiritAccountRepo):
    TABLE_NAME = "spirit_account"

    def get_by_user_id(self, user_id: int) -> SpiritAccount:
        sql = f"SELECT * FROM {self.TABLE_NAME} WHERE user_id = %s"
        rows = execute_query(sql, (user_id,))
        if rows:
            return self._row_to_account(rows[0])

        # 不存在则创建默认账户
        cfg = get_spirit_system_config()
        unlocked = cfg.get_default_unlocked_elements()
        unlocked_json = json.dumps(unlocked, ensure_ascii=False)

        insert_sql = f"""
            INSERT INTO {self.TABLE_NAME} (user_id, spirit_power, unlocked_elements, free_refine_date, free_refine_used)
            VALUES (%s, %s, %s, %s, %s)
        """
        execute_update(insert_sql, (user_id, 0, unlocked_json, None, 0))

        return SpiritAccount(user_id=user_id, spirit_power=0, unlocked_elements=unlocked)

    def save(self, account: SpiritAccount) -> None:
        unlocked_json = json.dumps(list(account.unlocked_elements or []), ensure_ascii=False)

        sql = f"""
            INSERT INTO {self.TABLE_NAME}
                (user_id, spirit_power, unlocked_elements, free_refine_date, free_refine_used)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                spirit_power = VALUES(spirit_power),
                unlocked_elements = VALUES(unlocked_elements),
                free_refine_date = VALUES(free_refine_date),
                free_refine_used = VALUES(free_refine_used)
        """
        execute_update(
            sql,
            (
                account.user_id,
                int(account.spirit_power or 0),
                unlocked_json,
                account.free_refine_date,
                int(account.free_refine_used or 0),
            ),
        )

    def _row_to_account(self, row: dict) -> SpiritAccount:
        unlocked_raw = row.get("unlocked_elements")
        unlocked = []
        if isinstance(unlocked_raw, str) and unlocked_raw:
            try:
                unlocked = json.loads(unlocked_raw)
            except Exception:
                unlocked = []
        elif isinstance(unlocked_raw, list):
            unlocked = unlocked_raw

        free_date: Optional[date] = row.get("free_refine_date")

        return SpiritAccount(
            user_id=row.get("user_id", 0) or 0,
            spirit_power=int(row.get("spirit_power", 0) or 0),
            unlocked_elements=list(unlocked or []),
            free_refine_date=free_date,
            free_refine_used=int(row.get("free_refine_used", 0) or 0),
        )
