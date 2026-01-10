from dataclasses import dataclass, field
from typing import Optional, List, Dict
from pathlib import Path
import json


# ===================== 幻兽升级经验配置加载 =====================
_level_exp_cache: Dict[int, int] = {}
_max_level_config: Optional[int] = None


def _load_level_exp_config() -> Dict[int, int]:
    """从 configs/beast_level_up_exp.json 加载每级升级所需经验。

    支持三种格式：
    1) 简单映射：{ "1": 50, "2": 100, ... }
    2) 列表形式：[{"level": 1, "exp": 50}, ...]
    3) 当前使用的格式：
       {
         "max_level": 100,
         "exp_to_next_level": { "1": 4, "2": 10, ... },
         "description": "..."
       }

    若文件不存在或解析失败，将返回空字典，后续调用会使用默认公式 level * 50。
    """
    global _level_exp_cache, _max_level_config
    if _level_exp_cache:
        return _level_exp_cache

    base_dir = Path(__file__).resolve().parents[2]
    path = base_dir / "configs" / "beast_level_up_exp.json"
    if not path.exists():
        _level_exp_cache = {}
        _max_level_config = None
        return _level_exp_cache

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        _level_exp_cache = {}
        _max_level_config = None
        return _level_exp_cache

    mapping: Dict[int, int] = {}
    if isinstance(data, dict):
        # 3) 带 max_level / exp_to_next_level 的结构
        raw_mapping = None
        if isinstance(data.get("exp_to_next_level"), dict):
            raw_mapping = data["exp_to_next_level"]
        else:
            # 1) 简单映射：直接用顶层键值
            raw_mapping = data

        for k, v in raw_mapping.items():
            try:
                lvl = int(k)
                mapping[lvl] = int(v)
            except Exception:
                continue

        # 记录 max_level（若提供）
        max_level_val = data.get("max_level")
        if isinstance(max_level_val, int):
            _max_level_config = max_level_val
    elif isinstance(data, list):
        for item in data:
            if not isinstance(item, dict):
                continue
            lvl = item.get("level")
            exp = item.get("exp")
            if lvl is None or exp is None:
                continue
            try:
                mapping[int(lvl)] = int(exp)
            except Exception:
                continue

    _level_exp_cache = mapping
    return _level_exp_cache


def _get_max_level_from_config() -> Optional[int]:
    """获取配置中的最大等级（若未配置则返回 None）。"""
    _load_level_exp_config()
    return _max_level_config


def _get_required_exp_for_level(level: int) -> int:
    """获取从当前等级升到下一等级所需经验。

    优先使用配置文件中的数值；若未配置，则退回到默认公式：level * 50。
    若 level 超出配置范围，则使用配置中的最大等级经验或默认公式。
    """
    config = _load_level_exp_config()
    if config:
        if level in config:
            return config[level]
        # 若未找到精确等级，使用配置中的最大等级经验
        max_defined_level = max(config.keys())
        if level > max_defined_level:
            return config[max_defined_level]
    # 默认公式（兼容旧逻辑）
    return level * 50


@dataclass
class BeastTemplate:
    """幻兽模板（从 configs/beast_templates.json 加载）"""

    # 基本信息
    id: int
    name: str = ""
    description: str = ""

    # 实例专属特性
    personality: str = ""         # 物系善攻  法系善攻之类的特性 会在模板直接获得

    # 世界观 / 图鉴标签
    race: str = ""       # 本体种族，如：兽族 / 龙族
    realm: str = ""      # 境界，如：人界 / 地界 / 天界 / 神界
    trait: str = ""      # 特性，如：物系高速 / 法系爆发
    rarity: str = ""     # 稀有度：普通 / 稀有 / 史诗 / 传说
    habitat: str = ""    # 属地：森林秘境 / 火山遗迹 等
    
    realms: Dict[str, Dict] = field(default_factory=dict)  # 各境界配置

    # 攻击类型：物攻 或 法攻（physical / magic）
    attack_type: str = "physical"

    # 基础属性 + 成长（保持不变，兼容现有公式）
    base_hp: int = 100             # 模板基础气血（1级起始）
    base_attack: int = 10          # 模板基础攻击（物/法由 attack_type 决定）
    base_defense: int = 10         # 模板基础防御
    base_speed: int = 10           # 模板基础速度

    growth_hp: int = 10            # 每升1级增加的气血
    growth_attack: int = 2         # 每升1级增加的攻击
    growth_defense: int = 1        # 每升1级增加的防御
    growth_speed: int = 1          # 每升1级增加的速度

    # 成长评分 & 各项资质上限
    growth_score: int = 0                # 成长率总评分，例如 840（★★★★★）

    hp_aptitude_max: int = 0             # 气血资质上限
    speed_aptitude_max: int = 0          # 速度资质上限
    physical_atk_aptitude_max: int = 0   # 物攻资质上限
    magic_atk_aptitude_max: int = 0      # 法攻资质上限
    physical_def_aptitude_max: int = 0   # 物防资质上限
    magic_def_aptitude_max: int = 0      # 法防资质上限

    # 技能池（全技能ID列表）
    all_skill_ids: List[int] = field(default_factory=list)
    
    # 技能池（全技能名称列表）
    all_skill_names: List[str] = field(default_factory=list)


