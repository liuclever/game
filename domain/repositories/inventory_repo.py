try:
    from typing import Protocol, Optional, List
except ImportError:
    from typing_extensions import Protocol
    from typing import Optional, List
from datetime import datetime
from domain.entities.item import InventoryItem, PlayerBag


class IInventoryRepo(Protocol):
    """背包数据访问接口"""

    def get_by_user_id(self, user_id: int, include_temp: bool = True) -> List[InventoryItem]:
        """获取玩家所有背包物品"""
        ...

    def find_item(self, user_id: int, item_id: int, is_temporary: bool = False) -> Optional[InventoryItem]:
        """查找玩家背包中某个物品（返回第一个匹配项）"""
        ...

    def find_all_items(self, user_id: int, item_id: int, is_temporary: bool = False) -> List[InventoryItem]:
        """查找玩家背包中某物品的所有格子"""
        ...

    def save(self, inv_item: InventoryItem) -> None:
        """保存/更新背包物品"""
        ...

    def delete(self, inv_item_id: int) -> None:
        """删除背包物品（数量为0时）"""
        ...
    
    def get_slot_count(self, user_id: int, is_temporary: bool = False) -> int:
        """获取已占用的格子数"""
        ...
    
    def get_bag_info(self, user_id: int) -> PlayerBag:
        """获取玩家背包信息（等级和容量）"""
        ...
    
    def save_bag_info(self, bag: PlayerBag) -> None:
        """保存背包信息"""
        ...
    
    def delete_temp_items_before(self, before_time: datetime) -> int:
        """删除指定时间之前的临时物品，返回删除数量"""
        ...
    
    def clean_zero_quantity_items(self) -> int:
        """清理所有数量为0的物品，返回清理的数量"""
        ...