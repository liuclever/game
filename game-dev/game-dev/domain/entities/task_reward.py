from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TaskRewardClaim:
    """玩家已经领取的任务奖励"""

    id: Optional[int]
    user_id: int
    reward_key: str
    claimed_at: datetime
