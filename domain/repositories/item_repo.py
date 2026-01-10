try:
    from typing import Protocol, Optional, Dict
except ImportError:
    from typing_extensions import Protocol
    from typing import Optional, Dict
from domain.entities.item import Item


class IItemRepo(Protocol):
    """物品模板数据访问接口（只读）"""

    def get_by_id(self, item_id: int) -> Optional[Item]:
        ...

    def get_all(self) -> Dict[int, Item]:
        ...