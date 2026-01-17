from typing import Optional, Dict, Tuple
from domain.entities.tower import TowerState
from domain.repositories.tower_repo import ITowerStateRepo


class InMemoryTowerStateRepo(ITowerStateRepo):
    """内存版闯塔状态存储"""
    
    def __init__(self):
        # key: (user_id, tower_type)
        self._data: Dict[Tuple[int, str], TowerState] = {}
    
    def get_by_user_id(self, user_id: int, tower_type: str) -> Optional[TowerState]:
        key = (user_id, tower_type)
        if key not in self._data:
            # 创建默认状态
            self._data[key] = TowerState(user_id=user_id, tower_type=tower_type)
        return self._data[key]
    
    def save(self, state: TowerState) -> None:
        key = (state.user_id, state.tower_type)
        self._data[key] = state
