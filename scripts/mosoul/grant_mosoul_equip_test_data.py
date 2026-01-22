"""
为指定用户发放“魔魂装备冲突规则”测试数据（无需启动HTTP服务，直接写DB）。

目标：
- 给 user_id=20051 准备一只玩家“正常可获得”的高等级幻兽（便于解锁足够槽位）
- 预装备 3 个魔魂到该幻兽，且与后续测试用魔魂形成冲突场景
- 在储魂器（beast_id=NULL）发放若干魔魂用于尝试装备并触发冲突提示

运行方式（项目根目录）：
    python scripts/mosoul/grant_mosoul_equip_test_data.py
"""

from __future__ import annotations

import sys
from typing import Optional

sys.path.insert(0, ".")

from infrastructure.db.connection import execute_query, execute_update, execute_insert


USER_ID = 20051

# 选择一只“玩家正常可获得”的幻兽作为测试载体（来自 configs/beast_templates.json）
# 例如：追风狼（template_id=6，地界）
TEST_BEAST_TEMPLATE_ID = 6
TEST_BEAST_REALM = "地界"
# 为了便于测试足够槽位，这里提升到较高等级；会先把玩家等级同步提升到可达范围（正常玩法可达）
TEST_PLAYER_TARGET_LEVEL = 100
TEST_BEAST_TARGET_LEVEL = 100


# ===== 测试用魔魂模板（来自 configs/mosoul_types.json）=====
# 预装备（用于制造冲突前置条件）
EQUIP_SEED = [
    # 龙魂：谁与争锋（速度%） -> 会阻止装备“速度%”的天/地/玄/黄魔魂
    {"template_id": 103, "slot_index": 1, "note": "龙魂·谁与争锋（速度%）"},
    # 天魂：天绝地灭（法攻%） -> 会阻止装备“法攻%”的地/玄/黄魂
    {"template_id": 203, "slot_index": 2, "note": "天魂·天绝地灭（法攻%）"},
    # 天魂：守护之魂（气血+） -> 会阻止装备“气血固定值”的地/玄/黄魂
    {"template_id": 202, "slot_index": 3, "note": "天魂·守护之魂（气血+）"},
]

# 储魂器发放（用于你在前端/接口上手动尝试装备，触发冲突）
STORAGE_GRANTS = [
    # 同名冲突：再给 1 个“天绝地灭”（同名同模板）
    {"template_id": 203, "count": 1, "note": "天魂·天绝地灭（同名冲突用）"},
    # 四系同属性%冲突：地魂·死亡吻（法攻%） 与已装备的天魂·天绝地灭冲突
    {"template_id": 303, "count": 1, "note": "地魂·死亡吻（法攻%冲突用）"},
    # 四系同属性固定值冲突：地魂·光明术（气血+） 与已装备的天魂·守护之魂冲突
    {"template_id": 309, "count": 1, "note": "地魂·光明术（气血固定值冲突用）"},
    # 龙魂%冲突：天魂·流星赶月（速度%）与已装备的龙魂·谁与争锋冲突
    {"template_id": 212, "count": 1, "note": "天魂·流星赶月（速度%与龙魂%冲突用）"},
    # 对照组：天魂·摄影逐日（速度+）不与龙魂速度%冲突
    {"template_id": 211, "count": 1, "note": "天魂·摄影逐日（速度+对照用）"},
]


def _require_player_exists(user_id: int) -> None:
    rows = execute_query("SELECT user_id FROM player WHERE user_id = %s", (int(user_id),))
    if not rows:
        raise RuntimeError(
            f"user_id={user_id} 不存在于 player 表，请先创建/注册该账号后再执行脚本。"
        )


def _ensure_player_level(user_id: int, level: int) -> None:
    """将玩家等级提升到指定值（仅用于测试准备，玩法可达的数据）。"""
    execute_update(
        "UPDATE player SET level = %s, exp = 0 WHERE user_id = %s",
        (int(level), int(user_id)),
    )


def _get_or_obtain_normal_beast(user_id: int) -> int:
    """获取或通过正规服务链路获得一只“可正常获取”的幻兽（避免造假名字/非法数据）。"""
    rows = execute_query(
        "SELECT id FROM player_beast WHERE user_id = %s AND template_id = %s AND realm = %s LIMIT 1",
        (int(user_id), int(TEST_BEAST_TEMPLATE_ID), TEST_BEAST_REALM),
    )
    if rows:
        return int(rows[0]["id"])

    # 通过 BeastService.obtain_beast_randomly 生成（与召唤球/捕捉等同链路，属于“正规可获得”）
    from interfaces.web_api.bootstrap import services

    beast = services.beast_service.obtain_beast_randomly(
        user_id=int(user_id),
        template_id=int(TEST_BEAST_TEMPLATE_ID),
        realm=TEST_BEAST_REALM,
        level=int(TEST_BEAST_TARGET_LEVEL),
    )
    return int(beast.id)


def _ensure_beast_level(beast_id: int, level: int) -> None:
    execute_update(
        "UPDATE player_beast SET level = %s, exp = 0 WHERE id = %s",
        (int(level), int(beast_id)),
    )


def _create_mosoul(user_id: int, template_id: int) -> int:
    return int(
        execute_insert(
            "INSERT INTO player_mosoul (user_id, template_id, level, exp, beast_id, slot_index) VALUES (%s, %s, 1, 0, NULL, NULL)",
            (int(user_id), int(template_id)),
        )
    )


