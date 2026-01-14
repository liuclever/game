from dataclasses import dataclass
from datetime import datetime
from typing import Optional


STATUS_CANCELLED = 0
STATUS_REGISTERED = 1
STATUS_PENDING = 2
STATUS_CONFIRMED = 3
STATUS_IN_BATTLE = 4
STATUS_ELIMINATED = 5
STATUS_VICTOR = 6

ACTIVE_STATUSES = {
    STATUS_REGISTERED,
    STATUS_PENDING,
    STATUS_CONFIRMED,
    STATUS_IN_BATTLE,
}


@dataclass
class AllianceRegistration:
    """Alliance registration for targeting a land during war."""

    id: Optional[int]
    alliance_id: int
    land_id: int
    army: Optional[str]
    status: int
    cost: int
    registration_time: datetime
    created_at: datetime
    bye_waiting_round: Optional[int] = None
    last_bye_round: Optional[int] = None

    def is_active(self) -> bool:
        return self.status in ACTIVE_STATUSES

    def has_completed_battle(self) -> bool:
        return self.status in {STATUS_ELIMINATED, STATUS_VICTOR}
