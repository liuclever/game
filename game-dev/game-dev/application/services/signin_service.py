# game/application/services/signin_service.py
from datetime import date

from domain.entities.player import Player
from domain.repositories.player_repo import IPlayerRepo
from domain.rules.signin_rules import can_signin, apply_signin_reward


class SigninError(Exception):
    """签到相关错误（例如重复签到）"""
    pass


class SigninService:
    def __init__(self, player_repo: IPlayerRepo):
        self.player_repo = player_repo

    def do_signin(self, player_id: int, today: date | None = None) -> Player:
        """执行一次签到，返回更新后的 Player"""
        if today is None:
            today = date.today()

        player = self.player_repo.get_by_id(player_id)
        if player is None:
            raise SigninError(f"player {player_id} not found")

        if not can_signin(player, today):
            raise SigninError("already_signed_today")

        # 发奖励
        apply_signin_reward(player)
        # 记录签到日期
        player.last_signin_date = today

        self.player_repo.save(player)
        return player
