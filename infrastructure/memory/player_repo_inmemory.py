from typing import Optional, Dict
from domain.entities.player import Player
from domain.repositories.player_repo import IPlayerRepo


class InMemoryPlayerRepo(IPlayerRepo):
    """用字典存玩家的内存仓库，用来本地测试"""

    def __init__(self, initial_players: Optional[Dict[int, Player]] = None):
        self._players: Dict[int, Player] = initial_players or {}

    def get_by_id(self, player_id: int) -> Optional[Player]:
        return self._players.get(player_id)

    def save(self, player: Player) -> None:
        # 简单起见，没有 id 的话自动分配一个
        if player.id is None:
            new_id = max(self._players.keys(), default=0) + 1
            player.id = new_id
        self._players[player.id] = player

