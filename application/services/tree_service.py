"""
古树模块应用服务（用例编排层）。

职责：
- 从仓库加载/保存古树周数据与玩家周数据；
- 调用领域规则计算“能否领取/开奖/奖励星级”等；
- 发放奖励（铜钱走 player_repo 保存；道具走 InventoryService 入背包）。

"""

from __future__ import annotations

from datetime import date, datetime
from typing import Dict, Optional

from application.services.inventory_service import InventoryService
from domain.entities.tree import TreePlayerWeek, TreeWeek
from domain.repositories.player_repo import IPlayerRepo
from domain.repositories.tree_repo import ITreeRepo
from domain.rules.tree_lottery_rules import (
    calc_star_by_match,
    can_draw_today,
    draw_unique_number,
    generate_winning_numbers,
    is_sunday,
    match_count,
    reward_by_star,
    week_start_of,
)


class TreeError(Exception):
    """古树相关错误（例如重复领取、非周日领奖等）"""


REBIRTH_PILL_ITEM_ID = 6017  # configs/items.json: 重生丹


class TreeService:
    def __init__(self, tree_repo: ITreeRepo, player_repo: IPlayerRepo, inventory_service: InventoryService):
        self.tree_repo = tree_repo
        self.player_repo = player_repo
        self.inventory_service = inventory_service

    def get_status(self, user_id: int, today: Optional[date] = None) -> Dict:
        if today is None:
            today = date.today()

        ws = week_start_of(today)

        week = self.tree_repo.get_week(ws) or TreeWeek(week_start=ws, winning_numbers=[])
        state = self.tree_repo.get_player_week(user_id, ws) or TreePlayerWeek(
            user_id=user_id,
            week_start=ws,
            my_numbers=[],
            last_draw_date=None,
            claimed_at=None,
            claim_star=0,
            match_count=0,
        )

        # 周日：展示开奖数字（第一次访问周日页面时生成并固化，保证全服一致）
        if is_sunday(today) and len(week.winning_numbers or []) != 7:
            week.winning_numbers = generate_winning_numbers()
            self.tree_repo.upsert_week(week)

        my_nums = list(state.my_numbers or [])
        win_nums = list(week.winning_numbers or []) if is_sunday(today) else []
        cnt = match_count(my_nums, win_nums) if win_nums else 0
        star = calc_star_by_match(cnt) if win_nums else 0

        return {
            "week_start": ws.isoformat(),
            "today": today.isoformat(),
            "is_sunday": bool(is_sunday(today)),
            "my_numbers": my_nums,
            "drawn_count": len(my_nums),
            "can_draw_today": bool(can_draw_today(state.last_draw_date, today)) and len(my_nums) < 7,
            "last_draw_date": state.last_draw_date.isoformat() if state.last_draw_date else None,
            "winning_numbers": win_nums,
            "match_count": int(cnt),
            "star": int(star),
            "claimed": bool(state.claimed_at is not None),
            "claimed_at": state.claimed_at.isoformat() if state.claimed_at else None,
            "claim_star": int(state.claim_star or 0),
        }

    def draw_today_number(self, user_id: int, today: Optional[date] = None) -> Dict:
        if today is None:
            today = date.today()

        ws = week_start_of(today)
        state = self.tree_repo.get_player_week(user_id, ws) or TreePlayerWeek(user_id=user_id, week_start=ws)

        my_nums = list(state.my_numbers or [])
        if len(my_nums) >= 7:
            raise TreeError("already_draw_7_numbers")
        if not can_draw_today(state.last_draw_date, today):
            raise TreeError("already_draw_today")

        n = draw_unique_number(my_nums)
        my_nums.append(n)
        state.my_numbers = my_nums
        state.last_draw_date = today
        self.tree_repo.upsert_player_week(state)

        return {
            "drawn_number": int(n),
            "my_numbers": my_nums,
            "drawn_count": len(my_nums),
            "week_start": ws.isoformat(),
        }

    def claim_week_reward(self, user_id: int, today: Optional[date] = None) -> Dict:
        if today is None:
            today = date.today()

        if not is_sunday(today):
            raise TreeError("only_sunday_can_claim")

        ws = week_start_of(today)
        week = self.tree_repo.get_week(ws) or TreeWeek(week_start=ws, winning_numbers=[])
        if len(week.winning_numbers or []) != 7:
            week.winning_numbers = generate_winning_numbers()
            self.tree_repo.upsert_week(week)

        state = self.tree_repo.get_player_week(user_id, ws) or TreePlayerWeek(user_id=user_id, week_start=ws)

        if state.claimed_at is not None:
            raise TreeError("already_claimed")

        my_nums = list(state.my_numbers or [])
        win_nums = list(week.winning_numbers or [])
        cnt = match_count(my_nums, win_nums)
        star = calc_star_by_match(cnt)
        if star <= 0:
            # 需求未提“安慰奖”，按未中奖处理
            raise TreeError("no_reward")

        copper_gain, rebirth_pill_count = reward_by_star(star)

        # 发放奖励：铜钱（玩家表） + 重生丹（背包）
        player = self.player_repo.get_by_id(user_id)
        if player is None:
            raise TreeError("player_not_found")
        player.copper = int(getattr(player, "copper", 0) or 0) + int(copper_gain)
        self.player_repo.save(player)

        if rebirth_pill_count > 0:
            self.inventory_service.add_item(user_id=user_id, item_id=REBIRTH_PILL_ITEM_ID,
                                            quantity=int(rebirth_pill_count))

        state.match_count = int(cnt)
        state.claim_star = int(star)
        state.claimed_at = datetime.now()
        self.tree_repo.upsert_player_week(state)

        return {
            "week_start": ws.isoformat(),
            "winning_numbers": win_nums,
            "my_numbers": my_nums,
            "match_count": int(cnt),
            "star": int(star),
            "reward": {
                "copper": int(copper_gain),
                "rebirth_pill": int(rebirth_pill_count),
            },
        }
