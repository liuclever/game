import random
from dataclasses import dataclass

from application.configs.refine_pot_config import (
    get_attr_field,
    get_refine_cost,
    DIFF_RANGE_CONFIGS,
    REFINE_PILL_ITEM_ID,
)
from infrastructure.db.refine_pot_log_repo_mysql import RefinePotLogEntry


class RefinePotError(Exception):
    """炼妖相关错误"""


@dataclass
class RefineResult:
    main_beast_id: int
    attr_type: str
    before: int
    after: int
    delta: int
    diff_x: int
    cost_gold: int
    cost_pill: int
    sacrifice_hint: str

    def to_dict(self):
        return {
            "main_beast_id": self.main_beast_id,
            "attr_type": self.attr_type,
            "before": self.before,
            "after": self.after,
            "delta": self.delta,
            "diff_x": self.diff_x,
            "cost": {
                "gold": self.cost_gold,
                "pill": self.cost_pill,
            },
            "sacrifice_hint": self.sacrifice_hint,
        }


class RefinePotService:
    def __init__(
        self,
        player_repo,
        player_beast_repo,
        inventory_service,
        refine_log_repo=None,
        rand_func=None,
    ):
        self.player_repo = player_repo
        self.player_beast_repo = player_beast_repo
        self.inventory_service = inventory_service
        self.refine_log_repo = refine_log_repo
        self._rand_func = rand_func or random.randint

    def refine(self, user_id: int, main_id: int, material_id: int, attr_type: str) -> dict:
        attr_field = self._resolve_attr_field(attr_type)
        main_beast = self._get_owned_beast(user_id, main_id, label="主幻兽")
        material_beast = self._get_owned_beast(user_id, material_id, label="副幻兽")

        if main_beast.id == material_beast.id:
            raise RefinePotError("主幻兽与副幻兽不能相同")

        main_value = int(getattr(main_beast, attr_field, 0) or 0)
        sub_value = int(getattr(material_beast, attr_field, 0) or 0)

        diff_x = sub_value - main_value
        if diff_x <= 0:
            raise RefinePotError("副幻兽资质必须高于主幻兽")

        delta = self._roll_delta(diff_x)
        cost = get_refine_cost(attr_type)
        cost_gold = int(cost.get("gold", 0) or 0)
        cost_pill = int(cost.get("pill", 0) or 0)

        self._deduct_costs(user_id, cost_gold, cost_pill)

        after_value = max(0, main_value + delta)
        setattr(main_beast, attr_field, after_value)
        self.player_beast_repo.save(main_beast)

        deleted = False
        if hasattr(self.player_beast_repo, "delete_beast"):
            deleted = self.player_beast_repo.delete_beast(material_id, user_id)
        if not deleted and hasattr(self.player_beast_repo, "delete"):
            self.player_beast_repo.delete(material_id)

        self._write_log(
            user_id=user_id,
            main_id=main_id,
            material_id=material_id,
            attr_type=attr_type,
            before=main_value,
            after=after_value,
            delta=delta,
            diff_x=diff_x,
            cost_gold=cost_gold,
            cost_pill=cost_pill,
        )

        sacrifice_name = getattr(material_beast, "nickname", None) or getattr(material_beast, "name", "")
        hint = f'副幻兽「{sacrifice_name or material_beast.id}」已献祭，资质提升{delta}点'

        result = RefineResult(
            main_beast_id=main_id,
            attr_type=attr_type,
            before=main_value,
            after=after_value,
            delta=delta,
            diff_x=diff_x,
            cost_gold=cost_gold,
            cost_pill=cost_pill,
            sacrifice_hint=hint,
        )
        return result.to_dict()

    def _resolve_attr_field(self, attr_type: str) -> str:
        try:
            return get_attr_field(attr_type)
        except KeyError as exc:
            raise RefinePotError(str(exc)) from exc

    def _get_owned_beast(self, user_id: int, beast_id: int, label: str):
        beast = self.player_beast_repo.get_by_user_and_id(user_id, beast_id)
        if not beast:
            raise RefinePotError(f"{label}不存在")
        return beast

    def _roll_delta(self, diff_x: int) -> int:
        for cfg in DIFF_RANGE_CONFIGS:
            if diff_x >= cfg.min_diff and (cfg.max_diff is None or diff_x < cfg.max_diff):
                low, high = cfg.delta_range
                if low > high:
                    low, high = high, low
                return self._rand_func(low, high)
        return 0

    def _deduct_costs(self, user_id: int, gold: int, pills: int):
        if gold > 0:
            player = self.player_repo.get_by_id(user_id)
            if player is None:
                raise RefinePotError("玩家不存在")
            if player.gold < gold:
                raise RefinePotError("铜钱不足")
            player.gold -= gold
            self.player_repo.save(player)

        if pills > 0:
            if not self.inventory_service.has_item(user_id, REFINE_PILL_ITEM_ID, pills):
                raise RefinePotError("炼魂丹不足")
            self.inventory_service.remove_item(user_id, REFINE_PILL_ITEM_ID, pills)

    def _write_log(
        self,
        user_id: int,
        main_id: int,
        material_id: int,
        attr_type: str,
        before: int,
        after: int,
        delta: int,
        diff_x: int,
        cost_gold: int,
        cost_pill: int,
    ):
        if not self.refine_log_repo:
            return
        entry = RefinePotLogEntry(
            user_id=user_id,
            main_beast_id=main_id,
            material_beast_id=material_id,
            attr_type=attr_type,
            before_value=before,
            after_value=after,
            delta=delta,
            diff_x=diff_x,
            cost_gold=cost_gold,
            cost_pill=cost_pill,
        )
        self.refine_log_repo.insert_log(entry)
