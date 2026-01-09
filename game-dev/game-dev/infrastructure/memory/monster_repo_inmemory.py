from typing import Optional, Dict
from domain.entities.monster import Monster
from domain.repositories.monster_repo import IMonsterRepo


class InMemoryMonsterRepo(IMonsterRepo):
    """用字典存怪物的内存仓库，用来本地测试"""

    def __init__(self, initial_monsters: Optional[Dict[int, Monster]] = None):
        self._monsters: Dict[int, Monster] = initial_monsters or {}

    def get_by_id(self, monster_id: int) -> Optional[Monster]:
        return self._monsters.get(monster_id)
