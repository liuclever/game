from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from domain.entities.handbook import HandbookCategory, HandbookPet, HandbookSkillInfo


class IHandbookRepo(ABC):
    @abstractmethod
    def list_categories(self) -> List[HandbookCategory]:
        pass

    @abstractmethod
    def get_category(self, category_id: int) -> Optional[HandbookCategory]:
        pass

    @abstractmethod
    def list_pet_ids_by_page(self, category_id: int, page: int) -> List[int]:
        """返回指定分类在某一页展示的 pet id 列表（用于严格模仿分页展示）。"""
        pass

    @abstractmethod
    def get_pet_by_id(self, pet_id: int) -> Optional[HandbookPet]:
        pass

    @abstractmethod
    def list_all_pets_in_category(self, category_id: int) -> List[HandbookPet]:
        """可用于后续扩展（搜索/全量分页）。当前实现允许返回空。"""
        pass

    @abstractmethod
    def get_meta(self) -> Dict:
        """返回图鉴的元信息（如 realms / realm_multipliers）。"""
        pass

    @abstractmethod
    def get_skill_detail(self, skill_key: str) -> Optional[HandbookSkillInfo]:
        """返回技能详情（用于技能说明页）。"""
        pass

    @abstractmethod
    def get_doc_text(self) -> List[str]:
        """返回图鉴说明 doc 的原文（逐行），用于 1:1 同步展示。"""
        pass


