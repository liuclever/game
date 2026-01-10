from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from domain.entities.manor import ManorLand, PlayerManor

class IManorRepo(ABC):
    @abstractmethod
    def get_user_lands(self, user_id: int) -> List[ManorLand]:
        """获取玩家所有土地信息"""
        pass

    @abstractmethod
    def get_land(self, user_id: int, land_index: int) -> Optional[ManorLand]:
        """获取特定土地信息"""
        pass

    @abstractmethod
    def open_land(self, user_id: int, land_index: int) -> bool:
        """开启土地"""
        pass

    @abstractmethod
    def start_planting(self, user_id: int, land_index: int, tree_type: int, plant_time: datetime) -> bool:
        """开始种植"""
        pass

    @abstractmethod
    def reset_land(self, user_id: int, land_index: int) -> bool:
        """收获后重置土地状态"""
        pass

    @abstractmethod
    def get_player_manor(self, user_id: int) -> Optional[PlayerManor]:
        """获取玩家庄园扩展信息"""
        pass

    @abstractmethod
    def update_player_manor(self, player_manor: PlayerManor) -> bool:
        """更新玩家庄园扩展信息"""
        pass

    @abstractmethod
    def create_player_manor_if_not_exists(self, user_id: int) -> bool:
        """如果不存在则创建玩家庄园信息"""
        pass
