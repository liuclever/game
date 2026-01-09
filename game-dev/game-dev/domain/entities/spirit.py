from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Optional, List, Dict


@dataclass
class SpiritLine:
    """战灵词条（百分比属性）。

    value_bp：basis points，1 = 0.01%（例如 123 = 1.23%）。
    """

    attr_key: str
    value_bp: int
    unlocked: bool = False
    locked: bool = False

    def value_percent(self) -> float:
        return float(self.value_bp) / 100.0

    def to_dict(self) -> Dict:
        return {
            "attr": self.attr_key,
            "value_bp": self.value_bp,
            "value_percent": self.value_percent(),
            "unlocked": self.unlocked,
            "locked": self.locked,
        }


@dataclass
class Spirit:
    """玩家拥有的战灵实例（可装备到某只幻兽上）。"""

    id: Optional[int] = None
    user_id: int = 0
    beast_id: Optional[int] = None

    element: str = ""   # earth/fire/water/wood/metal/god
    race: str = ""      # 兽族/龙族/虫族/飞禽/神兽...

    lines: List[SpiritLine] = field(default_factory=list)

    def get_line(self, index: int) -> SpiritLine:
        if index < 1 or index > 3:
            raise ValueError("line_index must be 1..3")
        if len(self.lines) < 3:
            # 补齐到 3 条
            while len(self.lines) < 3:
                self.lines.append(SpiritLine(attr_key="", value_bp=0, unlocked=False, locked=False))
        return self.lines[index - 1]

    def unlocked_lines(self) -> List[SpiritLine]:
        return [ln for ln in self.lines if ln.unlocked]

    def locked_unlocked_count(self) -> int:
        return sum(1 for ln in self.lines if ln.unlocked and ln.locked)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "beast_id": self.beast_id,
            "element": self.element,
            "race": self.race,
            "lines": [ln.to_dict() for ln in (self.lines or [])],
        }


@dataclass
class SpiritAccount:
    """玩家战灵账户：灵力、已解锁元素槽位、每日免费洗练计数等。"""

    user_id: int
    spirit_power: int = 0
    unlocked_elements: List[str] = field(default_factory=list)

    free_refine_date: Optional[date] = None
    free_refine_used: int = 0

    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "spirit_power": self.spirit_power,
            "unlocked_elements": list(self.unlocked_elements or []),
            "free_refine_date": self.free_refine_date.isoformat() if self.free_refine_date else None,
            "free_refine_used": self.free_refine_used,
        }
