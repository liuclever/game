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
    announce_date_of,
    calc_star_by_match,
    can_draw_today,
    draw_blue_number,
    draw_red_number,
    generate_winning_numbers,
    is_sunday,
    match_count,
    reward_by_star,
    week_index,
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
        week_no = week_index(ws)
        announce_date = announce_date_of(ws)

        # 本周领取记录
        state = self.tree_repo.get_player_week(user_id, ws) or TreePlayerWeek(
            user_id=user_id,
            week_start=ws,
            red_numbers=[],
            blue_number=None,
            last_draw_date=None,
            claimed_at=None,
            claim_star=0,
            match_count=0,
        )

        # 今日幸运数字（玩家今日领取到的数字）
        today_number = None
        if state.last_draw_date == today:
            if is_sunday(today):
                today_number = state.blue_number
            else:
                today_number = state.red_numbers[-1] if state.red_numbers else None

        # 上周（已在本周周一公布）
        last_ws = ws.fromordinal(ws.toordinal() - 7)
        last_announce = ws  # 上周公布时间 = 本周周一
        last_week = self.tree_repo.get_week(last_ws) or TreeWeek(
            week_start=last_ws,
            announce_date=last_announce,
            winning_red_numbers=[],
            winning_blue_number=None,
        )
        # 若上周尚未生成/落库幸运数字，则在“公布周一”首次访问时生成并固化（保证全服一致）
        if (today >= ws) and (len(last_week.winning_red_numbers or []) != 6 or last_week.winning_blue_number is None):
            red6, blue1 = generate_winning_numbers()
            last_week.announce_date = last_announce
            last_week.winning_red_numbers = red6
            last_week.winning_blue_number = blue1
            self.tree_repo.upsert_week(last_week)

        last_state = self.tree_repo.get_player_week(user_id, last_ws) or TreePlayerWeek(
            user_id=user_id,
            week_start=last_ws,
            red_numbers=[],
            blue_number=None,
            last_draw_date=None,
            claimed_at=None,
            claim_star=0,
            match_count=0,
        )
        last_cnt = match_count(
            my_red_numbers=list(last_state.red_numbers or []),
            my_blue_number=last_state.blue_number,
            winning_red_numbers=list(last_week.winning_red_numbers or []),
            winning_blue_number=last_week.winning_blue_number,
        )
        last_star = calc_star_by_match(last_cnt)

        return {
            "week_no": int(week_no),
            "week_start": ws.isoformat(),
            "announce_date": announce_date.isoformat(),
            "today": today.isoformat(),
            "is_sunday": bool(is_sunday(today)),
            "today_number": int(today_number) if today_number is not None else None,
            "red_numbers": list(state.red_numbers or []),
            "blue_number": int(state.blue_number) if state.blue_number is not None else None,
            "can_draw_today": bool(can_draw_today(state.last_draw_date, today))
            and ((is_sunday(today) and state.blue_number is None) or ((not is_sunday(today)) and len(state.red_numbers or []) < 6)),
            "last_draw_date": state.last_draw_date.isoformat() if state.last_draw_date else None,
            "last_week": {
                "week_start": last_ws.isoformat(),
                "announce_date": last_announce.isoformat(),
                "red_numbers": list(last_state.red_numbers or []),
                "blue_number": int(last_state.blue_number) if last_state.blue_number is not None else None,
                "winning_red_numbers": list(last_week.winning_red_numbers or []),
                "winning_blue_number": int(last_week.winning_blue_number) if last_week.winning_blue_number is not None else None,
                "match_count": int(last_cnt),
                "star": int(last_star),
                "claimed": bool(last_state.claimed_at is not None),
                "claim_expires_at": announce_date.isoformat(),
            },
        }

    def draw_today_number(self, user_id: int, today: Optional[date] = None) -> Dict:
        if today is None:
            today = date.today()

        ws = week_start_of(today)
        state = self.tree_repo.get_player_week(user_id, ws) or TreePlayerWeek(user_id=user_id, week_start=ws)

        if not can_draw_today(state.last_draw_date, today):
            raise TreeError("already_draw_today")

        if is_sunday(today):
            # 周日：领取蓝果实（每周最多 1 个）
            if state.blue_number is not None:
                raise TreeError("already_draw_blue")
            n = draw_blue_number()
            state.blue_number = int(n)
        else:
            # 周一至周六：领取红果实（每周最多 6 个）
            red = list(getattr(state, "red_numbers", []) or [])
            if len(red) >= 6:
                raise TreeError("already_draw_6_red")
            n = draw_red_number()
            red.append(int(n))
            state.red_numbers = red

        state.last_draw_date = today
        self.tree_repo.upsert_player_week(state)

        return {
            "drawn_number": int(n),
            "week_start": ws.isoformat(),
        }

    def claim_week_reward(self, user_id: int, today: Optional[date] = None) -> Dict:
        if today is None:
            today = date.today()

        # 领奖对象：上周（本周周一已公布的幸运数字）
        current_ws = week_start_of(today)
        ws = current_ws.fromordinal(current_ws.toordinal() - 7)
        announce_date = current_ws

        week = self.tree_repo.get_week(ws) or TreeWeek(
            week_start=ws,
            announce_date=announce_date,
            winning_red_numbers=[],
            winning_blue_number=None,
        )
        if len(week.winning_red_numbers or []) != 6 or week.winning_blue_number is None:
            red6, blue1 = generate_winning_numbers()
            week.announce_date = announce_date
            week.winning_red_numbers = red6
            week.winning_blue_number = blue1
            self.tree_repo.upsert_week(week)

        state = self.tree_repo.get_player_week(user_id, ws) or TreePlayerWeek(user_id=user_id, week_start=ws)
        if state.claimed_at is not None:
            raise TreeError("already_claimed")

        cnt = match_count(
            my_red_numbers=list(getattr(state, "red_numbers", []) or []),
            my_blue_number=getattr(state, "blue_number", None),
            winning_red_numbers=list(week.winning_red_numbers or []),
            winning_blue_number=week.winning_blue_number,
        )
        star = calc_star_by_match(cnt)
        if star <= 0:
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
            "announce_date": announce_date.isoformat(),
            "winning_red_numbers": list(week.winning_red_numbers or []),
            "winning_blue_number": int(week.winning_blue_number) if week.winning_blue_number is not None else None,
            "red_numbers": list(getattr(state, "red_numbers", []) or []),
            "blue_number": int(getattr(state, "blue_number", 0) or 0) if getattr(state, "blue_number", None) is not None else None,
            "match_count": int(cnt),
            "star": int(star),
            "reward": {
                "copper": int(copper_gain),
                "rebirth_pill": int(rebirth_pill_count),
            },
        }
