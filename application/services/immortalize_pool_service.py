from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from application.services.inventory_service import InventoryService, InventoryError
from domain.entities.immortalize_pool import ImmortalizePool
from domain.repositories.immortalize_pool_repo import IImmortalizePoolRepo
from domain.repositories.player_repo import IPlayerRepo
from infrastructure.config.immortalize_config import ImmortalizeConfig
from infrastructure.db.player_repo_mysql import update_gold


class ImmortalizeError(Exception):
    """化仙池业务异常"""


class ImmortalizePoolService:
    def __init__(
        self,
        pool_repo: IImmortalizePoolRepo,
        player_repo: IPlayerRepo,
        inventory_service: Optional[InventoryService] = None,
        config: Optional[ImmortalizeConfig] = None,
    ):
        self.pool_repo = pool_repo
        self.player_repo = player_repo
        self.inventory_service = inventory_service
        self.config = config or ImmortalizeConfig()

    def _now(self) -> datetime:
        return datetime.utcnow()

    @staticmethod
    def _ensure_datetime(value) -> Optional[datetime]:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(str(value))
        except ValueError:
            return None

    def _format_formation_status(self, pool: ImmortalizePool) -> Dict:
        start = self._ensure_datetime(pool.formation_started_at)
        end = self._ensure_datetime(pool.formation_ends_at)
        if not start or not end:
            return {"active": False}
        now = self._now()
        remaining_seconds = max(0, int((end - now).total_seconds()))
        duration_hours = self.config.get_formation_duration_hours()
        hourly_exp = self.config.get_formation_hourly_exp(
            pool.formation_level or pool.pool_level
        )
        return {
            "active": now < end,
            "level": pool.formation_level or pool.pool_level,
            "started_at": start.isoformat(),
            "ends_at": end.isoformat(),
            "remaining_seconds": remaining_seconds,
            "duration_hours": duration_hours,
            "hourly_exp": hourly_exp,
        }

    def _clear_formation(self, pool: ImmortalizePool) -> None:
        pool.formation_level = 0
        pool.formation_started_at = None
        pool.formation_ends_at = None
        pool.formation_last_grant_at = None

    # ===================== 基础 =====================
    def _ensure_pool(self, user_id: int) -> ImmortalizePool:
        pool = self.pool_repo.get_by_user_id(user_id)
        if pool:
            return pool
        pool = ImmortalizePool(user_id=user_id)
        self.pool_repo.upsert(pool)
        return pool

    def _get_capacity(self, level: int) -> int:
        capacity = self.config.get_pool_capacity(level)
        if capacity <= 0:
            raise ImmortalizeError("化仙池容量配置缺失，请稍后重试")
        return capacity

    def get_status(self, user_id: int) -> Dict:
        pool = self._ensure_pool(user_id)
        capacity = self._get_capacity(pool.pool_level)
        next_req = self.config.get_pool_upgrade_requirement(pool.pool_level)
        return {
            "level": pool.pool_level,
            "current_exp": pool.current_exp,
            "capacity": capacity,
            "is_full": pool.current_exp >= capacity,
            "next_upgrade": next_req,
            "formation": self._format_formation_status(pool),
        }

    # ===================== 经验操作 =====================
    def add_exp(self, user_id: int, amount: int) -> Dict:
        if amount <= 0:
            raise ImmortalizeError("注入经验必须大于0")
        pool = self._ensure_pool(user_id)
        capacity = self._get_capacity(pool.pool_level)
        added = pool.add_exp(amount, capacity)
        self.pool_repo.upsert(pool)
        return {
            "added_exp": added,
            "current_exp": pool.current_exp,
            "capacity": capacity,
            "is_full": pool.current_exp >= capacity,
        }

    # ===================== 化仙阵 =====================
    def start_formation(self, user_id: int) -> Dict:
        pool = self._ensure_pool(user_id)
        now = self._now()
        end = self._ensure_datetime(pool.formation_ends_at)
        if end and now < end:
            raise ImmortalizeError("化仙阵正在运行中")

        # 检查并扣除7种结晶各1个
        if not self.inventory_service:
            raise ImmortalizeError("系统错误：背包服务未初始化")
        
        # 7种结晶ID：金、木、水、火、土、风、电
        crystal_item_ids = [1001, 1002, 1003, 1004, 1005, 1006, 1007]
        crystal_names = {
            1001: "金之结晶",
            1002: "木之结晶",
            1003: "水之结晶",
            1004: "火之结晶",
            1005: "土之结晶",
            1006: "风之结晶",
            1007: "电之结晶"
        }
        required_qty = 1
        
        # 检查结晶是否足够
        missing = []
        for item_id in crystal_item_ids:
            owned = self.inventory_service.get_item_count(user_id, item_id)
            if owned < required_qty:
                crystal_name = crystal_names.get(item_id, f"结晶{item_id}")
                missing.append({
                    "item_id": item_id,
                    "name": crystal_name,
                    "required": required_qty,
                    "owned": owned
                })
        
        if missing:
            missing_str = "、".join([f"{m['name']}({m['owned']}/{m['required']})" for m in missing])
            raise ImmortalizeError(f"结晶不足：{missing_str}")
        
        # 扣除结晶
        try:
            for item_id in crystal_item_ids:
                self.inventory_service.remove_item(user_id, item_id, required_qty)
        except InventoryError as exc:
            raise ImmortalizeError(f"扣除结晶失败：{str(exc)}") from exc

        duration_hours = self.config.get_formation_duration_hours()
        pool.formation_level = pool.pool_level
        pool.formation_started_at = now
        pool.formation_ends_at = now + timedelta(hours=duration_hours)
        pool.formation_last_grant_at = now
        self.pool_repo.upsert(pool)
        return self._format_formation_status(pool)

    def grant_formation_exp_for_user(
        self, user_id: int, now: Optional[datetime] = None
    ) -> Optional[Dict]:
        pool = self.pool_repo.get_by_user_id(user_id)
        if not pool:
            return None
        return self._grant_formation_exp(pool, now)

    def _grant_formation_exp(
        self, pool: ImmortalizePool, now: Optional[datetime] = None
    ) -> Optional[Dict]:
        start = self._ensure_datetime(pool.formation_started_at)
        end = self._ensure_datetime(pool.formation_ends_at)
        if not start or not end:
            return None

        last = self._ensure_datetime(pool.formation_last_grant_at) or start
        now = now or self._now()
        if last >= end or now <= last:
            if now >= end:
                self._clear_formation(pool)
                self.pool_repo.upsert(pool)
            return None

        grant_until = min(now, end)
        elapsed_seconds = (grant_until - last).total_seconds()
        hours_to_grant = int(elapsed_seconds // 3600)
        if hours_to_grant <= 0:
            return None

        hourly_exp = self.config.get_formation_hourly_exp(
            pool.formation_level or pool.pool_level
        )
        total_added = 0
        remaining_hours = hours_to_grant
        processed_hours = 0
        while remaining_hours > 0:
            capacity = self._get_capacity(pool.pool_level)
            added = pool.add_exp(hourly_exp, capacity)
            if added <= 0:
                break
            total_added += added
            remaining_hours -= 1
            processed_hours += 1

        pool.formation_last_grant_at = last + timedelta(hours=processed_hours)
        finished = False
        if processed_hours <= 0:
            if grant_until >= end:
                self._clear_formation(pool)
                finished = True
            self.pool_repo.upsert(pool)
            return None

        if grant_until >= end or remaining_hours > 0:
            # 阵结束或容量不足，终止化仙阵
            self._clear_formation(pool)
            finished = True

        self.pool_repo.upsert(pool)
        return {
            "user_id": pool.user_id,
            "hours_processed": processed_hours,
            "exp_per_hour": hourly_exp,
            "total_added": total_added,
            "finished": finished,
        }

    def spend_exp(self, user_id: int, amount: int) -> Dict:
        if amount <= 0:
            raise ImmortalizeError("消耗经验必须大于0")
        pool = self._ensure_pool(user_id)
        if not pool.spend_exp(amount):
            raise ImmortalizeError("化仙池经验不足")
        self.pool_repo.upsert(pool)
        return {
            "spent_exp": amount,
            "current_exp": pool.current_exp,
        }

    # ===================== 升级 =====================
    def upgrade_pool(self, user_id: int) -> Dict:
        pool = self._ensure_pool(user_id)
        req = self.config.get_pool_upgrade_requirement(pool.pool_level)
        if not req:
            raise ImmortalizeError("化仙池已达最高等级")

        player = self.player_repo.get_by_id(user_id)
        if not player:
            raise ImmortalizeError("玩家不存在")
        required_level = req.get("required_player_level", 0)
        if player.level < required_level:
            raise ImmortalizeError(f"需要玩家等级≥{required_level}")

        if not self.inventory_service:
            raise ImmortalizeError("系统错误：背包服务未初始化")

        crystal_ids: List[int] = req.get("crystal_item_ids", [])
        crystal_qty = req.get("crystal_qty_per_type", 0)
        if not crystal_ids or crystal_qty <= 0:
            raise ImmortalizeError("化仙池升级材料配置缺失")

        missing = []
        for item_id in crystal_ids:
            owned = self.inventory_service.get_item_count(user_id, item_id)
            if owned < crystal_qty:
                missing.append({"item_id": item_id, "required": crystal_qty, "owned": owned})
        if missing:
            raise ImmortalizeError(
                "结晶不足：" + ", ".join([f"{m['item_id']}({m['owned']}/{m['required']})" for m in missing])
            )

        copper_cost = req.get("copper_cost", 0)
        if player.gold < copper_cost:
            raise ImmortalizeError("铜钱不足")

        # 扣除材料
        try:
            for item_id in crystal_ids:
                self.inventory_service.remove_item(user_id, item_id, crystal_qty)
        except InventoryError as exc:
            raise ImmortalizeError(str(exc)) from exc

        if copper_cost > 0:
            if not update_gold(user_id, -copper_cost):
                raise ImmortalizeError("铜钱不足")

        pool.pool_level += 1
        self.pool_repo.upsert(pool)
        capacity = self._get_capacity(pool.pool_level)
        return {
            "new_level": pool.pool_level,
            "current_exp": pool.current_exp,
            "capacity": capacity,
        }

    # ===================== 化仙丹 =====================
    def add_dan_exp(self, user_id: int) -> Dict:
        pool = self._ensure_pool(user_id)
        dan_exp = self.config.get_dan_exp(pool.pool_level)
        if dan_exp <= 0:
            raise ImmortalizeError("化仙丹配置缺失，请稍后重试")

        capacity = self._get_capacity(pool.pool_level)
        added = pool.add_exp(dan_exp, capacity)
        self.pool_repo.upsert(pool)

        return {
            "added_exp": added,
            "dan_exp": dan_exp,
            "pool_level": pool.pool_level,
            "current_exp": pool.current_exp,
            "capacity": capacity,
            "is_full": pool.current_exp >= capacity,
        }
