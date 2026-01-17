"""为指定玩家发放所有“召唤球”道具（用于测试）。

运行示例（项目根目录）：
    python scripts/grant_summon_balls.py --user_id 20052
    python scripts/grant_summon_balls.py --user_id 20052 --quantity 1 --dry_run
    python scripts/grant_summon_balls.py --user_id 20052 --quantity 5 --only_divine

默认逻辑：
- 从 configs/items.json 读取所有 name 包含“召唤球”的道具
- 默认排除 type == "special"（可用 --include_special 包含）
- 默认发放每种 1 个（可用 --quantity 调整）
"""

import argparse
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Windows 下默认控制台编码可能导致中文乱码，这里强制 UTF-8 输出（失败则忽略）
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from infrastructure.config.item_repo_from_config import ConfigItemRepo
from infrastructure.db.connection import execute_query, execute_update
from infrastructure.db.inventory_repo_mysql import MySQLInventoryRepo
from application.services.inventory_service import InventoryService, InventoryError


def has_unique_index_user_item_temp() -> bool:
    rows = execute_query(
        """
        SELECT COUNT(*) AS cnt
        FROM information_schema.statistics
        WHERE table_schema = DATABASE()
          AND table_name = 'player_inventory'
          AND index_name = 'uk_user_item_temp'
        """
    )
    try:
        return int(rows[0].get("cnt", 0) or 0) > 0
    except Exception:
        return False


def upsert_add_quantity(user_id: int, item_id: int, quantity: int) -> None:
    rows = execute_query(
        "SELECT id, quantity FROM player_inventory WHERE user_id=%s AND item_id=%s AND is_temporary=0 LIMIT 1",
        (user_id, item_id),
    )
    if rows:
        execute_update(
            "UPDATE player_inventory SET quantity = quantity + %s WHERE id=%s",
            (int(quantity), int(rows[0]["id"])),
        )
    else:
        execute_update(
            "INSERT INTO player_inventory (user_id, item_id, quantity, is_temporary, created_at) VALUES (%s,%s,%s,0,NOW())",
            (user_id, item_id, int(quantity)),
        )


def main():
    parser = argparse.ArgumentParser(description="为指定玩家发放所有召唤球道具")
    parser.add_argument("--user_id", type=int, required=True, help="玩家ID（必填）")
    parser.add_argument("--quantity", type=int, default=1, help="每种召唤球发放数量（默认1）")
    parser.add_argument("--dry_run", action="store_true", help="仅打印，不写入数据库")
    parser.add_argument("--only_divine", action="store_true", help="仅发放神兽召唤球（神·开头）")
    parser.add_argument("--include_special", action="store_true", help="包含 special 类型召唤球（默认不包含）")
    parser.add_argument(
        "--force_normal",
        action="store_true",
        help="强制写入正式背包（忽略背包容量，不放入临时背包；适合“背包满了看不到”的测试场景）",
    )
    args = parser.parse_args()

    user_id = int(args.user_id)
    quantity = int(args.quantity)
    dry_run = bool(args.dry_run)
    only_divine = bool(args.only_divine)
    include_special = bool(args.include_special)
    force_normal = bool(args.force_normal)

    if user_id <= 0:
        print("错误：user_id 必须为正整数")
        sys.exit(1)
    if quantity <= 0 or quantity > 9999:
        print("错误：quantity 必须在 1-9999 之间")
        sys.exit(1)

    item_repo = ConfigItemRepo()
    all_items = item_repo.get_all()

    summon_ball_ids: list[int] = []
    for item_id, tpl in (all_items or {}).items():
        name = getattr(tpl, "name", "") or ""
        t = getattr(tpl, "type", "") or ""
        if "召唤球" not in name:
            continue
        if only_divine and not name.startswith("神·"):
            continue
        if (not include_special) and t == "special":
            continue
        summon_ball_ids.append(int(item_id))

    summon_ball_ids = sorted(set(summon_ball_ids))
    if not summon_ball_ids:
        print("未找到任何召唤球道具（请检查 configs/items.json）")
        sys.exit(1)

    print(f"目标玩家：{user_id}")
    print(f"召唤球种类：{len(summon_ball_ids)}")
    print(f"每种发放：{quantity}")
    print(f"only_divine：{only_divine}")
    print(f"include_special：{include_special}")
    print(f"force_normal：{force_normal}")
    print(f"dry_run：{dry_run}")
    print("-" * 60)

    unique_idx_exists = has_unique_index_user_item_temp()
    if unique_idx_exists:
        print("检测到 player_inventory 存在唯一索引 uk_user_item_temp：将用 UPDATE/INSERT 方式加数量（不拆分99）")
    else:
        print("未检测到 uk_user_item_temp：将用 InventoryService.add_item 方式发放（遵循单格上限99）")

    inventory_repo = MySQLInventoryRepo()
    inventory_service = InventoryService(item_repo=item_repo, inventory_repo=inventory_repo, player_repo=None)

    granted_counter = Counter()
    errors = []

    for item_id in summon_ball_ids:
        tpl = item_repo.get_by_id(int(item_id))
        name = getattr(tpl, "name", "") if tpl else str(item_id)
        if dry_run:
            print(f"[dry-run] +{quantity}  {item_id}  {name}")
            granted_counter[item_id] += quantity
            continue
        try:
            if force_normal or unique_idx_exists:
                upsert_add_quantity(user_id=user_id, item_id=int(item_id), quantity=quantity)
                print(f"[ok] +{quantity}  {item_id}  {name}  -> 正式背包")
            else:
                _, is_temp = inventory_service.add_item(user_id=user_id, item_id=int(item_id), quantity=quantity)
                where = "临时背包" if is_temp else "正式背包"
                print(f"[ok] +{quantity}  {item_id}  {name}  -> {where}")
            granted_counter[item_id] += quantity
        except (InventoryError, Exception) as e:
            errors.append((item_id, name, str(e)))
            print(f"[fail] {item_id} {name}: {e}")

    print("-" * 60)
    if errors:
        print(f"失败：{len(errors)} 个")
        for item_id, name, err in errors[:10]:
            print(f"  - {item_id} {name}: {err}")
        if len(errors) > 10:
            print(f"  ... 其余 {len(errors) - 10} 条略")

    print(f"成功发放：{len(granted_counter)} 种召唤球")


if __name__ == "__main__":
    main()


