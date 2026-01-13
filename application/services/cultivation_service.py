# game/application/services/cultivation_service.py
from datetime import datetime
from typing import Dict, List, Optional, Any
import re
import json
from pathlib import Path

from domain.entities.player import Player
from domain.repositories.player_repo import IPlayerRepo
from domain.repositories.beast_repo import IBeastRepo
from domain.repositories.item_repo import IItemRepo
from application.services.inventory_service import InventoryService
from infrastructure.db.connection import execute_query
from infrastructure.db.player_effect_repo_mysql import MySQLPlayerEffectRepo
from application.services.inventory_service import NINGSHEN_INCENSE_EFFECT_KEY
from domain.rules.cultivation_rules import (
    check_cultivation_eligibility,
    calculate_cultivation_rewards,
    round_cultivation_minutes,
    load_cultivation_config,
    CultivationReward
)

class CultivationError(Exception):
    """修行系统异常"""
    pass


_prestige_cost_cache: Dict[int, int] = {}
_prestige_cost_max_level: Optional[int] = None


def _load_prestige_cost_config() -> Dict[int, int]:
    global _prestige_cost_cache, _prestige_cost_max_level
    if _prestige_cost_cache:
        return _prestige_cost_cache

    base_dir = Path(__file__).resolve().parents[2]
    path = base_dir / "configs" / "player_level_up_exp.json"
    if not path.exists():
        _prestige_cost_cache = {}
        _prestige_cost_max_level = None
        return _prestige_cost_cache

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        _prestige_cost_cache = {}
        _prestige_cost_max_level = None
        return _prestige_cost_cache

    mapping: Dict[int, int] = {}
    raw_mapping = {}
    if isinstance(data, dict) and isinstance(data.get("exp_to_next_level"), dict):
        raw_mapping = data.get("exp_to_next_level") or {}
        max_level_val = data.get("max_level")
        if isinstance(max_level_val, int):
            _prestige_cost_max_level = max_level_val
    elif isinstance(data, dict):
        raw_mapping = data
    
    if isinstance(raw_mapping, dict):
        for k, v in raw_mapping.items():
            try:
                lvl = int(k)
                mapping[lvl] = int(v)
            except Exception:
                continue

    _prestige_cost_cache = mapping
    return _prestige_cost_cache


def _get_max_level() -> int:
    _load_prestige_cost_config()
    if isinstance(_prestige_cost_max_level, int) and _prestige_cost_max_level > 0:
        return _prestige_cost_max_level
    return 100


def _get_required_prestige_for_next_level(player_level: int) -> Optional[int]:
    max_level = _get_max_level()
    if player_level >= max_level:
        return None
    config = _load_prestige_cost_config()
    if not config:
        return None
    return config.get(player_level)


