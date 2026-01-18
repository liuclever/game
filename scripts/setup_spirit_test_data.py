"""为指定玩家灌入“战灵系统”测试数据（默认 user_id=20052）。

目标：用于测试本次战灵拓展功能（灵石开启/词条激活钥匙消耗/洗练/出售/灵力水晶兑换）。

运行示例（项目根目录）：
  python scripts/setup_spirit_test_data.py --user_id 20052 --dry_run
  python scripts/setup_spirit_test_data.py --user_id 20052

说明（最小入侵）：
- 不强行创建幻兽/不自动装备战灵（避免污染其它业务），仅往灵件室生成战灵样本。
- 直接把 spirit_account 的 unlocked_elements 设置为 6 元素（便于测试激活/装备等路径）。
- 给背包发放：战灵钥匙(6006)、灵力水晶(6101)、六系灵石(7101-7106)。
"""

import argparse
import os
import sys
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Windows 控制台乱码兼容
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from infrastructure.db.connection import execute_query, execute_update
from infrastructure.config.item_repo_from_config import ConfigItemRepo
from infrastructure.db.inventory_repo_mysql import MySQLInventoryRepo
from infrastructure.db.player_repo_mysql import MySQLPlayerRepo
from infrastructure.db.spirit_repo_mysql import MySQLSpiritRepo
from infrastructure.db.spirit_account_repo_mysql import MySQLSpiritAccountRepo
from infrastructure.db.tower_state_repo_mysql import MySQLTowerStateRepo
from infrastructure.db.player_beast_repo_mysql import MySQLPlayerBeastRepo

from application.services.inventory_service import InventoryService
from application.services.spirit_service import SpiritService
from infrastructure.config.spirit_system_config import get_spirit_system_config


ALL_ELEMENTS = ["earth", "fire", "water", "wood", "metal", "god"]
ELEMENT_NAME = {"earth": "土", "fire": "火", "water": "水", "wood": "木", "metal": "金", "god": "神"}

SPIRIT_KEY_ITEM_ID = 6006
SPIRIT_CRYSTAL_ITEM_ID = 6101
STONE_ITEM_IDS = {"earth": 7101, "fire": 7102, "water": 7103, "wood": 7104, "metal": 7105, "god": 7106}

def _load_spirit_system_json() -> dict:
    base_dir = Path(__file__).resolve().parents[1]
    path = base_dir / "configs" / "spirit_system.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _get_all_races() -> list[str]:
    """按配置获取所有种族（默认：虫族/兽族/水族/羽族）。"""
    try:
        cfg = _load_spirit_system_json()
        races = cfg.get("races", []) or []
        races = [str(x) for x in races if str(x).strip()]
        if races:
            return races
    except Exception:
        pass
    return ["虫族", "兽族", "水族", "羽族"]


def _get_all_attr_keys() -> list[str]:
    """按配置获取词条属性 key 列表（如 hp_pct/physical_attack_pct/...）。"""
    cfg = get_spirit_system_config()
    pool = cfg.get_attr_pool() or []
    keys: list[str] = []
    for p in pool:
        k = str((p or {}).get("key") or "").strip()
        if k:
            keys.append(k)
    return keys


def get_player_row(user_id: int) -> dict | None:
    rows = execute_query("SELECT * FROM player WHERE user_id=%s", (user_id,))
    return rows[0] if rows else None


def update_player_for_spirit_test(user_id: int, *, level: int, vip_level: int, gold: int, yuanbao: int, dry_run: bool):
    row = get_player_row(user_id)
    if not row:
        raise RuntimeError(f"player 表不存在 user_id={user_id} 的玩家，请先创建账号/导入数据")

    new_level = max(int(row.get("level", 1) or 1), int(level))
    new_vip = max(int(row.get("vip_level", 0) or 0), int(vip_level))
    new_gold = max(int(row.get("gold", 0) or 0), int(gold))
    new_yuanbao = max(int(row.get("yuanbao", 0) or 0), int(yuanbao))

    if dry_run:
        print(f"[dry-run] player: level {row.get('level')} -> {new_level}, vip {row.get('vip_level')} -> {new_vip}, gold -> >= {new_gold}, yuanbao -> >= {new_yuanbao}")
        return

    execute_update(
        "UPDATE player SET level=%s, vip_level=%s, gold=%s, yuanbao=%s WHERE user_id=%s",
        (new_level, new_vip, new_gold, new_yuanbao, user_id),
    )


