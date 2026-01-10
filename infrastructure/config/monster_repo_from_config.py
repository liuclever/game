# game/infrastructure/config/monster_repo_from_config.py
from typing import Optional, Dict

from domain.entities.monster import Monster
from domain.repositories.monster_repo import IMonsterRepo
from .load_data import load_monsters


class ConfigMonsterRepo(IMonsterRepo):
    """从 configs/monsters.json 读取怪物数据的仓库实现（只读）"""

    def __init__(self, monsters: Optional[Dict[int, Monster]] = None):
        # 默认启动时加载一份
        self._monsters: Dict[int, Monster] = monsters or load_monsters()

    def get_by_id(self, monster_id: int) -> Optional[Monster]:
        return self._monsters.get(monster_id)