@dataclass
class Beast:
    """玩家拥有的幻兽实例"""

    # 基础标识
    id: Optional[int] = None      # 幻兽实例ID
    user_id: int = 0              # 所属玩家
    template_id: int = 0          # 幻兽模板ID（对应 BeastTemplate.id）

    # 基础养成信息
    nickname: str = ""            # 昵称（可自定义）
    level: int = 1                # 等级
    exp: int = 0                  # 当前经验
    is_main: bool = False         # 是否出战（出战中 / 未出战）

    # 实例性格（五种之一）：勇敢 / 精明 / 胆小 / 谨慎 / 傻瓜
    personality: str = ""

    # 实例攻击类型（可选）。为空字符串时，使用模板的 attack_type
    attack_type: str = ""

    # 实例境界（可选）。为空字符串时，使用模板的 realm
    realm: str = ""

    # 实际资质（区别于模板中的资质上限）
    hp_aptitude: int = 0              # 气血资质
    speed_aptitude: int = 0           # 速度资质
    physical_atk_aptitude: int = 0    # 物攻资质
    magic_atk_aptitude: int = 0       # 法攻资质
    physical_def_aptitude: int = 0    # 物防资质
    magic_def_aptitude: int = 0       # 法防资质

    growth_rate: int = 0              # 成长率修正（0 表示使用模板默认）

    # 当前携带技能（存技能ID或技能编码字符串）
    skills: List[str] = field(default_factory=list)

    def exp_to_next_level(self) -> int:
        """从当前等级升到下一等级所需经验（从配置中读取）。"""
        return _get_required_exp_for_level(self.level)

    def add_exp(self, amount: int) -> bool:
        """增加经验，返回本次是否至少升级 1 次。

        新规则（支持溢出经验与连升多级）：
        - 经验先加入当前 exp；
        - 若当前 exp >= 升级所需经验，则：
            * 升级（level +1）；
            * 消耗掉本级所需经验，其余经验作为下一级的当前 exp；
            * 若新等级的 exp 依然 >= 对应的升级所需经验，则继续自动升级；
        - 一直循环，直到经验不足以再升 1 级，或达到最大等级。

        例如：
        - 1→2 需要 4 点经验，2→3 需要 10 点：
          * 从 1 级 0exp 一次性获得 5 点经验 -> 变为 2 级，exp=1；
          * 从 1 级 0exp 一次性获得 15 点经验 -> 变为 3 级，exp=1。
        """
        if amount <= 0:
            return False

        max_level = _get_max_level_from_config()
        leveled_up = False

        # 循环处理可能的多级升级与溢出经验
        while amount > 0:
            # 已达或超过最大等级时，不再获得经验/升级
            if max_level is not None and self.level >= max_level:
                break

            required = self.exp_to_next_level()
            # 当前等级距离升级还差多少经验
            need = max(required - self.exp, 0)

            # 如果这次获得的经验不够升一级，就直接加在当前 exp 上结束
            if amount < need or need == 0 and required <= 0:
                self.exp += amount
                amount = 0
                break

            # 这次至少可以升 1 级：先补足当前等级所需经验
            amount -= need
            self.exp += need  # 这时 self.exp 应该正好等于 required

            # 升级
            self.level += 1
            leveled_up = True

            # 消耗完本级经验后，当前等级从 0 开始累积剩余经验
            self.exp = 0

            # 再进入下一轮循环，看剩余 amount 是否还能再升一级

        return leveled_up

    def calc_hp(self, template: BeastTemplate) -> int:
        """计算当前HP"""
        return template.base_hp + template.growth_hp * (self.level - 1)

    def calc_attack(self, template: BeastTemplate) -> int:
        """计算当前攻击力"""
        return template.base_attack + template.growth_attack * (self.level - 1)

    def calc_defense(self, template: BeastTemplate) -> int:
        """计算当前防御力"""
        return template.base_defense + template.growth_defense * (self.level - 1)

    def calc_speed(self, template: BeastTemplate) -> int:
        """计算当前速度"""
        return template.base_speed + template.growth_speed * (self.level - 1)
