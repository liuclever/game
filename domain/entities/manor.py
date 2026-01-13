from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

@dataclass
class ManorLand:
    """庄园土地实体"""
    id: Optional[int] = None
    user_id: int = 0
    land_index: int = 0  # 0-9:普通土地, 10:黄土地, 11:银土地, 12:金土地
    status: int = 0      # 0:未开启, 1:空闲, 2:种植中
    tree_type: int = 0   # 1, 2, 4, 6, 8株
    plant_time: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def is_mature(self, current_time: datetime, growth_hours: int = 6) -> bool:
        """检查摇钱树是否成熟"""
        if self.status != 2 or not self.plant_time:
            return False
        return current_time >= self.plant_time + timedelta(hours=growth_hours)

    def get_remaining_seconds(self, current_time: datetime, growth_hours: int = 6) -> int:
        """获取成熟剩余秒数"""
        if self.status != 2 or not self.plant_time:
            return 0
        mature_time = self.plant_time + timedelta(hours=growth_hours)
        remaining = (mature_time - current_time).total_seconds()
        return max(0, int(remaining))

@dataclass
class PlayerManor:
    """玩家庄园扩展实体"""
    user_id: int
    total_harvest_count: int = 0
    total_gold_earned: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
