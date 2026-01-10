from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Item:
    """物品模板（从 configs/items.json 加载）"""
    id: int
    name: str = ""
    type: str = "material"        # material / consumable / equipment
    description: str = ""
    stackable: bool = True
    max_stack: int = 9999
    use_effect: Optional[str] = None


@dataclass
class InventoryItem:
    """背包中的物品实例"""
    id: Optional[int] = None      # 背包格子ID
    user_id: int = 0              # 所属玩家
    item_id: int = 0              # 物品模板ID
    quantity: int = 1             # 数量
    is_temporary: bool = False    # 是否临时存放（背包满时）
    created_at: Optional[datetime] = None  # 创建时间（临时物品用）

    def can_stack(self, item_template: Item) -> bool:
        """是否还能堆叠更多"""
        return item_template.stackable and self.quantity < item_template.max_stack

    def add(self, amount: int, item_template: Item) -> int:
        """
        添加数量，返回溢出数量（放不下的部分）
        """
        if not item_template.stackable:
            return amount  # 不可堆叠，全部溢出

        space = item_template.max_stack - self.quantity
        if amount <= space:
            self.quantity += amount
            return 0
        else:
            self.quantity = item_template.max_stack
            return amount - space


@dataclass
class PlayerBag:
    """玩家背包信息"""
    user_id: int
    bag_level: int = 1            # 背包等级
    capacity: int = 100           # 背包容量（格子数）
    
    # 每格物品数量上限
    MAX_STACK_SIZE = 99
    
    @staticmethod
    def calc_capacity(level: int) -> int:
        """根据等级计算容量: 100 + (等级-1) * 40"""
        return 100 + (level - 1) * 40