from datetime import datetime
from dataclasses import dataclass
from typing import Tuple, List, Optional, TYPE_CHECKING

from domain.entities.battle_record import BattleRecord
from domain.repositories.player_repo import IPlayerRepo
from domain.repositories.monster_repo import IMonsterRepo
from domain.rules.battle_rules import calc_battle
from domain.entities.player import Player

if TYPE_CHECKING:
    from application.services.drop_service import DropService, DropResult


@dataclass
class BattleOutcome:
    """应用层对外返回的结果"""
    record: BattleRecord      # 战斗记录
    player: Player            # 已更新后的玩家快照
    drops: List["DropResult"] = None  # 掉落物品
    map_id: int = 0           # 战斗地图ID（用于后续捕捉）

    def __post_init__(self):
        if self.drops is None:
            self.drops = []


class BattleService:
    def __init__(
        self,
        player_repo: IPlayerRepo,
        monster_repo: IMonsterRepo,
        drop_service: Optional["DropService"] = None,
    ):
        self.player_repo = player_repo
        self.monster_repo = monster_repo
        self.drop_service = drop_service

    def start_battle(self, player_id: int, monster_id: int) -> BattleOutcome:
        """打一次怪：取数据 -> 算结果 -> 更新玩家 -> 生成记录"""

        player = self.player_repo.get_by_id(player_id)
        monster = self.monster_repo.get_by_id(monster_id)

        if player is None:
            raise ValueError(f"Player {player_id} not found")
        if monster is None:
            raise ValueError(f"Monster {monster_id} not found")

        # 1. 用领域规则算战斗结果
        result = calc_battle(player, monster)

        # 2. 更新玩家状态
        if result.win:
            player.add_exp(result.exp_gain)
            player.gold += result.gold_gain
        player.energy -= result.energy_cost

        self.player_repo.save(player)

        # 3. 计算掉落
        drops = []
        if result.win and self.drop_service:
            drops = self.drop_service.calc_drops(monster.map_id)
            self.drop_service.apply_drops(player_id, drops)

        # 4. 生成一条战斗记录（先只在内存里，之后再写入数据库）
        record = BattleRecord(
            id=None,
            user_id=player.id or player_id,
            monster_id=monster.id or monster_id,
            result="win" if result.win else "lose",
            created_at=datetime.utcnow(),
        )

        return BattleOutcome(record=record, player=player, drops=drops, map_id=monster.map_id)
