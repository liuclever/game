"""
玩家实体
"""
from dataclasses import dataclass
from datetime import datetime, date, timedelta
import json
from pathlib import Path
from typing import Dict, Optional, Tuple


# ===================== 玩家升级经验配置加载 =====================
_player_level_exp_cache: Dict[int, int] = {}
_player_max_level_config: Optional[int] = None


def _load_player_level_exp_config() -> Dict[int, int]:
    """从 configs/player_level_up_exp.json 加载每级升级所需经验。

    支持三种格式：
    1) 简单映射：{ "1": 89, "2": 131, ... }
    2) 列表形式：[{'level': 1, 'exp': 89}, ...]
    3) 当前推荐格式：
       {
         "max_level": 100,
         "exp_to_next_level": { "1": 89, "2": 131, ... },
         "description": "..."
       }

    若文件不存在或解析失败，将返回空字典，后续调用会使用默认公式 level * 100。
    """
    global _player_level_exp_cache, _player_max_level_config
    if _player_level_exp_cache:
        return _player_level_exp_cache

    base_dir = Path(__file__).resolve().parents[2]
    path = base_dir / "configs" / "player_level_up_exp.json"
    if not path.exists():
        _player_level_exp_cache = {}
        _player_max_level_config = None
        return _player_level_exp_cache

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        _player_level_exp_cache = {}
        _player_max_level_config = None
        return _player_level_exp_cache

    mapping: Dict[int, int] = {}
    if isinstance(data, dict):
        raw_mapping = None
        if isinstance(data.get("exp_to_next_level"), dict):
            raw_mapping = data["exp_to_next_level"]
        else:
            raw_mapping = data

        for k, v in raw_mapping.items():
            try:
                lvl = int(k)
                mapping[lvl] = int(v)
            except Exception:
                continue

        max_level_val = data.get("max_level")
        if isinstance(max_level_val, int):
            _player_max_level_config = max_level_val
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

    _player_level_exp_cache = mapping
    return _player_level_exp_cache


def _get_player_max_level_from_config() -> Optional[int]:
    """获取配置中的最大等级（若未配置则返回 None）。"""
    _load_player_level_exp_config()
    return _player_max_level_config


def _get_required_exp_for_player_level(level: int) -> int:
    """获取从当前等级升到下一等级所需经验。

    优先使用配置文件中的数值；若未配置，则退回到默认公式：level * 100。
    若 level 超出配置范围，则使用配置中的最大等级经验或默认公式。
    """
    config = _load_player_level_exp_config()
    if config:
        if level in config:
            return config[level]
        max_defined_level = max(config.keys())
        if level > max_defined_level:
            return config[max_defined_level]
    return level * 100


# 等级段配置：(最小等级, 最大等级, 阶位名称, 可镇妖层数范围)
RANK_CONFIG = [
    (1, 29, "黄阶", None),           # 不能镇妖
    (30, 39, "玄阶", (1, 20)),
    (40, 49, "地阶", (21, 40)),
    (50, 59, "天阶", (41, 60)),
    (60, 69, "飞马", (61, 80)),
    (70, 79, "玄武", (81, 100)),
    (80, 100, "战神", (101, 120)),
]


