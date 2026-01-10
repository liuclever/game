from typing import Optional, List, Dict
from domain.entities.beast import Beast
from domain.repositories.beast_repo import IBeastRepo


class InMemoryBeastRepo(IBeastRepo):
    """内存幻兽仓库，用于开发测试"""

    def __init__(self):
        self._data: Dict[int, Beast] = {}  # id -> Beast
        self._next_id = 1

    def get_by_user_id(self, user_id: int) -> List[Beast]:
        return [b for b in self._data.values() if b.user_id == user_id]

    def get_by_id(self, beast_id: int) -> Optional[Beast]:
        return self._data.get(beast_id)

    def get_main_beast(self, user_id: int) -> Optional[Beast]:
        for b in self._data.values():
            if b.user_id == user_id and b.is_main:
                return b
        return None

    def save(self, beast: Beast) -> None:
        if beast.id is None:
            beast.id = self._next_id
            self._next_id += 1
        self._data[beast.id] = beast

    def delete(self, beast_id: int) -> None:
        if beast_id in self._data:
            del self._data[beast_id]
