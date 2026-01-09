# game/infrastructure/config/map_repo_from_config.py
from typing import Optional, Dict, List

from domain.entities.map import Map
from domain.repositories.map_repo import IMapRepo
from .load_data import load_maps


class ConfigMapRepo(IMapRepo):
    """从 configs/maps.json 读取地图数据的仓库实现（只读）"""

    def __init__(self, maps: Optional[Dict[int, Map]] = None):
        self._maps: Dict[int, Map] = maps or load_maps()

    def get_by_id(self, map_id: int) -> Optional[Map]:
        return self._maps.get(map_id)

    def list_all(self) -> List[Map]:
        return list(self._maps.values())
