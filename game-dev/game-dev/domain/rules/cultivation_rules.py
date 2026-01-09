# game/domain/rules/cultivation_rules.py
import json
import random
import math
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass, field

from domain.entities.player import Player
from domain.entities.beast import Beast

# 加载修行配置
def load_cultivation_config() -> Dict[str, Any]:
    config_path = Path(__file__).resolve().parents[2] / "configs" / "cultivation_maps.json"
    if not config_path.exists():
        return {"areas": []}
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

@dataclass
class BeastExpGain:
    beast_id: int
    beast_name: str
    exp_gain: int
    level_up: bool = False

@dataclass
class CultivationReward:
    prestige: int = 0
    spirit_stones: int = 0
    beast_exp_gains: List[BeastExpGain] = field(default_factory=list)
    items: List[str] = field(default_factory=list)  # 获得的召唤球等物品

def round_cultivation_minutes(seconds: int) -> int:
    """
    修行时间修约逻辑：
    60秒内都舍去，只保留整数分钟。
    """
    return seconds // 60


def _round_half_up(value: float) -> int:
    return int(math.floor(value + 0.5))

def check_cultivation_eligibility(player: Player, area_name: str, seconds: int) -> Tuple[bool, Optional[str]]:
    """
    校验修行资格：
    1. 至少修行5分钟。
    2. 地图是否允许修行（定老城及以上）。
    3. VIP时长限制（12h/24h）。
    """
    # 基础时长校验
    if seconds < 300: # 5分钟
        return False, "修行时间不足5分钟，无法获得奖励"
    
    # 获取配置
    config = load_cultivation_config()
    area_config = next((a for a in config["areas"] if a["name"] == area_name), None)
    
    if not area_config or not area_config.get("can_cultivate", False):
        return False, f"{area_name} 不支持修行"

    # VIP 时长校验
    hours = seconds / 3600
    if hours > 24:
        return False, "单次修行时间上限为24小时"
    if hours > 12:
        if player.vip_level < 2:
            return False, "修行超过12小时需要 VIP 2"

    return True, None

def calculate_cultivation_rewards(
    player: Player, 
    beasts: List[Beast], 
    area_name: str, 
    dungeon_name: str, 
    seconds: int
) -> CultivationReward:
    """
    根据规则计算奖励
    """
    reward = CultivationReward()
    
    # 1. 计算有效分钟
    effective_minutes = round_cultivation_minutes(seconds)
    
    # 2. 获取地图配置
    config = load_cultivation_config()
    area_config = next((a for a in config["areas"] if a["name"] == area_name), None)
    if not area_config:
        return reward
    
    # 3. 计算基础奖励（声望、强化石）
    reward.prestige = _round_half_up(effective_minutes * area_config.get("prestige_rate", 0))
    reward.spirit_stones = _round_half_up(effective_minutes * area_config.get("stone_rate", 0))
    
    # 4. 计算幻兽经验
    beast_exp_rate = area_config.get("beast_exp_rate", 0)
    for beast in beasts:
        exp_gain = 0
        # 规则：幻兽高于人物5级，无法获得幻兽经验
        if beast.level <= player.level + 5:
            exp_gain = _round_half_up(effective_minutes * beast_exp_rate)
        
        reward.beast_exp_gains.append(BeastExpGain(
            beast_id=beast.id or 0,
            beast_name=beast.nickname or "未知幻兽",
            exp_gain=exp_gain
        ))
    
    # 5. 掉落逻辑：2小时及以上，15%概率获得召唤球
    if seconds >= 7200: # 2小时
        dungeon_config = next((d for d in area_config.get("dungeons", []) if d["name"] == dungeon_name), None)
        if dungeon_config and dungeon_config.get("capture_balls"):
            if random.random() < 0.15:
                ball = random.choice(dungeon_config["capture_balls"])
                reward.items.append(f"{ball}×1")
                
    return reward
