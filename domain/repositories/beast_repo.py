try:
    from typing import Protocol, Optional, List, Dict
except ImportError:
    from typing_extensions import Protocol
    from typing import Optional, List, Dict
from domain.entities.beast import Beast, BeastTemplate


class IBeastTemplateRepo(Protocol):
    """幻兽模板数据访问接口（只读）"""

    def get_by_id(self, template_id: int) -> Optional[BeastTemplate]:
        ...

    def get_by_name(self, name: str) -> Optional[BeastTemplate]:
        ...

    def get_all(self) -> Dict[int, BeastTemplate]:
        ...


class IBeastRepo(Protocol):
    """玩家幻兽数据访问接口"""

    def get_by_user_id(self, user_id: int) -> List[Beast]:
        """获取玩家所有幻兽"""
        ...

    def get_by_id(self, beast_id: int) -> Optional[Beast]:
        """根据ID获取幻兽"""
        ...

    def get_main_beast(self, user_id: int) -> Optional[Beast]:
        """获取玩家出战幻兽"""
        ...

    def save(self, beast: Beast) -> None:
        """保存/更新幻兽"""
        ...

    def delete(self, beast_id: int) -> None:
        """删除幻兽"""
        ...

    def get_by_user_and_id(self, user_id: int, beast_id: int) -> Optional[Beast]:
        """根据ID获取某个玩家的幻兽"""
        ...
