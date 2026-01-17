from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Tuple

from application.services.inventory_service import InventoryService, InventoryError
from domain.repositories.player_repo import IPlayerRepo


class ExchangeError(Exception):
    pass


@dataclass(frozen=True)
class DivineBeastExchangeDef:
    key: str
    template_id: int
    ball_item_id: int
    cost_nilin: int
    min_player_level: int
    success_message: str


class ExchangeService:
    """兑换服务（神兽召唤球限次/等级/唯一持有等规则）。"""

    NILIN_ITEM_ID = 3010

    def __init__(self, inventory_service: InventoryService, player_repo: IPlayerRepo, player_beast_repo, exchange_claim_repo):
        self.inventory_service = inventory_service
        self.player_repo = player_repo
        self.player_beast_repo = player_beast_repo
        self.exchange_claim_repo = exchange_claim_repo

        self._divine_defs: Dict[str, DivineBeastExchangeDef] = {
            "qinglong": DivineBeastExchangeDef(
                key="qinglong", template_id=64, ball_item_id=26064, cost_nilin=12, min_player_level=70,
                success_message="兑换成功，获得神·青龙召唤球×1",
            ),
            "xuanwu": DivineBeastExchangeDef(
                key="xuanwu", template_id=63, ball_item_id=26063, cost_nilin=10, min_player_level=70,
                success_message="兑换成功，获得神·玄武召唤球×1",
            ),
            "zhuque": DivineBeastExchangeDef(
                key="zhuque", template_id=62, ball_item_id=26062, cost_nilin=10, min_player_level=60,
                success_message="兑换成功，获得神·朱雀召唤球×1",
            ),
            "jueying": DivineBeastExchangeDef(
                key="jueying", template_id=61, ball_item_id=26061, cost_nilin=8, min_player_level=50,
                success_message="兑换成功，获得神·绝影召唤球×1",
            ),
            "baihu": DivineBeastExchangeDef(
                key="baihu", template_id=60, ball_item_id=26058, cost_nilin=6, min_player_level=40,
                success_message="兑换成功，获得神·白虎召唤球×1",
            ),
            "businiao": DivineBeastExchangeDef(
                key="businiao", template_id=59, ball_item_id=26059, cost_nilin=4, min_player_level=40,
                success_message="兑换成功，获得神·不死鸟召唤球×1",
            ),
            "luosha": DivineBeastExchangeDef(
                key="luosha", template_id=58, ball_item_id=26060, cost_nilin=6, min_player_level=30,
                success_message="兑换成功，获得神·罗刹召唤球×1",
            ),
        }

    @staticmethod
    def _claim_key(beast_key: str) -> str:
        return f"exchange:divine_beast:{beast_key}"

    def _has_divine_beast(self, user_id: int, template_id: int) -> bool:
        beasts = self.player_beast_repo.get_all_by_user(user_id)
        return any(int(getattr(b, "template_id", 0) or 0) == int(template_id) for b in (beasts or []))

    def get_divine_beast_status(self, user_id: int, beast_key: str) -> Dict[str, Any]:
        d = self._divine_defs.get(str(beast_key))
        if not d:
            raise ExchangeError("未知神兽兑换")

        player = self.player_repo.get_by_id(user_id)
        player_level = int(getattr(player, "level", 0) or 0) if player else 0

        current_nilin = self.inventory_service.get_item_count(user_id, self.NILIN_ITEM_ID)
        ball_count = self.inventory_service.get_item_count(user_id, d.ball_item_id)
        claimed = bool(self.exchange_claim_repo.is_claimed(user_id, self._claim_key(d.key)))
        has_beast = self._has_divine_beast(user_id, d.template_id)

        return {
            "ok": True,
            "required": d.cost_nilin,
            "current_nilin": current_nilin,
            "has_ball": ball_count > 0,
            "player_level": player_level,
            "min_player_level": d.min_player_level,
            "claimed": claimed,
            "has_beast": has_beast,
            "can_exchange": (player_level >= d.min_player_level) and (not claimed) and (not has_beast) and (current_nilin >= d.cost_nilin),
        }

    def exchange_divine_beast(self, user_id: int, beast_key: str) -> Dict[str, Any]:
        d = self._divine_defs.get(str(beast_key))
        if not d:
            raise ExchangeError("未知神兽兑换")

        player = self.player_repo.get_by_id(user_id)
        player_level = int(getattr(player, "level", 0) or 0) if player else 0
        if player_level < d.min_player_level:
            raise ExchangeError(f"人物等级不足，需要{d.min_player_level}级")

        if self.exchange_claim_repo.is_claimed(user_id, self._claim_key(d.key)):
            raise ExchangeError("该神兽召唤球已兑换过（限1次）")

        if self._has_divine_beast(user_id, d.template_id):
            raise ExchangeError("你已拥有该神兽，无法再次兑换")

        if not self.inventory_service.has_item(user_id, self.NILIN_ITEM_ID, d.cost_nilin):
            raise ExchangeError(f"神·逆鳞不足（需要{d.cost_nilin}块）")

        try:
            self.inventory_service.remove_item(user_id, self.NILIN_ITEM_ID, d.cost_nilin)
            self.inventory_service.add_item(user_id, d.ball_item_id, 1)
            self.exchange_claim_repo.mark_claimed(user_id, self._claim_key(d.key))
        except InventoryError as exc:
            raise ExchangeError(str(exc))

        current_nilin = self.inventory_service.get_item_count(user_id, self.NILIN_ITEM_ID)
        return {"ok": True, "message": d.success_message, "current_nilin": current_nilin}


