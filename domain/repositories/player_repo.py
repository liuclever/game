try:
    from typing import Protocol, Optional, List
except ImportError:
    from typing_extensions import Protocol
    from typing import Optional, List
from domain.entities.player import Player, ZhenyaoFloor


class IPlayerRepo(Protocol):
    """玩家数据访问接口（不关心具体存在哪）"""

    def get_by_id(self, player_id: int) -> Optional[Player]:
        ...

    def save(self, player: Player) -> None:
        ...


class IZhenyaoRepo(Protocol):
    """镇妖（聚魂阵）数据访问接口"""

    def get_floor(self, floor: int) -> Optional[ZhenyaoFloor]:
        ...

    def get_floors_in_range(self, start: int, end: int) -> List[ZhenyaoFloor]:
        ...

    def occupy_floor(self, floor: int, user_id: int, nickname: str, duration_minutes: int) -> bool:
        ...

    def release_floor(self, floor: int) -> bool:
        ...

    def get_floors_by_occupant(self, user_id: int) -> List[ZhenyaoFloor]:
        ...

    def mark_floor_rewarded(self, floor: int) -> bool:
        ...
