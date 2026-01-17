from typing import Optional, List, Dict
from pathlib import Path
import json

from domain.entities.tower import TowerGuardian
from domain.repositories.tower_repo import ITowerConfigRepo
from domain.services.beast_stats import get_growth_multiplier


# 资质→属性系数（与 beast_stats.py 保持一致）
HP_COEFF = 0.102
ATK_COEFF = 0.051
ATK_COEFF_BONUS = 0.0765  # 善攻系
DEF_COEFF = 0.046
DEF_COEFF_LOW = 0.0391
LEVEL_BONUS = 50


class ConfigTowerRepo(ITowerConfigRepo):
    """从配置文件读取闯塔配置"""
    
    def __init__(self):
        self._tower_config: Dict = {}
        self._guardians_config: Dict = {}
        self._rewards_config: Dict = {}
        self._tongtian_beasts_config: Dict = {}  # 通天塔精确幻兽配置
        self._load()
    
    def _load(self):
        base_dir = Path(__file__).resolve().parents[2]
        
        # 加载塔配置
        config_path = base_dir / "configs" / "tower_config.json"
        with config_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            self._tower_config = data.get("towers", {})
        
        # 加载守塔幻兽配置
        guardians_path = base_dir / "configs" / "tower_guardians.json"
        with guardians_path.open("r", encoding="utf-8") as f:
            self._guardians_config = json.load(f)
        
        # 加载奖励配置
        rewards_path = base_dir / "configs" / "tower_rewards.json"
        with rewards_path.open("r", encoding="utf-8") as f:
            self._rewards_config = json.load(f)
        
        # 加载通天塔精确幻兽配置
        tongtian_beasts_path = base_dir / "configs" / "tower_tongtian_beasts.json"
        if tongtian_beasts_path.exists():
            with tongtian_beasts_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                # 将 floors 列表转换为 floor -> config 的字典便于快速查找
                self._tongtian_beasts_config = {
                    floor_data["floor"]: floor_data
                    for floor_data in data.get("floors", [])
                }
    
    def get_tower_config(self, tower_type: str) -> dict:
        return self._tower_config.get(tower_type, {})
    
    def get_guardian_count_for_floor(self, tower_type: str, floor: int) -> int:
        """获取某层需要的守塔幻兽数量"""
        config = self.get_tower_config(tower_type)
        for item in config.get("guardian_count_by_floor", []):
            floor_range = item["floor_range"]
            if floor_range[0] <= floor <= floor_range[1]:
                return item["count"]
        return 1
    
    def _create_guardian_from_beast_config(self, beast_config: dict, floor: int) -> TowerGuardian:
        """根据精确幻兽配置创建TowerGuardian
        
        使用与 beast_stats.py 相同的公式计算属性
        """
        level = beast_config.get("level", floor)
        characteristic = beast_config.get("characteristic", "物系")
        growth_rate = beast_config.get("growth_rate", 1540)
        aptitudes = beast_config.get("aptitudes", {})
        skills = beast_config.get("skills", [])
        
        # 获取成长率倍率
        growth_mult = get_growth_multiplier(growth_rate)
        # 守塔幻兽默认天界境界，倍率为1.0
        realm_mult = 1.0
        
        # 等级加成基数
        level_bonus_base = (level - 1) * LEVEL_BONUS * realm_mult * growth_mult
        
        # 获取各项资质值
        hp_apt = aptitudes.get("hp", {}).get("value", 1500)
        speed_apt = aptitudes.get("speed", {}).get("value", 1500)
        p_def_apt = aptitudes.get("p_defense", {}).get("value", 1500)
        m_def_apt = aptitudes.get("m_defense", {}).get("value", 1500)
        
        # 判断攻击类型（物系/法系）
        # 特性格式为 "法系XX" 或 "物系XX"，需要判断前缀
        is_magic = characteristic.startswith("法系")
        if is_magic:
            atk_apt = aptitudes.get("m_attack", {}).get("value", 1500)
        else:
            atk_apt = aptitudes.get("p_attack", {}).get("value", 1500)
        
        # 判断特性类型
        is_bonus_atk = "善攻" in characteristic
        is_high_speed = "高速" in characteristic
        
        # 计算气血
        # 气血初始值 = 0.102 * 资质 * 境界倍率（不乘成长倍率）
        # 气血最终值 = 初始值 + 等级加成
        hp_base = hp_apt * HP_COEFF * realm_mult
        hp = int(hp_base + level_bonus_base)
        
        # 计算攻击
        atk_coeff = ATK_COEFF_BONUS if is_bonus_atk else ATK_COEFF
        atk_base = atk_apt * atk_coeff * realm_mult * growth_mult
        attack = int(atk_base + level_bonus_base)
        
        if is_magic:
            physical_attack = 0
            magic_attack = attack
        else:
            physical_attack = attack
            magic_attack = 0
        
        # 计算防御
        if is_high_speed:
            # 高速系：两防均使用标准系数
            phys_def_coeff = DEF_COEFF
            magic_def_coeff = DEF_COEFF
        else:
            # 非高速系：资质较低的防御使用低系数
            if p_def_apt < m_def_apt:
                phys_def_coeff = DEF_COEFF_LOW
                magic_def_coeff = DEF_COEFF
            elif m_def_apt < p_def_apt:
                phys_def_coeff = DEF_COEFF
                magic_def_coeff = DEF_COEFF_LOW
            else:
                phys_def_coeff = DEF_COEFF
                magic_def_coeff = DEF_COEFF
        
        phys_def_base = p_def_apt * phys_def_coeff * realm_mult * growth_mult
        magic_def_base = m_def_apt * magic_def_coeff * realm_mult * growth_mult
        physical_defense = int(phys_def_base + level_bonus_base)
        magic_defense = int(magic_def_base + level_bonus_base)
        
        # 计算速度：资质 // 1100 + 1
        speed = max(1, speed_apt // 1100 + 1)
        
        # 用于兼容旧逻辑的attack和defense取主要值
        main_attack = magic_attack if is_magic else physical_attack
        main_defense = max(physical_defense, magic_defense)
        
        return TowerGuardian(
            name=f"通天塔{floor}层守护兽",
            level=level,
            hp=hp,
            attack=main_attack,
            defense=main_defense,
            speed=speed,
            nature=characteristic,
            description=f"特性: {characteristic}",
            physical_attack=physical_attack,
            magic_attack=magic_attack,
            physical_defense=physical_defense,
            magic_defense=magic_defense,
        )
    
    def get_guardians_for_floor(self, tower_type: str, floor: int) -> List[TowerGuardian]:
        """获取某层的守塔幻兽列表"""
        guardians = []
        
        # 优先使用通天塔精确配置
        if tower_type == "tongtian" and floor in self._tongtian_beasts_config:
            floor_config = self._tongtian_beasts_config[floor]
            beasts = floor_config.get("beasts", [])
            for beast_config in beasts:
                guardian = self._create_guardian_from_beast_config(beast_config, floor)
                guardians.append(guardian)
            return guardians
        
        # Fallback: 使用原有的模板+层级成长方式
        count = self.get_guardian_count_for_floor(tower_type, floor)
        
        tower_guardians = self._guardians_config.get(tower_type, [])
        
        # 找到对应层范围的配置
        guardian_templates = []
        for config in tower_guardians:
            floor_range = config["floor_range"]
            if floor_range[0] <= floor <= floor_range[1]:
                guardian_templates = config["guardians"]
                base_floor = floor_range[0]
                break
        
        if not guardian_templates:
            return guardians
        
        # 生成指定数量的守塔幻兽
        for i in range(count):
            template_index = i % len(guardian_templates)
            template = guardian_templates[template_index]
            
            floors_offset = floor - base_floor
            
            level = template["base_level"] + floors_offset * template["level_per_floor"]
            attack = template["base_attack"] + floors_offset * template["attack_per_floor"]
            defense = template["base_defense"] + floors_offset * template["defense_per_floor"]
            
            guardian = TowerGuardian(
                name=template["name"],
                level=level,
                hp=template["base_hp"] + floors_offset * template["hp_per_floor"],
                attack=attack,
                defense=defense,
                speed=template["base_speed"] + floors_offset * template["speed_per_floor"],
                nature=template.get("nature", "物系"),
                description=template.get("description", ""),
                # 物攻法攻物防法防按等级推算
                physical_attack=attack,
                magic_attack=int(attack * 0.9),
                physical_defense=defense,
                magic_defense=int(defense * 0.6),
            )
            guardians.append(guardian)
        
        return guardians
    
    def get_floor_rewards(self, tower_type: str, floor: int) -> dict:
        """获取某层的奖励"""
        tower_rewards = self._rewards_config.get(tower_type, {})
        floor_rewards = tower_rewards.get("floor_rewards", [])
        
        for config in floor_rewards:
            floor_range = config["floor_range"]
            if floor_range[0] <= floor <= floor_range[1]:
                return {
                    "gold": config.get("gold", 0),
                    "exp": config.get("exp", 0),
                    "items": config.get("items", []),
                }
        
        return {"gold": 0, "exp": 0, "items": []}
    
    def get_milestone_reward(self, tower_type: str, floor: int) -> Optional[dict]:
        """获取里程碑奖励（如果有）"""
        tower_rewards = self._rewards_config.get(tower_type, {})
        milestone_rewards = tower_rewards.get("milestone_rewards", [])
        
        for config in milestone_rewards:
            if config["floor"] == floor:
                return {
                    "gold": config.get("gold", 0),
                    "items": config.get("items", []),
                }
        
        return None
    
    def get_special_reward_config(self, tower_type: str, floor: int = 0) -> Optional[dict]:
        """获取特殊奖励配置（每N层奖励）"""
        tower_rewards = self._rewards_config.get(tower_type, {})
        
        # 先检查是否有按层范围的配置（如龙纹塔）
        floor_configs = tower_rewards.get("special_rewards_by_floor", [])
        for config in floor_configs:
            floor_range = config.get("floor_range", [0, 0])
            if floor_range[0] <= floor <= floor_range[1]:
                return config
        
        # 否则使用全局配置（如通天塔）
        return tower_rewards.get("special_reward", None)
    
    def should_give_special_reward(self, tower_type: str, floor: int) -> bool:
        """判断是否应该给予特殊奖励"""
        config = self.get_special_reward_config(tower_type, floor)
        if not config:
            return False
        every_n = config.get("every_n_floors", 5)
        return floor > 0 and floor % every_n == 0
    
    def get_spirit_drop_config(self, tower_type: str) -> Optional[dict]:
        """获取战灵掉落配置"""
        tower_rewards = self._rewards_config.get(tower_type, {})
        return tower_rewards.get("spirit_drop", None)
    
    def is_spirit_drop_floor(self, tower_type: str, floor: int) -> bool:
        """判断当前层是否可掉战灵"""
        config = self.get_spirit_drop_config(tower_type)
        if not config:
            return False
        floors = config.get("floors", [])
        return floor in floors
