"""Battlefield (古战场) battle log repository (MySQL)."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from infrastructure.db.connection import execute_insert, execute_query


@dataclass
class BattlefieldBattleLog:
    id: int
    battlefield_type: str
    period: int
    round_num: int
    match_num: int
    first_user_id: int
    first_user_name: str
    second_user_id: int
    second_user_name: str
    first_user_team: Optional[str]
    second_user_team: Optional[str]
    is_first_win: bool
    result_label: str
    battle_data: Dict[str, Any]
    created_at: Optional[datetime]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "battlefield_type": self.battlefield_type,
            "period": self.period,
            "round_num": self.round_num,
            "match_num": self.match_num,
            "first_user_id": self.first_user_id,
            "first_user_name": self.first_user_name,
            "second_user_id": self.second_user_id,
            "second_user_name": self.second_user_name,
            "first_user_team": self.first_user_team,
            "second_user_team": self.second_user_team,
            "is_first_win": self.is_first_win,
            "result_label": self.result_label,
            "battle_data": self.battle_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class MySQLBattlefieldBattleRepo:
    """Repository for battlefield_battle_log table."""

    def save_battle(
        self,
        *,
        battlefield_type: str,
        period: int,
        round_num: int,
        match_num: int,
        first_user_id: int,
        first_user_name: str,
        second_user_id: int,
        second_user_name: str,
        first_user_team: Optional[str],
        second_user_team: Optional[str],
        is_first_win: bool,
        result_label: str,
        battle_data: Dict[str, Any],
    ) -> int:
        """Insert a battlefield battle log and return its ID."""
        sql = (
            "INSERT INTO battlefield_battle_log ("
            "battlefield_type, period, round_num, match_num, "
            "first_user_id, first_user_name, second_user_id, second_user_name, "
            "first_user_team, second_user_team, is_first_win, result_label, battle_data"
            ") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        params = (
            battlefield_type,
            period,
            round_num,
            match_num,
            first_user_id,
            first_user_name,
            second_user_id,
            second_user_name,
            first_user_team,
            second_user_team,
            1 if is_first_win else 0,
            result_label,
            json.dumps(battle_data, ensure_ascii=False),
        )
        return execute_insert(sql, params)

    # ---------- Query helpers ----------

    def _row_to_log(self, row: Dict[str, Any]) -> BattlefieldBattleLog:
        battle_data: Dict[str, Any] = {}
        raw_data = row.get("battle_data")
        if raw_data:
            try:
                battle_data = json.loads(raw_data)
            except Exception:
                battle_data = {}

        created_at = row.get("created_at")

        return BattlefieldBattleLog(
            id=row["id"],
            battlefield_type=row.get("battlefield_type", ""),
            period=row.get("period", 0),
            round_num=row.get("round_num", 0),
            match_num=row.get("match_num", 0),
            first_user_id=row.get("first_user_id", 0),
            first_user_name=row.get("first_user_name", ""),
            second_user_id=row.get("second_user_id", 0),
            second_user_name=row.get("second_user_name", ""),
            first_user_team=row.get("first_user_team"),
            second_user_team=row.get("second_user_team"),
            is_first_win=bool(row.get("is_first_win", 0)),
            result_label=row.get("result_label", ""),
            battle_data=battle_data,
            created_at=created_at,
        )

    def get_by_id(self, battle_id: int) -> Optional[BattlefieldBattleLog]:
        rows = execute_query(
            "SELECT * FROM battlefield_battle_log WHERE id = %s", (battle_id,)
        )
        if not rows:
            return None
        return self._row_to_log(rows[0])

    def get_latest_period(self, battlefield_type: str) -> Optional[int]:
        rows = execute_query(
            "SELECT MAX(period) AS max_period FROM battlefield_battle_log WHERE battlefield_type = %s",
            (battlefield_type,),
        )
        if not rows:
            return None
        value = rows[0].get("max_period")
        return int(value) if value is not None else None

    def get_matches_for_period(
        self,
        battlefield_type: str,
        period: Optional[int] = None,
    ) -> List[BattlefieldBattleLog]:
        """Get all matches for a battlefield type & period, ordered by round/match.

        If period is None, use the latest one.
        """
        if period is None:
            period = self.get_latest_period(battlefield_type)
            if period is None:
                return []

        rows = execute_query(
            "SELECT * FROM battlefield_battle_log WHERE battlefield_type = %s AND period = %s "
            "ORDER BY round_num ASC, match_num ASC, id ASC",
            (battlefield_type, period),
        )
        return [self._row_to_log(r) for r in rows]
