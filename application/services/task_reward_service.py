from dataclasses import dataclass
from typing import List

from domain.entities.task_reward import TaskRewardClaim
from domain.repositories.task_reward_repo import ITaskRewardRepo
from domain.repositories.player_repo import IPlayerRepo
from application.services.inventory_service import InventoryService, InventoryError


class TaskRewardError(Exception):
    pass


@dataclass(frozen=True)
class TaskRewardDefinition:
    key: str
    name: str
    reward_type: str  # "item" or "gold"
    amount: int
    item_id: int | None = None
    description: str | None = None


PRESTIGE_STONE_ITEM_ID = 12001


class TaskRewardService:
    """负责任务奖励的查询与领取"""

    REWARD_DEFINITIONS: List[TaskRewardDefinition] = [
        TaskRewardDefinition(
            key="prestige_stone",
            name="声望石",
            reward_type="item",
            amount=6,
            item_id=PRESTIGE_STONE_ITEM_ID,
            description="声望石 x6，可快速提升声望",
        ),
        TaskRewardDefinition(
            key="gold",
            name="铜钱",
            reward_type="gold",
            amount=500_000,
            description="铜钱 x500000",
        ),
    ]

    def __init__(
        self,
        reward_repo: ITaskRewardRepo,
        player_repo: IPlayerRepo,
        inventory_service: InventoryService,
    ):
        self.reward_repo = reward_repo
        self.player_repo = player_repo
        self.inventory_service = inventory_service

    def list_rewards(self, user_id: int) -> List[dict]:
        claims = {c.reward_key for c in self.reward_repo.list_claims(user_id)}
        return [
            {
                "key": reward.key,
                "name": reward.name,
                "description": reward.description,
                "amount": reward.amount,
                "reward_type": reward.reward_type,
                "claimed": reward.key in claims,
            }
            for reward in self.REWARD_DEFINITIONS
        ]

    def claim_reward(self, user_id: int, reward_key: str) -> dict:
        reward_def = next(
            (r for r in self.REWARD_DEFINITIONS if r.key == reward_key), None
        )
        if not reward_def:
            raise TaskRewardError("无效的任务奖励")

        if self.reward_repo.get_claim(user_id, reward_key):
            raise TaskRewardError("奖励已领取")

        if reward_def.reward_type == "item":
            if not reward_def.item_id:
                raise TaskRewardError("奖励配置错误：缺少物品ID")
            try:
                self.inventory_service.add_item(
                    user_id=user_id,
                    item_id=reward_def.item_id,
                    quantity=reward_def.amount,
                )
            except InventoryError as exc:
                raise TaskRewardError(str(exc)) from exc
        elif reward_def.reward_type == "gold":
            player = self.player_repo.get_by_id(user_id)
            if not player:
                raise TaskRewardError("玩家不存在")
            player.gold += reward_def.amount
            self.player_repo.save(player)
        else:
            raise TaskRewardError("未知的奖励类型")

        claim = TaskRewardClaim(
            id=None,
            user_id=user_id,
            reward_key=reward_def.key,
            claimed_at=None,
        )
        self.reward_repo.add_claim(claim)

        return {
            "ok": True,
            "reward": {
                "key": reward_def.key,
                "name": reward_def.name,
                "amount": reward_def.amount,
                "reward_type": reward_def.reward_type,
            },
        }
