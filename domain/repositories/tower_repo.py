try:
    from typing import Protocol, Optional, List, Dict
except ImportError:
    from typing_extensions import Protocol
    from typing import Optional, List, Dict
from domain.entities.tower import TowerState, TowerGuardian


class ITowerStateRepo(Protocol):
    """闯塔状态存储接口"""
    
    def get_by_user_id(self, user_id: int, tower_type: str) -> Optional[TowerState]:
        """获取玩家某塔的状态"""
        ...
    
    def save(self, state: TowerState) -> None:
        """保存状态"""
        ...


class ITowerConfigRepo(Protocol):
    """闯塔配置接口"""
    
    def get_tower_config(self, tower_type: str) -> dict:
        """获取塔配置"""
        ...
    
    def get_guardians_for_floor(self, tower_type: str, floor: int) -> List[TowerGuardian]:
        """获取某层的守塔幻兽列表"""
        ...
    
    def get_guardian_count_for_floor(self, tower_type: str, floor: int) -> int:
        """获取某层需要的守塔幻兽数量"""
        ...
    
    def get_floor_rewards(self, tower_type: str, floor: int) -> dict:
        """获取某层的奖励"""
        ...
    
    def get_milestone_reward(self, tower_type: str, floor: int) -> Optional[dict]:
        """获取里程碑奖励（如果有）"""
        ...
