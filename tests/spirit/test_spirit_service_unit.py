"""战灵服务单元测试（无需启动HTTP服务 / 无需数据库）

运行方式（项目根目录）：
    python -m pytest tests/spirit/test_spirit_service_unit.py -vv -s
"""

import pytest
import sys

sys.path.insert(0, '.')

from domain.entities.player import Player
from domain.entities.spirit import Spirit, SpiritLine, SpiritAccount
from application.services.spirit_service import SpiritService, SpiritError
from application.services.inventory_service import InventoryError


class MockSpiritRepo:
    def __init__(self):
        self._data = {}
        self._next_id = 1

    def get_by_user_id(self, user_id: int):
        return [s for s in self._data.values() if s.user_id == user_id]

    def get_by_id(self, spirit_id: int):
        return self._data.get(spirit_id)

    def get_by_beast_id(self, beast_id: int):
        return [s for s in self._data.values() if s.beast_id == beast_id]

    def save(self, spirit: Spirit) -> None:
        if spirit.id is None:
            spirit.id = self._next_id
            self._next_id += 1
        self._data[spirit.id] = spirit

    def delete(self, spirit_id: int) -> None:
        if spirit_id in self._data:
            del self._data[spirit_id]


class MockSpiritAccountRepo:
    def __init__(self):
        self._data = {}

    def get_by_user_id(self, user_id: int) -> SpiritAccount:
        acc = self._data.get(user_id)
        if acc is None:
            acc = SpiritAccount(user_id=user_id, spirit_power=0, unlocked_elements=[])
            self._data[user_id] = acc
        return acc

    def save(self, account: SpiritAccount) -> None:
        self._data[account.user_id] = account


class MockInventoryService:
    def __init__(self):
        self.items = {}  # (user_id, item_id) -> qty

    def add_item(self, user_id: int, item_id: int, quantity: int) -> None:
        key = (user_id, item_id)
        self.items[key] = self.items.get(key, 0) + quantity

    def remove_item(self, user_id: int, item_id: int, quantity: int = 1):
        key = (user_id, item_id)
        owned = self.items.get(key, 0)
        if owned < quantity:
            raise InventoryError("物品数量不足")
        self.items[key] = owned - quantity
        return True


class MockPlayerRepo:
    def __init__(self):
        self.players = {}

    def get_by_id(self, user_id: int):
        return self.players.get(user_id)

    def save(self, player: Player) -> None:
        self.players[player.user_id] = player


class MockTowerState:
    def __init__(self, max_floor_record: int):
        self.max_floor_record = max_floor_record


class MockTowerStateRepo:
    def __init__(self, max_floor_record: int = 1):
        self.max_floor_record = max_floor_record

    def get_by_user_id(self, user_id: int, tower_type: str):
        return MockTowerState(self.max_floor_record)


class MockPlayerBeast:
    def __init__(self, beast_id: int, user_id: int, race: str, nature: str):
        self.id = beast_id
        self.user_id = user_id
        self.race = race
        self.nature = nature


class MockPlayerBeastRepo:
    def __init__(self):
        self.beasts = {}

    def add(self, b: MockPlayerBeast):
        self.beasts[b.id] = b

    def get_by_id(self, beast_id: int):
        return self.beasts.get(beast_id)


@pytest.fixture()
def svc():
    spirit_repo = MockSpiritRepo()
    account_repo = MockSpiritAccountRepo()
    inv = MockInventoryService()
    player_repo = MockPlayerRepo()
    tower_repo = MockTowerStateRepo(max_floor_record=120)
    beast_repo = MockPlayerBeastRepo()

    player_repo.players[1] = Player(user_id=1, nickname="p1", level=1, exp=0, gold=200000)

    service = SpiritService(
        spirit_repo=spirit_repo,
        account_repo=account_repo,
        inventory_service=inv,
        player_repo=player_repo,
        tower_state_repo=tower_repo,
        player_beast_repo=beast_repo,
    )

    return service