def _find_unequipped_mosoul_id(user_id: int, template_id: int) -> Optional[int]:
    rows = execute_query(
        """
        SELECT id FROM player_mosoul
        WHERE user_id = %s AND template_id = %s AND beast_id IS NULL
        ORDER BY id ASC
        LIMIT 1
        """,
        (int(user_id), int(template_id)),
    )
    return int(rows[0]["id"]) if rows else None


def _count_unequipped(user_id: int, template_id: int) -> int:
    rows = execute_query(
        """
        SELECT COUNT(*) AS cnt FROM player_mosoul
        WHERE user_id = %s AND template_id = %s AND beast_id IS NULL
        """,
        (int(user_id), int(template_id)),
    )
    return int(rows[0]["cnt"]) if rows else 0


def _ensure_unequipped_count(user_id: int, template_id: int, need_count: int) -> int:
    """确保储魂器中至少有 need_count 个该模板的魔魂，返回本次新增数量。"""
    cur = _count_unequipped(user_id, template_id)
    to_add = max(0, int(need_count) - int(cur))
    for _ in range(to_add):
        _create_mosoul(user_id, template_id)
    return to_add


def _ensure_equipped_template_in_slot(
    user_id: int, beast_id: int, template_id: int, slot_index: int
) -> int:
    """确保某模板魔魂已装备在指定槽位，返回该魔魂id（必要时创建新的）。"""
    # 若该槽位已经是同模板，直接复用
    rows = execute_query(
        """
        SELECT id FROM player_mosoul
        WHERE user_id = %s AND beast_id = %s AND slot_index = %s AND template_id = %s
        LIMIT 1
        """,
        (int(user_id), int(beast_id), int(slot_index), int(template_id)),
    )
    if rows:
        return int(rows[0]["id"])

    # 若槽位被占，先清空（仅限测试幻兽，最小入侵：只动这一只兽的这一格）
    execute_update(
        "UPDATE player_mosoul SET beast_id = NULL, slot_index = NULL WHERE beast_id = %s AND slot_index = %s",
        (int(beast_id), int(slot_index)),
    )

    # 找一个未装备的同模板，没有就创建
    soul_id = _find_unequipped_mosoul_id(user_id, template_id)
    if soul_id is None:
        soul_id = _create_mosoul(user_id, template_id)

    # 装备到指定槽位
    execute_update(
        "UPDATE player_mosoul SET beast_id = %s, slot_index = %s WHERE id = %s",
        (int(beast_id), int(slot_index), int(soul_id)),
    )
    return int(soul_id)


def main() -> None:
    _require_player_exists(USER_ID)

    # 保证玩家等级足够（否则 BeastService 会按“玩家等级+5”上限裁剪幻兽等级）
    _ensure_player_level(USER_ID, TEST_PLAYER_TARGET_LEVEL)

    beast_id = _get_or_obtain_normal_beast(USER_ID)
    _ensure_beast_level(beast_id, TEST_BEAST_TARGET_LEVEL)

    # 输出真实幻兽信息（来自数据库，便于你核对“正常可获得”）
    rows = execute_query(
        "SELECT id, template_id, name, nickname, realm, level FROM player_beast WHERE id = %s LIMIT 1",
        (int(beast_id),),
    )
    if rows:
        r = rows[0]
        print(
            f"[OK] user_id={USER_ID} 测试幻兽 beast_id={r.get('id')} template_id={r.get('template_id')} "
            f"name={r.get('name')} nickname={r.get('nickname')} realm={r.get('realm')} level={r.get('level')}"
        )
    else:
        print(f"[OK] user_id={USER_ID} 测试幻兽 beast_id={beast_id}")

    # 预装备种子魔魂
    equipped_ids = []
    for item in EQUIP_SEED:
        sid = _ensure_equipped_template_in_slot(
            USER_ID, beast_id, item["template_id"], item["slot_index"]
        )
        equipped_ids.append((sid, item["template_id"], item["slot_index"], item["note"]))

    print("[OK] 已预装备魔魂：")
    for sid, tid, slot, note in equipped_ids:
        print(f"  - slot={slot} mosoul_id={sid} template_id={tid} ({note})")

    # 发放储魂器魔魂
    print("[OK] 发放储魂器魔魂：")
    for g in STORAGE_GRANTS:
        added = _ensure_unequipped_count(USER_ID, g["template_id"], g["count"])
        print(
            f"  - template_id={g['template_id']} need={g['count']} added={added} ({g['note']})"
        )

    print("\n你现在可以用前端/接口对 beast_id 进行装备测试，重点验证：")
    print("1) 同名冲突：再次装备 天魂·天绝地灭(template_id=203) 应被拒绝")
    print("2) 四系同属性%冲突：装备 地魂·死亡吻(template_id=303) 应被拒绝（与天魂·天绝地灭冲突）")
    print("3) 四系同属性固定值冲突：装备 地魂·光明术(template_id=309) 应被拒绝（与天魂·守护之魂冲突）")
    print("4) 龙魂%冲突：装备 天魂·流星赶月(template_id=212) 应被拒绝（与龙魂·谁与争锋冲突）")
    print("5) 对照：装备 天魂·摄影逐日(template_id=211) 应允许（速度+ 不与龙魂速度%冲突）")


if __name__ == "__main__":
    main()