class CultivationService:
    def __init__(
        self, 
        player_repo: IPlayerRepo, 
        beast_repo: IBeastRepo,
        item_repo: IItemRepo,
        inventory_service: InventoryService,
        player_effect_repo: Optional[MySQLPlayerEffectRepo] = None,
    ):
        self.player_repo = player_repo
        self.beast_repo = beast_repo
        self.item_repo = item_repo
        self.inventory_service = inventory_service
        self.player_effect_repo = player_effect_repo

    def _apply_incense_bonus(self, user_id: int, reward: CultivationReward) -> CultivationReward:
        if reward.prestige <= 0:
            return reward
        if not self.player_effect_repo:
            return reward
        if not self.player_effect_repo.is_active(user_id, NINGSHEN_INCENSE_EFFECT_KEY, now=datetime.now()):
            return reward

        # +20% prestige, effect does not stack
        reward.prestige = int(reward.prestige * 1.2 + 0.5)
        return reward

    def _get_incense_remaining_seconds(self, user_id: int, now: Optional[datetime] = None) -> int:
        if now is None:
            now = datetime.now()
        if not self.player_effect_repo:
            return 0
        end_time = self.player_effect_repo.get_end_time(user_id, NINGSHEN_INCENSE_EFFECT_KEY)
        if not end_time:
            return 0
        remaining = int((end_time - now).total_seconds())
        return remaining if remaining > 0 else 0

    def get_status(self, user_id: int) -> Dict[str, Any]:
        """获取玩家当前修行状态"""
        player = self.player_repo.get_by_id(user_id)
        if not player:
            raise CultivationError("玩家不存在")

        enhancement_stone = self.inventory_service.get_item_count(user_id, 9001, include_temp=True)

        prestige_required = _get_required_prestige_for_next_level(player.level)
        can_levelup = prestige_required is not None and player.prestige >= prestige_required
        rank_name = player.get_rank_name()

        now = datetime.now()
        incense_remaining_seconds = self._get_incense_remaining_seconds(user_id, now=now)

        if not player.cultivation_start_time:
            return {
                "is_cultivating": False,
                "player_level": player.level,
                "vip_level": getattr(player, "vip_level", 0),
                "prestige": player.prestige,
                "enhancement_stone": enhancement_stone,
                "prestige_required": prestige_required,
                "can_levelup": can_levelup,
                "rank_name": rank_name,
                "incense_remaining_seconds": incense_remaining_seconds,
            }

        # 计算已修行时长
        # now 已在上面生成
        seconds = int((now - player.cultivation_start_time).total_seconds())
        
        max_duration_seconds = int(player.cultivation_duration or 0)
        if max_duration_seconds <= 0:
            if player.vip_level >= 4:
                max_duration_seconds = 24 * 3600
            elif player.vip_level >= 2:
                max_duration_seconds = 12 * 3600
            else:
                max_duration_seconds = 8 * 3600
        
        # 计算剩余时间（用于倒计时显示）
        remaining_seconds = max(0, max_duration_seconds - seconds)
        
        can_harvest = seconds >= max_duration_seconds
        
        # 获取出战幻兽进行预览奖励计算
        beasts = self.beast_repo.get_by_user_id(user_id)
        main_beasts = [b for b in beasts if b.is_main]

        preview_seconds = max_duration_seconds
        reward = calculate_cultivation_rewards(
            player,
            main_beasts,
            player.cultivation_area,
            player.cultivation_dungeon,
            preview_seconds,
        )
        reward = self._apply_incense_bonus(user_id, reward)

        return {
            "is_cultivating": True,
            "start_time": player.cultivation_start_time.isoformat(),
            "area": player.cultivation_area,
            "dungeon": player.cultivation_dungeon,
            "elapsed_seconds": seconds,
            "remaining_seconds": remaining_seconds,
            "max_duration_seconds": max_duration_seconds,
            "effective_minutes": round_cultivation_minutes(seconds),
            "can_harvest": can_harvest,
            "vip_level": getattr(player, "vip_level", 0),
            "prestige": player.prestige,
            "prestige_required": prestige_required,
            "can_levelup": can_levelup,
            "rank_name": rank_name,
            "incense_remaining_seconds": incense_remaining_seconds,
            "preview_rewards": {
                "prestige": reward.prestige,
                "spirit_stones": reward.spirit_stones,
                "beast_exp": [
                    {"name": b.beast_name, "exp": b.exp_gain} 
                    for b in reward.beast_exp_gains
                ],
                "items": reward.items
            }
        }

    def levelup(self, user_id: int) -> Dict[str, Any]:
        player = self.player_repo.get_by_id(user_id)
        if not player:
            raise CultivationError("玩家不存在")

        max_level = _get_max_level()
        start_level = int(player.level or 1)
        start_prestige = int(player.prestige or 0)

        leveled = 0
        spent = 0

        required = _get_required_prestige_for_next_level(player.level)
        if required is not None and player.level < max_level and player.prestige >= required:
            player.prestige -= required
            if player.prestige < 0:
                player.prestige = 0
            player.level += 1
            leveled = 1
            spent = required

        self.player_repo.save(player)

        next_required = _get_required_prestige_for_next_level(player.level)
        return {
            "ok": True,
            "message": "晋级成功" if leveled > 0 else "声望不足，无法晋级",
            "start_level": start_level,
            "end_level": player.level,
            "levels_gained": leveled,
            "start_prestige": start_prestige,
            "end_prestige": player.prestige,
            "prestige_spent": spent,
            "prestige_required": next_required,
        }

    def start(self, user_id: int, area_name: str, dungeon_name: str, duration_hours: int = 2) -> Dict[str, Any]:
        """开始修行"""
        player = self.player_repo.get_by_id(user_id)
        if not player:
            raise CultivationError("玩家不存在")

        if player.cultivation_start_time:
            raise CultivationError("已在修行中")

        # 校验地图是否存在
        config = load_cultivation_config()
        area_config = next((a for a in config["areas"] if a["name"] == area_name), None)
        if not area_config:
            raise CultivationError(f"未知区域: {area_name}")
        
        dungeon_config = next((d for d in area_config.get("dungeons", []) if d["name"] == dungeon_name), None)
        if not dungeon_config:
            raise CultivationError(f"区域 {area_name} 中不存在副本: {dungeon_name}")

        # 校验是否开启修行（定老城及以上）
        if not area_config.get("can_cultivate", False):
            raise CultivationError(f"{area_name} 暂不支持修行")

        requested_duration_hours = duration_hours
        try:
            duration_hours = int(duration_hours)
        except Exception:
            duration_hours = 2
        if duration_hours not in (2, 4, 8, 12, 24):
            raise CultivationError("修行时长无效，仅支持2/4/8/12/24小时")
        # VIP5+才能使用24小时修炼
        if duration_hours >= 24 and player.vip_level < 5:
            raise CultivationError("24小时修行需要 VIP5")
        # VIP2+才能使用12小时修炼
        if duration_hours >= 12 and player.vip_level < 2:
            raise CultivationError("12小时修行需要 VIP2")

        # 设置开始修行状态
        player.cultivation_start_time = datetime.now()
        player.cultivation_duration = duration_hours * 3600
        player.cultivation_area = area_name
        player.cultivation_dungeon = dungeon_name
        
        self.player_repo.save(player)
        
        return {
            "ok": True,
            "message": f"在 {area_name}-{dungeon_name} 开始修行（{duration_hours}小时）",
            "start_time": player.cultivation_start_time.isoformat(),
            "requested_duration_hours": requested_duration_hours,
            "applied_duration_hours": duration_hours,
            "vip_level": getattr(player, "vip_level", 0),
        }

    def end(self, user_id: int) -> Dict[str, Any]:
        """结束修行并领取奖励"""
        player = self.player_repo.get_by_id(user_id)
        if not player:
            raise CultivationError("玩家不存在")

        if not player.cultivation_start_time:
            raise CultivationError("当前未在修行")

        now = datetime.now()
        seconds = int((now - player.cultivation_start_time).total_seconds())

        duration_seconds = int(player.cultivation_duration or 0)
        if duration_seconds > 0 and seconds < duration_seconds:
            raise CultivationError("修行未完成，暂不可收获")
        
        # 校验基本资格（5分钟规则等）
        eligible, reason = check_cultivation_eligibility(player, player.cultivation_area, seconds)
        if not eligible:
            # 如果不符合资格，也允许结束，但不发奖励
            player.cultivation_start_time = None
            player.cultivation_duration = None
            player.cultivation_area = None
            player.cultivation_dungeon = None
            self.player_repo.save(player)
            return {"ok": False, "error": reason}

        # 计算最终奖励
        beasts = self.beast_repo.get_by_user_id(user_id)
        main_beasts = [b for b in beasts if b.is_main]
        
        reward = calculate_cultivation_rewards(
            player, 
            main_beasts, 
            player.cultivation_area, 
            player.cultivation_dungeon, 
            min(seconds, duration_seconds) if duration_seconds > 0 else seconds
        )
        reward = self._apply_incense_bonus(user_id, reward)

        # 1. 应用玩家基础奖励
        player.prestige += reward.prestige
        if reward.spirit_stones > 0:
            self.inventory_service.add_item(user_id, 9001, reward.spirit_stones)
        
        # 2. 应用幻兽经验
        beast_summaries = []
        for beast_gain in reward.beast_exp_gains:
            beast = next((b for b in main_beasts if b.id == beast_gain.beast_id), None)
            if beast and beast_gain.exp_gain > 0:
                leveled_up = beast.add_exp(beast_gain.exp_gain)
                self.beast_repo.save(beast)
                beast_summaries.append({
                    "name": beast.nickname or beast.id,
                    "exp_gain": beast_gain.exp_gain,
                    "leveled_up": leveled_up,
                    "current_level": beast.level
                })
        
        # 3. 处理物品奖励
        item_summaries = []
        for item_str in reward.items:
            # 解析 "水草兽召唤球×1"
            match = re.match(r"(.+?)×(\d+)", item_str)
            if match:
                item_name = match.group(1)
                quantity = int(match.group(2))
                
                # 寻找物品ID
                item_template = self.item_repo.get_by_name(item_name)
                if item_template:
                    self.inventory_service.add_item(user_id, item_template.id, quantity)
                    item_summaries.append(item_str)

        # 重置修行状态
        player.cultivation_start_time = None
        player.cultivation_duration = None
        player.cultivation_area = None
        player.cultivation_dungeon = None
        self.player_repo.save(player)

        return {
            "ok": True,
            "message": "修行完成",
            "rewards": {
                "prestige": reward.prestige,
                "spirit_stones": reward.spirit_stones,
                "beasts": beast_summaries,
                "items": item_summaries
            },
            "duration_minutes": round_cultivation_minutes(seconds)
        }

    def stop(self, user_id: int) -> Dict[str, Any]:
        """终止修行，根据时间决定是否发放奖励"""
        player = self.player_repo.get_by_id(user_id)
        if not player:
            raise CultivationError("玩家不存在")

        # 添加调试日志
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[Cultivation Stop] user_id={user_id}, cultivation_start_time={player.cultivation_start_time}, cultivation_area={player.cultivation_area}, cultivation_dungeon={player.cultivation_dungeon}")
        
        if not player.cultivation_start_time:
            raise CultivationError("当前未在修行")

        now = datetime.now()
        seconds = int((now - player.cultivation_start_time).total_seconds())
        min_seconds = 5 * 60  # 至少5分钟才能获得奖励
        
        # 清除修行状态
        area = player.cultivation_area
        dungeon = player.cultivation_dungeon
        player.cultivation_start_time = None
        player.cultivation_duration = None
        player.cultivation_area = None
        player.cultivation_dungeon = None
        
        # 如果修行时间不足5分钟，不发放奖励
        if seconds < min_seconds:
            self.player_repo.save(player)
            return {
                "ok": True,
                "message": f"修行时间不足5分钟，未获得奖励",
                "rewards": None
            }
        
        # 修行时间足够，计算并发放奖励
        beasts = self.beast_repo.get_by_user_id(user_id)
        main_beasts = [b for b in beasts if b.is_main]
        
        reward = calculate_cultivation_rewards(
            player, main_beasts, area, dungeon, seconds
        )
        reward = self._apply_incense_bonus(user_id, reward)

        # 应用奖励
        player.prestige += reward.prestige
        if reward.spirit_stones > 0:
            self.inventory_service.add_item(user_id, 9001, reward.spirit_stones)
        
        beast_summaries = []
        for beast_gain in reward.beast_exp_gains:
            beast = next((b for b in main_beasts if b.id == beast_gain.beast_id), None)
            if beast and beast_gain.exp_gain > 0:
                leveled_up = beast.add_exp(beast_gain.exp_gain)
                self.beast_repo.save(beast)
                beast_summaries.append({
                    "name": beast.nickname or beast.id,
                    "exp_gain": beast_gain.exp_gain,
                    "leveled_up": leveled_up
                })
        
        # 处理物品奖励
        item_summaries = []
        for item_str in reward.items:
            match = re.match(r"(.+?)×(\d+)", item_str)
            if match:
                item_name = match.group(1)
                quantity = int(match.group(2))
                item_template = self.item_repo.get_by_name(item_name)
                if item_template:
                    self.inventory_service.add_item(user_id, item_template.id, quantity)
                    item_summaries.append(item_str)

        self.player_repo.save(player)

        return {
            "ok": True,
            "message": "修行结束",
            "rewards": {
                "prestige": reward.prestige,
                "spirit_stones": reward.spirit_stones,
                "beasts": beast_summaries,
                "items": item_summaries
            },
            "duration_minutes": round_cultivation_minutes(seconds)
        }
