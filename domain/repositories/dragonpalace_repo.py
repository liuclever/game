from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Optional

from domain.entities.dragonpalace import DragonPalaceDailyState


class IDragonPalaceRepo(ABC):
    """龙宫之谜：每日进度仓库接口。"""

    @abstractmethod
    def get_daily_state(self, user_id: int, play_date: date) -> Optional[DragonPalaceDailyState]:
        raise NotImplementedError

    @abstractmethod
    def upsert_daily_state(self, state: DragonPalaceDailyState) -> None:
        raise NotImplementedError


