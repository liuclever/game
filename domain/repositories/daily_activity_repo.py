from abc import ABC, abstractmethod
from typing import Optional
from domain.entities.daily_activity import DailyActivity

class IDailyActivityRepo(ABC):
    @abstractmethod
    def get_by_user_id(self, user_id: int) -> Optional[DailyActivity]:
        pass

    @abstractmethod
    def save(self, activity: DailyActivity) -> None:
        pass
