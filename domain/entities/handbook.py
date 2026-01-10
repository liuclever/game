from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class HandbookCategory:
    id: int
    name: str
    total_pages: int = 1


@dataclass(frozen=True)
class HandbookAptitude:
    value: int
    stars: int = 0
    label: str = ""


@dataclass(frozen=True)
class HandbookEvolution:
    from_realm: str = ""
    to_realm: str = ""


@dataclass(frozen=True)
class HandbookSkill:
    """技能引用（用于宠物技能列表）。"""
    name: str
    key: str = ""


@dataclass(frozen=True)
class HandbookSkillInfo:
    """技能详情（用于技能说明页）。"""
    key: str
    name: str
    desc: str = ""
    source_url: str = ""


@dataclass(frozen=True)
class HandbookImage:
    # type: "local" | "url"
    type: str = "local"
    local_key: str = ""
    url: str = ""


@dataclass(frozen=True)
class HandbookPet:
    id: int
    category_id: int
    name: str

    body: str = ""
    evolution: HandbookEvolution = field(default_factory=HandbookEvolution)
    evolution_chain: List[str] = field(default_factory=list)
    nature: str = ""
    rarity: str = ""
    location: str = ""

    # key -> aptitude
    max_initial_aptitudes: Dict[str, HandbookAptitude] = field(default_factory=dict)
    skills: List[HandbookSkill] = field(default_factory=list)

    image: Optional[HandbookImage] = None
    source: Dict[str, str] = field(default_factory=dict)


