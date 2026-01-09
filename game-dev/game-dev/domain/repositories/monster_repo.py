try:
    from typing import Protocol, Optional
except ImportError:
    from typing_extensions import Protocol
    from typing import Optional
from domain.entities.monster import Monster


class IMonsterRepo(Protocol):
    """怪物数据访问接口"""

    def get_by_id(self, monster_id: int) -> Optional[Monster]:
        ...
