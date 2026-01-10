"""
月卡服务 - 简化版
只有一个月卡，购买后30天有效期
"""
from __future__ import annotations

from datetime import datetime, timedelta, date
from typing import Dict, Optional, Callable

from infrastructure.db.connection import execute_query, execute_update


MONTH_CARD_DAYS = 30
PURCHASE_COST_GEMS = 30
INITIAL_REWARD = 1000
DAILY_REWARD = 200


class MonthCardError(Exception):
    """月卡业务错误"""


class MonthCardService:
    def __init__(
        self,
        player_repo=None,
        inventory_service=None,
        month_card_repo=None,
        clock: Optional[Callable[[], datetime]] = None,
    ):
        self.player_repo = player_repo
        self.inventory_service = inventory_service
        self.month_card_repo = month_card_repo
        self._clock = clock or datetime.now

    def _now(self) -> datetime:
        return self._clock()

    def _calc_vip_level(self, diamond_spent: int) -> int:
        """根据消耗宝石数计算VIP等级"""
        import json
        import os
        config_path = os.path.join(
            os.path.dirname(__file__), 
            '..', '..', 'configs', 'vip_privileges.json'
        )
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                vip_config = json.load(f)
            vip_level = 0
            for lv in vip_config.get('vip_levels', []):
                if diamond_spent >= lv.get('required_diamond', 0):
                    vip_level = lv.get('level', 0)
            return vip_level
        except Exception:
            return 0

    def _get_card(self, user_id: int) -> Optional[Dict]:
        """获取玩家月卡记录"""
        rows = execute_query(
            """SELECT id, user_id, start_date, end_date, last_claim_date, days_claimed
               FROM player_month_card WHERE user_id = %s LIMIT 1""",
            (user_id,)
        )
        return rows[0] if rows else None

    def get_status(self, user_id: int) -> Dict:
        """获取月卡状态"""
        now = self._now()
        card = self._get_card(user_id)
        
        if not card:
            return {
                "is_active": False,
                "days_left": 0,
                "can_claim_today": False,
                "today_claimed": False,
                "end_date": None,
            }
        
        end_date = card['end_date']
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date).date()
        elif isinstance(end_date, datetime):
            end_date = end_date.date()
        
        is_active = now.date() <= end_date
        days_left = max(0, (end_date - now.date()).days + 1) if is_active else 0
        
        last_claim = card.get('last_claim_date')
        if isinstance(last_claim, str):
            last_claim = datetime.fromisoformat(last_claim).date()
        elif isinstance(last_claim, datetime):
            last_claim = last_claim.date()
        
        today_claimed = last_claim == now.date() if last_claim else False
        can_claim_today = is_active and not today_claimed
        
        return {
            "is_active": is_active,
            "days_left": days_left,
            "can_claim_today": can_claim_today,
            "today_claimed": today_claimed,
            "end_date": end_date.isoformat() if end_date else None,
        }

    def purchase(self, user_id: int) -> Dict:
        """购买月卡 - 可重复购买，叠加30天"""
        now = self._now()
        
        # 检查宝石
        rows = execute_query(
            "SELECT silver_diamond FROM player WHERE user_id = %s",
            (user_id,)
        )
        if not rows:
            raise MonthCardError("玩家不存在")
        
        current_gems = rows[0].get('silver_diamond', 0) or 0
        if current_gems < PURCHASE_COST_GEMS:
            raise MonthCardError(f"宝石不足，购买月卡需要{PURCHASE_COST_GEMS}颗宝石")
        
        # 扣除宝石，发放立即奖励，累加消耗宝石数
        execute_update(
            "UPDATE player SET silver_diamond = silver_diamond - %s, yuanbao = yuanbao + %s, diamond_spent = diamond_spent + %s WHERE user_id = %s",
            (PURCHASE_COST_GEMS, INITIAL_REWARD, PURCHASE_COST_GEMS, user_id)
        )
        
        # 重新计算VIP等级
        spent_rows = execute_query(
            "SELECT diamond_spent FROM player WHERE user_id = %s",
            (user_id,)
        )
        total_spent = spent_rows[0].get('diamond_spent', 0) if spent_rows else 0
        new_vip_level = self._calc_vip_level(total_spent)
        execute_update(
            "UPDATE player SET vip_level = %s WHERE user_id = %s",
            (new_vip_level, user_id)
        )
        
        # 检查是否已有月卡
        card = self._get_card(user_id)
        
        if card:
            # 已有月卡，叠加30天
            old_end_date = card['end_date']
            if isinstance(old_end_date, str):
                old_end_date = datetime.fromisoformat(old_end_date).date()
            elif isinstance(old_end_date, datetime):
                old_end_date = old_end_date.date()
            
            # 如果月卡已过期，从今天开始；否则从原结束日期叠加
            if now.date() > old_end_date:
                start_date = now.date()
                end_date = start_date + timedelta(days=MONTH_CARD_DAYS - 1)
            else:
                start_date = card['start_date']
                if isinstance(start_date, str):
                    start_date = datetime.fromisoformat(start_date).date()
                elif isinstance(start_date, datetime):
                    start_date = start_date.date()
                end_date = old_end_date + timedelta(days=MONTH_CARD_DAYS)
            
            execute_update(
                """UPDATE player_month_card 
                   SET end_date = %s
                   WHERE user_id = %s""",
                (end_date, user_id)
            )
        else:
            # 新购买
            start_date = now.date()
            end_date = start_date + timedelta(days=MONTH_CARD_DAYS - 1)
            execute_update(
                """INSERT INTO player_month_card (user_id, start_date, end_date)
                   VALUES (%s, %s, %s)""",
                (user_id, start_date, end_date)
            )
        
        return {
            "start_date": start_date.isoformat() if isinstance(start_date, date) else start_date,
            "end_date": end_date.isoformat(),
            "immediate_reward": INITIAL_REWARD,
        }

    def claim_daily_reward(self, user_id: int) -> Dict:
        """领取每日奖励"""
        now = self._now()
        
        card = self._get_card(user_id)
        if not card:
            raise MonthCardError("您还没有购买月卡")
        
        end_date = card['end_date']
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date).date()
        elif isinstance(end_date, datetime):
            end_date = end_date.date()
        
        if now.date() > end_date:
            raise MonthCardError("月卡已过期，请重新购买")
        
        last_claim = card.get('last_claim_date')
        if isinstance(last_claim, str):
            last_claim = datetime.fromisoformat(last_claim).date()
        elif isinstance(last_claim, datetime):
            last_claim = last_claim.date()
        
        if last_claim == now.date():
            raise MonthCardError("今日已领取")
        
        # 发放奖励
        execute_update(
            "UPDATE player SET yuanbao = yuanbao + %s WHERE user_id = %s",
            (DAILY_REWARD, user_id)
        )
        
        # 更新领取记录
        days_claimed = (card.get('days_claimed') or 0) + 1
        execute_update(
            "UPDATE player_month_card SET last_claim_date = %s, days_claimed = %s WHERE user_id = %s",
            (now.date(), days_claimed, user_id)
        )
        
        days_left = max(0, (end_date - now.date()).days)
        
        return {
            "claimed_today": True,
            "days_left": days_left,
            "reward": DAILY_REWARD,
        }
