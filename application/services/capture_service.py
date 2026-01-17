from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from pathlib import Path
import json
import random

from domain.entities.beast import Beast
from application.services.inventory_service import InventoryService, InventoryError
from application.services.beast_service import BeastService


# 捕捉球物品ID
CAPTURE_BALL_ID = 4002         # 普通捕捉球
STRONG_CAPTURE_BALL_ID = 4003  # 强力捕捉球


class CaptureError(Exception):
    """捕捉相关错误"""
    pass


@dataclass
class CaptureAttempt:
    """捕捉尝试结果"""
    success: bool
    beast: Optional[Beast] = None
    message: str = ""


@dataclass
class MapBeastEntry:
    """地图可捕捉幻兽配置"""
    template_id: int
    rate: int           # 出现概率
    capture_rate: int   # 基础捕捉率


class CaptureService:
    """捕捉服务"""

    def __init__(
        self,
        inventory_service: InventoryService,
        beast_service: BeastService,
    ):
        self.inventory_service = inventory_service
        self.beast_service = beast_service
        self._map_beasts: Dict[int, List[MapBeastEntry]] = {}
        self._load_map_beasts()

    def _load_map_beasts(self):
        """加载地图可捕捉幻兽配置"""
        base_dir = Path(__file__).resolve().parents[2]
        path = base_dir / "configs" / "map_dungeons.json"
        if not path.exists():
            return

        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        dungeons = data.get("dungeons", [])
        if isinstance(dungeons, dict):
            dungeons = list(dungeons.values())
        for dungeon in dungeons:
            map_id = dungeon.get("map_id")
            if map_id is None:
                continue
            
            beasts = []
            for b in dungeon.get("beasts", []):
                # 将 0.15 转换成 15
                capture_rate = int(b.get("capture_rate", 0.1) * 100)
                beasts.append(
                    MapBeastEntry(
                        template_id=b["template_id"],
                        rate=20,  # 默认 20% 遭遇率，因为 map_dungeons.json 没提供
                        capture_rate=capture_rate,
                    )
                )
            
            if map_id not in self._map_beasts:
                self._map_beasts[map_id] = []
            self._map_beasts[map_id].extend(beasts)

    def get_encounter(self, map_id: int) -> Optional[MapBeastEntry]:
        """
        战斗后随机遇到幻兽
        返回 None 表示没有遇到
        """
        beasts = self._map_beasts.get(map_id, [])
        for beast in beasts:
            if random.randint(1, 100) <= beast.rate:
                return beast
        return None

    def attempt_capture(
        self,
        user_id: int,
        map_id: int,
        use_strong_ball: bool = False,
    ) -> CaptureAttempt:
        """
        尝试捕捉幻兽
        """
        # 1. 检查是否遇到幻兽
        encounter = self.get_encounter(map_id)
        if encounter is None:
            return CaptureAttempt(
                success=False,
                message="没有遇到可捕捉的幻兽",
            )

        # 2. 检查并消耗捕捉球
        ball_id = STRONG_CAPTURE_BALL_ID if use_strong_ball else CAPTURE_BALL_ID
        ball_name = "强力捕捉球" if use_strong_ball else "捕捉球"

        if not self.inventory_service.has_item(user_id, ball_id, 1):
            return CaptureAttempt(
                success=False,
                message=f"没有{ball_name}",
            )

        try:
            self.inventory_service.remove_item(user_id, ball_id, 1)
        except InventoryError as e:
            return CaptureAttempt(
                success=False,
                message=str(e),
            )

        # 3. 计算捕捉成功率
        base_rate = encounter.capture_rate
        ball_bonus = 1.5 if use_strong_ball else 1.0
        final_rate = int(base_rate * ball_bonus)

        # 4. 判定捕捉
        roll = random.randint(1, 100)
        if roll <= final_rate:
            # 捕捉成功
            beast = self.beast_service.add_beast(
                user_id=user_id,
                template_id=encounter.template_id,
            )
            return CaptureAttempt(
                success=True,
                beast=beast,
                message="捕捉成功！",
            )
        else:
            return CaptureAttempt(
                success=False,
                message=f"捕捉失败（成功率{final_rate}%，掷出{roll}）",
            )
