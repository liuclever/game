from typing import Optional, Dict
from domain.entities.player import Player

class AllianceRules:
    CREATE_LEVEL_REQUIREMENT = 30
    LEAGUE_LEADER_TOKEN_ID = 11001
    TRAINING_DURATION_MINUTES = 120  # 默认2小时（兼容旧数据）
    TRAINING_DAILY_LIMIT = 1
    FIRE_ORE_CONTRIBUTION_COST = 5  # 领取火能原石需要消耗的贡献值
    FIRE_ORE_ITEM_ID = 1004  # 火能原石物品ID
    MIN_TRAINING_PARTICIPANTS = 2  # 开始修行所需的最少人数
    
    # 修行时长和活力消耗配置（小时 -> 活力）
    TRAINING_DURATION_OPTIONS = {
        2: {"hours": 2, "minutes": 120, "energy_cost": 16},
        4: {"hours": 4, "minutes": 240, "energy_cost": 32},
        8: {"hours": 8, "minutes": 480, "energy_cost": 40},
        12: {"hours": 12, "minutes": 720, "energy_cost": 50},
        24: {"hours": 24, "minutes": 1440, "energy_cost": 100},
    }
    
    @staticmethod
    def get_training_energy_cost(duration_hours: int) -> int:
        """根据修行时长（小时）获取活力消耗"""
        option = AllianceRules.TRAINING_DURATION_OPTIONS.get(duration_hours)
        if option:
            return option["energy_cost"]
        # 默认值：2小时消耗16活力
        return 16
    
    @staticmethod
    def get_training_duration_minutes(duration_hours: int) -> int:
        """根据修行时长（小时）获取分钟数"""
        option = AllianceRules.TRAINING_DURATION_OPTIONS.get(duration_hours)
        if option:
            return option["minutes"]
        # 默认值：2小时=120分钟
        return 120
    RENAME_MIN_LENGTH = 2
    RENAME_MAX_LENGTH = 13
    RENAME_COST_YUANBAO = 1000

    DONATION_RULES = {
        "gold_bag": {
            "item_id": 6005,
            "item_name": "金袋",
            "funds": 100,
            "prosperity": 100,
            "crystals": 0,
            "contribution": 10,
        },
        "fire_crystal": {
            "item_id": 1004,
            "item_name": "焚火晶",
            "funds": 0,
            "prosperity": 10,
            "crystals": 1,
            "contribution": 1,
        },
    }

    ROLE_MEMBER = 0
    ROLE_LEADER = 1
    ROLE_VICE_LEADER = 2
    ROLE_ELDER = 3

    ROLE_LABELS = {
        ROLE_LEADER: "盟主",
        ROLE_VICE_LEADER: "副盟主",
        ROLE_ELDER: "长老",
        ROLE_MEMBER: "盟众",
    }

    NOTICE_EDIT_ROLES = {ROLE_LEADER, ROLE_VICE_LEADER, ROLE_ELDER}

    ARMY_DRAGON = "dragon"
    ARMY_TIGER = "tiger"
    ARMY_LABELS = {
        ARMY_DRAGON: "飞龙军",
        ARMY_TIGER: "伏虎军",
    }

    TALENT_KEYS = ["atk", "int", "def", "resist", "spd", "hp"]
    TALENT_LABELS = {
        "atk": "高级攻击",
        "int": "高级智慧",
        "def": "高级防御",
        "resist": "高级魔抗",
        "spd": "高级速度",
        "hp": "高级生命",
    }
    TALENT_PERCENT_PER_LEVEL = 1
    TALENT_LEARN_CONTRIBUTION_PER_LEVEL = 10

    BUILDING_KEYS = ["council", "furnace", "talent", "beast", "warehouse"]
    BUILDING_LABELS = {
        "council": "议事厅",
        "furnace": "焚天炉",
        "talent": "天赋池",
        "beast": "幻兽室",
        "warehouse": "寄存仓库",
    }

    COUNCIL_UPGRADE_RULES = [
        {
            "level": 1,
            "next_level": 2,
            "requires": {"furnace": 1, "warehouse": 1, "beast": 1},
            "funds": 1000,
            "crystals": 3000,
            "prosperity": 40_000,
        },
        {
            "level": 2,
            "next_level": 3,
            "requires": {"furnace": 2, "warehouse": 2, "beast": 2},
            "funds": 3000,
            "crystals": 6000,
            "prosperity": 80_000,
        },
        {
            "level": 3,
            "next_level": 4,
            "requires": {"furnace": 3, "warehouse": 3, "beast": 3},
            "funds": 5000,
            "crystals": 9000,
            "prosperity": 160_000,
        },
        {
            "level": 4,
            "next_level": 5,
            "requires": {"furnace": 4, "warehouse": 4, "beast": 4},
            "funds": 7000,
            "crystals": 12_000,
            "prosperity": 320_000,
        },
        {
            "level": 5,
            "next_level": 6,
            "requires": {"furnace": 5, "warehouse": 5, "beast": 5},
            "funds": 9000,
            "crystals": 15_000,
            "prosperity": 640_000,
        },
        {
            "level": 6,
            "next_level": 7,
            "requires": {"furnace": 6, "warehouse": 6, "beast": 6},
            "funds": 12_000,
            "crystals": 19_000,
            "prosperity": 1_000_000,
        },
        {
            "level": 7,
            "next_level": 8,
            "requires": {"furnace": 7, "warehouse": 7, "beast": 7},
            "funds": 15_000,
            "crystals": 23_000,
            "prosperity": 2_000_000,
        },
        {
            "level": 8,
            "next_level": 9,
            "requires": {"furnace": 8, "warehouse": 8, "beast": 8},
            "funds": 18_000,
            "crystals": 27_000,
            "prosperity": 4_000_000,
        },
        {
            "level": 9,
            "next_level": 10,
            "requires": {"furnace": 9, "warehouse": 9, "beast": 9},
            "funds": 25_000,
            "crystals": 35_000,
            "prosperity": 6_500_000,
        },
    ]

    FURNACE_UPGRADE_RULES = [
        {
            "level": 1,
            "next_level": 2,
            "council_level": 2,
            "funds": 1000,
            "crystals": 300,
            "prosperity": 40_000,
        },
        {
            "level": 2,
            "next_level": 3,
            "council_level": 3,
            "funds": 2000,
            "crystals": 600,
            "prosperity": 80_000,
        },
        {
            "level": 3,
            "next_level": 4,
            "council_level": 4,
            "funds": 3000,
            "crystals": 900,
            "prosperity": 160_000,
        },
        {
            "level": 4,
            "next_level": 5,
            "council_level": 5,
            "funds": 4000,
            "crystals": 1200,
            "prosperity": 320_000,
        },
        {
            "level": 5,
            "next_level": 6,
            "council_level": 6,
            "funds": 5000,
            "crystals": 1500,
            "prosperity": 640_000,
        },
        {
            "level": 6,
            "next_level": 7,
            "council_level": 7,
            "funds": 6000,
            "crystals": 1900,
            "prosperity": 1_000_000,
        },
        {
            "level": 7,
            "next_level": 8,
            "council_level": 8,
            "funds": 7000,
            "crystals": 2300,
            "prosperity": 2_000_000,
        },
        {
            "level": 8,
            "next_level": 9,
            "council_level": 9,
            "funds": 8000,
            "crystals": 2700,
            "prosperity": 4_000_000,
        },
        {
            "level": 9,
            "next_level": 10,
            "council_level": 10,
            "funds": 9000,
            "crystals": 3500,
            "prosperity": 6_500_000,
        },
    ]

    TALENT_POOL_UPGRADE_RULES = [
        {
            "level": 1,
            "next_level": 2,
            "council_level": 2,
            "funds": 1000,
            "crystals": 300,
            "prosperity": 40_000,
        },
        {
            "level": 2,
            "next_level": 3,
            "council_level": 3,
            "funds": 2000,
            "crystals": 600,
            "prosperity": 80_000,
        },
        {
            "level": 3,
            "next_level": 4,
            "council_level": 4,
            "funds": 3000,
            "crystals": 900,
            "prosperity": 160_000,
        },
        {
            "level": 4,
            "next_level": 5,
            "council_level": 5,
            "funds": 4000,
            "crystals": 1200,
            "prosperity": 320_000,
        },
        {
            "level": 5,
            "next_level": 6,
            "council_level": 6,
            "funds": 5000,
            "crystals": 1500,
            "prosperity": 640_000,
        },
        {
            "level": 6,
            "next_level": 7,
            "council_level": 7,
            "funds": 6000,
            "crystals": 1900,
            "prosperity": 1_000_000,
        },
        {
            "level": 7,
            "next_level": 8,
            "council_level": 8,
            "funds": 7000,
            "crystals": 2300,
            "prosperity": 2_000_000,
        },
        {
            "level": 8,
            "next_level": 9,
            "council_level": 9,
            "funds": 8000,
            "crystals": 2700,
            "prosperity": 4_000_000,
        },
        {
            "level": 9,
            "next_level": 10,
            "council_level": 10,
            "funds": 9000,
            "crystals": 3500,
            "prosperity": 6_500_000,
        },
    ]

    BEAST_ROOM_UPGRADE_RULES = [
        {
            "level": 1,
            "next_level": 2,
            "council_level": 2,
            "funds": 1000,
            "crystals": 300,
            "prosperity": 40_000,
        },
        {
            "level": 2,
            "next_level": 3,
            "council_level": 3,
            "funds": 2000,
            "crystals": 600,
            "prosperity": 80_000,
        },
        {
            "level": 3,
            "next_level": 4,
            "council_level": 4,
            "funds": 3000,
            "crystals": 900,
            "prosperity": 160_000,
        },
        {
            "level": 4,
            "next_level": 5,
            "council_level": 5,
            "funds": 4000,
            "crystals": 1200,
            "prosperity": 320_000,
        },
        {
            "level": 5,
            "next_level": 6,
            "council_level": 6,
            "funds": 5000,
            "crystals": 1500,
            "prosperity": 640_000,
        },
        {
            "level": 6,
            "next_level": 7,
            "council_level": 7,
            "funds": 6000,
            "crystals": 1900,
            "prosperity": 1_000_000,
        },
        {
            "level": 7,
            "next_level": 8,
            "council_level": 8,
            "funds": 7000,
            "crystals": 2300,
            "prosperity": 2_000_000,
        },
        {
            "level": 8,
            "next_level": 9,
            "council_level": 9,
            "funds": 8000,
            "crystals": 2700,
            "prosperity": 4_000_000,
        },
        {
            "level": 9,
            "next_level": 10,
            "council_level": 10,
            "funds": 9000,
            "crystals": 3500,
            "prosperity": 6_500_000,
        },
    ]

    ITEM_STORAGE_UPGRADE_RULES = [
        {
            "level": 1,
            "next_level": 2,
            "council_level": 2,
            "funds": 1000,
            "crystals": 300,
            "prosperity": 40_000,
        },
        {
            "level": 2,
            "next_level": 3,
            "council_level": 3,
            "funds": 2000,
            "crystals": 600,
            "prosperity": 80_000,
        },
        {
            "level": 3,
            "next_level": 4,
            "council_level": 4,
            "funds": 3000,
            "crystals": 900,
            "prosperity": 160_000,
        },
        {
            "level": 4,
            "next_level": 5,
            "council_level": 5,
            "funds": 4000,
            "crystals": 1200,
            "prosperity": 320_000,
        },
        {
            "level": 5,
            "next_level": 6,
            "council_level": 6,
            "funds": 5000,
            "crystals": 1500,
            "prosperity": 640_000,
        },
        {
            "level": 6,
            "next_level": 7,
            "council_level": 7,
            "funds": 6000,
            "crystals": 1900,
            "prosperity": 1_000_000,
        },
        {
            "level": 7,
            "next_level": 8,
            "council_level": 8,
            "funds": 7000,
            "crystals": 2300,
            "prosperity": 2_000_000,
        },
        {
            "level": 8,
            "next_level": 9,
            "council_level": 9,
            "funds": 8000,
            "crystals": 2700,
            "prosperity": 4_000_000,
        },
        {
            "level": 9,
            "next_level": 10,
            "council_level": 10,
            "funds": 9000,
            "crystals": 3500,
            "prosperity": 6_500_000,
        },
    ]

    FURNACE_BASE_ROOMS = 4
    FURNACE_ROOM_PER_LEVEL = 1
    FURNACE_BASE_CRYSTAL_BONUS = 0
    FURNACE_CRYSTAL_BONUS_PER_LEVEL = 1  # 每升一级，火能修行每个人所获得的焚火晶增加1个

    TALENT_POOL_BASE_CAP = 1
    TALENT_POOL_CAP_PER_LEVEL = 1

    BEAST_ROOM_BASE_CAP = 1
    BEAST_ROOM_CAP_PER_LEVEL = 1

    ITEM_STORAGE_BASE_CAP = 5
    ITEM_STORAGE_CAP_PER_LEVEL = 5

    TALENT_RESEARCH_COST_RULES = {
        2: {"funds": 1000, "crystals": 500},
        3: {"funds": 1200, "crystals": 600},
        4: {"funds": 1400, "crystals": 700},
        5: {"funds": 1600, "crystals": 800},
        6: {"funds": 1900, "crystals": 1000},
        7: {"funds": 2200, "crystals": 1200},
        8: {"funds": 2500, "crystals": 1400},
        9: {"funds": 2800, "crystals": 1600},
        10: {"funds": 3200, "crystals": 2000},
    }

    MEMBER_BASE_CAPACITY = 40  # 1级联盟成员上限为40人
    MEMBER_PER_LEVEL = 10  # 每升一级增加10人上限

    @staticmethod
    def can_create_alliance(player: Player, has_token: bool) -> tuple:
        """
        判断是否可以创建联盟
        返回: (bool, error_message)
        """
        if player.level < AllianceRules.CREATE_LEVEL_REQUIREMENT:
            return False, f"等级不足{AllianceRules.CREATE_LEVEL_REQUIREMENT}级，无法创建联盟"
        
        if not has_token:
            return False, "缺少盟主证明，无法创建联盟"
            
        return True, ""

    @staticmethod
    def role_priority(role: int) -> int:
        priority = {
            AllianceRules.ROLE_LEADER: 0,
            AllianceRules.ROLE_VICE_LEADER: 1,
            AllianceRules.ROLE_ELDER: 2,
            AllianceRules.ROLE_MEMBER: 3
        }
        return priority.get(role, 4)

    @staticmethod
    def can_edit_notice(role: int) -> bool:
        return role in AllianceRules.NOTICE_EDIT_ROLES

    @staticmethod
    def can_manage_roles(role: int) -> bool:
        return role == AllianceRules.ROLE_LEADER

    @staticmethod
    def can_assign_role_to(target_role: int) -> bool:
        return target_role in {
            AllianceRules.ROLE_MEMBER,
            AllianceRules.ROLE_VICE_LEADER,
            AllianceRules.ROLE_ELDER
        }

    @staticmethod
    def can_kick_member(actor_role: int, target_role: int) -> bool:
        if actor_role == AllianceRules.ROLE_LEADER:
            return target_role != AllianceRules.ROLE_LEADER
        if actor_role == AllianceRules.ROLE_VICE_LEADER:
            return target_role in (AllianceRules.ROLE_ELDER, AllianceRules.ROLE_MEMBER)
        return False

    @classmethod
    def role_label(cls, role: int) -> str:
        return cls.ROLE_LABELS.get(role, "未知职位")

    @classmethod
    def army_label_for_key(cls, army_key: Optional[str]) -> str:
        if not army_key:
            return "未报名"
        return cls.ARMY_LABELS.get(army_key, "未报名")

    @staticmethod
    def is_valid_talent_key(talent_key: str) -> bool:
        return talent_key in AllianceRules.TALENT_KEYS

    @staticmethod
    def talent_label(talent_key: str) -> str:
        return AllianceRules.TALENT_LABELS.get(talent_key, "未知天赋")

    @staticmethod
    def is_valid_building_key(building_key: str) -> bool:
        return building_key in AllianceRules.BUILDING_KEYS

    @staticmethod
    def building_label(building_key: str) -> str:
        return AllianceRules.BUILDING_LABELS.get(building_key, building_key)

    @staticmethod
    def get_council_upgrade_rule(current_level: int):
        for rule in AllianceRules.COUNCIL_UPGRADE_RULES:
            if rule["level"] == current_level:
                return rule
        return None

    @staticmethod
    def get_furnace_upgrade_rule(current_level: int):
        for rule in AllianceRules.FURNACE_UPGRADE_RULES:
            if rule["level"] == current_level:
                return rule
        return None

    @staticmethod
    def get_talent_pool_upgrade_rule(current_level: int):
        for rule in AllianceRules.TALENT_POOL_UPGRADE_RULES:
            if rule["level"] == current_level:
                return rule
        return None

    @staticmethod
    def get_beast_room_upgrade_rule(current_level: int):
        for rule in AllianceRules.BEAST_ROOM_UPGRADE_RULES:
            if rule["level"] == current_level:
                return rule
        return None

    @staticmethod
    def get_item_storage_upgrade_rule(current_level: int):
        for rule in AllianceRules.ITEM_STORAGE_UPGRADE_RULES:
            if rule["level"] == current_level:
                return rule
        return None

    @staticmethod
    def furnace_training_room_count(furnace_level: int) -> int:
        level = max(1, furnace_level or 1)
        return AllianceRules.FURNACE_BASE_ROOMS + (level - 1) * AllianceRules.FURNACE_ROOM_PER_LEVEL

    @staticmethod
    def furnace_crystal_bonus(furnace_level: int) -> int:
        level = max(1, furnace_level or 1)
        return AllianceRules.FURNACE_BASE_CRYSTAL_BONUS + (level - 1) * AllianceRules.FURNACE_CRYSTAL_BONUS_PER_LEVEL

    @staticmethod
    def talent_pool_research_cap(talent_pool_level: int) -> int:
        level = max(1, talent_pool_level or 1)
        return AllianceRules.TALENT_POOL_BASE_CAP + (level - 1) * AllianceRules.TALENT_POOL_CAP_PER_LEVEL

    @staticmethod
    def talent_pool_max_talent_level(talent_pool_level: int) -> int:
        return AllianceRules.talent_pool_research_cap(talent_pool_level)

    @staticmethod
    def beast_room_capacity_from_level(beast_room_level: int) -> int:
        level = max(1, beast_room_level or 1)
        return AllianceRules.BEAST_ROOM_BASE_CAP + (level - 1) * AllianceRules.BEAST_ROOM_CAP_PER_LEVEL

    @staticmethod
    def item_storage_capacity_from_level(storage_level: int) -> int:
        level = max(1, storage_level or 1)
        return AllianceRules.ITEM_STORAGE_BASE_CAP + (level - 1) * AllianceRules.ITEM_STORAGE_CAP_PER_LEVEL

    @staticmethod
    def get_talent_research_cost(next_research_level: int, talent_key: str) -> Optional[dict]:
        """
        next_research_level 表示目标研究等级（当前 + 1），有效范围 2~10
        所有天赋成本一致，talent_key 仅作校验
        """
        if not AllianceRules.is_valid_talent_key(talent_key):
            return None
        return AllianceRules.TALENT_RESEARCH_COST_RULES.get(next_research_level)

    @staticmethod
    def member_capacity(alliance_level: int) -> int:
        level = max(1, alliance_level or 1)
        return AllianceRules.MEMBER_BASE_CAPACITY + (level - 1) * AllianceRules.MEMBER_PER_LEVEL

    @staticmethod
    def can_research_talent(role: int) -> bool:
        return role == AllianceRules.ROLE_LEADER

    @staticmethod
    def clamp_talent_research_level(building_level: int, desired_level: int) -> int:
        """
        研究等级上限由建筑等级决定
        """
        return min(building_level, max(1, desired_level))

    @staticmethod
    def get_talent_max_level(building_level: int, research_level: int) -> int:
        return min(building_level, research_level)

    @staticmethod
    def get_talent_effect_percent(level: int) -> int:
        return level * AllianceRules.TALENT_PERCENT_PER_LEVEL

    @staticmethod
    def get_talent_learn_contribution_cost(next_level: int) -> Dict[str, int]:
        """
        盟众学习天赋所需贡献：
        - 单项贡献 = 目标等级 * 10 点
        - 6 项天赋合计贡献 = 单项贡献 * 6
        """
        level = max(1, min(next_level or 1, 10))
        per_talent = level * AllianceRules.TALENT_LEARN_CONTRIBUTION_PER_LEVEL
        total = per_talent * len(AllianceRules.TALENT_KEYS)
        return {
            "per_talent": per_talent,
            "total": total,
        }

    @staticmethod
    def beast_storage_capacity(alliance_level: int) -> int:
        """
        幻兽室容量 = 联盟等级 (至少 1)
        """
        return max(1, alliance_level or 1)

    @staticmethod
    def item_storage_capacity(alliance_level: int) -> int:
        """
        道具寄存仓库容量：1级 5 格，每升一级 +5 格
        """
        level = max(1, alliance_level or 1)
        return level * 5

    @staticmethod
    def training_crystal_reward(furnace_level: int) -> int:
        """
        火能修行奖励：根据焚火炉等级获得焚火晶
        1级获得6个，2级获得7个，3级获得8个，...，10级获得15个
        """
        level = max(1, min(furnace_level or 1, 10))
        return 5 + level  # 1级=6, 2级=7, ..., 10级=15

    @staticmethod
    def get_donation_rule(key: str):
        return AllianceRules.DONATION_RULES.get(key)

    @staticmethod
    def donation_keys():
        return list(AllianceRules.DONATION_RULES.keys())

    @staticmethod
    def validate_alliance_name(name: str) -> Optional[str]:
        cleaned = (name or "").strip()
        if not cleaned:
            return "请输入联盟名称"
        if len(cleaned) < AllianceRules.RENAME_MIN_LENGTH or len(cleaned) > AllianceRules.RENAME_MAX_LENGTH:
            return f"联盟名称需在{AllianceRules.RENAME_MIN_LENGTH}到{AllianceRules.RENAME_MAX_LENGTH}个字符之间"
        return None
