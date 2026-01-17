"""MySQL版战灵仓库"""

from __future__ import annotations

from typing import List, Optional

from domain.entities.spirit import Spirit, SpiritLine
from domain.repositories.spirit_repo import ISpiritRepo
from infrastructure.db.connection import execute_query, execute_update, execute_insert


class MySQLSpiritRepo(ISpiritRepo):
    TABLE_NAME = "player_spirit"

    def get_by_user_id(self, user_id: int) -> List[Spirit]:
        sql = f"SELECT * FROM {self.TABLE_NAME} WHERE user_id = %s ORDER BY id DESC"
        rows = execute_query(sql, (user_id,))
        return [self._row_to_spirit(r) for r in rows]

    def get_by_id(self, spirit_id: int) -> Optional[Spirit]:
        sql = f"SELECT * FROM {self.TABLE_NAME} WHERE id = %s"
        rows = execute_query(sql, (spirit_id,))
        if rows:
            return self._row_to_spirit(rows[0])
        return None

    def get_by_beast_id(self, beast_id: int) -> List[Spirit]:
        sql = f"SELECT * FROM {self.TABLE_NAME} WHERE beast_id = %s ORDER BY id DESC"
        rows = execute_query(sql, (beast_id,))
        return [self._row_to_spirit(r) for r in rows]

    def save(self, spirit: Spirit) -> None:
        lines = list(spirit.lines or [])
        while len(lines) < 3:
            lines.append(SpiritLine(attr_key="", value_bp=0, unlocked=False, locked=False))
        lines = lines[:3]

        if spirit.id is None:
            sql = f"""
                INSERT INTO {self.TABLE_NAME} (
                    user_id, beast_id, element, race,
                    line1_attr, line1_value_bp, line1_unlocked, line1_locked,
                    line2_attr, line2_value_bp, line2_unlocked, line2_locked,
                    line3_attr, line3_value_bp, line3_unlocked, line3_locked
                ) VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s
                )
            """
            spirit.id = execute_insert(
                sql,
                (
                    spirit.user_id,
                    spirit.beast_id,
                    spirit.element,
                    spirit.race,
                    lines[0].attr_key,
                    lines[0].value_bp,
                    1 if lines[0].unlocked else 0,
                    1 if lines[0].locked else 0,
                    lines[1].attr_key,
                    lines[1].value_bp,
                    1 if lines[1].unlocked else 0,
                    1 if lines[1].locked else 0,
                    lines[2].attr_key,
                    lines[2].value_bp,
                    1 if lines[2].unlocked else 0,
                    1 if lines[2].locked else 0,
                ),
            )
            spirit.lines = lines
            return

        sql = f"""
            UPDATE {self.TABLE_NAME} SET
                user_id = %s,
                beast_id = %s,
                element = %s,
                race = %s,
                line1_attr = %s,
                line1_value_bp = %s,
                line1_unlocked = %s,
                line1_locked = %s,
                line2_attr = %s,
                line2_value_bp = %s,
                line2_unlocked = %s,
                line2_locked = %s,
                line3_attr = %s,
                line3_value_bp = %s,
                line3_unlocked = %s,
                line3_locked = %s
            WHERE id = %s
        """
        execute_update(
            sql,
            (
                spirit.user_id,
                spirit.beast_id,
                spirit.element,
                spirit.race,
                lines[0].attr_key,
                lines[0].value_bp,
                1 if lines[0].unlocked else 0,
                1 if lines[0].locked else 0,
                lines[1].attr_key,
                lines[1].value_bp,
                1 if lines[1].unlocked else 0,
                1 if lines[1].locked else 0,
                lines[2].attr_key,
                lines[2].value_bp,
                1 if lines[2].unlocked else 0,
                1 if lines[2].locked else 0,
                spirit.id,
            ),
        )
        spirit.lines = lines

    def delete(self, spirit_id: int) -> None:
        sql = f"DELETE FROM {self.TABLE_NAME} WHERE id = %s"
        execute_update(sql, (spirit_id,))

    def _row_to_spirit(self, row: dict) -> Spirit:
        lines = [
            SpiritLine(
                attr_key=row.get("line1_attr", "") or "",
                value_bp=int(row.get("line1_value_bp", 0) or 0),
                unlocked=bool(row.get("line1_unlocked", 0)),
                locked=bool(row.get("line1_locked", 0)),
            ),
            SpiritLine(
                attr_key=row.get("line2_attr", "") or "",
                value_bp=int(row.get("line2_value_bp", 0) or 0),
                unlocked=bool(row.get("line2_unlocked", 0)),
                locked=bool(row.get("line2_locked", 0)),
            ),
            SpiritLine(
                attr_key=row.get("line3_attr", "") or "",
                value_bp=int(row.get("line3_value_bp", 0) or 0),
                unlocked=bool(row.get("line3_unlocked", 0)),
                locked=bool(row.get("line3_locked", 0)),
            ),
        ]

        return Spirit(
            id=row.get("id"),
            user_id=row.get("user_id", 0) or 0,
            beast_id=row.get("beast_id"),
            element=row.get("element", "") or "",
            race=row.get("race", "") or "",
            lines=lines,
        )
