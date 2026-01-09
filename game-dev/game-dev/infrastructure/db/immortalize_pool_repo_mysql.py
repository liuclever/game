from typing import Optional

from domain.entities.immortalize_pool import ImmortalizePool
from domain.repositories.immortalize_pool_repo import IImmortalizePoolRepo
from infrastructure.db.connection import execute_query, execute_update


class MySQLImmortalizePoolRepo(IImmortalizePoolRepo):
    """玩家化仙池 MySQL 仓库"""

    def get_by_user_id(self, user_id: int) -> Optional[ImmortalizePool]:
        sql = """
            SELECT user_id, pool_level, current_exp, formation_level,
                   formation_started_at, formation_ends_at, formation_last_grant_at,
                   created_at, updated_at
            FROM player_immortalize_pool
            WHERE user_id = %s
        """
        rows = execute_query(sql, (user_id,))
        if not rows:
            return None
        row = rows[0]
        return ImmortalizePool(
            user_id=row["user_id"],
            pool_level=row["pool_level"],
            current_exp=row["current_exp"],
            formation_level=row.get("formation_level", 0),
            formation_started_at=row.get("formation_started_at"),
            formation_ends_at=row.get("formation_ends_at"),
            formation_last_grant_at=row.get("formation_last_grant_at"),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )

    def upsert(self, pool: ImmortalizePool) -> ImmortalizePool:
        sql = """
            INSERT INTO player_immortalize_pool (
                user_id, pool_level, current_exp,
                formation_level, formation_started_at, formation_ends_at, formation_last_grant_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                pool_level = VALUES(pool_level),
                current_exp = VALUES(current_exp),
                formation_level = VALUES(formation_level),
                formation_started_at = VALUES(formation_started_at),
                formation_ends_at = VALUES(formation_ends_at),
                formation_last_grant_at = VALUES(formation_last_grant_at),
                updated_at = CURRENT_TIMESTAMP
        """
        execute_update(
            sql,
            (
                pool.user_id,
                pool.pool_level,
                pool.current_exp,
                pool.formation_level,
                pool.formation_started_at,
                pool.formation_ends_at,
                pool.formation_last_grant_at,
            ),
        )
        return pool
