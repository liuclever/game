"""
古树（每周幸运数字）MySQL 仓库实现。

表结构由 sql/035_tree_schema.sql 提供（可重复执行）。
"""

from __future__ import annotations

import json
from datetime import date, datetime
from typing import Optional

from domain.entities.tree import TreePlayerWeek, TreeWeek
from domain.repositories.tree_repo import ITreeRepo
from infrastructure.db.connection import execute_query, execute_update


def _loads_int_list(s: str | None) -> list[int]:
    if not s:
        return []
    try:
        arr = json.loads(s)
    except Exception:
        return []
    if not isinstance(arr, list):
        return []
    out: list[int] = []
    for x in arr:
        try:
            out.append(int(x))
        except Exception:
            continue
    return out


class MySQLTreeRepo(ITreeRepo):
    def get_week(self, week_start: date) -> Optional[TreeWeek]:
        rows = execute_query(
            "SELECT week_start, winning_numbers_json FROM tree_week WHERE week_start = %s",
            (week_start,),
        )
        if not rows:
            return None
        row = rows[0]
        return TreeWeek(
            week_start=row["week_start"],
            winning_numbers=_loads_int_list(row.get("winning_numbers_json")),
        )

    def upsert_week(self, week: TreeWeek) -> None:
        sql = """
        INSERT INTO tree_week (week_start, winning_numbers_json, updated_at)
        VALUES (%s, %s, NOW())
        ON DUPLICATE KEY UPDATE
          winning_numbers_json = VALUES(winning_numbers_json),
          updated_at = NOW()
        """
        execute_update(sql, (week.week_start, json.dumps(list(week.winning_numbers or []), ensure_ascii=False)))

    def get_player_week(self, user_id: int, week_start: date) -> Optional[TreePlayerWeek]:
        rows = execute_query(
            """
            SELECT user_id, week_start, my_numbers_json, last_draw_date, claimed_at, claim_star, match_count
            FROM tree_player_week
            WHERE user_id = %s AND week_start = %s
            """,
            (user_id, week_start),
        )
        if not rows:
            return None
        row = rows[0]
        return TreePlayerWeek(
            user_id=int(row["user_id"]),
            week_start=row["week_start"],
            my_numbers=_loads_int_list(row.get("my_numbers_json")),
            last_draw_date=row.get("last_draw_date"),
            claimed_at=row.get("claimed_at"),
            claim_star=int(row.get("claim_star") or 0),
            match_count=int(row.get("match_count") or 0),
        )

    def upsert_player_week(self, state: TreePlayerWeek) -> None:
        sql = """
        INSERT INTO tree_player_week
          (user_id, week_start, my_numbers_json, last_draw_date, claimed_at, claim_star, match_count, updated_at)
        VALUES
          (%s, %s, %s, %s, %s, %s, %s, NOW())
        ON DUPLICATE KEY UPDATE
          my_numbers_json = VALUES(my_numbers_json),
          last_draw_date = VALUES(last_draw_date),
          claimed_at = VALUES(claimed_at),
          claim_star = VALUES(claim_star),
          match_count = VALUES(match_count),
          updated_at = NOW()
        """
        execute_update(
            sql,
            (
                int(state.user_id),
                state.week_start,
                json.dumps(list(state.my_numbers or []), ensure_ascii=False),
                state.last_draw_date,
                state.claimed_at,
                int(state.claim_star or 0),
                int(state.match_count or 0),
            ),
        )


