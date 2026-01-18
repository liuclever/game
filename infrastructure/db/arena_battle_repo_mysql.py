"""\
擂台战斗记录仓库 - MySQL 实现

用于战神擂台挑战战报的存取，结构与镇妖战报类似，方便前端展示“擂台动态 + 详细战报”。
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict
import json

from infrastructure.db.connection import execute_query, execute_insert


@dataclass
class ArenaBattleLog:
    """擂台战斗记录"""

    id: int
    arena_type: str
    rank_name: str
    challenger_id: int
    challenger_name: str
    champion_id: int
    champion_name: str
    is_challenger_win: bool
    battle_data: Dict
    created_at: datetime

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "arena_type": self.arena_type,
            "rank_name": self.rank_name,
            "challenger_id": self.challenger_id,
            "challenger_name": self.challenger_name,
            "champion_id": self.champion_id,
            "champion_name": self.champion_name,
            "is_challenger_win": self.is_challenger_win,
            "battle_data": self.battle_data,
            "created_at": self.created_at.strftime("%Y年%m月%d日 %H:%M") if self.created_at else "",
        }


class MySQLArenaBattleRepo:
    """擂台战斗记录仓库"""

    def save_battle(
        self,
        *,
        arena_type: str,
        rank_name: str,
        challenger_id: int,
        challenger_name: str,
        champion_id: int,
        champion_name: str,
        is_challenger_win: bool,
        battle_data: Dict,
    ) -> int:
        """保存一条擂台战报，返回自增ID。"""

        sql = """
            INSERT INTO arena_battle_log (
                arena_type, rank_name,
                challenger_id, challenger_name,
                champion_id, champion_name,
                is_challenger_win, battle_data
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        battle_json = json.dumps(battle_data, ensure_ascii=False)
        return execute_insert(
            sql,
            (
                arena_type,
                rank_name,
                challenger_id,
                challenger_name,
                champion_id,
                champion_name,
                1 if is_challenger_win else 0,
                battle_json,
            ),
        )

    def _row_to_log(self, row) -> ArenaBattleLog:
        data: Dict = {}
        if row.get("battle_data"):
            try:
                data = json.loads(row["battle_data"])
            except Exception:
                data = {}
        return ArenaBattleLog(
            id=row["id"],
            arena_type=row["arena_type"],
            rank_name=row["rank_name"],
            challenger_id=row["challenger_id"],
            challenger_name=row["challenger_name"],
            champion_id=row["champion_id"],
            champion_name=row["champion_name"],
            is_challenger_win=bool(row["is_challenger_win"]),
            battle_data=data,
            created_at=row["created_at"],
        )

    def get_by_id(self, battle_id: int) -> Optional[ArenaBattleLog]:
        """根据 ID 获取单条战报。"""
        sql = """
            SELECT id, arena_type, rank_name,
                   challenger_id, challenger_name,
                   champion_id, champion_name,
                   is_challenger_win, battle_data, created_at
            FROM arena_battle_log
            WHERE id = %s
        """
        rows = execute_query(sql, (battle_id,))
        if not rows:
            return None
        return self._row_to_log(rows[0])

    def get_recent_battles(self, arena_type: Optional[str] = None, limit: int = 20, offset: int = 0) -> List[ArenaBattleLog]:
        """获取最近的战报列表（全服动态）。"""
        if arena_type:
            sql = """
                SELECT id, arena_type, rank_name,
                       challenger_id, challenger_name,
                       champion_id, champion_name,
                       is_challenger_win, battle_data, created_at
                FROM arena_battle_log
                WHERE arena_type = %s
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            rows = execute_query(sql, (arena_type, limit, offset))
        else:
            sql = """
                SELECT id, arena_type, rank_name,
                       challenger_id, challenger_name,
                       champion_id, champion_name,
                       is_challenger_win, battle_data, created_at
                FROM arena_battle_log
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            rows = execute_query(sql, (limit, offset))

        return [self._row_to_log(row) for row in rows]

    def get_user_battles(self, user_id: int, limit: int = 20, offset: int = 0) -> List[ArenaBattleLog]:
        """获取与某玩家相关的战报（个人动态）。"""
        sql = """
            SELECT id, arena_type, rank_name,
                   challenger_id, challenger_name,
                   champion_id, champion_name,
                   is_challenger_win, battle_data, created_at
            FROM arena_battle_log
            WHERE challenger_id = %s OR champion_id = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        rows = execute_query(sql, (user_id, user_id, limit, offset))
        return [self._row_to_log(row) for row in rows]
