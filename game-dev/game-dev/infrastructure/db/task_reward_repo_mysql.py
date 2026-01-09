from datetime import datetime
from typing import List, Optional

from domain.entities.task_reward import TaskRewardClaim
from domain.repositories.task_reward_repo import ITaskRewardRepo
from infrastructure.db.connection import execute_query, execute_insert


class MySQLTaskRewardRepo(ITaskRewardRepo):
    """任务奖励领取记录 MySQL 实现"""

    def list_claims(self, user_id: int) -> List[TaskRewardClaim]:
        sql = """
            SELECT id, user_id, reward_key, claimed_at
            FROM task_reward_claims
            WHERE user_id = %s
            ORDER BY claimed_at ASC
        """
        rows = execute_query(sql, (user_id,))
        return [
            TaskRewardClaim(
                id=row["id"],
                user_id=row["user_id"],
                reward_key=row["reward_key"],
                claimed_at=row["claimed_at"],
            )
            for row in rows
        ]

    def get_claim(self, user_id: int, reward_key: str) -> Optional[TaskRewardClaim]:
        sql = """
            SELECT id, user_id, reward_key, claimed_at
            FROM task_reward_claims
            WHERE user_id = %s AND reward_key = %s
            LIMIT 1
        """
        rows = execute_query(sql, (user_id, reward_key))
        if not rows:
            return None
        row = rows[0]
        return TaskRewardClaim(
            id=row["id"],
            user_id=row["user_id"],
            reward_key=row["reward_key"],
            claimed_at=row["claimed_at"],
        )

    def add_claim(self, claim: TaskRewardClaim) -> TaskRewardClaim:
        if claim.claimed_at is None:
            claim.claimed_at = datetime.now()
        sql = """
            INSERT INTO task_reward_claims (user_id, reward_key, claimed_at)
            VALUES (%s, %s, %s)
        """
        new_id = execute_insert(sql, (claim.user_id, claim.reward_key, claim.claimed_at))
        claim.id = new_id
        return claim
