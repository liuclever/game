"""给指定玩家发放所有6种元素的战灵。

运行示例（项目根目录）：
    python scripts/grant_all_spirits.py --user_id 1
    python scripts/grant_all_spirits.py --user_id 1 --quantity 3  # 每种元素发3个
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.db.spirit_repo_mysql import MySQLSpiritRepo
from infrastructure.db.spirit_account_repo_mysql import MySQLSpiritAccountRepo
from infrastructure.db.inventory_repo_mysql import MySQLInventoryRepo
from infrastructure.db.player_repo_mysql import MySQLPlayerRepo
from infrastructure.db.tower_state_repo_mysql import MySQLTowerStateRepo
from infrastructure.db.player_beast_repo_mysql import MySQLPlayerBeastRepo
from infrastructure.config.item_repo_from_config import ConfigItemRepo
from application.services.inventory_service import InventoryService
from application.services.spirit_service import SpiritService


ALL_ELEMENTS = ["earth", "fire", "water", "wood", "metal", "god"]
ELEMENT_NAMES = {
    "earth": "土灵",
    "fire": "火灵",
    "water": "水灵",
    "wood": "木灵",
    "metal": "金灵",
    "god": "神灵",
}


def main():
    parser = argparse.ArgumentParser(description="给指定玩家发放所有战灵")
    parser.add_argument("--user_id", type=int, required=True, help="玩家ID")
    parser.add_argument("--quantity", type=int, default=1, help="每种元素发放数量 (默认1)")
    args = parser.parse_args()

    user_id = args.user_id
    quantity = args.quantity

    if quantity <= 0 or quantity > 100:
        print("错误: quantity 必须在 1-100 之间")
        sys.exit(1)

    spirit_repo = MySQLSpiritRepo()
    account_repo = MySQLSpiritAccountRepo()
    inventory_repo = MySQLInventoryRepo()
    item_repo = ConfigItemRepo()
    player_repo = MySQLPlayerRepo()
    tower_state_repo = MySQLTowerStateRepo()
    player_beast_repo = MySQLPlayerBeastRepo()

    inventory_service = InventoryService(
        item_repo=item_repo,
        inventory_repo=inventory_repo,
        player_repo=player_repo,
    )

    spirit_service = SpiritService(
        spirit_repo=spirit_repo,
        account_repo=account_repo,
        inventory_service=inventory_service,
        player_repo=player_repo,
        tower_state_repo=tower_state_repo,
        player_beast_repo=player_beast_repo,
    )

    print(f"开始为玩家 {user_id} 发放战灵 (每种元素 {quantity} 个)...")
    print("-" * 50)

    total_created = 0
    for element in ALL_ELEMENTS:
        created_count = 0
        for _ in range(quantity):
            spirit = spirit_service._roll_new_spirit(user_id=user_id, element_key=element)
            spirit_repo.save(spirit)
            created_count += 1
            total_created += 1
        print(f"  {ELEMENT_NAMES[element]}: 已发放 {created_count} 个")

    print("-" * 50)
    print(f"完成! 共发放 {total_created} 个战灵给玩家 {user_id}")


if __name__ == "__main__":
    main()
