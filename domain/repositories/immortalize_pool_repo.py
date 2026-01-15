from abc import ABC, abstractmethod
from typing import Optional

from domain.entities.immortalize_pool import ImmortalizePool


class IImmortalizePoolRepo(ABC):
    @abstractmethod
    def get_by_user_id(self, user_id: int) -> Optional[ImmortalizePool]:
        """获取玩家化仙池信息"""

    @abstractmethod
    def upsert(self, pool: ImmortalizePool) -> ImmortalizePool:
        """保存或创建玩家化仙池信息"""
