from dataclasses import dataclass
from typing import Optional


@dataclass
class Map:
    """游戏中的地图对象（纯领域模型，不依赖任何框架）"""
    id: Optional[int] = None          # 数据库主键
    name: str = ""                    # 地图名称
    min_level: int = 1                # 进入该地图的最低等级
    max_level: int = 100              # 进入该地图的最高等级

    def can_enter(self, player_level: int) -> bool:
        """检查玩家等级是否满足进入条件"""
        return self.min_level <= player_level <= self.max_level
