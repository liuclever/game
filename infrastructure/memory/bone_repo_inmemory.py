from typing import Optional, List, Dict

from domain.entities.bone import BeastBone
from domain.repositories.bone_repo import IBoneRepo


class InMemoryBoneRepo(IBoneRepo):
    """内存战骨仓库，用于开发测试（重启进程会清空）"""

    def __init__(self):
        self._data: Dict[int, BeastBone] = {}  # id -> BeastBone
        self._next_id = 1

    def get_by_user_id(self, user_id: int) -> List[BeastBone]:
        return [b for b in self._data.values() if b.user_id == user_id]

    def get_by_id(self, bone_id: int) -> Optional[BeastBone]:
        return self._data.get(bone_id)

    def get_by_beast_id(self, beast_id: int) -> List[BeastBone]:
        return [b for b in self._data.values() if b.beast_id == beast_id]

    def save(self, bone: BeastBone) -> None:
        if bone.id is None:
            bone.id = self._next_id
            self._next_id += 1
        self._data[bone.id] = bone

    def delete(self, bone_id: int) -> None:
        if bone_id in self._data:
            del self._data[bone_id]
