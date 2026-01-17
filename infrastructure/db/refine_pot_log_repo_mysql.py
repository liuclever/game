"""炼妖日志仓库 (MySQL)"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from infrastructure.db.connection import execute_insert, execute_query


@dataclass
class RefinePotLogEntry:
    """炼妖日志条目"""
    user_id: int
    main_beast_id: int
    material_beast_id: int
    attr_type: str
    before_value: int
    after_value: int
    delta: int
    diff_x: int
    cost_gold: int
    cost_pill: int
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "main_beast_id": self.main_beast_id,
            "material_beast_id": self.material_beast_id,
            "attr_type": self.attr_type,
            "before_value": self.before_value,
            "after_value": self.after_value,
            "delta": self.delta,
            "diff_x": self.diff_x,
            "cost_gold": self.cost_gold,
            "cost_pill": self.cost_pill,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class MySQLRefinePotLogRepo:
    """MySQL版炼妖日志仓库"""

    def insert_log(self, entry: RefinePotLogEntry) -> int:
        """插入炼妖日志记录，返回自增ID"""
        sql = """
            INSERT INTO refine_pot_log (
                user_id, main_beast_id, material_beast_id, attr_type,
                before_value, after_value, delta, diff_x,
                cost_gold, cost_pill
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            entry.user_id,
            entry.main_beast_id,
            entry.material_beast_id,
            entry.attr_type,
            entry.before_value,
            entry.after_value,
            entry.delta,
            entry.diff_x,
            entry.cost_gold,
            entry.cost_pill,
        )
        return execute_insert(sql, params)

    def get_logs_by_user(self, user_id: int, limit: int = 100) -> list[RefinePotLogEntry]:
        """获取玩家的炼妖日志"""
        sql = """
            SELECT id, user_id, main_beast_id, material_beast_id, attr_type,
                   before_value, after_value, delta, diff_x,
                   cost_gold, cost_pill, created_at
            FROM refine_pot_log
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        rows = execute_query(sql, (user_id, limit))
        return [
            RefinePotLogEntry(
                id=row['id'],
                user_id=row['user_id'],
                main_beast_id=row['main_beast_id'],
                material_beast_id=row['material_beast_id'],
                attr_type=row['attr_type'],
                before_value=row['before_value'],
                after_value=row['after_value'],
                delta=row['delta'],
                diff_x=row['diff_x'],
                cost_gold=row['cost_gold'],
                cost_pill=row['cost_pill'],
                created_at=row.get('created_at'),
            )
            for row in rows
        ]