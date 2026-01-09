"""
古树（每周幸运数字）MySQL 仓库实现。

表结构由 sql/035_tree_schema.sql 提供（可重复执行）。

兼容策略：
- 旧版本字段：tree_week.winning_numbers_json / tree_player_week.my_numbers_json
- 新版本字段：tree_week.winning_red_numbers_json + winning_blue_number / tree_player_week.red_numbers_json + blue_number
- 读取时优先新字段；写入时尽量同步写入新旧字段，便于平滑升级。
"""

from __future__ import annotations

import json
from datetime import date
from typing import Optional, Tuple

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
        sql_candidates = [
            "SELECT week_start, announce_date, winning_red_numbers_json, winning_blue_number, winning_numbers_json FROM tree_week WHERE week_start = %s",
            "SELECT week_start, winning_numbers_json FROM tree_week WHERE week_start = %s",
        ]
        rows = []
        last_err: Exception | None = None
        for sql in sql_candidates:
            try:
                rows = execute_query(sql, (week_start,))
                last_err = None
                break
            except Exception as e:
                last_err = e
                continue
        if last_err is not None and not rows:
            raise last_err
        if not rows:
            return None
        row = rows[0]
        # 兼容：若新字段不存在，则从 winning_numbers_json 拆分（红6+蓝1）
        combined = _loads_int_list(row.get("winning_numbers_json"))
        red = _loads_int_list(row.get("winning_red_numbers_json")) if "winning_red_numbers_json" in row else combined[:6]
        blue = row.get("winning_blue_number") if "winning_blue_number" in row else (combined[6] if len(combined) >= 7 else None)
        announce_date = row.get("announce_date") if "announce_date" in row else None
        # announce_date 允许为空（旧数据）；由 service 兜底计算
        return TreeWeek(
            week_start=row["week_start"],
            announce_date=announce_date or row["week_start"],
            winning_red_numbers=red[:6],
            winning_blue_number=int(blue) if blue is not None else None,
        )

    def upsert_week(self, week: TreeWeek) -> None:
        red = list(week.winning_red_numbers or [])[:6]
        blue = week.winning_blue_number
        combined = red + ([int(blue)] if blue is not None else [])
        sql_candidates = [
            """
            INSERT INTO tree_week (week_start, announce_date, winning_red_numbers_json, winning_blue_number, winning_numbers_json, updated_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE
              announce_date = VALUES(announce_date),
              winning_red_numbers_json = VALUES(winning_red_numbers_json),
              winning_blue_number = VALUES(winning_blue_number),
              winning_numbers_json = VALUES(winning_numbers_json),
              updated_at = NOW()
            """,
            """
            INSERT INTO tree_week (week_start, winning_numbers_json, updated_at)
            VALUES (%s, %s, NOW())
            ON DUPLICATE KEY UPDATE
              winning_numbers_json = VALUES(winning_numbers_json),
              updated_at = NOW()
            """,
        ]
        params_candidates = [
            (
                week.week_start,
                week.announce_date,
                json.dumps(red, ensure_ascii=False),
                int(blue) if blue is not None else None,
                json.dumps(combined, ensure_ascii=False),
            ),
            (week.week_start, json.dumps(combined, ensure_ascii=False)),
        ]
        last_err: Exception | None = None
        for sql, params in zip(sql_candidates, params_candidates):
            try:
                execute_update(sql, params)
                last_err = None
                break
            except Exception as e:
                last_err = e
                continue
        if last_err is not None:
            raise last_err

    def get_player_week(self, user_id: int, week_start: date) -> Optional[TreePlayerWeek]:
        sql_candidates = [
            """
            SELECT user_id, week_start, red_numbers_json, blue_number, my_numbers_json, last_draw_date, claimed_at, claim_star, match_count
            FROM tree_player_week
            WHERE user_id = %s AND week_start = %s
            """,
            """
            SELECT user_id, week_start, my_numbers_json, last_draw_date, claimed_at, claim_star, match_count
            FROM tree_player_week
            WHERE user_id = %s AND week_start = %s
            """,
        ]
        rows = []
        last_err: Exception | None = None
        for sql in sql_candidates:
            try:
                rows = execute_query(sql, (user_id, week_start))
                last_err = None
                break
            except Exception as e:
                last_err = e
                continue
        if last_err is not None and not rows:
            raise last_err
        if not rows:
            return None
        row = rows[0]
        combined = _loads_int_list(row.get("my_numbers_json"))
        red = _loads_int_list(row.get("red_numbers_json")) if "red_numbers_json" in row else combined[:6]
        blue = row.get("blue_number") if "blue_number" in row else (combined[-1] if len(combined) >= 1 and len(combined) > len(red) else None)
        return TreePlayerWeek(
            user_id=int(row["user_id"]),
            week_start=row["week_start"],
            red_numbers=red[:6],
            blue_number=int(blue) if blue is not None else None,
            last_draw_date=row.get("last_draw_date"),
            claimed_at=row.get("claimed_at"),
            claim_star=int(row.get("claim_star") or 0),
            match_count=int(row.get("match_count") or 0),
        )

    def upsert_player_week(self, state: TreePlayerWeek) -> None:
        red = list(state.red_numbers or [])[:6]
        blue = state.blue_number
        combined = red + ([int(blue)] if blue is not None else [])
        sql_candidates = [
            """
            INSERT INTO tree_player_week
              (user_id, week_start, red_numbers_json, blue_number, my_numbers_json, last_draw_date, claimed_at, claim_star, match_count, updated_at)
            VALUES
              (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE
              red_numbers_json = VALUES(red_numbers_json),
              blue_number = VALUES(blue_number),
              my_numbers_json = VALUES(my_numbers_json),
              last_draw_date = VALUES(last_draw_date),
              claimed_at = VALUES(claimed_at),
              claim_star = VALUES(claim_star),
              match_count = VALUES(match_count),
              updated_at = NOW()
            """,
            """
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
            """,
        ]
        params_candidates = [
            (
                int(state.user_id),
                state.week_start,
                json.dumps(red, ensure_ascii=False),
                int(blue) if blue is not None else None,
                json.dumps(combined, ensure_ascii=False),
                state.last_draw_date,
                state.claimed_at,
                int(state.claim_star or 0),
                int(state.match_count or 0),
            ),
            (
                int(state.user_id),
                state.week_start,
                json.dumps(combined, ensure_ascii=False),
                state.last_draw_date,
                state.claimed_at,
                int(state.claim_star or 0),
                int(state.match_count or 0),
            ),
        ]
        last_err: Exception | None = None
        for sql, params in zip(sql_candidates, params_candidates):
            try:
                execute_update(sql, params)
                last_err = None
                break
            except Exception as e:
                last_err = e
                continue
        if last_err is not None:
            raise last_err


