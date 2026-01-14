# game/application/services/map_service.py
from typing import List

from domain.entities.player import Player
from domain.entities.map import Map
from domain.entities.monster import Monster
from domain.repositories.map_repo import IMapRepo
from domain.repositories.monster_repo import IMonsterRepo


class MapService:
    """地图相关用例：列出可进入的地图、地图里的怪物"""

    def __init__(self, map_repo: IMapRepo, monster_repo: IMonsterRepo):
        self.map_repo = map_repo
        self.monster_repo = monster_repo

    def list_maps_for_player(self, player: Player) -> List[Map]:
        """根据玩家等级筛选可进入的地图"""
        all_maps = self.map_repo.list_all()
        level = player.level
        return [
            m for m in all_maps
            if m.min_level <= level <= m.max_level
        ]

    def list_monsters_in_map(self, map_id: int) -> List[Monster]:
        """列出某个地图中的怪物"""
        # 目前怪物都在 monster_repo 内存里，简单遍历
        # ConfigMonsterRepo 里是 dict，可以暴露一个 list_all() 会更优，
        # 这里先临时做个兼容：通过 _monsters 属性（因为你自己写的实现）
        monsters_dict = getattr(self.monster_repo, "_monsters", {})
        return [m for m in monsters_dict.values() if m.map_id == map_id]
