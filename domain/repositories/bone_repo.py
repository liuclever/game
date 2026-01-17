try:
    from typing import Protocol, Optional, Dict, List
except ImportError:
    from typing_extensions import Protocol
    from typing import Optional, Dict, List

from domain.entities.bone import BoneTemplate, BeastBone


class IBoneTemplateRepo(Protocol):
    """战骨模板数据访问接口（只读）"""

    def get_by_id(self, template_id: int) -> Optional[BoneTemplate]:
        ...

    def get_all(self) -> Dict[int, BoneTemplate]:
        ...


class IBoneRepo(Protocol):
    """玩家战骨数据访问接口"""

    def get_by_user_id(self, user_id: int) -> List[BeastBone]:
        ...

    def get_by_id(self, bone_id: int) -> Optional[BeastBone]:
        ...

    def get_by_beast_id(self, beast_id: int) -> List[BeastBone]:
        ...

    def save(self, bone: BeastBone) -> None:
        ...

    def delete(self, bone_id: int) -> None:
        ...
