from typing import Optional, List, Dict
from domain.entities.item import InventoryItem
from domain.repositories.inventory_repo import IInventoryRepo


class InMemoryInventoryRepo(IInventoryRepo):
    """内存背包仓库，用于开发测试"""

    def __init__(self):
        self._data: Dict[int, InventoryItem] = {}  # id -> InventoryItem
        self._next_id = 1

    def get_by_user_id(self, user_id: int, include_temp: bool = True) -> List[InventoryItem]:
        if include_temp:
            return [inv for inv in self._data.values() if inv.user_id == user_id]
        else:
            return [inv for inv in self._data.values() if inv.user_id == user_id and not inv.is_temporary]

    def get_by_id(self, inv_item_id: int) -> Optional[InventoryItem]:
        return self._data.get(inv_item_id)

    def find_item(self, user_id: int, item_id: int, is_temporary: bool = False) -> Optional[InventoryItem]:
        for inv in self._data.values():
            if inv.user_id == user_id and inv.item_id == item_id and inv.is_temporary == is_temporary:
                return inv
        return None

    def find_all_items(self, user_id: int, item_id: int, is_temporary: bool = False) -> List[InventoryItem]:
        return [inv for inv in self._data.values() if inv.user_id == user_id and inv.item_id == item_id and inv.is_temporary == is_temporary]

    def save(self, inv_item: InventoryItem) -> None:
        if inv_item.id is None:
            inv_item.id = self._next_id
            self._next_id += 1
        self._data[inv_item.id] = inv_item

    def delete(self, inv_item_id: int) -> None:
        if inv_item_id in self._data:
            del self._data[inv_item_id]