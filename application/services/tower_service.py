from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import random

from domain.entities.tower import (
    TowerGuardian, TowerState, BattleRound, FloorBattle, AutoChallengeResult
)
from domain.entities.beast import Beast, BeastTemplate
from domain.repositories.tower_repo import ITowerStateRepo, ITowerConfigRepo
from domain.repositories.player_repo import IPlayerRepo
from application.services.inventory_service import InventoryService
from domain.services.pvp_battle_engine import PvpBeast, PvpPlayer, run_pvp_battle
from domain.services.skill_system import apply_buff_debuff_skills


class TowerError(Exception):
    pass


@dataclass
class PlayerBeast:
    """战斗用的玩家幻兽数据"""
    id: int
    name: str
    realm: str
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

    # 技能列表（用于接入统一技能系统）
    skills: List[str] = field(default_factory=list)

    current_hp: int = 0
    
    def __post_init__(self):
        if self.current_hp == 0:
            self.current_hp = self.hp
        # 如果没有设置物攻法攻，则从attack推算
        if self.physical_attack == 0:
            self.physical_attack = self.attack
        if self.magic_attack == 0:
            self.magic_attack = int(self.attack * 0.9)
        if self.physical_defense == 0:
            self.physical_defense = self.defense
        if self.magic_defense == 0:
            self.magic_defense = int(self.defense * 1.2)
    
    @property
    def full_name(self) -> str:
        return f"{self.name}-{self.realm}"
    
    def is_magic_type(self) -> bool:
        """判断是否为法系"""
        return "法" in self.nature and "系" in self.nature


