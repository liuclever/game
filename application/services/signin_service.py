from __future__ import annotations

import random
from datetime import date
from typing import Dict, Optional

from domain.entities.player import Player
from domain.repositories.alliance_repo import IAllianceRepo
from domain.repositories.player_repo import IPlayerRepo
from domain.rules.signin_reward_rules import calc_next_signin_streak, calc_signin_copper
from domain.rules.signin_rules import apply_signin_reward, can_signin


class SigninError(Exception):
    """签到相关错误（例如重复签到）"""
    pass


class SigninService:
    def __init__(self, player_repo: IPlayerRepo, alliance_repo: IAllianceRepo):
        self.player_repo = player_repo
        self.alliance_repo = alliance_repo

    def do_signin(self, player_id: int, today: date | None = None) -> Dict:
        """执行一次签到并返回奖励明细（用于前端展示“颁发者”与发放数值）。

        约束：
        - 奖励数值按等级段决定；
        - 连续签到>=5天时基础铜钱×2；
        - 颁发者从盟战排行榜前三联盟中随机选一个联盟名（若榜单为空/异常，则 issuer_name 不返回）。
        """
        if today is None:
            today = date.today()

        player = self.player_repo.get_by_id(player_id)
        if player is None:
            raise SigninError(f"player {player_id} not found")

        if not can_signin(player, today):
            raise SigninError("already_signed_today")

        streak_after = calc_next_signin_streak(
            last_signin_date=getattr(player, "last_signin_date", None),
            prev_streak=int(getattr(player, "signin_streak", 0) or 0),
            today=today,
        )

        base_copper, copper_gain = calc_signin_copper(level=int(player.level or 0), streak_after_signin=streak_after)

        # 颁发者：盟战排行榜前三联盟随机一个；若榜单为空/异常，则不返回 issuer_name（前端也不展示）
        issuer_name: Optional[str] = None
        try:
            issuer_candidates = self.alliance_repo.list_top_alliance_names_by_war_honor_history(3)
            issuer_name = random.choice(issuer_candidates) if issuer_candidates else None
        except Exception:
            issuer_name = None

        # 发奖励（当前需求只强调铜钱；经验不发放）
        apply_signin_reward(player, exp_gain=0, copper_gain=copper_gain)

        # 记录签到日期 + 连续签到
        player.last_signin_date = today
        player.signin_streak = streak_after

        self.player_repo.save(player)
        result = {
            "reward": {
                "base_copper": int(base_copper),
                "copper": int(copper_gain),
                "multiplier": 2 if streak_after >= 5 else 1,
            },
            "signin_streak": int(streak_after),
            "last_signin_date": today.isoformat(),
        }
        if issuer_name:
            result["issuer_name"] = issuer_name
        return result
