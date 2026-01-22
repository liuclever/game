"""
招财神符(6004) - VIP 每日使用次数限制 单元测试（不连数据库）

运行方式（项目根目录）：
    python -m pytest tests/inventory/test_fortune_talisman_limit_unit.py -vv -s
"""

import sys
import pytest

sys.path.insert(0, ".")

import application.services.inventory_service as invsvc


class _MockInvItem:
    def __init__(self, inv_id: int, user_id: int, item_id: int, quantity: int):
        self.id = inv_id
        self.user_id = user_id
        self.item_id = item_id
        self.quantity = quantity
        self.is_temporary = False


class _MockItemTemplate:
    def __init__(self, item_id: int, name: str, type_: str = "consumable"):
        self.id = item_id
        self.name = name
        self.type = type_
        self.stackable = True


class _MockInventoryRepo:
    def __init__(self, inv_item: _MockInvItem):
        self._item = inv_item
        self.deleted = False
        self.saved = False

    def get_by_id(self, inv_id: int):
        return self._item if (not self.deleted and self._item and self._item.id == inv_id) else None

    def delete(self, inv_id: int):
        self.deleted = True

    def save(self, inv_item):
        self.saved = True
        self._item = inv_item


class _MockItemRepo:
    def __init__(self, template: _MockItemTemplate):
        self._tpl = template

    def get_by_id(self, item_id: int):
        return self._tpl if int(item_id) == int(self._tpl.id) else None


class _MockPlayer:
    def __init__(self, level: int, vip_level: int, gold: int = 0):
        self.level = level
        self.vip_level = vip_level
        self.gold = gold


class _MockPlayerRepo:
    def __init__(self, player: _MockPlayer):
        self._p = player

    def get_by_id(self, user_id: int):
        return self._p

    def save(self, player):
        self._p = player


def test_vip8_limit_10_blocks_11th(monkeypatch):
    # 伪造 DB：fortune_talisman_daily 今日已用 10 次
    state = {"count": 10}

    def fake_execute_query(sql: str, params=None):
        if "FROM fortune_talisman_daily" in sql:
            return [{"use_count": state["count"]}]
        return []

    def fake_execute_update(sql: str, params=None):
        # set used today
        if "INSERT INTO fortune_talisman_daily" in sql:
            # params = (user_id, cnt)
            state["count"] = int(params[1])
        return 1

    monkeypatch.setattr(invsvc, "execute_query", fake_execute_query)
    monkeypatch.setattr(invsvc, "execute_update", fake_execute_update)

    inv_item = _MockInvItem(inv_id=1, user_id=20052, item_id=6004, quantity=99)
    svc = invsvc.InventoryService(
        item_repo=_MockItemRepo(_MockItemTemplate(6004, "招财神符")),
        inventory_repo=_MockInventoryRepo(inv_item),
        player_repo=_MockPlayerRepo(_MockPlayer(level=50, vip_level=8, gold=0)),
    )

    with pytest.raises(invsvc.InventoryError) as e:
        svc.use_item(user_id=20052, inv_item_id=1, quantity=1)
    assert "已达上限" in str(e.value)


def test_vip8_allows_up_to_10_and_consumes_only_allowed(monkeypatch):
    # 今日已用 9 次，本次请求用 3，应该只用 1（剩余=1）
    state = {"count": 9}

    def fake_execute_query(sql: str, params=None):
        if "FROM fortune_talisman_daily" in sql:
            return [{"use_count": state["count"]}]
        return []

    def fake_execute_update(sql: str, params=None):
        if "INSERT INTO fortune_talisman_daily" in sql:
            state["count"] = int(params[1])
        return 1

    monkeypatch.setattr(invsvc, "execute_query", fake_execute_query)
    monkeypatch.setattr(invsvc, "execute_update", fake_execute_update)

    inv_item = _MockInvItem(inv_id=1, user_id=20052, item_id=6004, quantity=99)
    player = _MockPlayer(level=50, vip_level=8, gold=0)
    svc = invsvc.InventoryService(
        item_repo=_MockItemRepo(_MockItemTemplate(6004, "招财神符")),
        inventory_repo=_MockInventoryRepo(inv_item),
        player_repo=_MockPlayerRepo(player),
    )

    result = svc.use_item(user_id=20052, inv_item_id=1, quantity=3)
    assert "招财神符×1" in result.get("message", "")
    assert state["count"] == 10
    assert inv_item.quantity == 98  # 只扣 1 个