def main():
    parser = argparse.ArgumentParser(description="灌入战灵系统测试数据")
    parser.add_argument("--user_id", type=int, default=20052, help="玩家ID（默认20052）")
    parser.add_argument("--level", type=int, default=35, help="最低等级（默认35）")
    parser.add_argument("--vip_level", type=int, default=10, help="最低VIP等级（默认10，用于测试免费洗练次数）")
    parser.add_argument("--gold", type=int, default=5000000, help="最低铜钱（默认500万）")
    parser.add_argument("--yuanbao", type=int, default=5000, help="最低元宝（默认5000）")
    parser.add_argument("--key_qty", type=int, default=200, help="战灵钥匙数量（默认200）")
    parser.add_argument("--crystal_qty", type=int, default=200, help="灵力水晶数量（默认200）")
    parser.add_argument("--stone_qty", type=int, default=50, help="每系灵石数量（默认50）")
    parser.add_argument(
        "--gen_mode",
        type=str,
        default="coverage_race_attr",
        choices=["coverage_race_attr", "random_per_element"],
        help="战灵样本生成模式：coverage_race_attr=覆盖每个种族×每个属性；random_per_element=按元素随机生成",
    )
    parser.add_argument(
        "--coverage_element",
        type=str,
        default="",
        choices=["", "earth", "fire", "water", "wood", "metal", "god"],
        help="coverage_race_attr 模式：若指定元素，则在该元素内覆盖生成（例如 god 表示生成 神灵·各族×各属性）",
    )
    parser.add_argument("--spirits_per_element", type=int, default=3, help="random_per_element 模式：每系生成战灵样本数量（默认3）")
    parser.add_argument("--dry_run", action="store_true", help="仅打印，不写入数据库")
    args = parser.parse_args()

    user_id = int(args.user_id)
    if user_id <= 0:
        print("错误：user_id 必须为正整数")
        sys.exit(1)

    dry_run = bool(args.dry_run)

    print(f"战灵测试数据灌入 - user_id={user_id}  dry_run={dry_run}")
    print("-" * 60)

    # 1) 玩家基础条件（等级>=35）
    update_player_for_spirit_test(
        user_id,
        level=args.level,
        vip_level=args.vip_level,
        gold=args.gold,
        yuanbao=args.yuanbao,
        dry_run=dry_run,
    )

    # 2) 初始化服务
    item_repo = ConfigItemRepo()
    inventory_repo = MySQLInventoryRepo()
    player_repo = MySQLPlayerRepo()
    spirit_repo = MySQLSpiritRepo()
    account_repo = MySQLSpiritAccountRepo()
    tower_state_repo = MySQLTowerStateRepo()
    player_beast_repo = MySQLPlayerBeastRepo()

    inventory_service = InventoryService(item_repo=item_repo, inventory_repo=inventory_repo, player_repo=player_repo)
    spirit_service = SpiritService(
        spirit_repo=spirit_repo,
        account_repo=account_repo,
        inventory_service=inventory_service,
        player_repo=player_repo,
        tower_state_repo=tower_state_repo,
        player_beast_repo=player_beast_repo,
    )

    # 3) 战灵账户：解锁全部元素（便于测试）
    acc = account_repo.get_by_user_id(user_id)
    acc.unlocked_elements = list(ALL_ELEMENTS)
    acc.free_refine_date = None
    acc.free_refine_used = 0
    if dry_run:
        print(f"[dry-run] spirit_account: unlocked_elements -> {acc.unlocked_elements}")
    else:
        account_repo.save(acc)
        print(f"[ok] spirit_account 已解锁元素：{acc.unlocked_elements}")

    # 4) 发放背包物资
    grants = [
        (SPIRIT_KEY_ITEM_ID, int(args.key_qty)),
        (SPIRIT_CRYSTAL_ITEM_ID, int(args.crystal_qty)),
    ]
    for element, stone_id in STONE_ITEM_IDS.items():
        grants.append((int(stone_id), int(args.stone_qty)))

    for item_id, qty in grants:
        if qty <= 0:
            continue
        name = item_repo.get_by_id(item_id).name if item_repo.get_by_id(item_id) else str(item_id)
        if dry_run:
            print(f"[dry-run] +{qty}  item={item_id}  {name}")
        else:
            inventory_service.add_item(user_id, item_id, qty)
            print(f"[ok] +{qty}  item={item_id}  {name}")

    # 5) 生成战灵样本（在灵件室）
    # 仓库容量保护：脚本直接写 player_spirit，需自行避免溢出
    system_cfg = get_spirit_system_config()
    capacity = int(system_cfg.get_warehouse_capacity() or 100)
    rows = execute_query("SELECT COUNT(*) AS cnt FROM player_spirit WHERE user_id=%s", (user_id,))
    existing_cnt = int(rows[0].get("cnt", 0) or 0) if rows else 0
    free_slots = max(capacity - existing_cnt, 0)

    if free_slots <= 0:
        print(f"[skip] 灵件室已满：{existing_cnt}/{capacity}，跳过生成战灵样本")
    else:
        if args.gen_mode == "random_per_element":
            per = int(args.spirits_per_element)
            if per < 0:
                per = 0
            if per > 30:
                per = 30

            if per > 0:
                for element in ALL_ELEMENTS:
                    need = min(per, free_slots)
                    if need <= 0:
                        break
                    if dry_run:
                        print(f"[dry-run] 生成战灵样本 {ELEMENT_NAME[element]}灵 × {need}")
                        free_slots -= need
                        continue
                    for _ in range(need):
                        sp = spirit_service._roll_new_spirit(user_id=user_id, element_key=element)
                        spirit_repo.save(sp)
                    free_slots -= need
                    print(f"[ok] 生成战灵样本 {ELEMENT_NAME[element]}灵 × {need}")
        else:
            # 覆盖生成：每个种族 × 每个属性 key 至少 1 份（元素按轮转分配）
            races = _get_all_races()
            attr_keys = _get_all_attr_keys()
            tasks: list[tuple[str, str, str]] = []
            fixed_element = str(args.coverage_element or "").strip()
            if fixed_element:
                for race in races:
                    for ak in attr_keys:
                        tasks.append((fixed_element, race, ak))
            else:
                idx = 0
                for race in races:
                    for ak in attr_keys:
                        element = ALL_ELEMENTS[idx % len(ALL_ELEMENTS)]
                        tasks.append((element, race, ak))
                        idx += 1

            if len(tasks) > free_slots:
                print(f"[warn] 计划生成 {len(tasks)} 个战灵样本，但剩余容量仅 {free_slots}，将截断为 {free_slots} 个")
                tasks = tasks[:free_slots]

            if dry_run:
                print(f"[dry-run] 覆盖生成战灵样本：{len(tasks)} 个（种族×属性），元素轮转分配")
                for (element, race, ak) in tasks:
                    print(f"  - {ELEMENT_NAME[element]}灵·{race}  line1={ak}")
            else:
                print(f"[ok] 覆盖生成战灵样本：{len(tasks)} 个（种族×属性），元素轮转分配")
                for (element, race, ak) in tasks:
                    sp = spirit_service._roll_new_spirit(user_id=user_id, element_key=element)
                    # 覆盖：种族 & 第一条属性 key（保持“初始仅1条解锁”以测试钥匙激活流程）
                    sp.race = race
                    if not sp.lines:
                        sp.get_line(1)
                    sp.lines[0].attr_key = ak
                    sp.lines[0].unlocked = True
                    sp.lines[0].locked = False
                    # 保证第2/3条保持未激活
                    sp.get_line(2).unlocked = False
                    sp.get_line(2).locked = False
                    sp.get_line(3).unlocked = False
                    sp.get_line(3).locked = False
                    spirit_repo.save(sp)

    # 6) 汇总
    if not dry_run:
        acc2 = account_repo.get_by_user_id(user_id)
        print("-" * 60)
        print(f"当前灵力：{acc2.spirit_power}")
        print(f"已解锁元素：{acc2.unlocked_elements}")
        for item_id, _ in grants:
            cnt = inventory_service.get_item_count(user_id, item_id, include_temp=True)
            nm = item_repo.get_by_id(item_id).name if item_repo.get_by_id(item_id) else str(item_id)
            print(f"背包物品：{nm}({item_id}) = {cnt}")
        # 汇总战灵（总数/按元素）
        rows = execute_query("SELECT COUNT(*) AS cnt FROM player_spirit WHERE user_id=%s", (user_id,))
        total_sp = int(rows[0].get("cnt", 0) or 0) if rows else 0
        print(f"战灵总数：{total_sp}/{capacity}")
        for element in ALL_ELEMENTS:
            rows = execute_query("SELECT COUNT(*) AS cnt FROM player_spirit WHERE user_id=%s AND element=%s", (user_id, element))
            c = int(rows[0].get("cnt", 0) or 0) if rows else 0
            print(f"战灵数量：{ELEMENT_NAME[element]}灵 = {c}")

    print("完成。")


if __name__ == "__main__":
    main()


