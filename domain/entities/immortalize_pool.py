from dataclasses import dataclass
from typing import Optional


@dataclass
class ImmortalizePool:
    """玩家化仙池实体"""

    user_id: int
    pool_level: int = 1
    current_exp: int = 0
    formation_level: int = 0
    formation_started_at: Optional[str] = None
    formation_ends_at: Optional[str] = None
    formation_last_grant_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def add_exp(self, amount: int, capacity: int) -> int:
        """向化仙池添加经验，返回实际增加量（受容量限制）"""
        if amount <= 0:
            return 0
        free_space = max(capacity - self.current_exp, 0)
        delta = min(amount, free_space)
        self.current_exp += delta
        return delta

    def spend_exp(self, amount: int) -> bool:
        """消耗化仙池经验"""
        if amount < 0:
            return False
        if self.current_exp < amount:
            return False
        self.current_exp -= amount
        return True

    def is_formation_active(self) -> bool:
        return bool(self.formation_started_at and self.formation_ends_at)
