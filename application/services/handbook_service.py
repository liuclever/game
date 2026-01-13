from __future__ import annotations

from typing import Dict, List, Optional

from domain.entities.handbook import HandbookCategory, HandbookPet, HandbookSkill, HandbookSkillInfo
from domain.repositories.handbook_repo import IHandbookRepo


class HandbookService:
    """图鉴用例服务（独立模块，不依赖玩家/背包/数据库）。"""

    def __init__(self, repo: IHandbookRepo):
        self.repo = repo

    def get_index(self, pacename: int, page: int = 1, page_size: int = 10) -> Dict:
        """图鉴列表（分页）。

        说明：
        - 分页/分类均来自 configs/handbook.json（配置驱动，便于协作补数据）。
        - 这里只返回列表所需的最小字段：id/name/image，避免 API 过度暴露内部结构。
        """
        try:
            category_id = int(pacename or 1)
        except Exception:
            category_id = 1

        try:
            page_i = int(page or 1)
        except Exception:
            page_i = 1
        page_i = max(1, page_i)

        try:
            page_size_i = int(page_size or 10)
        except Exception:
            page_size_i = 10
        page_size_i = max(1, min(50, page_size_i))

        categories: List[HandbookCategory] = self.repo.list_categories()
        cat: Optional[HandbookCategory] = self.repo.get_category(category_id)
        if cat is None and categories:
            cat = categories[0]
            category_id = int(cat.id)

        total_pages = int(cat.total_pages if cat else 1)
        total_pages = max(1, total_pages)
        if page_i > total_pages:
            page_i = total_pages

        pet_ids = self.repo.list_pet_ids_by_page(category_id=category_id, page=page_i)
        pets: List[HandbookPet] = []
        for pid in pet_ids:
            p = self.repo.get_pet_by_id(pid)
            if p is None:
                continue
            pets.append(p)

        # 分页由配置决定，允许某些页为空
        return {
            "ok": True,
            "world_name": "灵武世界",
            "title": "【图鉴】",
            "categories": [{"id": c.id, "name": c.name} for c in categories],
            "category_id": category_id,
            "page": page_i,
            "total_pages": total_pages,
            "page_size": page_size_i,
            "pets": [
                {
                    "id": p.id,
                    "name": p.name,
                    "image": (
                        {
                            "type": p.image.type,
                            "local_key": p.image.local_key,
                            "url": p.image.url,
                        }
                        if p.image
                        else None
                    ),
                }
                for p in pets
            ],
        }

    def get_pet_detail(self, pet_id: int, evolution: int = 0) -> Dict:
        """图鉴详情。

        说明：
        - evolution 仅用于“地界/灵界/神界”点击切换后的稳定增幅展示（前端基于倍率计算显示值）。
        - 不返回任何外站 URL（只做 UI/文案模仿）。
        """
        try:
            pid = int(pet_id)
        except Exception:
            pid = 0
        if not pid:
            return {"ok": False, "error": "pet_id 无效"}

        pet = self.repo.get_pet_by_id(pid)
        if pet is None:
            return {"ok": False, "error": "图鉴不存在"}

        meta = self.repo.get_meta() or {}
        realms = meta.get("realms") or ["地界", "灵界", "神界"]
        realm_multipliers = meta.get("realm_multipliers") or {"地界": 1.0, "灵界": 1.1, "神界": 1.2}

        # 详情页优先按宠物自己的进化链展示（更贴近原站）
        pet_realms = list(pet.evolution_chain or [])
        if not pet_realms:
            pet_realms = list(realms)

        try:
            evo_i = int(evolution or 0)
        except Exception:
            evo_i = 0
        evo_i = max(0, min(len(pet_realms) - 1, evo_i)) if pet_realms else 0
        selected_realm = pet_realms[evo_i] if pet_realms else "地界"

        aptitudes = []
        for k, a in (pet.max_initial_aptitudes or {}).items():
            aptitudes.append({
                "key": k,
                "label": a.label or k,
                "value": int(a.value or 0),
                "stars": int(a.stars or 0),
            })

        image = None
        if pet.image:
            image = {
                "type": pet.image.type,
                "local_key": pet.image.local_key,
                "url": pet.image.url,
            }

        skills = []
        for s in (pet.skills or []):
            if isinstance(s, HandbookSkill):
                skills.append({"name": s.name, "key": s.key})
            else:
                # 兼容旧数据
                try:
                    skills.append({"name": str(s), "key": ""})
                except Exception:
                    continue

        return {
            "ok": True,
            "meta": {
                "realms": list(realms),
                "realm_multipliers": dict(realm_multipliers),
            },
            "selected_realm": selected_realm,
            "pet": {
                "id": pet.id,
                "category_id": pet.category_id,
                "name": pet.name,
                "body": pet.body,
                "evolution": {"from": pet.evolution.from_realm, "to": pet.evolution.to_realm},
                "evolution_chain": list(pet.evolution_chain or []),
                "nature": pet.nature,
                "rarity": pet.rarity,
                "location": pet.location,
                "max_initial_aptitudes": aptitudes,
                "skills": skills,
                "image": image,
            },
        }

    def get_skill_detail(self, skill_key: str) -> Dict:
        """技能详情（用于“全技能”点击进入的单独页面）。不返回外站链接。"""
        key = str(skill_key or "").strip()
        if not key:
            return {"ok": False, "error": "skill_key 无效"}
        info: Optional[HandbookSkillInfo] = self.repo.get_skill_detail(key)
        if info is None:
            return {"ok": False, "error": "技能不存在"}
        return {
            "ok": True,
            "skill": {
                "key": info.key,
                "name": info.name,
                "desc": info.desc,
            },
        }


