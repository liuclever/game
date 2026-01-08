from dataclasses import dataclass
from typing import Optional


@dataclass
class Monster:
    """游戏中的怪物对象（纯领域模型，不依赖任何框架）"""
    id: Optional[int] = None          # 数据库主键
    name: str = ""                    # 怪物名称
    map_id: int = 0                   # 所属地图ID
    level: int = 1                    # 怪物等级
    base_exp: int = 10                # 击杀获得的基础经验
    base_gold: int = 5                # 击杀获得的基础金币

    def calc_exp_reward(self, player_level: int) -> int:
        """根据玩家等级计算实际经验奖励"""
        level_diff = self.level - player_level
        multiplier = max(0.5, min(1.5, 1 + level_diff * 0.1))
        return int(self.base_exp * multiplier)

    def calc_gold_reward(self) -> int:
        """计算金币奖励"""
        return self.base_gold
