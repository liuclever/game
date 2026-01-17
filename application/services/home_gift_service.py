import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

from application.services.inventory_service import InventoryService, InventoryError


class HomeGiftError(Exception):
    pass


@dataclass
class GiftReward:
    type: str
    item_id: Optional[int] = None
    quantity: int = 0
    amount: int = 0
    pool: Optional[List[int]] = None


@dataclass
class GiftDef:
    key: str
    name: str
    detail: str
    rewards: List[GiftReward]


CRYSTAL_POOL = [1001, 1002, 1003, 1004, 1005, 1006, 1007]


class HomeGiftService:
    def __init__(self, gift_claim_repo, inventory_service: InventoryService, player_repo, item_repo):
        self.gift_claim_repo = gift_claim_repo
        self.inventory_service = inventory_service
        self.player_repo = player_repo
        self.item_repo = item_repo
        self._gifts = self._build_gifts()
        self._gift_map = {g.key: g for g in self._gifts}

    def _build_gifts(self) -> List[GiftDef]:
        return [
            GiftDef(
                key="old_player",
                name="老玩家回馈礼包",
                detail=(
                    "活力草×1、强力捕捉球×1、骰子包×1、化仙丹×1、双倍卡×1、重生丹×1、"
                    "追魂法宝×1、焚火晶×1、传送符×1、迷踪符×1、灵力水晶×1、招财神符×1、"
                    "庄园建造手册×1、镇妖符×1、炼魂丹×1、金袋×1"
                ),
                rewards=[
                    GiftReward(type="item", item_id=4001, quantity=1),
                    GiftReward(type="item", item_id=4003, quantity=1),
                    GiftReward(type="item", item_id=6010, quantity=1),
                    GiftReward(type="item", item_id=6015, quantity=1),
                    GiftReward(type="item", item_id=6024, quantity=1),
                    GiftReward(type="item", item_id=6017, quantity=1),
                    GiftReward(type="item", item_id=6019, quantity=1),
                    GiftReward(type="item", item_id=6102, quantity=1),
                    GiftReward(type="item", item_id=6018, quantity=1),
                    GiftReward(type="item", item_id=6002, quantity=1),
                    GiftReward(type="item", item_id=6101, quantity=1),
                    GiftReward(type="item", item_id=6004, quantity=1),
                    GiftReward(type="item", item_id=6029, quantity=1),
                    GiftReward(type="item", item_id=6001, quantity=1),
                    GiftReward(type="item", item_id=6028, quantity=1),
                    GiftReward(type="item", item_id=6005, quantity=1),
                ],
            ),
            GiftDef(
                key="beta_luxury",
                name="内测豪华礼包",
                detail=(
                    "铜钱88万、元宝3888、神·逆鳞碎片×50、骰子包×2、七类结晶随机×10、"
                    "强力捕捉球×3、重置卡×1、镇妖符×2、技能书口袋×1"
                ),
                rewards=[
                    GiftReward(type="gold", amount=880000),
                    GiftReward(type="yuanbao", amount=3888),
                    GiftReward(type="item", item_id=3011, quantity=50),
                    GiftReward(type="item", item_id=6010, quantity=2),
                    GiftReward(type="random_from_pool", pool=CRYSTAL_POOL, quantity=10),
                    GiftReward(type="item", item_id=4003, quantity=3),
                    GiftReward(type="item", item_id=6033, quantity=1),
                    GiftReward(type="item", item_id=6001, quantity=2),
                    GiftReward(type="item", item_id=6007, quantity=1),
                ],
            ),
            GiftDef(
                key="launch_luxury",
                name="开服豪华礼包",
                detail=(
                    "铜钱88万、元宝3888、远古秘银宝箱×5、神·逆鳞碎片×50、远古钛金宝箱×2、"
                    "七类结晶随机×10"
                ),
                rewards=[
                    GiftReward(type="gold", amount=880000),
                    GiftReward(type="yuanbao", amount=3888),
                    GiftReward(type="item", item_id=6003, quantity=5),
                    GiftReward(type="item", item_id=3011, quantity=50),
                    GiftReward(type="item", item_id=6014, quantity=2),
                    GiftReward(type="random_from_pool", pool=CRYSTAL_POOL, quantity=10),
                ],
            ),
            GiftDef(
                key="dragon_palace_compensation",
                name="龙宫补偿礼包",
                detail="进化神草×7、进化水晶×3",
                rewards=[
                    GiftReward(type="item", item_id=3012, quantity=7),
                    GiftReward(type="item", item_id=3014, quantity=3),
                ],
            ),
        ]

    def list_gifts(self, user_id: int) -> Dict[str, Any]:
        claimed = set(self.gift_claim_repo.get_claimed_keys(user_id))
        return {
            "ok": True,
            "gifts": [
                {
                    "key": g.key,
                    "name": g.name,
                    "detail": g.detail,
                    "claimed": g.key in claimed,
                }
                for g in self._gifts
            ],
        }

    def _validate_gift_rewards(self, gift: GiftDef) -> None:
        """领取前做完整校验，避免“发了一半就报错”导致无限领取/部分道具丢失。"""
        for r in gift.rewards:
            if r.type in ("gold", "yuanbao"):
                continue

            if r.type == "item":
                if not r.item_id or int(r.quantity or 0) <= 0:
                    raise HomeGiftError("礼包配置错误：物品奖励缺少 item_id 或数量无效")
                item = self.item_repo.get_by_id(int(r.item_id))
                if item is None:
                    raise HomeGiftError(f"礼包配置错误：物品不存在({r.item_id})")
                continue

            if r.type == "random_from_pool":
                pool = r.pool or []
                if not pool or int(r.quantity or 0) <= 0:
                    raise HomeGiftError("礼包配置错误：随机奖池为空或数量无效")
                for item_id in pool:
                    item = self.item_repo.get_by_id(int(item_id))
                    if item is None:
                        raise HomeGiftError(f"礼包配置错误：奖池物品不存在({item_id})")
                continue

            raise HomeGiftError(f"礼包配置错误：未知奖励类型({r.type})")

    def claim(self, user_id: int, gift_key: str) -> Dict[str, Any]:
        gift = self._gift_map.get(gift_key)
        if not gift:
            raise HomeGiftError("未知礼包")

        if self.gift_claim_repo.is_claimed(user_id, gift_key):
            raise HomeGiftError("该礼包已领取")

        player = self.player_repo.get_by_id(user_id)
        if not player:
            raise HomeGiftError("玩家不存在")

        # 关键：先校验所有奖励都能正常发放，再进入实际发放流程
        self._validate_gift_rewards(gift)

        granted_items: Dict[str, int] = {}
        gold_added = 0
        yuanbao_added = 0

        try:
            for r in gift.rewards:
                if r.type == "gold":
                    player.gold += int(r.amount or 0)
                    gold_added += int(r.amount or 0)
                elif r.type == "yuanbao":
                    player.yuanbao += int(r.amount or 0)
                    yuanbao_added += int(r.amount or 0)
                elif r.type == "item":
                    self.inventory_service.add_item(user_id, int(r.item_id), int(r.quantity))
                    item = self.item_repo.get_by_id(int(r.item_id))
                    name = item.name if item else f"物品{r.item_id}"
                    granted_items[name] = granted_items.get(name, 0) + int(r.quantity)
                elif r.type == "random_from_pool":
                    pool = r.pool or []
                    for _ in range(int(r.quantity)):
                        item_id = random.choice(pool)
                        self.inventory_service.add_item(user_id, int(item_id), 1)
                        item = self.item_repo.get_by_id(int(item_id))
                        name = item.name if item else f"物品{item_id}"
                        granted_items[name] = granted_items.get(name, 0) + 1
                else:
                    raise HomeGiftError(f"未知奖励类型: {r.type}")
        except InventoryError as exc:
            # 兼容：如底层仍报错，转成可读错误，避免“接口500但已发部分道具”不知原因
            raise HomeGiftError(str(exc))

        self.player_repo.save(player)
        self.gift_claim_repo.mark_claimed(user_id, gift_key)

        items_payload = [{"name": k, "quantity": v} for k, v in granted_items.items()]
        return {
            "ok": True,
            "gift": {"key": gift.key, "name": gift.name},
            "rewards": {
                "gold": gold_added,
                "yuanbao": yuanbao_added,
                "items": items_payload,
            },
        }
