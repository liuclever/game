from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class AllianceArmySignup:
    id: Optional[int]
    registration_id: int
    alliance_id: int
    army: str
    user_id: int
    signup_order: int
    hp_state: Optional[Dict[str, Any]]
    status: int
    created_at: Optional[datetime] = None


@dataclass
class AllianceLandBattle:
    id: Optional[int]
    land_id: int
    left_registration_id: int
    right_registration_id: int
    phase: int
    current_round: int
    started_at: Optional[datetime]
    finished_at: Optional[datetime]


@dataclass
class AllianceLandBattleRound:
    id: Optional[int]
    battle_id: int
    round_no: int
    left_alive: int
    right_alive: int
    status: int
    started_at: Optional[datetime]
    finished_at: Optional[datetime]


@dataclass
class AllianceLandBattleDuel:
    id: Optional[int]
    round_id: int
    attacker_signup_id: int
    defender_signup_id: int
    attacker_result: int
    log_data: Dict[str, Any]
    created_at: Optional[datetime] = None
