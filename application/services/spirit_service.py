from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Dict, Optional, Any
import random

from domain.entities.spirit import Spirit, SpiritLine, SpiritAccount
from domain.repositories.spirit_repo import ISpiritRepo, ISpiritAccountRepo
from domain.repositories.player_repo import IPlayerRepo
from domain.repositories.tower_repo import ITowerStateRepo
from infrastructure.config.spirit_system_config import get_spirit_system_config
from application.services.inventory_service import InventoryError


class SpiritError(Exception):
    pass


@dataclass
class SpiritWithInfo:
    spirit: Spirit
    element_name: str = ""

    def to_dict(self) -> Dict[str, Any]:
        data = self.spirit.to_dict()
        data["element_name"] = self.element_name
        return data


class SpiritService:
    def __init__(
        self,
        *,
        spirit_repo: ISpiritRepo,
        account_repo: ISpiritAccountRepo,
        inventory_service,
        player_repo: IPlayerRepo,
        tower_state_repo: ITowerStateRepo,
        player_beast_repo,
    ) -> None:
        self.spirit_repo = spirit_repo
        self.account_repo = account_repo
        self.inventory_service = inventory_service
        self.player_repo = player_repo
        self.tower_state_repo = tower_state_repo
        self.player_beast_repo = player_beast_repo
        self.config = get_spirit_system_config()

    def _require_level_35(self, user_id: int) -> None:
        player = self.player_repo.get_by_id(user_id)
        player_level = int(getattr(player, "level", 0) or 0) if player else 0
        if player_level < 35:
            raise SpiritError("35级才能解锁战灵功能")

    # ===================== 账户 =====================
    def get_account(self, user_id: int) -> SpiritAccount:
        acc = self.account_repo.get_by_user_id(user_id)

        player = self.player_repo.get_by_id(user_id)
        player_level = int(getattr(player, "level", 0) or 0) if player else 0
        all_elements = [str(e.get("key")) for e in (self.config.get_elements() or []) if e and e.get("key")]

        if player_level >= 35:
            defaults = set(self.config.get_default_unlocked_elements())
            current = set(acc.unlocked_elements or [])
            merged = list(sorted(current | defaults | set(all_elements)))
        else:
            merged = []

        if merged != (acc.unlocked_elements or []):
            acc.unlocked_elements = merged
            self.account_repo.save(acc)
        return acc

    # ===================== 查询 =====================
    def get_spirits(self, user_id: int) -> List[SpiritWithInfo]:
        spirits = self.spirit_repo.get_by_user_id(user_id)
        res: List[SpiritWithInfo] = []
        for s in spirits:
            res.append(SpiritWithInfo(spirit=s, element_name=self.config.get_element_name(s.element)))
        return res

    def get_spirit(self, user_id: int, spirit_id: int) -> Optional[SpiritWithInfo]:
        s = self.spirit_repo.get_by_id(spirit_id)
        if s is None or s.user_id != user_id:
            return None
        return SpiritWithInfo(spirit=s, element_name=self.config.get_element_name(s.element))

    # ===================== 解锁元素孔位 =====================
    def unlock_element(self, user_id: int, element_key: str) -> SpiritAccount:
        if not self.config.is_valid_element(element_key):
            raise SpiritError("未知元素")

        player = self.player_repo.get_by_id(user_id)
        player_level = int(getattr(player, "level", 0) or 0) if player else 0
        if player_level < 35:
            raise SpiritError("35级才能解锁")

        acc = self.get_account(user_id)
        if element_key in (acc.unlocked_elements or []):
            return acc

        req = self.config.get_unlock_requirement(element_key)
        if not req:
            raise SpiritError("元素解锁配置缺失")

        tower_type = req.get("tower_type", "zhanling")
        need_floor = int(req.get("min_floor_record", 0) or 0)
        gold_cost = int(req.get("gold_cost", 0) or 0)

        state = self.tower_state_repo.get_by_user_id(user_id, tower_type)
        if state.max_floor_record < need_floor:
            raise SpiritError(f"战灵塔层数不足，需要达到{need_floor}层")

        player = self.player_repo.get_by_id(user_id)
        if player is None:
            raise SpiritError("玩家不存在")

        if gold_cost > 0:
            if player.gold < gold_cost:
                raise SpiritError("铜钱不足")
            player.gold -= gold_cost
            self.player_repo.save(player)

        acc.unlocked_elements = list(sorted(set(acc.unlocked_elements or []) | {element_key}))
        self.account_repo.save(acc)
        return acc

    # ===================== 开启灵石 =====================
    def open_stone(self, user_id: int, element_key: str, quantity: int = 1) -> List[SpiritWithInfo]:
        self._require_level_35(user_id)
        if quantity <= 0:
            raise SpiritError("quantity 必须是正整数")
        if not self.config.is_valid_element(element_key):
            raise SpiritError("未知元素")

        stone_item_id = self.config.get_unopened_stone_item_id(element_key)
        if stone_item_id <= 0:
            raise SpiritError("未配置该元素的灵石 item_id")

        # 仓库容量检查（按“总战灵数”限制）
        current_count = len(self.spirit_repo.get_by_user_id(user_id))
        capacity = self.config.get_warehouse_capacity()
        if current_count + quantity > capacity:
            raise SpiritError("战灵仓库已满")

        # 扣除灵石
        try:
            self.inventory_service.remove_item(user_id=user_id, item_id=stone_item_id, quantity=quantity)
        except InventoryError as e:
            raise SpiritError(str(e))

        created: List[SpiritWithInfo] = []
        for _ in range(quantity):
            sp = self._roll_new_spirit(user_id=user_id, element_key=element_key)
            self.spirit_repo.save(sp)
            created.append(SpiritWithInfo(spirit=sp, element_name=self.config.get_element_name(sp.element)))
        return created

    # ===================== 穿戴/卸下 =====================
    def equip_spirit(self, user_id: int, beast_id: int, spirit_id: int) -> SpiritWithInfo:
        if beast_id <= 0:
            raise SpiritError("beast_id 必须是正整数")

        player = self.player_repo.get_by_id(user_id)
        player_level = int(getattr(player, "level", 0) or 0) if player else 0
        if player_level < 35:
            raise SpiritError("35级才能解锁")

        sp = self.spirit_repo.get_by_id(spirit_id)
        if sp is None or sp.user_id != user_id:
            raise SpiritError("战灵不存在")

        beast = self.player_beast_repo.get_by_id(beast_id)
        if beast is None or getattr(beast, "user_id", 0) != user_id:
            raise SpiritError("幻兽不存在")

        acc = self.get_account(user_id)
        if sp.element not in (acc.unlocked_elements or []):
            raise SpiritError("该元素孔位未解锁")

        # 种族匹配
        beast_race = getattr(beast, "race", "") or ""
        # 若幻兽种族为空（历史数据缺失），不阻断装备；否则严格匹配
        if sp.race and beast_race and sp.race != beast_race:
            raise SpiritError("战灵种族与幻兽不匹配")

        # 同一只幻兽同一元素只能装备一枚：先卸下旧的
        for old in self.spirit_repo.get_by_beast_id(beast_id):
            if old.id != sp.id and old.element == sp.element:
                old.beast_id = None
                self.spirit_repo.save(old)

        sp.beast_id = beast_id
        self.spirit_repo.save(sp)
        return SpiritWithInfo(spirit=sp, element_name=self.config.get_element_name(sp.element))

    def unequip_spirit(self, user_id: int, spirit_id: int) -> SpiritWithInfo:
        sp = self.spirit_repo.get_by_id(spirit_id)
        if sp is None or sp.user_id != user_id:
            raise SpiritError("战灵不存在")
        sp.beast_id = None
        self.spirit_repo.save(sp)
        return SpiritWithInfo(spirit=sp, element_name=self.config.get_element_name(sp.element))

    # ===================== 词条解锁/锁定 =====================
    def unlock_line(self, user_id: int, spirit_id: int, line_index: int) -> SpiritWithInfo:
        self._require_level_35(user_id)
        if line_index not in (2, 3):
            raise SpiritError("仅支持解锁第2/第3条词条")

        sp = self.spirit_repo.get_by_id(spirit_id)
        if sp is None or sp.user_id != user_id:
            raise SpiritError("战灵不存在")

        line = sp.get_line(line_index)
        if line.unlocked:
            return SpiritWithInfo(spirit=sp, element_name=self.config.get_element_name(sp.element))

        cost = self.config.get_line_unlock_cost(sp.element, line_index)
        if not cost:
            raise SpiritError("词条解锁配置缺失")

        item_id = int(cost.get("key_item_id", 0) or 0)
        qty = int(cost.get("quantity", 0) or 0)
        if item_id <= 0 or qty <= 0:
            raise SpiritError("词条解锁配置无效")

        try:
            self.inventory_service.remove_item(user_id=user_id, item_id=item_id, quantity=qty)
        except InventoryError as e:
            raise SpiritError(str(e))

        # 解锁后，为该词条补一次随机（避免空词条）
        if not line.attr_key:
            line.attr_key, line.value_bp = self._roll_attr_and_value(sp.element, exclude_attrs=self._current_attr_set(sp, exclude_index=line_index))
        line.unlocked = True
        line.locked = False

        self.spirit_repo.save(sp)
        return SpiritWithInfo(spirit=sp, element_name=self.config.get_element_name(sp.element))

    def set_line_lock(self, user_id: int, spirit_id: int, line_index: int, locked: bool) -> SpiritWithInfo:
        self._require_level_35(user_id)
        # 兼容前端旧实现：line_index=0 表示锁定/解锁第1条（用于“整只战灵锁定”）
        if line_index == 0:
            line_index = 1
        if line_index not in (1, 2, 3):
            raise SpiritError("line_index must be 1..3")

        sp = self.spirit_repo.get_by_id(spirit_id)
        if sp is None or sp.user_id != user_id:
            raise SpiritError("战灵不存在")

        line = sp.get_line(line_index)
        if not line.unlocked:
            raise SpiritError("词条未解锁")
        line.locked = bool(locked)

        self.spirit_repo.save(sp)
        return SpiritWithInfo(spirit=sp, element_name=self.config.get_element_name(sp.element))

    # ===================== 洗练 =====================
    def refine(self, user_id: int, spirit_id: int) -> Dict[str, Any]:
        self._require_level_35(user_id)
        sp = self.spirit_repo.get_by_id(spirit_id)
        if sp is None or sp.user_id != user_id:
            raise SpiritError("战灵不存在")

        acc = self.get_account(user_id)
        player = self.player_repo.get_by_id(user_id)
        vip = int(getattr(player, "vip_level", 0) or 0) if player else 0

        # 每日免费次数重置
        today = date.today()
        if acc.free_refine_date != today:
            acc.free_refine_date = today
            acc.free_refine_used = 0

        free_total = self.config.get_vip_free_refines_per_day(vip)
        free_left = max(0, free_total - int(acc.free_refine_used or 0))

        locked_count = sp.locked_unlocked_count()
        cost_power = 0
        used_free = False

        if free_left > 0:
            used_free = True
            acc.free_refine_used = int(acc.free_refine_used or 0) + 1
        else:
            cost_power = self.config.get_refine_cost_by_element_and_locked(sp.element, locked_count)
            if acc.spirit_power < cost_power:
                raise SpiritError("灵力不足")
            acc.spirit_power -= cost_power

        # 重新随机未锁定且已解锁的词条
        used_attrs = set()
        # 先把锁定词条占用的属性放进 used_attrs，防止重复
        for idx in (1, 2, 3):
            ln = sp.get_line(idx)
            if ln.unlocked and ln.locked and ln.attr_key:
                used_attrs.add(ln.attr_key)

        for idx in (1, 2, 3):
            ln = sp.get_line(idx)
            if not ln.unlocked:
                continue
            if ln.locked:
                continue

            ln.attr_key, ln.value_bp = self._roll_attr_and_value(sp.element, exclude_attrs=used_attrs)
            used_attrs.add(ln.attr_key)

        self.spirit_repo.save(sp)
        self.account_repo.save(acc)

        return {
            "spirit": SpiritWithInfo(spirit=sp, element_name=self.config.get_element_name(sp.element)).to_dict(),
            "cost_spirit_power": cost_power,
            "used_free": used_free,
            "account": acc.to_dict(),
        }

    # ===================== 出售 =====================
    def sell(self, user_id: int, spirit_id: int) -> Dict[str, Any]:
        self._require_level_35(user_id)
        sp = self.spirit_repo.get_by_id(spirit_id)
        if sp is None or sp.user_id != user_id:
            raise SpiritError("战灵不存在")

        gain = self.config.get_sell_spirit_power(sp.element)
        acc = self.get_account(user_id)
        acc.spirit_power += gain
        self.account_repo.save(acc)

        self.spirit_repo.delete(spirit_id)

        return {"gained_spirit_power": gain, "account": acc.to_dict()}

    # ===================== 灵力水晶兑换灵力 =====================
    def consume_spirit_crystal(self, user_id: int, quantity: int = 1) -> Dict[str, Any]:
        self._require_level_35(user_id)
        """
        消耗“灵力水晶”获得灵力。
        规则（战灵拓展.txt）：1 个灵力水晶 = +10 灵力
        """
        qty = int(quantity or 0)
        if qty <= 0:
            raise SpiritError("quantity 必须是正整数")
        if qty > 10:
            # 与背包批量规则一致，避免一次性过大（可多次兑换）
            qty = 10

        SPIRIT_CRYSTAL_ITEM_ID = 6101
        POWER_PER_CRYSTAL = 10

        try:
            self.inventory_service.remove_item(user_id=user_id, item_id=SPIRIT_CRYSTAL_ITEM_ID, quantity=qty)
        except InventoryError as e:
            raise SpiritError(str(e))

        acc = self.get_account(user_id)
        acc.spirit_power = int(acc.spirit_power or 0) + qty * POWER_PER_CRYSTAL
        self.account_repo.save(acc)

        return {
            "gained_spirit_power": qty * POWER_PER_CRYSTAL,
            "used_crystals": qty,
            "account": acc.to_dict(),
        }

    # ===================== 计算加成（供战斗/展示复用） =====================
    def calc_percent_bonus_bp_for_beast(self, beast_id: int, beast_nature: str) -> Dict[str, int]:
        """计算某只幻兽身上所有已装备战灵带来的百分比加成（basis points）。

        attack_pct 需要按主攻类型映射：nature 含“法”则映射到 magic_attack_pct，否则映射到 physical_attack_pct。
        """
        equipped = self.spirit_repo.get_by_beast_id(beast_id)

        is_magic = "法" in (beast_nature or "")

        bonus = {
            "hp_pct": 0,
            "physical_attack_pct": 0,
            "magic_attack_pct": 0,
            "physical_defense_pct": 0,
            "magic_defense_pct": 0,
            "speed_pct": 0,
        }

        for sp in equipped:
            for ln in sp.unlocked_lines():
                if not ln.attr_key:
                    continue
                if ln.attr_key == "attack_pct":
                    key = "magic_attack_pct" if is_magic else "physical_attack_pct"
                    bonus[key] += int(ln.value_bp)
                elif ln.attr_key in bonus:
                    bonus[ln.attr_key] += int(ln.value_bp)

        return bonus

    def calc_spirit_bonus_for_beast(
        self, beast_id: int, beast_nature: str, base_stats: Dict[str, int]
    ) -> Dict[str, int]:
        """计算战灵对幻兽各属性的实际加成值"""
        bonus_bp = self.calc_percent_bonus_bp_for_beast(beast_id, beast_nature)
        return {
            "hp": int(base_stats.get("hp", 0) * bonus_bp.get("hp_pct", 0) / 10000),
            "physical_attack": int(base_stats.get("physical_attack", 0) * bonus_bp.get("physical_attack_pct", 0) / 10000),
            "magic_attack": int(base_stats.get("magic_attack", 0) * bonus_bp.get("magic_attack_pct", 0) / 10000),
            "physical_defense": int(base_stats.get("physical_defense", 0) * bonus_bp.get("physical_defense_pct", 0) / 10000),
            "magic_defense": int(base_stats.get("magic_defense", 0) * bonus_bp.get("magic_defense_pct", 0) / 10000),
            "speed": int(base_stats.get("speed", 0) * bonus_bp.get("speed_pct", 0) / 10000),
        }

    # ===================== 内部：随机逻辑 =====================
    def _roll_new_spirit(self, user_id: int, element_key: str) -> Spirit:
        race = self._pick_weighted(self.config.get_race_weights(element_key))

        # 战灵初始自带 1 条属性，最多 3 条；第2/3条需战灵钥匙激活
        attr, val_bp = self._roll_attr_and_value(element_key)
        lines: List[SpiritLine] = [
            SpiritLine(attr_key=attr, value_bp=val_bp, unlocked=True, locked=False),
            SpiritLine(attr_key="", value_bp=0, unlocked=False, locked=False),
            SpiritLine(attr_key="", value_bp=0, unlocked=False, locked=False),
        ]

        return Spirit(user_id=user_id, beast_id=None, element=element_key, race=race, lines=lines)

    def _pick_weighted(self, weights: Dict[str, int]) -> str:
        if not weights:
            return ""
        total = sum(max(0, int(v)) for v in weights.values())
        if total <= 0:
            return next(iter(weights.keys()))
        roll = random.randint(1, total)
        cur = 0
        for k, v in weights.items():
            cur += max(0, int(v))
            if roll <= cur:
                return str(k)
        return str(next(iter(weights.keys())))

    def _roll_attr_and_value(self, element_key: str, exclude_attrs: set[str] = None) -> tuple[str, int]:
        """ 随机选择一个属性和对应的数值（等概率选择6种属性之一） """
        if exclude_attrs is None:
            exclude_attrs = set()
            
        pool = self.config.get_attr_pool()
        candidates = [p for p in pool if p.get("key") and p.get("key") not in exclude_attrs]
        if not candidates:
            candidates = [p for p in pool if p.get("key")]
        if not candidates:
            return "", 0

        # 等概率选择属性
        total_weight = sum(int(p.get("weight", 1) or 1) for p in candidates)
        roll = random.randint(1, total_weight)
        cur = 0
        picked = candidates[0]
        for p in candidates:
            cur += int(p.get("weight", 1) or 1)
            if roll <= cur:
                picked = p
                break

        attr_key = str(picked.get("key") or "")
        
        # 获取该元素的属性值范围（所有属性共享同一范围）
        mn, mx = self.config.get_value_range_bp(element_key)
        if mn == 0 and mx == 0:
            mx = 1
        value_bp = random.randint(mn, mx)
        return attr_key, int(value_bp)

    def _current_attr_set(self, sp: Spirit, exclude_index: int = 0) -> set[str]:
        s = set()
        for idx in (1, 2, 3):
            if idx == exclude_index:
                continue
            ln = sp.get_line(idx)
            if ln.attr_key:
                s.add(ln.attr_key)
        return s
