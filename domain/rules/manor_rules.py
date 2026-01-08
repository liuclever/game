from typing import Dict, List, Tuple, Optional

# --- 扩建规则配置 ---
# 普通土地索引 0-9 对应 1-10 块地
# 要求格式: {land_index: (required_level, required_manuals)}
LAND_EXPANSION_CONFIG: Dict[int, Tuple[int, int]] = {
    0: (10, 1),
    1: (20, 2),
    2: (30, 3),
    3: (40, 4),
    4: (50, 5),
    5: (60, 6),
    6: (70, 7),
    7: (80, 8),
    8: (90, 9),
    9: (100, 10),
}

# 特殊土地配置
# 要求格式: {land_index: (required_vip_level, required_manuals, name)}
SPECIAL_LAND_CONFIG: Dict[int, Tuple[int, int, str]] = {
    10: (4, 2, "黄土地"),
    11: (6, 3, "银土地"),
    12: (8, 4, "金土地"),
}

# 土地收益加成配置
# {land_index: bonus_multiplier} 例如 1.05 表示 5% 加成
LAND_BONUS_CONFIG: Dict[int, float] = {
    10: 1.05,  # 黄土地 5% 加成
    11: 1.10,  # 银土地 10% 加成
    12: 1.20,  # 金土地 20% 加成
}

# --- 摇钱树配置 ---
# 种类对应费用 (元宝)
TREE_COST_CONFIG: Dict[int, int] = {
    1: 10,
    2: 60,
    4: 80,
    6: 100,
    8: 120,
}

# --- 收益配置 ---
# 等级段对应 1 株树的基础收益 (铜钱)
EARNINGS_LEVEL_SEGMENTS: List[Tuple[int, int, int]] = [
    (1, 29, 18850),
    (30, 39, 25350),
    (40, 49, 31850),
    (50, 59, 38350),
    (60, 69, 44850),
    (70, 79, 51350),
    (80, 89, 57850),
    (90, 100, 64350),
]

GROWTH_HOURS = 6

class ManorRules:
    @staticmethod
    def get_expansion_requirement(land_index: int) -> Optional[Tuple[int, int]]:
        """获取扩建土地的要求 (等级/VIP等级, 手册数量)"""
        if land_index in LAND_EXPANSION_CONFIG:
            return LAND_EXPANSION_CONFIG[land_index]
        return None

    @staticmethod
    def get_special_land_requirement(land_index: int) -> Optional[Tuple[int, int, str]]:
        """获取特殊土地的要求 (VIP等级, 手册数量, 名称)"""
        if land_index in SPECIAL_LAND_CONFIG:
            return SPECIAL_LAND_CONFIG[land_index]
        return None

    @staticmethod
    def can_expand(land_index: int, player_level: int, player_vip_level: int, item_count: int) -> Tuple[bool, str]:
        """校验是否满足扩建条件"""
        # 普通土地
        if land_index in LAND_EXPANSION_CONFIG:
            req_lv, req_manuals = LAND_EXPANSION_CONFIG[land_index]
            if player_level < req_lv:
                star = req_lv // 10
                return False, f"等级不足，开启第{land_index + 1}块普通土地需要{star}星0品召唤师（{req_lv}级）"
            if item_count < req_manuals:
                return False, f"道具不足，开启第{land_index + 1}块普通土地需要庄园建造手册×{req_manuals}"
            return True, ""
        
        # 特殊土地
        if land_index in SPECIAL_LAND_CONFIG:
            req_vip, req_manuals, name = SPECIAL_LAND_CONFIG[land_index]
            if player_vip_level < req_vip:
                return False, f"VIP等级不足，开启{name}需要VIP {req_vip}"
            if item_count < req_manuals:
                return False, f"道具不足，开启{name}需要庄园建造手册×{req_manuals}"
            return True, ""
            
        return False, "非法的土地索引"

    @staticmethod
    def calculate_earnings(player_level: int, tree_type: int, land_index: int = 0) -> int:
        """计算收获铜钱收益
        
        Args:
            player_level: 玩家等级
            tree_type: 树种类型
            land_index: 土地索引，用于判断是否有加成（默认0为普通土地）
        
        Returns:
            最终收益（铜钱），已应用土地加成
        """
        base_earnings = 0
        for min_lv, max_lv, gold in EARNINGS_LEVEL_SEGMENTS:
            if min_lv <= player_level <= max_lv:
                base_earnings = gold
                break
        
        # 如果超过100级，按最高档算
        if player_level > 100:
            base_earnings = EARNINGS_LEVEL_SEGMENTS[-1][2]
        
        # 计算基础收益
        earnings = base_earnings * tree_type
        
        # 应用土地加成
        bonus_multiplier = LAND_BONUS_CONFIG.get(land_index, 1.0)
        final_earnings = int(earnings * bonus_multiplier)
        
        return final_earnings

    @staticmethod
    def get_tree_cost(tree_type: int) -> int:
        """获取种植费用 (元宝)"""
        return TREE_COST_CONFIG.get(tree_type, 0)
