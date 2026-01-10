"""
古树（每周幸运数字）仓储接口（领域层）。

说明：领域层只定义抽象接口，不关心 MySQL/缓存等实现细节。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Optional

from domain.entities.tree import TreePlayerWeek, TreeWeek


class ITreeRepo(ABC):
    @abstractmethod
    def get_week(self, week_start: date) -> Optional[TreeWeek]:
        """获取某周开奖信息。"""
        raise NotImplementedError

    @abstractmethod
    def upsert_week(self, week: TreeWeek) -> None:
        """写入/更新某周开奖信息。"""
        raise NotImplementedError

    @abstractmethod
    def get_player_week(self, user_id: int, week_start: date) -> Optional[TreePlayerWeek]:
        """获取玩家某周的领取/领奖信息。"""
        raise NotImplementedError

    @abstractmethod
    def upsert_player_week(self, state: TreePlayerWeek) -> None:
        """写入/更新玩家某周的领取/领奖信息。"""
        raise NotImplementedError


