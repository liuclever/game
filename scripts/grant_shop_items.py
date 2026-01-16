"""为指定玩家发放“商城已有的所有商品”各 N 个（默认100个）。

运行示例（项目根目录）：
    python scripts/grant_shop_items.py --user_id 20052
    python scripts/grant_shop_items.py --user_id 20052 --quantity 100 --dry_run

说明：
- 商品列表来源：configs/shop.json 的 items[*].item_id（去重后发放）
- 兼容两种数据库结构：
  1) 若 player_inventory 上仍存在唯一键 (user_id,item_id,is_temporary)，则直接 UPDATE 数量（不拆分99）
  2) 若唯一键已移除（推荐，允许同一物品多格拆分），则走 InventoryService.add_item 以遵循单格上限99
"""

import argparse
import json
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


def load_shop_item_ids() -> list[int]:
    shop_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "configs", "shop.json")
    with open(shop_path, "r", encoding="utf-8") as f:
        cfg = json.load(f) or {}

    ids: list[int] = []
    for it in (cfg.get("items") or []):
        try:
            item_id = int(it.get("item_id", 0) or 0)
        except Exception:
            item_id = 0
        if item_id > 0:
            ids.append(item_id)
    # 去重但保持稳定顺序
    seen = set()
    uniq = []
    for x in ids:
        if x in seen:
            continue
        seen.add(x)
        uniq.append(x)
    return uniq


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
    # 若已存在，则加数量；否则插入一条
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
    parser = argparse.ArgumentParser(description="为指定玩家发放商城全部商品")
    parser.add_argument("--user_id", type=int, default=20052, help="玩家ID（默认20052）")
    parser.add_argument("--quantity", type=int, default=100, help="每个商品发放数量（默认100）")
    parser.add_argument("--dry_run", action="store_true", help="仅打印，不写入数据库")
    args = parser.parse_args()

    user_id = int(args.user_id)
    quantity = int(args.quantity)
    dry_run = bool(args.dry_run)

    if user_id <= 0:
        print("错误：user_id 必须为正整数")
        sys.exit(1)
    if quantity <= 0 or quantity > 9999:
        print("错误：quantity 必须在 1-9999 之间")
        sys.exit(1)

    item_repo = ConfigItemRepo()
    item_ids = load_shop_item_ids()
    if not item_ids:
        print("错误：未从 configs/shop.json 读取到任何商品 item_id")
        sys.exit(1)

    print(f"目标玩家：{user_id}")
    print(f"商品数量：{len(item_ids)} 种（来自 configs/shop.json）")
    print(f"每种发放：{quantity}")
    print(f"dry_run：{dry_run}")
    print("-" * 60)

    unique_idx_exists = has_unique_index_user_item_temp()
    if unique_idx_exists:
        print("检测到 player_inventory 存在唯一索引 uk_user_item_temp：将用 UPDATE/INSERT 方式加数量（不拆分99）")
    else:
        print("未检测到 uk_user_item_temp：将用 InventoryService.add_item 方式发放（遵循单格上限99）")

    inventory_repo = MySQLInventoryRepo()
    inventory_service = InventoryService(item_repo=item_repo, inventory_repo=inventory_repo, player_repo=None)

    skipped = []
    errors = []
    granted_counter = Counter()

    for item_id in item_ids:
        tpl = item_repo.get_by_id(int(item_id))
        if tpl is None:
            skipped.append(item_id)
            continue

        name = getattr(tpl, "name", "") or str(item_id)
        if dry_run:
            print(f"[dry-run] +{quantity}  {item_id}  {name}")
            granted_counter[item_id] += quantity
            continue

        try:
            if unique_idx_exists:
                upsert_add_quantity(user_id=user_id, item_id=int(item_id), quantity=quantity)
            else:
                inventory_service.add_item(user_id=user_id, item_id=int(item_id), quantity=quantity)
            granted_counter[item_id] += quantity
            print(f"[ok] +{quantity}  {item_id}  {name}")
        except (InventoryError, Exception) as e:
            errors.append((item_id, name, str(e)))
            print(f"[fail] {item_id} {name}: {e}")

    print("-" * 60)
    if skipped:
        print(f"跳过（items.json 不存在模板）：{len(skipped)} 个 -> {skipped}")
    if errors:
        print(f"失败：{len(errors)} 个")
        for item_id, name, err in errors[:10]:
            print(f"  - {item_id} {name}: {err}")
        if len(errors) > 10:
            print(f"  ... 其余 {len(errors) - 10} 条略")

    print(f"成功发放：{len(granted_counter)} 种商品")


if __name__ == "__main__":
    main()


