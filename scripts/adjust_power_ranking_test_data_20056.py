"""为 user_id=20056 调整“战力排行”测试数据（最高等级段：战神/北斗）。

目标：让测试号在“战力排行-最高等级段（战神/北斗）”里能搜到并有可验证排名。
实现方式（最小入侵）：
- 确保 player.level >= 80（落入最高段位）
- 确保至少存在 1 只出战幻兽（player_beast.is_in_team=1）
- 把出战队伍 combat_power 总和调整到“当前该段位最大值 + delta”

运行：
  python scripts/adjust_power_ranking_test_data_20056.py --dry_run
  python scripts/adjust_power_ranking_test_data_20056.py

可选：
  python scripts/adjust_power_ranking_test_data_20056.py --user_id 20056 --delta 50000
"""

import argparse
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from infrastructure.db.connection import execute_query, execute_update, execute_insert


TOP_TIER_MIN_LEVEL = 80
TOP_TIER_MAX_LEVEL = 100


def get_player(user_id: int) -> dict | None:
    rows = execute_query("SELECT user_id, nickname, level FROM player WHERE user_id=%s", (user_id,))
    return rows[0] if rows else None


def ensure_player_level(user_id: int, *, level: int, dry_run: bool) -> None:
    row = get_player(user_id)
    if not row:
        raise RuntimeError(f"player 不存在 user_id={user_id}")
    cur = int(row.get("level", 1) or 1)
    new_level = max(cur, int(level))
    if new_level == cur:
        return
    if dry_run:
        print(f"[dry-run] player.level {cur} -> {new_level}")
        return
    execute_update("UPDATE player SET level=%s WHERE user_id=%s", (new_level, user_id))
    print(f"[ok] player.level {cur} -> {new_level}")


def get_team_beasts(user_id: int) -> list[dict]:
    return execute_query(
        "SELECT id, name, combat_power FROM player_beast WHERE user_id=%s AND is_in_team=1 ORDER BY team_position ASC, id ASC",
        (user_id,),
    )


def insert_default_team_beast(user_id: int, *, dry_run: bool) -> int:
    """插入一只最小可用的出战幻兽，返回 beast_id"""
    name = f"测试幻兽{datetime.now().strftime('%H%M%S')}"
    realm = "神界"
    payload = (
        user_id,
        name,
        realm,
        "",  # race
        1,  # level
        "物系",
        1000, 100, 100, 100, 100, 100,  # 六维
        0,  # combat_power
        1,  # is_in_team
        1,  # team_position
        "[]",
    )
    sql = """
        INSERT INTO player_beast
        (user_id, name, realm, race, level, nature,
         hp, physical_attack, magic_attack, physical_defense, magic_defense, speed,
         combat_power, is_in_team, team_position, skills)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    if dry_run:
        print(f"[dry-run] insert player_beast user_id={user_id} name={name} is_in_team=1")
        return 0
    beast_id = execute_insert(sql, payload)
    print(f"[ok] inserted team beast id={beast_id} name={name}")
    return int(beast_id or 0)


def get_top_tier_max_power_excluding(user_id: int) -> int:
    rows = execute_query(
        """
        SELECT COALESCE(MAX(t.power), 0) AS mx FROM (
          SELECT p.user_id, COALESCE(SUM(b.combat_power), 0) AS power
          FROM player p
          LEFT JOIN player_beast b ON p.user_id=b.user_id AND b.is_in_team=1
          WHERE p.level BETWEEN %s AND %s AND p.user_id <> %s
          GROUP BY p.user_id
        ) t
        """,
        (TOP_TIER_MIN_LEVEL, TOP_TIER_MAX_LEVEL, user_id),
    )
    return int(rows[0].get("mx", 0) or 0) if rows else 0


def get_my_power(user_id: int) -> int:
    rows = execute_query(
        "SELECT COALESCE(SUM(combat_power),0) AS power FROM player_beast WHERE user_id=%s AND is_in_team=1",
        (user_id,),
    )
    return int(rows[0].get("power", 0) or 0) if rows else 0


def get_my_rank_in_top_tier(user_id: int) -> int | None:
    my_power = get_my_power(user_id)
    rows = execute_query(
        """
        SELECT COUNT(*) + 1 AS rk FROM (
          SELECT p.user_id, COALESCE(SUM(b.combat_power), 0) AS power
          FROM player p
          LEFT JOIN player_beast b ON p.user_id=b.user_id AND b.is_in_team=1
          WHERE p.level BETWEEN %s AND %s
          GROUP BY p.user_id
        ) t
        WHERE t.power > %s
        """,
        (TOP_TIER_MIN_LEVEL, TOP_TIER_MAX_LEVEL, my_power),
    )
    return int(rows[0].get("rk", 0) or 0) if rows else None


def set_team_power(user_id: int, target_total_power: int, *, dry_run: bool) -> None:
    beasts = get_team_beasts(user_id)
    if not beasts:
        insert_default_team_beast(user_id, dry_run=dry_run)
        beasts = get_team_beasts(user_id)

    if not beasts:
        raise RuntimeError("无法确保出战幻兽存在（player_beast 插入失败）")

    n = len(beasts)
    per = int((target_total_power + n - 1) / n)

    if dry_run:
        print(f"[dry-run] set team total_power -> {target_total_power} (n={n}, per_beast={per})")
        return

    for idx, b in enumerate(beasts):
        execute_update("UPDATE player_beast SET combat_power=%s WHERE id=%s", (per, int(b["id"])))
    print(f"[ok] updated {n} team beasts combat_power -> {per} each (target_total_power≈{per*n})")


def main():
    parser = argparse.ArgumentParser(description="调整战力排行测试数据（最高等级段）")
    parser.add_argument("--user_id", type=int, default=20056)
    parser.add_argument("--level", type=int, default=80, help="最低等级，落入最高段（默认80）")
    parser.add_argument("--delta", type=int, default=1000, help="比当前最高战力多多少（默认1000）")
    parser.add_argument("--dry_run", action="store_true")
    args = parser.parse_args()

    user_id = int(args.user_id)
    dry_run = bool(args.dry_run)
    delta = max(1, int(args.delta))

    p = get_player(user_id)
    if not p:
        raise SystemExit(f"玩家不存在 user_id={user_id}")

    print(f"调整战力排行测试数据：user_id={user_id} nickname={p.get('nickname')} dry_run={dry_run}")

    ensure_player_level(user_id, level=args.level, dry_run=dry_run)

    mx = get_top_tier_max_power_excluding(user_id)
    target = mx + delta
    print(f"最高段位(80-100) 其他玩家最大战力={mx}，目标战力={target}")

    set_team_power(user_id, target, dry_run=dry_run)

    if not dry_run:
        my_power = get_my_power(user_id)
        rk = get_my_rank_in_top_tier(user_id)
        print(f"[ok] 当前出战战力={my_power}，在最高段位榜单排名≈{rk}")


if __name__ == "__main__":
    main()


