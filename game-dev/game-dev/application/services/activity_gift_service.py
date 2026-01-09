import json
import os
import random
from typing import Dict, List

from application.services.inventory_service import InventoryError
from application.services.daily_activity_service import DailyActivityService


class ActivityGiftError(Exception):
    pass


class ActivityGiftService:
    def __init__(self, inventory_service, daily_activity_service: DailyActivityService, player_repo):
        self.inventory_service = inventory_service
        self.daily_activity_service = daily_activity_service
        self.player_repo = player_repo
        self._config = self._load_config()
        self._gift_map = {gift["key"]: gift for gift in self._config.get("gifts", [])}
        self._pools = self._config.get("pools", {})

    def _load_config(self):
        config_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "configs",
            "activity_gifts.json",
        )
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def claim_gift(self, user_id: int, gift_key: str) -> dict:
        gift_def = self._gift_map.get(gift_key)
        if not gift_def:
            raise ActivityGiftError("未知的礼包类型")

        activity = self.daily_activity_service.get_activity(user_id)
        threshold = gift_def.get("threshold", 0)
        if activity.activity_value < threshold:
            raise ActivityGiftError("活跃度不足，无法领取该礼包")

        claim_marker = self._gift_claim_marker(gift_key)
        if claim_marker in activity.completed_tasks:
            raise ActivityGiftError("该礼包已领取")

        item_id = gift_def.get("item_id")
        if not item_id:
            raise ActivityGiftError("礼包配置缺少 item_id")

        try:
            self.inventory_service.add_item(user_id, item_id, 1)
        except InventoryError as exc:
            raise ActivityGiftError(str(exc)) from exc

        activity.completed_tasks.append(claim_marker)
        self.daily_activity_service.daily_activity_repo.save(activity)

        return {
            "ok": True,
            "gift": {
                "key": gift_def["key"],
                "name": gift_def["name"],
                "item_id": item_id,
            },
        }

    def open_gift(self, user_id: int, effect_key: str) -> dict:
        gift_key = self._normalize_gift_key(effect_key)
        gift_def = self._gift_map.get(gift_key)
        if not gift_def:
            raise ActivityGiftError("未知的礼包类型")

        rewards_payload = []
        for reward in gift_def.get("rewards", []):
            r_type = reward.get("type")
            if r_type == "gold":
                amount = reward.get("amount", 0)
                if not self.player_repo:
                    raise ActivityGiftError("系统错误：PlayerRepo 未配置")
                player = self.player_repo.get_by_id(user_id)
                if not player:
                    raise ActivityGiftError("玩家不存在")
                player.gold += amount
                self.player_repo.save(player)
                rewards_payload.append({"type": "gold", "amount": amount})
            elif r_type == "item":
                item_id = reward.get("item_id")
                qty = reward.get("quantity", 1)
                if not item_id:
                    raise ActivityGiftError("礼包配置缺少物品ID")
                self.inventory_service.add_item(user_id, item_id, qty)
                item_name = self._item_name(item_id, reward.get("name"))
                rewards_payload.append(
                    {"type": "item", "item_id": item_id, "name": item_name, "quantity": qty}
                )
            elif r_type == "random_from_pool":
                pool_name = reward.get("pool")
                qty = reward.get("quantity", 1)
                pool_items = self._pools.get(pool_name) or []
                if not pool_items:
                    raise ActivityGiftError(f"礼包配置错误：奖池 {pool_name} 未定义")
                for _ in range(qty):
                    item_id = random.choice(pool_items)
                    self.inventory_service.add_item(user_id, item_id, 1)
                    rewards_payload.append(
                        {
                            "type": "item",
                            "item_id": item_id,
                            "name": self._item_name(item_id, reward.get("name")),
                            "quantity": 1,
                        }
                    )
            else:
                raise ActivityGiftError(f"未知的奖励类型: {r_type}")

        return {"ok": True, "rewards": rewards_payload}

    def _item_name(self, item_id: int, fallback: str | None) -> str:
        item = self.inventory_service.item_repo.get_by_id(item_id)
        if item:
            return item.name
        return fallback or f"物品{item_id}"

    @staticmethod
    def _gift_claim_marker(gift_key: str) -> str:
        return f"claimed_gift:{gift_key}"

    @staticmethod
    def _normalize_gift_key(effect_key: str) -> str:
        prefix = "activity_gift_"
        return effect_key[len(prefix) :] if effect_key.startswith(prefix) else effect_key
