from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, List, Dict


@dataclass
class TowerGuardian:
    """守塔幻兽"""
    name: str
    level: int
    hp: int
    attack: int
    defense: int
    speed: int
    
    # 新增属性
    nature: str = "物系"           # 特性：物系/法系
    physical_attack: int = 0       # 物攻
    magic_attack: int = 0          # 法攻
    physical_defense: int = 0      # 物防
    magic_defense: int = 0         # 法防
    description: str = ""          # 描述
    
    # 战斗中的当前HP
    current_hp: int = 0
    
    def __post_init__(self):
        if self.current_hp == 0:
            self.current_hp = self.hp
        # 如果没有设置物攻法攻，则从attack推算
        if self.physical_attack == 0:
            self.physical_attack = self.attack
        if self.magic_attack == 0:
            self.magic_attack = int(self.attack * 0.8)
        if self.physical_defense == 0:
            self.physical_defense = self.defense
        if self.magic_defense == 0:
            self.magic_defense = int(self.defense * 0.6)
    
    def is_magic_type(self) -> bool:
        """判断是否为法系"""
        # 特性格式为 "法系XX" 或 "物系XX"，需要判断前缀
        return self.nature.startswith("法系")


@dataclass
class TowerState:
    """玩家闯塔状态"""
    user_id: int
    tower_type: str = "tongtian"
    current_floor: int = 1
    max_floor_record: int = 1
    today_count: int = 0
    last_challenge_date: Optional[date] = None
    
    def can_challenge(self, daily_limit: int) -> bool:
        """检查今日是否还能挑战"""
        today = date.today()
        if self.last_challenge_date != today:
            return True
        return self.today_count < daily_limit
    
    def reset_daily_if_needed(self):
        """如果是新的一天，重置每日次数"""
        today = date.today()
        if self.last_challenge_date != today:
            self.today_count = 0
            self.last_challenge_date = today


@dataclass
class BattleRound:
    """单回合记录"""
    round_num: int
    attacker_side: str          # "player" | "guardian"
    attacker_name: str
    defender_name: str
    damage: int
    attacker_hp_after: int
    defender_hp_after: int
    # 新增字段：技能名与完整描述（来自统一PVP战斗引擎）
    skill_name: str = ""
    description: str = ""


@dataclass
class FloorBattle:
    """单层战斗记录"""
    floor: int
    guardians: List[Dict]       # 守塔幻兽信息列表
    beasts_used: List[str]      # 参战的幻兽名列表
    rounds: List[BattleRound] = field(default_factory=list)
    is_victory: bool = False
    rewards: Dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "floor": self.floor,
            "guardians": self.guardians,
            "beasts_used": self.beasts_used,
            "rounds_count": len(self.rounds),
            # 提供给前端的简要回合列表，结构与镇妖战报保持一致：
            # [{"round": 1, "action": "『玩家』的圣灵蚁使用高级必杀攻击『通天塔第1层』的远古谜兽，气血-1234"}, ...]
            "rounds": [
                {
                    "round": r.round_num,
                    "action": r.description,
                    "attacker_hp": r.attacker_hp_after,
                    "defender_hp": r.defender_hp_after,
                }
                for r in self.rounds
            ],
            "is_victory": self.is_victory,
            "rewards": self.rewards,
        }
    
    def to_detail_dict(self) -> dict:
        """详细战报"""
        return {
            "floor": self.floor,
            "guardians": self.guardians,
            "beasts_used": self.beasts_used,
            "rounds": [
                {
                    "round_num": r.round_num,
                    "attacker_side": r.attacker_side,
                    "attacker_name": r.attacker_name,
                    "defender_name": r.defender_name,
                    "damage": r.damage,
                    "attacker_hp_after": r.attacker_hp_after,
                    "defender_hp_after": r.defender_hp_after,
                    "skill_name": r.skill_name,
                    "description": r.description,
                }
                for r in self.rounds
            ],
            "is_victory": self.is_victory,
            "rewards": self.rewards,
        }


@dataclass
class AutoChallengeResult:
    """自动闯塔结果"""
    user_id: int
    tower_type: str
    start_floor: int
    end_floor: int
    battles: List[FloorBattle] = field(default_factory=list)
    total_rewards: Dict = field(default_factory=dict)
    stopped_reason: str = ""    # "all_dead" | "max_floor" | "daily_limit"
    
    def to_dict(self) -> dict:
        return {
            "tower_type": self.tower_type,
            "start_floor": self.start_floor,
            "end_floor": self.end_floor,
            "battles": [b.to_dict() for b in self.battles],
            "total_rewards": self.total_rewards,
            "stopped_reason": self.stopped_reason,
        }
