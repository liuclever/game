# game/domain/repositories/map_repo.py
try:
    from typing import Protocol, Optional, List
except ImportError:
    from typing_extensions import Protocol
    from typing import Optional, List
from domain.entities.map import Map


class IMapRepo(Protocol):
    """地图数据访问接口"""

    def get_by_id(self, map_id: int) -> Optional[Map]:
        ...

    def list_all(self) -> List[Map]:
        ...
