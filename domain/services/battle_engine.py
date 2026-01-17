"""
统一战斗引擎

使用策略模式，方便后期更换/扩展战斗规则
所有PVP战斗（古战场、竞技场、切磋等）都使用此引擎
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Protocol
import random


@dataclass
class BeastStats:
    """幻兽战斗属性"""
    id: int
    name: str
    realm: str = ""  # 境界
    level: int = 1
    hp: int = 100
    max_hp: int = 100
    attack: int = 10
    defense: int = 5
    speed: int = 10
    physical_attack: int = 10
    magic_attack: int = 10
    physical_defense: int = 5
    magic_defense: int = 5
    nature: str = "物理"  # 物理/法术
    
    def is_magic_type(self) -> bool:
        return self.nature in ("法术", "魔法", "法系")
    
    @property
    def full_name(self) -> str:
        if self.realm:
            return f"{self.name}-{self.realm}"
        return self.name


@dataclass
class BattleRoundResult:
    """单回合结果"""
    round_num: int
    attacker_name: str
    defender_name: str
    damage: int
    attacker_hp_after: int
    defender_hp_after: int
    action_text: str = ""


@dataclass
class SingleBattleResult:
    """单场战斗结果（一只幻兽 vs 一只幻兽）"""
    battle_num: int
    attacker_beast: str
    defender_beast: str
    winner: str  # "attacker" or "defender"
    rounds: List[BattleRoundResult] = field(default_factory=list)
    result_text: str = ""


@dataclass
class FullBattleResult:
    """完整战斗结果（多只幻兽 vs 多只幻兽）"""
    is_victory: bool  # 攻击方是否胜利
    attacker_wins: int
    defender_wins: int
    battles: List[SingleBattleResult] = field(default_factory=list)
    winner_name: str = ""
    loser_name: str = ""


class DamageCalculator(ABC):
    """伤害计算器接口 - 策略模式"""
    
    @abstractmethod
    def calculate(self, attacker: BeastStats, defender: BeastStats) -> int:
        """计算伤害"""
        pass


class SimpleDamageCalculator(DamageCalculator):
    """简单伤害计算：使用新的扣血公式
    
    新规则（2026年1月修订）：
    - 第一种情况（攻击 - 防御 >= 0）：伤害 = (攻击 - 防御) × 0.069，四舍五入
    - 第二种情况（攻击 - 防御 < 0）：固定扣血 5 点
    """
    
    def calculate(self, attacker: BeastStats, defender: BeastStats) -> int:
        if attacker.is_magic_type():
            diff = attacker.magic_attack - defender.magic_defense
        else:
            diff = attacker.physical_attack - defender.physical_defense
        
        if diff >= 0:
            damage = round(diff * 0.069)
        else:
            damage = 5
        
        return max(1, damage)


class RandomDamageCalculator(DamageCalculator):
    """带随机浮动的伤害计算（已废弃，建议统一使用 SimpleDamageCalculator）
    
    新规则（2026年1月修订）不再使用随机浮动，统一使用固定系数 0.069。
    保留此类仅为向后兼容，实际计算已改为使用新公式。
    """
    
    def __init__(self, variance: float = 0.0):
        # 新规则不再使用随机浮动，保留接口兼容性
        self.variance = 0.0
    
    def calculate(self, attacker: BeastStats, defender: BeastStats) -> int:
        # 统一使用新公式
        if attacker.is_magic_type():
            diff = attacker.magic_attack - defender.magic_defense
        else:
            diff = attacker.physical_attack - defender.physical_defense
        
        if diff >= 0:
            damage = round(diff * 0.069)
        else:
            damage = 5
        
        return max(1, damage)


class BattlePowerCalculator(DamageCalculator):
    """基于战力的伤害计算（临时，用于测试）"""
    
    def calculate(self, attacker: BeastStats, defender: BeastStats) -> int:
        # 简单按战力比例计算
        attacker_power = attacker.attack + attacker.physical_attack + attacker.magic_attack
        defender_power = defender.defense + defender.physical_defense + defender.magic_defense
        damage = max(1, attacker_power - defender_power // 2)
        return damage


class BattleEngine:
    """
    统一战斗引擎
    
    使用方式：
        engine = BattleEngine()
        result = engine.fight(player1_beasts, player2_beasts, "玩家1", "玩家2")
    
    更换战斗规则：
        engine = BattleEngine(damage_calculator=CustomDamageCalculator())
    """
    
    def __init__(
        self,
        damage_calculator: Optional[DamageCalculator] = None,
        max_rounds_per_battle: int = 20,
    ):
        self.damage_calculator = damage_calculator or SimpleDamageCalculator()
        self.max_rounds = max_rounds_per_battle
    
    def set_damage_calculator(self, calculator: DamageCalculator):
        """动态更换伤害计算器"""
        self.damage_calculator = calculator
    
    def fight(
        self,
        attacker_beasts: List[BeastStats],
        defender_beasts: List[BeastStats],
        attacker_name: str = "攻击方",
        defender_name: str = "防守方",
    ) -> FullBattleResult:
        """
        执行完整战斗
        
        规则：双方幻兽依次对战，先全灭的一方输
        """
        battles = []
        attacker_wins = 0
        defender_wins = 0
        
        # 复制HP状态
        a_beasts = [self._copy_beast(b) for b in attacker_beasts]
        d_beasts = [self._copy_beast(b) for b in defender_beasts]
        
        a_index = 0
        d_index = 0
        battle_num = 0
        
        while a_index < len(a_beasts) and d_index < len(d_beasts):
            battle_num += 1
            a_beast = a_beasts[a_index]
            d_beast = d_beasts[d_index]
            
            # 单场战斗
            result = self._battle_one(
                a_beast, d_beast,
                attacker_name, defender_name,
                battle_num
            )
            battles.append(result)
            
            if result.winner == "attacker":
                attacker_wins += 1
                d_index += 1  # 防守方换下一只
            else:
                defender_wins += 1
                a_index += 1  # 攻击方换下一只
        
        # 判断最终胜负
        is_victory = d_index >= len(d_beasts)
        
        return FullBattleResult(
            is_victory=is_victory,
            attacker_wins=attacker_wins,
            defender_wins=defender_wins,
            battles=battles,
            winner_name=attacker_name if is_victory else defender_name,
            loser_name=defender_name if is_victory else attacker_name,
        )
    
    def quick_fight(
        self,
        attacker_beasts: List[BeastStats],
        defender_beasts: List[BeastStats],
    ) -> bool:
        """
        快速战斗，只返回攻击方是否胜利
        用于批量模拟测试
        """
        result = self.fight(attacker_beasts, defender_beasts)
        return result.is_victory
    
    def fight_by_power(
        self,
        attacker_power: int,
        defender_power: int,
    ) -> bool:
        """
        基于战力的快速判定（用于测试）
        战力高的一方有更大概率获胜
        """
        total = attacker_power + defender_power
        if total == 0:
            return random.choice([True, False])
        
        win_rate = attacker_power / total
        return random.random() < win_rate
    
    def _copy_beast(self, beast: BeastStats) -> BeastStats:
        """复制幻兽，保留独立HP"""
        return BeastStats(
            id=beast.id,
            name=beast.name,
            realm=beast.realm,
            level=beast.level,
            hp=beast.max_hp,
            max_hp=beast.max_hp,
            attack=beast.attack,
            defense=beast.defense,
            speed=beast.speed,
            physical_attack=beast.physical_attack,
            magic_attack=beast.magic_attack,
            physical_defense=beast.physical_defense,
            magic_defense=beast.magic_defense,
            nature=beast.nature,
        )
    
    def _battle_one(
        self,
        attacker: BeastStats,
        defender: BeastStats,
        attacker_name: str,
        defender_name: str,
        battle_num: int,
    ) -> SingleBattleResult:
        """单场战斗"""
        a_hp = attacker.hp
        d_hp = defender.hp
        rounds = []
        round_num = 0
        
        while a_hp > 0 and d_hp > 0 and round_num < self.max_rounds:
            round_num += 1
            
            # 速度决定先后手
            if attacker.speed >= defender.speed:
                # 攻击方先手
                damage = self.damage_calculator.calculate(attacker, defender)
                d_hp = max(0, d_hp - damage)
                
                rounds.append(BattleRoundResult(
                    round_num=round_num,
                    attacker_name=attacker.full_name,
                    defender_name=defender.full_name,
                    damage=damage,
                    attacker_hp_after=a_hp,
                    defender_hp_after=d_hp,
                    action_text=f"『{attacker_name}』的{attacker.full_name}攻击『{defender_name}』的{defender.full_name}，造成{damage}伤害",
                ))
                
                if d_hp <= 0:
                    break
                
                # 防守方反击
                damage = self.damage_calculator.calculate(defender, attacker)
                a_hp = max(0, a_hp - damage)
                
                rounds.append(BattleRoundResult(
                    round_num=round_num,
                    attacker_name=defender.full_name,
                    defender_name=attacker.full_name,
                    damage=damage,
                    attacker_hp_after=d_hp,
                    defender_hp_after=a_hp,
                    action_text=f"『{defender_name}』的{defender.full_name}反击『{attacker_name}』的{attacker.full_name}，造成{damage}伤害",
                ))
            else:
                # 防守方先手
                damage = self.damage_calculator.calculate(defender, attacker)
                a_hp = max(0, a_hp - damage)
                
                rounds.append(BattleRoundResult(
                    round_num=round_num,
                    attacker_name=defender.full_name,
                    defender_name=attacker.full_name,
                    damage=damage,
                    attacker_hp_after=d_hp,
                    defender_hp_after=a_hp,
                    action_text=f"『{defender_name}』的{defender.full_name}先手攻击『{attacker_name}』的{attacker.full_name}，造成{damage}伤害",
                ))
                
                if a_hp <= 0:
                    break
                
                # 攻击方反击
                damage = self.damage_calculator.calculate(attacker, defender)
                d_hp = max(0, d_hp - damage)
                
                rounds.append(BattleRoundResult(
                    round_num=round_num,
                    attacker_name=attacker.full_name,
                    defender_name=defender.full_name,
                    damage=damage,
                    attacker_hp_after=a_hp,
                    defender_hp_after=d_hp,
                    action_text=f"『{attacker_name}』的{attacker.full_name}反击『{defender_name}』的{defender.full_name}，造成{damage}伤害",
                ))
        
        # 判断胜负
        if a_hp > 0 and d_hp <= 0:
            winner = "attacker"
            result_text = f"『{attacker_name}』的{attacker.full_name}获胜"
        elif d_hp > 0 and a_hp <= 0:
            winner = "defender"
            result_text = f"『{defender_name}』的{defender.full_name}获胜"
        elif a_hp > d_hp:
            winner = "attacker"
            result_text = f"回合结束，『{attacker_name}』的{attacker.full_name}剩余HP更高，获胜"
        else:
            winner = "defender"
            result_text = f"回合结束，『{defender_name}』的{defender.full_name}剩余HP更高，获胜"
        
        return SingleBattleResult(
            battle_num=battle_num,
            attacker_beast=attacker.full_name,
            defender_beast=defender.full_name,
            winner=winner,
            rounds=rounds,
            result_text=result_text,
        )
