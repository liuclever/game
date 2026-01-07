"""魔魂系统数据访问接口定义。"""
try:
    from typing import Protocol, Optional, List
except ImportError:
    from typing_extensions import Protocol
    from typing import Optional, List

from domain.entities.mosoul import (
    MoSoul,
    SoulStorage,
    BeastMoSoulSlot,
    HuntingState,
    GlobalPityCounter,
)


class IMoSoulRepo(Protocol):
    """魔魂实例数据访问接口"""

    def get_by_id(self, soul_id: int) -> Optional[MoSoul]:
        """根据ID获取魔魂"""
        ...

    def get_by_user_id(self, user_id: int) -> List[MoSoul]:
        """获取玩家所有魔魂"""
        ...

    def get_equipped_by_beast_id(self, beast_id: int) -> List[MoSoul]:
        """获取幻兽已装备的所有魔魂"""
        ...

    def save(self, soul: MoSoul) -> MoSoul:
        """保存/更新魔魂，返回带ID的魔魂"""
        ...

    def delete(self, soul_id: int) -> None:
        """删除魔魂"""
        ...

    def delete_batch(self, soul_ids: List[int]) -> None:
        """批量删除魔魂"""
        ...


class ISoulStorageRepo(Protocol):
    """储魂器数据访问接口"""

    def get_by_user_id(self, user_id: int) -> Optional[SoulStorage]:
        """获取玩家储魂器"""
        ...

    def save(self, storage: SoulStorage) -> None:
        """保存储魂器状态"""
        ...

    def get_soul_count(self, user_id: int) -> int:
        """获取玩家储魂器中的魔魂数量"""
        ...


class IBeastMoSoulRepo(Protocol):
    """幻兽魔魂装备数据访问接口"""

    def get_by_beast_id(self, beast_id: int) -> Optional[BeastMoSoulSlot]:
        """获取幻兽的魔魂装备槽位"""
        ...

    def get_by_user_id(self, user_id: int) -> List[BeastMoSoulSlot]:
        """获取玩家所有幻兽的魔魂装备信息"""
        ...

    def save(self, slot: BeastMoSoulSlot) -> None:
        """保存幻兽魔魂装备信息"""
        ...

    def equip_soul(self, beast_id: int, soul_id: int) -> bool:
        """装备魔魂到幻兽，返回是否成功"""
        ...

    def unequip_soul(self, beast_id: int, soul_id: int) -> bool:
        """从幻兽卸下魔魂，返回是否成功"""
        ...


class IHuntingStateRepo(Protocol):
    """猎魂状态数据访问接口"""

    def get_by_user_id(self, user_id: int) -> Optional[HuntingState]:
        """获取玩家猎魂状态"""
        ...

    def save(self, state: HuntingState) -> None:
        """保存猎魂状态"""
        ...

    def reset(self, user_id: int, field_type: str = "normal") -> None:
        """重置猎魂状态"""
        ...


class IGlobalPityRepo(Protocol):
    """全服保底计数器数据访问接口"""

    def get(self, counter_key: str = "kevin_adv_pity") -> GlobalPityCounter:
        """获取全服保底计数器"""
        ...

    def increment(self, counter_key: str = "kevin_adv_pity") -> bool:
        """增加计数，返回是否触发保底"""
        ...

    def reset(self, counter_key: str = "kevin_adv_pity") -> None:
        """重置计数器"""
        ...