class TowerBattleService:
    """闯塔战斗服务"""

    def __init__(
        self,
        state_repo: ITowerStateRepo,
        config_repo: ITowerConfigRepo,
        inventory_service: InventoryService = None,
        player_repo: IPlayerRepo | None = None,
    ):
        self.state_repo = state_repo
        self.config_repo = config_repo
        self.inventory_service = inventory_service
        self.player_repo = player_repo

    def _get_daily_limit(self) -> int:
        """获取每日闯塔次数限制（固定为4次）"""
        return 4

    def _ensure_can_challenge_today(self, user_id: int, state: TowerState, is_continue: bool = False) -> int:
        """检查今日是否还能闯塔
        
        规则：
        - 每日最多4次
        - 第1次免费
        - 第2-4次每次需要200元宝重置
        
        Args:
            is_continue: 是否是继续挑战（继续挑战不扣元宝，不重置层数）
        """
        daily_limit = self._get_daily_limit()
        current_count = int(state.today_count or 0)
        
        # 检查是否已达到每日上限
        if current_count >= daily_limit:
            raise TowerError(f"今日闯塔次数已用完（{daily_limit}次）")
        
        # 继续挑战不需要扣元宝和重置层数
        if is_continue:
            return daily_limit
        
        # 第1次免费，第2-4次需要花费元宝
        if current_count >= 1:
            if self.player_repo is None:
                raise TowerError("系统错误：PlayerRepo 未配置")
            
            player = self.player_repo.get_by_id(user_id)
            if player is None:
                raise TowerError("玩家不存在")
            
            cost = 200
            if int(getattr(player, "yuanbao", 0) or 0) < cost:
                raise TowerError(f"元宝不足，需要{cost}元宝开始第{current_count + 1}次闯塔")
            
            # 扣除元宝
            player.yuanbao = int(getattr(player, "yuanbao", 0) or 0) - cost
            self.player_repo.save(player)
            
            # 重置当前层数为1
            state.current_floor = 1
        
        return daily_limit
    
    def roll_special_reward(self, tower_type: str, floor: int) -> Optional[Dict]:
        """抽取特殊奖励（每5层一次）"""
        config = self.config_repo.get_special_reward_config(tower_type, floor)
        if not config:
            return None

        drop_rate = config.get("drop_rate", 100)
        try:
            drop_rate = int(drop_rate)
        except Exception:
            drop_rate = 100
        if drop_rate < 0:
            drop_rate = 0
        if drop_rate > 100:
            drop_rate = 100
        if random.randint(1, 100) > drop_rate:
            return None
        
        item_pool = config.get("item_pool", [])
        if not item_pool:
            return None
        
        # 根据权重随机选择
        total_weight = sum(item.get("weight", 10) for item in item_pool)
        roll = random.randint(1, total_weight)
        
        cumulative = 0
        for item in item_pool:
            cumulative += item.get("weight", 10)
            if roll <= cumulative:
                return {
                    "item_id": item["item_id"],
                    "name": item.get("name", ""),
                    "quantity": config.get("quantity", 1),
                }
        
        # 默认返回第一个
        return {
            "item_id": item_pool[0]["item_id"],
            "name": item_pool[0].get("name", ""),
            "quantity": config.get("quantity", 1),
        }
    
    def roll_spirit_drop(self, tower_type: str, floor: int) -> Optional[Dict]:
        """抽取战灵掉落（特定层数20%概率）"""
        if not self.config_repo.is_spirit_drop_floor(tower_type, floor):
            return None
        
        config = self.config_repo.get_spirit_drop_config(tower_type)
        if not config:
            return None
        
        # 检查是否触发掉落（20%概率）
        drop_rate = config.get("drop_rate", 20)
        if random.randint(1, 100) > drop_rate:
            return None
        
        item_pool = config.get("item_pool", [])
        if not item_pool:
            return None
        
        # 等概率随机选择一个战灵
        total_weight = sum(item.get("weight", 1) for item in item_pool)
        roll = random.randint(1, total_weight)
        
        cumulative = 0
        for item in item_pool:
            cumulative += item.get("weight", 1)
            if roll <= cumulative:
                return {
                    "item_id": item["item_id"],
                    "name": item.get("name", ""),
                    "quantity": 1,
                }
        
        return None
    
    def get_tower_info(self, user_id: int, tower_type: str = "tongtian") -> dict:
        """获取闯塔信息"""
        state = self.state_repo.get_by_user_id(user_id, tower_type)
        state.reset_daily_if_needed()
        
        config = self.config_repo.get_tower_config(tower_type)
        
        daily_limit = self._get_daily_limit()

        # 兼容旧逻辑遗留的超限次数（例如 5/4），钳制到上限并回写
        if int(state.today_count or 0) > int(daily_limit or 0):
            state.today_count = int(daily_limit or 0)
            self.state_repo.save(state)
        
        return {
            "tower_type": tower_type,
            "tower_name": config.get("name", ""),
            "current_floor": state.current_floor,
            "max_floor_record": state.max_floor_record,
            "max_floor": config.get("max_floor", 120),
            "today_count": state.today_count,
            "daily_limit": daily_limit,
            "energy_cost": config.get("energy_cost", 20),
            "buff": config.get("buff", {}),
        }
    
    def reset_tower(self, user_id: int, tower_type: str = "tongtian", pending_rewards: dict = None) -> dict:
        """退出闯塔，重置层数，发放累积奖励"""
        state = self.state_repo.get_by_user_id(user_id, tower_type)
        state.reset_daily_if_needed()
        
        # 发放累积的奖励到背包
        if pending_rewards and self.inventory_service:
            for item in pending_rewards.get("items", []):
                self.inventory_service.add_item(
                    user_id=user_id,
                    item_id=item["item_id"],
                    quantity=item.get("quantity", 1),
                )
        
        # 重置当前层数为1
        state.current_floor = 1
        
        self.state_repo.save(state)
        
        return self.get_tower_info(user_id, tower_type)
    
    def get_floor_guardians(self, tower_type: str, floor: int) -> List[dict]:
        """获取某层守塔幻兽信息"""
        guardians = self.config_repo.get_guardians_for_floor(tower_type, floor)
        return [
            {
                "name": g.name,
                "level": g.level,
                "hp": g.hp,
                "attack": g.attack,
                "defense": g.defense,
                "speed": g.speed,
            }
            for g in guardians
        ]
    
    def apply_buff(self, beast: PlayerBeast, buff_config: dict) -> PlayerBeast:
        """应用鼓舞加成。

        注意：必须保留原有的技能列表，否则鼓舞后的幻兽在闯塔战斗中将失去所有技能，
        导致统一 PVP 战斗引擎看不到任何技能，战报中也就不会出现“使用XX技能”的描述。
        """
        if not buff_config.get("enabled", False):
            return beast
        
        bonus = 1 + buff_config.get("attack_bonus", 0)
        def_bonus = 1 + buff_config.get("defense_bonus", 0)
        
        return PlayerBeast(
            id=beast.id,
            name=beast.name,
            realm=beast.realm,
            level=beast.level,
            hp=int(beast.hp * (1 + buff_config.get("hp_bonus", 0))),
            attack=int(beast.attack * bonus),
            defense=int(beast.defense * def_bonus),
            speed=int(beast.speed * (1 + buff_config.get("speed_bonus", 0))),
            nature=beast.nature,
            physical_attack=int(beast.physical_attack * bonus),
            magic_attack=int(beast.magic_attack * bonus),
            physical_defense=int(beast.physical_defense * def_bonus),
            magic_defense=int(beast.magic_defense * def_bonus),
            # 关键：继承原幻兽的技能列表
            skills=beast.skills,
        )
    
    def calc_damage(self, attacker_attack: int, defender_defense: int) -> int:
        """计算伤害（已废弃，闯塔现使用统一 PVP 引擎）
        
        新规则（2026年1月修订）：
        - 攻击 - 防御 >= 0：伤害 = (攻击 - 防御) × 0.069，四舍五入
        - 攻击 - 防御 < 0：固定扣血 5 点
        """
        diff = attacker_attack - defender_defense
        if diff >= 0:
            damage = round(diff * 0.069)
        else:
            damage = 5
        return max(1, damage)
    
    def calc_damage_with_type(
        self,
        attacker,  # PlayerBeast 或 TowerGuardian
        defender,  # PlayerBeast 或 TowerGuardian
    ) -> int:
        """根据特性计算伤害（已废弃，闯塔现使用统一 PVP 引擎）
        
        新规则（2026年1月修订）：
        - 攻击 - 防御 >= 0：伤害 = (攻击 - 防御) × 0.069，四舍五入
        - 攻击 - 防御 < 0：固定扣血 5 点
        """
        # 判断攻击方是法系还是物系
        if attacker.is_magic_type():
            diff = attacker.magic_attack - defender.magic_defense
        else:
            diff = attacker.physical_attack - defender.physical_defense
        
        if diff >= 0:
            damage = round(diff * 0.069)
        else:
            damage = 5
        
        return max(1, damage)
    
    def _to_pvp_beasts_from_players(self, player_beasts: List[PlayerBeast]) -> List[PvpBeast]:
        """将玩家幻兽转换为 PvpBeast，并应用技能系统的增益/负面效果。"""
        pvp_beasts: List[PvpBeast] = []
        for b in player_beasts:
            attack_type = "magic" if b.is_magic_type() else "physical"
            skills = b.skills or []

            (
                final_hp,
                final_physical_attack,
                final_magic_attack,
                final_physical_defense,
                final_magic_defense,
                final_speed,
                special_effects,
            ) = apply_buff_debuff_skills(
                skills=skills,
                attack_type=attack_type,
                raw_hp=b.hp,
                raw_physical_attack=b.physical_attack,
                raw_magic_attack=b.magic_attack,
                raw_physical_defense=b.physical_defense,
                raw_magic_defense=b.magic_defense,
                raw_speed=b.speed,
            )

            pvp_beasts.append(
                PvpBeast(
                    id=b.id,
                    name=b.full_name,
                    hp_max=final_hp,
                    hp_current=final_hp,
                    physical_attack=final_physical_attack,
                    magic_attack=final_magic_attack,
                    physical_defense=final_physical_defense,
                    magic_defense=final_magic_defense,
                    speed=final_speed,
                    grade=0,
                    hp_star=0,
                    attack_star=0,
                    physical_defense_star=0,
                    magic_defense_star=0,
                    speed_star=0,
                    hp_aptitude=0,
                    attack_aptitude=0,
                    physical_defense_aptitude=0,
                    magic_defense_aptitude=0,
                    speed_aptitude=0,
                    attack_type=attack_type,
                    skills=skills,
                    poison_enhance=special_effects.get("poison_enhance", 0.0) or 0.0,
                    critical_resist=special_effects.get("critical_resist", 0.0) or 0.0,
                    immune_counter=bool(special_effects.get("immune_counter", False)),
                    poison_resist=special_effects.get("poison_resist", 0.0) or 0.0,
                )
            )
        return pvp_beasts

    def _to_pvp_beasts_from_guardians(self, guardians: List[TowerGuardian]) -> List[PvpBeast]:
        """将守塔幻兽转换为 PvpBeast。当前暂不配置技能。"""
        pvp_beasts: List[PvpBeast] = []
        for g in guardians:
            attack_type = "magic" if g.is_magic_type() else "physical"
            # 守塔幻兽暂不使用技能，后续可在配置中增加 skills 字段再接入。
            skills: List[str] = []

            # 这里也走一遍 apply_buff_debuff_skills，便于未来给守塔幻兽加被动技能。
            (
                final_hp,
                final_physical_attack,
                final_magic_attack,
                final_physical_defense,
                final_magic_defense,
                final_speed,
                _special_effects,
            ) = apply_buff_debuff_skills(
                skills=skills,
                attack_type=attack_type,
                raw_hp=g.hp,
                raw_physical_attack=g.physical_attack,
                raw_magic_attack=g.magic_attack,
                raw_physical_defense=g.physical_defense,
                raw_magic_defense=g.magic_defense,
                raw_speed=g.speed,
            )

            pvp_beasts.append(
                PvpBeast(
                    id=id(g),  # 守塔幻兽没有全局ID，用内存id占位即可
                    name=g.name,
                    hp_max=final_hp,
                    hp_current=final_hp,
                    physical_attack=final_physical_attack,
                    magic_attack=final_magic_attack,
                    physical_defense=final_physical_defense,
                    magic_defense=final_magic_defense,
                    speed=final_speed,
                    grade=0,
                    hp_star=0,
                    attack_star=0,
                    physical_defense_star=0,
                    magic_defense_star=0,
                    speed_star=0,
                    hp_aptitude=0,
                    attack_aptitude=0,
                    physical_defense_aptitude=0,
                    magic_defense_aptitude=0,
                    speed_aptitude=0,
                    attack_type=attack_type,
                    skills=skills,
                )
            )
        return pvp_beasts

    def battle_one_floor(
        self,
        user_id: int,
        tower_type: str,
        player_beasts: List[PlayerBeast],
        guardians: List[TowerGuardian],
        floor: int,
    ) -> FloorBattle:
        """使用统一 PVP 战斗引擎挑战一层。

        - 每层内玩家与守塔幻兽按 PVP 规则对战（速度/品质/属性先手 + 统一伤害公式 + 技能系统）。
        - 每层战斗日志只保留前 50 回合，供前端展示详细战报。
        """
        rounds: List[BattleRound] = []

        # 记录参战幻兽（用于前端展示）
        beasts_used: List[str] = [b.full_name for b in player_beasts]

        # 获取玩家信息（用于日志中的玩家名称和等级）
        player_level = player_beasts[0].level if player_beasts else 1
        player_name = f"玩家{user_id}"
        if self.player_repo is not None:
            player = self.player_repo.get_by_id(user_id)
            if player is not None:
                player_level = player.level or player_level
                if player.nickname:
                    player_name = player.nickname

        # 塔名称用于作为“防守方玩家”的名字，便于日志展示：『通天塔第10层』
        tower_config = self.config_repo.get_tower_config(tower_type)
        tower_base_name = tower_config.get("name", tower_type)
        tower_player_name = f"{tower_base_name}{floor}层"

        # 转换为 PVP 引擎使用的实体
        attacker_beasts = self._to_pvp_beasts_from_players(player_beasts)
        defender_beasts = self._to_pvp_beasts_from_guardians(guardians)

        attacker_player = PvpPlayer(
            player_id=user_id,
            level=player_level,
            beasts=attacker_beasts,
            name=player_name,
        )
        defender_player = PvpPlayer(
            player_id=-1,
            level=guardians[0].level if guardians else player_level,
            beasts=defender_beasts,
            name=tower_player_name,
        )

        pvp_result = run_pvp_battle(attacker_player, defender_player, max_log_turns=50)

        # 将 AttackLog 转换为塔战斗用的 BattleRound
        for log in pvp_result.logs:
            attacker_side = "player" if log.attacker_player_id == attacker_player.player_id else "guardian"
            rounds.append(
                BattleRound(
                    round_num=log.turn,
                    attacker_side=attacker_side,
                    attacker_name=log.attacker_name,
                    defender_name=log.defender_name,
                    damage=log.damage,
                    attacker_hp_after=log.attacker_hp_after,
                    defender_hp_after=log.defender_hp_after,
                    skill_name=getattr(log, "skill_name", ""),
                    description=log.description,
                )
            )

        is_victory = pvp_result.winner_player_id == attacker_player.player_id

        # 奖励仍由上层 challenge_floor / auto_challenge 负责填充，这里先给空
        rewards: Dict = {}

        return FloorBattle(
            floor=floor,
            guardians=[
                {
                    "name": g.name,
                    "level": g.level,
                    "nature": g.nature,
                    "hp": g.hp,
                    "physical_attack": g.physical_attack,
                    "magic_attack": g.magic_attack,
                    "physical_defense": g.physical_defense,
                    "magic_defense": g.magic_defense,
                }
                for g in guardians
            ],
            beasts_used=beasts_used,
            rounds=rounds,
            is_victory=is_victory,
            rewards=rewards,
        )
    
    def challenge_floor(
        self,
        user_id: int,
        tower_type: str,
        player_beasts: List[PlayerBeast],
        use_buff: bool = True,
    ) -> FloorBattle:
        """
        手动挑战一层
        """
        state = self.state_repo.get_by_user_id(user_id, tower_type)
        state.reset_daily_if_needed()

        # 今日次数限制（第2-4次会自动扣元宝重置）
        self._ensure_can_challenge_today(user_id=user_id, state=state, is_continue=False)

        config = self.config_repo.get_tower_config(tower_type)

        # 应用buff
        if use_buff:
            buff_config = config.get("buff", {})
            player_beasts = [self.apply_buff(b, buff_config) for b in player_beasts]
        
        # 获取守塔幻兽
        guardians = self.config_repo.get_guardians_for_floor(tower_type, state.current_floor)
        
        # 战斗
        battle = self.battle_one_floor(
            user_id=user_id,
            tower_type=tower_type,
            player_beasts=player_beasts,
            guardians=guardians,
            floor=state.current_floor,
        )
        
        # 获取奖励
        if battle.is_victory:
            battle.rewards = self.config_repo.get_floor_rewards(tower_type, state.current_floor)
            # 检查里程碑奖励
            milestone = self.config_repo.get_milestone_reward(tower_type, state.current_floor)
            if milestone:
                battle.rewards["milestone"] = milestone

            if self.config_repo.should_give_special_reward(tower_type, state.current_floor):
                special_item = self.roll_special_reward(tower_type, state.current_floor)
                if special_item:
                    battle.rewards["special_item"] = special_item

            spirit_item = self.roll_spirit_drop(tower_type, state.current_floor)
            if spirit_item:
                battle.rewards["spirit_item"] = spirit_item
        
        # 更新状态
        state.today_count += 1
        if battle.is_victory:
            cleared_floor = state.current_floor
            state.current_floor += 1
            if cleared_floor > state.max_floor_record:
                state.max_floor_record = cleared_floor
        
        self.state_repo.save(state)
        
        return battle
    
    def auto_challenge(
        self,
        user_id: int,
        tower_type: str,
        player_beasts: List[PlayerBeast],
        use_buff: bool = True,
        is_continue: bool = False,
    ) -> AutoChallengeResult:
        """
        自动闯塔 - 一次性计算所有层
        
        Args:
            is_continue: 是否是继续挑战（不增加今日次数）
        """
        state = self.state_repo.get_by_user_id(user_id, tower_type)
        state.reset_daily_if_needed()

        # 今日次数限制（第2-4次会自动扣元宝重置）
        self._ensure_can_challenge_today(user_id=user_id, state=state, is_continue=is_continue)

        config = self.config_repo.get_tower_config(tower_type)
        max_floor = config.get("max_floor", 120)

        # 只有首次自动闯塔时才增加今日次数，继续挑战不增加
        if not is_continue:
            state.today_count += 1
        
        # 应用buff
        if use_buff:
            buff_config = config.get("buff", {})
            player_beasts = [self.apply_buff(b, buff_config) for b in player_beasts]
        
        start_floor = state.current_floor
        battles: List[FloorBattle] = []
        total_rewards = {"gold": 0, "exp": 0, "items": []}
        stopped_reason = ""
        
        while True:
            if state.current_floor > max_floor:
                stopped_reason = "max_floor"
                break
            
            # 每层幻兽HP恢复满
            for beast in player_beasts:
                beast.current_hp = beast.hp
            
            # 获取守塔幻兽
            guardians = self.config_repo.get_guardians_for_floor(tower_type, state.current_floor)

            # 战斗
            battle = self.battle_one_floor(
                user_id=user_id,
                tower_type=tower_type,
                player_beasts=player_beasts,
                guardians=guardians,
                floor=state.current_floor,
            )
            
            # 获取奖励
            if battle.is_victory:
                floor_rewards = self.config_repo.get_floor_rewards(tower_type, state.current_floor)
                battle.rewards = dict(floor_rewards)
                
                # 累加奖励
                total_rewards["gold"] += floor_rewards.get("gold", 0)
                total_rewards["exp"] += floor_rewards.get("exp", 0)
                
                # 检查里程碑奖励
                milestone = self.config_repo.get_milestone_reward(tower_type, state.current_floor)
                if milestone:
                    battle.rewards["milestone"] = milestone
                    total_rewards["gold"] += milestone.get("gold", 0)
                
                # 检查特殊奖励（每5层）
                if self.config_repo.should_give_special_reward(tower_type, state.current_floor):
                    special_item = self.roll_special_reward(tower_type, state.current_floor)
                    if special_item:
                        battle.rewards["special_item"] = special_item
                        total_rewards["items"].append(special_item)
                
                # 检查战灵掉落（特定层数20%概率）
                spirit_item = self.roll_spirit_drop(tower_type, state.current_floor)
                if spirit_item:
                    battle.rewards["spirit_item"] = spirit_item
                    total_rewards["items"].append(spirit_item)
            
            battles.append(battle)
            
            if battle.is_victory:
                cleared_floor = state.current_floor
                state.current_floor += 1
                if cleared_floor > state.max_floor_record:
                    state.max_floor_record = cleared_floor
            else:
                stopped_reason = "all_dead"
                break
        
        # daily_limit不再作为停止原因，因为次数只在开始时计算一次
        
        self.state_repo.save(state)
        
        return AutoChallengeResult(
            user_id=user_id,
            tower_type=tower_type,
            start_floor=start_floor,
            end_floor=state.current_floor - 1 if battles and battles[-1].is_victory else state.current_floor,
            battles=battles,
            total_rewards=total_rewards,
            stopped_reason=stopped_reason,
        )
