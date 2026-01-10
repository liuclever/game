from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.task_reward import TaskRewardClaim


class ITaskRewardRepo(ABC):
    """任务奖励领取记录仓库接口"""

    @abstractmethod
    def list_claims(self, user_id: int) -> List[TaskRewardClaim]:
        ...

    @abstractmethod
    def get_claim(self, user_id: int, reward_key: str) -> Optional[TaskRewardClaim]:
        ...

    @abstractmethod
    def add_claim(self, claim: TaskRewardClaim) -> TaskRewardClaim:
        ...
