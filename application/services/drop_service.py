from typing import List, Dict, Any
from dataclasses import dataclass
from pathlib import Path
import json
import random

from domain.repositories.item_repo import IItemRepo
from domain.repositories.inventory_repo import IInventoryRepo
from application.services.inventory_service import InventoryService


@dataclass
class DropResult:
    """单个掉落结果"""
    item_id: int
    item_name: str
    quantity: int


class DropService:
    """掉落服务"""

    def __init__(self, item_repo: IItemRepo, inventory_service: InventoryService):
        self.item_repo = item_repo
        self.inventory_service = inventory_service
        self._drop_tables: Dict[int, List[dict]] = {}
        self._load_drop_tables()

    def _load_drop_tables(self):
        """加载掉落表配置"""
        base_dir = Path(__file__).resolve().parents[2]
        path = base_dir / "configs" / "drop_tables.json"
        with path.open("r", encoding="utf-8") as f:
            raw_list = json.load(f)

        for entry in raw_list:
            self._drop_tables[entry["map_id"]] = entry["drops"]

    def calc_drops(self, map_id: int) -> List[DropResult]:
        """计算战斗掉落"""
        drops = self._drop_tables.get(map_id, [])
        results = []

        for drop in drops:
            # 概率判定
            if random.randint(1, 100) <= drop["rate"]:
                quantity = random.randint(drop["min_qty"], drop["max_qty"])
                item = self.item_repo.get_by_id(drop["item_id"])
                if item:
                    results.append(DropResult(
                        item_id=drop["item_id"],
                        item_name=item.name,
                        quantity=quantity,
                    ))

        return results

    def apply_drops(self, user_id: int, drops: List[DropResult]) -> None:
        """将掉落物品存入背包"""
        for drop in drops:
            self.inventory_service.add_item(
                user_id=user_id,
                item_id=drop.item_id,
                quantity=drop.quantity,
            )