@dataclass
class Player:
    """游戏中的玩家对象（纯领域模型，不依赖任何框架）"""

    # 统一主键命名：业务侧全部使用 user_id。
    # 为了兼容旧代码，下面提供了 id 属性（等同于 user_id）。
    user_id: Optional[int] = None          # 数据库主键

    # 登录信息（目前 MySQL 表里是明文 password；这里不强制约束）
    username: str = ""                     # 账号
    password: str = ""                     # 密码/密码哈希（由仓库层决定）

    nickname: str = ""                     # 昵称

    level: int = 1                         # 等级
    exp: int = 0                           # 当前等级内的经验
    gold: int = 0                          # 铜钱（旧字段）
    copper: int = 0                        # 铜钱（新字段）
    silver_diamond: int = 0                # 宝石（钻石）
    yuanbao: int = 0                       # 元宝
    dice: int = 0                          # 骰子数量
    enhancement_stone: int = 0             # 强化石

    energy: int = 100                      # 体力 / 活力
    last_energy_recovery_time: Optional[datetime] = None # 上次活力恢复时间
    prestige: int = 0                      # 声望
    spirit_stone: int = 0                  # 灵石（旧字段，暂保留）
    crystal_tower: int = 0                 # 水晶塔活力值
    charm: int = 0                         # 魅力值

    vip_level: int = 0                     # VIP 等级
    vip_exp: int = 0                       # VIP 经验

    # —— 修行相关字段 —— #
    cultivation_start_time: Optional[datetime] = None # 修行开始时间
    cultivation_duration: Optional[int] = None        # 修行目标时长(秒)
    cultivation_area: Optional[str] = None           # 修行区域（如：定老城）
    cultivation_dungeon: Optional[str] = None        # 修行副本（如：幻灵湖畔）

    @property
    def max_energy(self) -> int:
        """获取活力上限（基于 VIP 等级）"""
        # 从配置文件读取
        import json
        from pathlib import Path
        try:
            config_path = Path(__file__).resolve().parents[2] / "configs" / "vip_privileges.json"
            with config_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            for lv_data in data.get("vip_levels", []):
                if lv_data.get("level") == self.vip_level:
                    return lv_data.get("privileges", {}).get("vitality_max", 100)
        except Exception:
            pass
        return 100

    location: str = "林中空地"                # 当前所在地点
    last_signin_date: Optional[date] = None  # 上次签到日期
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def id(self) -> Optional[int]:
        """兼容旧代码：player.id 等同于 player.user_id。"""
        return self.user_id

    @id.setter
    def id(self, value: Optional[int]) -> None:
        self.user_id = value

    @property
    def password_hash(self) -> str:
        """兼容旧字段名：password_hash 视为 password。"""
        return self.password

    @password_hash.setter
    def password_hash(self, value: str) -> None:
        self.password = value

    # —— 经验 & 升级逻辑 —— #
    def exp_to_next_level(self) -> int:
        """当前等级升到下一级需要的经验（从配置中读取）。"""
        return _get_required_exp_for_player_level(self.level)

    def add_exp(self, amount: int) -> None:
        """增加经验并自动处理升级（支持溢出经验与连升多级）。"""
        if amount <= 0:
            return

        max_level = _get_player_max_level_from_config()
        # 已达最大等级：不再增加经验/升级（避免 exp 无限膨胀）
        if max_level is not None and self.level >= max_level:
            return

        self.exp += amount
        # 循环处理可能的多级升级与溢出经验
        while True:
            required = self.exp_to_next_level()
            # 防止配置异常导致死循环
            if required <= 0:
                break
            if self.exp < required:
                break

            self.exp -= required
            self.level += 1

            # 达到最大等级：将当前等级经验清零（按“满级不积累经验”处理）
            if max_level is not None and self.level >= max_level:
                self.exp = 0
                break

    def get_summoner_star_and_pin(self) -> Tuple[int, int]:
        """将等级转换为 (星数, 品数)。

        规则：
        - x星对应 10*x 级
        - x品对应 x 级（个位数）

        例如：
        - 9级 => 0星9品
        - 48级 => 4星8品
        """
        lv = int(self.level or 0)
        if lv < 0:
            lv = 0
        return lv // 10, lv % 10

    def get_summoner_title(self) -> str:
        """召唤师等级称号：x星x品召唤师。"""
        star, pin = self.get_summoner_star_and_pin()
        return f"{star}星{pin}品召唤师"

    def get_rank_name(self) -> str:
        """根据等级获取阶位名称"""
        for min_lv, max_lv, rank_name, _ in RANK_CONFIG:
            if min_lv <= self.level <= max_lv:
                return rank_name
        return "战神"
    
    def get_zhenyao_range(self) -> Optional[Tuple[int, int]]:
        """
        获取可镇妖的层数范围
        返回 (起始层, 结束层) 或 None（不能镇妖）
        """
        for min_lv, max_lv, _, floor_range in RANK_CONFIG:
            if min_lv <= self.level <= max_lv:
                return floor_range
        return (101, 120)  # 默认战神
    
    def can_zhenyao(self) -> bool:
        """是否可以进行镇妖"""
        return self.level >= 30
    
    def get_trial_and_hell_floors(self, tower_max_floor: int) -> Tuple[list, list]:
        """
        根据通天塔最高层计算试炼层和炼狱层
        
        Args:
            tower_max_floor: 通天塔已过的最高层
            
        Returns:
            (试炼层列表, 炼狱层列表)
        """
        floor_range = self.get_zhenyao_range()
        if not floor_range:
            return [], []
        
        start_floor, end_floor = floor_range
        mid_floor = start_floor + 9  # 前10层是试炼层
        
        # 实际可用层数（受通天塔进度限制）
        actual_end = min(end_floor, tower_max_floor)
        
        if actual_end < start_floor:
            return [], []
        
        # 试炼层：start_floor 到 min(mid_floor, actual_end)
        trial_end = min(mid_floor, actual_end)
        trial_floors = list(range(start_floor, trial_end + 1))
        
        # 炼狱层：mid_floor+1 到 actual_end
        hell_floors = []
        if actual_end > mid_floor:
            hell_floors = list(range(mid_floor + 1, actual_end + 1))
        
        return trial_floors, hell_floors

    def recover_energy(self, current_time: Optional[datetime] = None) -> bool:
        """
        每10分钟恢复1点活力，直到达到上限。
        返回是否发生了变化（恢复或强制修正上限）。
        """
        if current_time is None:
            current_time = datetime.now()
            
        modified = False
        
        # 规则 1: 强制修正当前活力不可以超过上限
        if self.energy > self.max_energy:
            self.energy = self.max_energy
            modified = True
            
        if self.last_energy_recovery_time is None:
            self.last_energy_recovery_time = current_time
            return modified
            
        # 规则 2: 每10分钟恢复1点活力
        # 如果已经达到上限，则只更新时间，不增加活力
        if self.energy >= self.max_energy:
            # 如果当前时间比上次记录时间晚，则更新时间戳，保留不满10分钟的部分（或直接对齐）
            # 这里的逻辑是：一旦能量满了，我们就让时间戳跟着走，或者停在满的那一刻
            # 推荐做法：停在满的那一刻或者平移，这样一旦消耗了，可以立刻开始计时
            diff = current_time - self.last_energy_recovery_time
            if diff.total_seconds() >= 600:
                self.last_energy_recovery_time = current_time
                modified = True
            return modified

        diff = current_time - self.last_energy_recovery_time
        minutes = int(diff.total_seconds() / 60)
        recovery_points = minutes // 10
        
        if recovery_points > 0:
            new_energy = self.energy + recovery_points
            self.energy = min(new_energy, self.max_energy)
            # 更新恢复时间，保留不足10分钟的余数
            self.last_energy_recovery_time = self.last_energy_recovery_time + timedelta(minutes=recovery_points * 10)
            modified = True
            
        return modified


@dataclass
class ZhenyaoFloor:
    """镇妖层信息"""
    id: Optional[int] = None
    floor: int = 0
    occupant_id: Optional[int] = None
    occupant_name: str = ""
    occupy_time: Optional[datetime] = None
    expire_time: Optional[datetime] = None
    rewarded: bool = False
    
    def is_occupied(self) -> bool:
        """是否被占领"""
        if not self.occupant_id:
            return False
        # 检查是否过期
        if self.expire_time and datetime.now() > self.expire_time:
            return False
        return True
    
    def get_remaining_seconds(self) -> int:
        """获取剩余秒数"""
        if not self.expire_time:
            return 0
        remaining = (self.expire_time - datetime.now()).total_seconds()
        return max(0, int(remaining))
