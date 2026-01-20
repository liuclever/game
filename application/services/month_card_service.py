"""
月卡服务 - 简化版
只有一个月卡，购买后30天有效期
"""
from __future__ import annotations

from datetime import datetime, timedelta, date
from typing import Dict, Optional, Callable

from infrastructure.db.connection import execute_query, execute_update
from infrastructure.db.month_card_repo_mysql import MySQLMonthCardRepo, PlayerMonthCard


MONTH_CARD_DAYS = 30
PURCHASE_COST_GEMS = 30
INITIAL_REWARD = 1000
DAILY_REWARD = 200
DEFAULT_MONTH_CARD_MONTH = 1


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
        # 优先走标准仓库（带 month 字段的表结构）
        if isinstance(self.month_card_repo, MySQLMonthCardRepo):
            rec = self.month_card_repo.get_by_user_and_month(user_id, DEFAULT_MONTH_CARD_MONTH)
            if not rec:
                return None
            return {
                "id": rec.id,
                "user_id": rec.user_id,
                "start_date": rec.start_date,
                "end_date": rec.end_date,
                "last_claim_date": rec.last_claim_date,
                "days_claimed": rec.days_claimed,
                "status": rec.status,
            }

        # 兼容旧库（早期简化表：可能没有 month 字段）
        rows = execute_query(
            "SELECT id, user_id, start_date, end_date, last_claim_date, days_claimed FROM player_month_card WHERE user_id = %s LIMIT 1",
            (user_id,),
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
        else:
            # MySQL DATE/DATETIME 之外的类型兜底
            try:
                end_date = datetime.fromisoformat(str(end_date)).date()
            except Exception:
                end_date = now.date()
        
        # 标准表中 status 也可能标记为 expired
        status = str(card.get("status") or "active")
        is_active = (status != "expired") and (now.date() <= end_date)
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

        # 必须有标准仓库，否则容易出现“扣费成功但月卡写入失败”的不一致
        if not isinstance(self.month_card_repo, MySQLMonthCardRepo):
            # 兜底：尝试自动初始化标准仓库（bootstrap 场景一定会注入）
            self.month_card_repo = MySQLMonthCardRepo()
        
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
        
        # 写入/更新月卡记录（标准表：带 month）
        repo: MySQLMonthCardRepo = self.month_card_repo
        rec = repo.get_by_user_and_month(user_id, DEFAULT_MONTH_CARD_MONTH)

        if rec:
            old_end_dt = rec.end_date
            old_end_date = old_end_dt.date() if isinstance(old_end_dt, datetime) else datetime.fromisoformat(str(old_end_dt)).date()
            # 过期从今天起；未过期从原 end_date 叠加 30 天
            if now.date() > old_end_date:
                start_dt = now
                end_dt = now + timedelta(days=MONTH_CARD_DAYS) - timedelta(seconds=1)
            else:
                start_dt = rec.start_date
                end_dt = rec.end_date + timedelta(days=MONTH_CARD_DAYS)
            rec.start_date = start_dt
            rec.end_date = end_dt
            rec.status = "active"
            repo.create_or_update(rec)
        else:
            start_dt = now
            end_dt = now + timedelta(days=MONTH_CARD_DAYS) - timedelta(seconds=1)
            rec = PlayerMonthCard(
                id=None,
                user_id=user_id,
                month=DEFAULT_MONTH_CARD_MONTH,
                start_date=start_dt,
                end_date=end_dt,
                days_total=MONTH_CARD_DAYS,
                days_claimed=0,
                last_claim_date=None,
                status="active",
                initial_reward=INITIAL_REWARD,
                daily_reward=DAILY_REWARD,
                initial_reward_claimed=True,  # 购买即发放了“立即奖励1000元宝”
            )
            repo.create_or_update(rec)
        
        return {
            "start_date": (rec.start_date.date().isoformat() if isinstance(rec.start_date, datetime) else str(rec.start_date)),
            "end_date": (rec.end_date.date().isoformat() if isinstance(rec.end_date, datetime) else str(rec.end_date)),
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
        
        # 更新领取记录（优先标准仓库）
        days_claimed = int(card.get("days_claimed") or 0) + 1
        if isinstance(self.month_card_repo, MySQLMonthCardRepo):
            self.month_card_repo.update_claim(
                user_id=user_id,
                month=DEFAULT_MONTH_CARD_MONTH,
                last_claim_date=now.date(),
                days_claimed=days_claimed,
                status="active",
            )
        else:
            execute_update(
                "UPDATE player_month_card SET last_claim_date = %s, days_claimed = %s WHERE user_id = %s",
                (now.date(), days_claimed, user_id),
            )
        
        days_left = max(0, (end_date - now.date()).days)
        
        return {
            "claimed_today": True,
            "days_left": days_left,
            "reward": DAILY_REWARD,
        }
