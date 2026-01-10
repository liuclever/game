from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class BattleRecord:
    """战斗记录（纯领域模型，不依赖任何框架）"""
    id: Optional[int] = None              # 数据库主键
    user_id: int = 0                      # 玩家ID
    monster_id: int = 0                   # 怪物ID
    result: str = ""                      # 战斗结果：win / lose
    created_at: Optional[datetime] = None # 战斗时间

    def is_victory(self) -> bool:
        """判断是否胜利"""
        return self.result == "win"