def test_unlock_element_requires_floor_and_gold(svc: SpiritService):
    # 让塔层不足
    svc.tower_state_repo.max_floor_record = 0
    with pytest.raises(SpiritError):
        svc.unlock_element(1, "fire")

    # 塔层够，但铜钱不足
    svc.tower_state_repo.max_floor_record = 120
    p = svc.player_repo.get_by_id(1)
    p.gold = 0
    svc.player_repo.save(p)

    with pytest.raises(SpiritError):
        svc.unlock_element(1, "fire")

    # 铜钱够，成功解锁
    p = svc.player_repo.get_by_id(1)
    p.gold = 200000
    svc.player_repo.save(p)

    acc = svc.unlock_element(1, "fire")
    assert "fire" in acc.unlocked_elements


def test_open_stone_creates_spirits_and_consumes_items(svc: SpiritService):
    # earth 的未开灵石 id = 7101（来自配置）
    svc.inventory_service.add_item(1, 7101, 2)

    created = svc.open_stone(1, "earth", quantity=2)
    assert len(created) == 2

    # 扣除
    assert svc.inventory_service.items[(1, 7101)] == 0

    # 战灵结构
    for s in created:
        assert s.spirit.element == "earth"
        assert len(s.spirit.lines) == 3
        assert s.spirit.lines[0].unlocked is True
        assert s.spirit.lines[1].unlocked in (False, True)

        keys = [ln.attr_key for ln in s.spirit.lines if ln.attr_key]
        assert len(keys) == len(set(keys))


def test_unlock_line_consumes_keys(svc: SpiritService):
    svc.inventory_service.add_item(1, 7101, 1)
    created = svc.open_stone(1, "earth", quantity=1)
    spirit_id = created[0].spirit.id

    # 解锁第2条需要钥匙 6006
    svc.inventory_service.add_item(1, 6006, 1)

    s2 = svc.unlock_line(1, spirit_id, 2)
    assert s2.spirit.get_line(2).unlocked is True
    assert svc.inventory_service.items[(1, 6006)] == 0


def test_refine_cost_and_lock_behavior(svc: SpiritService):
    # 造一个全解锁战灵
    sp = Spirit(
        user_id=1,
        element="earth",
        race="兽族",
        lines=[
            SpiritLine(attr_key="hp_pct", value_bp=100, unlocked=True, locked=True),
            SpiritLine(attr_key="attack_pct", value_bp=120, unlocked=True, locked=False),
            SpiritLine(attr_key="speed_pct", value_bp=130, unlocked=True, locked=False),
        ],
    )
    svc.spirit_repo.save(sp)

    acc = svc.get_account(1)
    acc.spirit_power = 999
    svc.account_repo.save(acc)

    result = svc.refine(1, sp.id)
    assert result["used_free"] is False
    assert result["cost_spirit_power"] == 20  # 1条锁定 => 20（来自配置）

    sp_after = svc.spirit_repo.get_by_id(sp.id)
    assert sp_after.get_line(1).locked is True
    assert sp_after.get_line(1).attr_key == "hp_pct"
    assert sp_after.get_line(1).value_bp == 100

    # 未锁定两条应与锁定条不重复，且互不重复
    attrs = [sp_after.get_line(i).attr_key for i in (1, 2, 3) if sp_after.get_line(i).unlocked]
    assert len(attrs) == len(set(attrs))


def test_attack_pct_maps_to_main_attack_type(svc: SpiritService):
    sp = Spirit(
        user_id=1,
        beast_id=999,
        element="earth",
        race="兽族",
        lines=[SpiritLine(attr_key="attack_pct", value_bp=123, unlocked=True, locked=False)],
    )
    svc.spirit_repo.save(sp)

    bonus_magic = svc.calc_percent_bonus_bp_for_beast(999, beast_nature="法系普攻")
    assert bonus_magic["magic_attack_pct"] == 123
    assert bonus_magic["physical_attack_pct"] == 0

    bonus_phys = svc.calc_percent_bonus_bp_for_beast(999, beast_nature="物系普攻")
    assert bonus_phys["physical_attack_pct"] == 123
    assert bonus_phys["magic_attack_pct"] == 0
