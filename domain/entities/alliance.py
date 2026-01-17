from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Alliance:
    """联盟实体"""
    id: Optional[int] = None
    name: str = ""
    leader_id: int = 0
    level: int = 1
    exp: int = 0
    funds: int = 0
    crystals: int = 0
    prosperity: int = 0
    notice: Optional[str] = None
    created_at: Optional[datetime] = None

@dataclass
class AllianceMember:
    """联盟成员实体"""
    alliance_id: int
    user_id: int
    role: int = 0  # 1: 盟主, 0: 成员
    contribution: int = 0
    army_type: int = 0  # 0: 未报名, 1: 飞龙军, 2: 伏虎军
    joined_at: Optional[datetime] = None
    nickname: Optional[str] = None
    level: Optional[int] = None
    battle_power: Optional[int] = None

@dataclass
class AllianceArmyAssignment:
    """联盟兵营报名"""
    alliance_id: int
    user_id: int
    army: str  # dragon / tiger
    signed_at: Optional[datetime] = None
    nickname: Optional[str] = None
    level: Optional[int] = None
    battle_power: Optional[int] = None

@dataclass
class AllianceChatMessage:
    """联盟聊天消息实体"""
    id: Optional[int] = None
    alliance_id: int = 0
    user_id: int = 0
    content: str = ""
    created_at: Optional[datetime] = None
    # 扩展字段（用于显示）
    nickname: Optional[str] = None


@dataclass
class AllianceTalentResearch:
    """联盟天赋研究等级"""
    alliance_id: int
    talent_key: str
    research_level: int = 1


@dataclass
class PlayerTalentLevel:
    """玩家在联盟中的天赋等级"""
    user_id: int
    talent_key: str
    level: int = 0


@dataclass
class AllianceBuilding:
    """联盟建筑等级"""
    alliance_id: int
    building_key: str
    level: int = 1


@dataclass
class AllianceBeastStorage:
    """联盟幻兽室存储记录"""
    id: Optional[int]
    alliance_id: int
    beast_id: int
    owner_user_id: int
    stored_at: Optional[datetime] = None


@dataclass
class AllianceItemStorage:
    """联盟寄存仓库物品记录"""
    id: Optional[int]
    alliance_id: int
    item_id: int
    quantity: int
    owner_user_id: int
    stored_at: Optional[datetime] = None


@dataclass
class AllianceTrainingRoom:
    """联盟修行房间"""
    id: Optional[int]
    alliance_id: int
    creator_user_id: int
    title: str
    status: str = "ongoing"  # ongoing/completed/closed
    max_participants: int = 4
    duration_hours: int = 2  # 修行时长（小时），默认2小时
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class AllianceTrainingParticipant:
    """联盟修行参与记录"""
    id: Optional[int]
    room_id: int
    user_id: int
    joined_at: Optional[datetime] = None
    claimed_at: Optional[datetime] = None
    reward_amount: int = 0
    nickname: Optional[str] = None


@dataclass
class AllianceActivity:
    """联盟动态记录"""
    id: Optional[int]
    alliance_id: int
    event_type: str
    actor_user_id: Optional[int] = None
    actor_name: Optional[str] = None
    target_user_id: Optional[int] = None
    target_name: Optional[str] = None
    item_name: Optional[str] = None
    item_quantity: Optional[int] = None
    created_at: Optional[datetime] = None
