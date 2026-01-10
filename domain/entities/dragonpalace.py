from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, Optional


@dataclass
class DragonPalaceStageState:
    """单个关卡的挑战结果与领奖状态（当天有效）。"""

    stage: int
    success: bool = False
    report: Optional[Dict[str, Any]] = None  # battle_data（用于“查看战报”）
    reward_item_id: Optional[int] = None
    reward_claimed: bool = False


@dataclass
class DragonPalaceDailyState:
    """龙宫之谜：玩家每日进度（当天有效，次日刷新）。"""

    user_id: int
    play_date: date

    # 每日免费一次 + 付费重置最多两次（对应第2、第3次进入）
    resets_used: int = 0  # 0~2

    # 运行状态：not_started/in_progress/failed/completed
    status: str = "not_started"
    current_stage: int = 1  # 1~3

    stage1: DragonPalaceStageState = field(default_factory=lambda: DragonPalaceStageState(stage=1))
    stage2: DragonPalaceStageState = field(default_factory=lambda: DragonPalaceStageState(stage=2))
    stage3: DragonPalaceStageState = field(default_factory=lambda: DragonPalaceStageState(stage=3))

    def get_stage_state(self, stage: int) -> DragonPalaceStageState:
        if int(stage) == 1:
            return self.stage1
        if int(stage) == 2:
            return self.stage2
        if int(stage) == 3:
            return self.stage3
        raise ValueError("invalid_stage")


