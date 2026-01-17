from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from domain.entities.handbook import (
    HandbookAptitude,
    HandbookCategory,
    HandbookEvolution,
    HandbookImage,
    HandbookPet,
    HandbookSkill,
    HandbookSkillInfo,
)
from domain.repositories.handbook_repo import IHandbookRepo


class ConfigHandbookRepo(IHandbookRepo):
    """从 configs/handbook.json 读取图鉴配置（只读）。

    约束：
    - 图鉴模块独立，不依赖数据库。
    - 允许在开发期热更新：检测文件 mtime 变化后自动 reload。
    """

    def __init__(self):
        base_dir = Path(__file__).resolve().parents[2]
        self._path = base_dir / "configs" / "handbook.json"
        self._last_mtime: Optional[float] = None
        self._raw: Dict = {}
        self._categories: List[HandbookCategory] = []
        self._pets_by_id: Dict[int, HandbookPet] = {}
        self._category_pages: Dict[int, Dict[int, List[int]]] = {}
        self._skills_by_key: Dict[str, HandbookSkillInfo] = {}
        self._load()

    def _ensure_latest(self):
        try:
            mtime = self._path.stat().st_mtime
        except OSError:
            return
        if self._last_mtime is None or mtime > self._last_mtime:
            self._load()

    def _load(self):
        with self._path.open("r", encoding="utf-8") as f:
            raw = json.load(f) or {}
        self._raw = raw
        try:
            self._last_mtime = self._path.stat().st_mtime
        except OSError:
            self._last_mtime = None

        categories: List[HandbookCategory] = []
        for c in raw.get("categories") or []:
            try:
                categories.append(
                    HandbookCategory(
                        id=int(c.get("id")),
                        name=str(c.get("name") or ""),
                        total_pages=int(c.get("total_pages") or 1),
                    )
                )
            except Exception:
                continue
        self._categories = categories

        pets_by_id: Dict[int, HandbookPet] = {}
        for p in raw.get("pets") or []:
            pet = self._map_pet(p)
            if pet is None:
                continue
            pets_by_id[pet.id] = pet
        self._pets_by_id = pets_by_id

        skills_by_key: Dict[str, HandbookSkillInfo] = {}
        raw_skills = raw.get("skills") or {}
        if isinstance(raw_skills, dict):
            for key, info in raw_skills.items():
                if not key:
                    continue
                if not isinstance(info, dict):
                    continue
                try:
                    skey = str(key)
                    skills_by_key[skey] = HandbookSkillInfo(
                        key=skey,
                        name=str(info.get("name") or skey),
                        desc=str(info.get("desc") or ""),
                        # 仅保留“技能说明文案”，不使用/不暴露任何外站 URL。
                        source_url="",
                    )
                except Exception:
                    continue
        self._skills_by_key = skills_by_key

        category_pages: Dict[int, Dict[int, List[int]]] = {}
        for cat_id_str, pages in (raw.get("category_pages") or {}).items():
            try:
                cat_id = int(cat_id_str)
            except Exception:
                continue
            page_map: Dict[int, List[int]] = {}
            if isinstance(pages, dict):
                for page_str, pet_ids in pages.items():
                    try:
                        page_no = int(page_str)
                    except Exception:
                        continue
                    ids: List[int] = []
                    for pid in pet_ids or []:
                        try:
                            ids.append(int(pid))
                        except Exception:
                            continue
                    page_map[page_no] = ids
            category_pages[cat_id] = page_map
        self._category_pages = category_pages

    def _map_pet(self, raw_pet: Dict) -> Optional[HandbookPet]:
        try:
            pet_id = int(raw_pet.get("id"))
            category_id = int(raw_pet.get("category_id"))
            pet_name = str(raw_pet.get("name") or "")
        except Exception:
            return None

        evolution_raw = raw_pet.get("evolution") or {}
        evolution = HandbookEvolution(
            from_realm=str(evolution_raw.get("from") or ""),
            to_realm=str(evolution_raw.get("to") or ""),
        )

        evolution_chain: List[str] = []
        raw_chain = raw_pet.get("evolution_chain")
        if isinstance(raw_chain, list):
            evolution_chain = [str(x).strip() for x in raw_chain if str(x).strip()]
        if not evolution_chain:
            # 兜底：由 evolution.from/to 推导（最多两段）
            if evolution.from_realm:
                evolution_chain.append(evolution.from_realm)
            if evolution.to_realm and evolution.to_realm != evolution.from_realm:
                evolution_chain.append(evolution.to_realm)

        aptitudes: Dict[str, HandbookAptitude] = {}
        for key, a in (raw_pet.get("max_initial_aptitudes") or {}).items():
            if not isinstance(a, dict):
                continue
            try:
                aptitudes[str(key)] = HandbookAptitude(
                    value=int(a.get("value") or 0),
                    stars=int(a.get("stars") or 0),
                    label=str(a.get("label") or ""),
                )
            except Exception:
                continue

        image_obj = None
        img_raw = raw_pet.get("image")
        if isinstance(img_raw, dict):
            image_obj = HandbookImage(
                type=str(img_raw.get("type") or "local"),
                local_key=str(img_raw.get("local_key") or ""),
                url=str(img_raw.get("url") or ""),
            )

        skills: List[HandbookSkill] = []
        for s in (raw_pet.get("skills") or []):
            if isinstance(s, str):
                skill_name = s.strip()
                if not skill_name:
                    continue
                skills.append(HandbookSkill(name=skill_name, key=""))
                continue
            if isinstance(s, dict):
                skill_name = str(s.get("name") or "").strip()
                key = str(s.get("key") or "").strip()
                if not skill_name:
                    continue
                skills.append(HandbookSkill(name=skill_name, key=key))
                continue

        return HandbookPet(
            id=pet_id,
            category_id=category_id,
            name=pet_name,
            body=str(raw_pet.get("body") or ""),
            evolution=evolution,
            evolution_chain=evolution_chain,
            nature=str(raw_pet.get("nature") or ""),
            rarity=str(raw_pet.get("rarity") or ""),
            location=str(raw_pet.get("location") or ""),
            max_initial_aptitudes=aptitudes,
            skills=skills,
            image=image_obj,
            source=dict(raw_pet.get("source") or {}),
        )

    def list_categories(self) -> List[HandbookCategory]:
        self._ensure_latest()
        return list(self._categories)

    def get_category(self, category_id: int) -> Optional[HandbookCategory]:
        self._ensure_latest()
        for c in self._categories:
            if int(c.id) == int(category_id):
                return c
        return None

    def list_pet_ids_by_page(self, category_id: int, page: int) -> List[int]:
        self._ensure_latest()
        page_map = self._category_pages.get(int(category_id)) or {}
        ids = page_map.get(int(page)) or []
        return list(ids)

    def get_pet_by_id(self, pet_id: int) -> Optional[HandbookPet]:
        self._ensure_latest()
        return self._pets_by_id.get(int(pet_id))

    def list_all_pets_in_category(self, category_id: int) -> List[HandbookPet]:
        self._ensure_latest()
        return [p for p in self._pets_by_id.values() if int(p.category_id) == int(category_id)]

    def get_meta(self) -> Dict:
        self._ensure_latest()
        raw = self._raw or {}
        realms = raw.get("realms") or []
        realm_multipliers = raw.get("realm_multipliers") or {}
        return {
            "realms": [str(x) for x in realms if str(x).strip()],
            "realm_multipliers": {str(k): float(v) for k, v in (realm_multipliers.items() if isinstance(realm_multipliers, dict) else [])},
        }

    def get_skill_detail(self, skill_key: str) -> Optional[HandbookSkillInfo]:
        self._ensure_latest()
        key = str(skill_key or "").strip()
        if not key:
            return None
        
        # 首先尝试通过key查询
        skill = self._skills_by_key.get(key)
        if skill:
            return skill
        
        # 如果key查询失败，尝试通过技能名称查询
        for skill_info in self._skills_by_key.values():
            if skill_info.name == key:
                return skill_info
        
        return None

    def get_doc_text(self) -> List[str]:
        self._ensure_latest()
        raw = self._raw or {}
        lines = raw.get("doc_text") or []
        if isinstance(lines, list):
            return [str(x) for x in lines]
        if isinstance(lines, str):
            # 兼容：若为单段文本，按行拆分
            return str(lines).splitlines()
        return []


