from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass

@dataclass
class CompetitionSession:
    """争霸赛届次"""
    id: int
    session_key: str
    session_name: str
    phase: str  # registration, signup, battle, finished
    registration_start: datetime
    registration_end: datetime
    signup_start: datetime
    signup_end: datetime
    battle_date: datetime
    battle_start: datetime
    battle_end: datetime
    result_published_at: Optional[datetime] = None

@dataclass
class CompetitionRegistration:
    """联盟报名"""
    id: int
    session_id: int
    alliance_id: int
    registered_by: int
    registered_at: datetime
    status: int

@dataclass
class CompetitionSignup:
    """成员签到"""
    id: int
    session_id: int
    alliance_id: int
    user_id: int
    team_key: str
    signed_at: datetime
    status: int

@dataclass
class CompetitionTeamMember:
    """战队成员"""
    id: int
    session_id: int
    alliance_id: int
    team_key: str
    user_id: int
    battle_order: int
    adjusted_by: Optional[int] = None
    adjusted_at: Optional[datetime] = None

@dataclass
class CompetitionScore:
    """战队积分"""
    id: int
    session_id: int
    alliance_id: int
    team_key: str
    team_score: int
    team_rank: Optional[int] = None
    team_final_rank: Optional[int] = None

@dataclass
class CompetitionPersonalScore:
    """个人积分"""
    id: int
    session_id: int
    user_id: int
    alliance_id: int
    team_key: str
    personal_score: int
    personal_rank: Optional[int] = None
    eliminated_count: int = 0

class ICompetitionRepo(ABC):
    """争霸赛数据访问接口"""
    
    @abstractmethod
    def get_current_session(self) -> Optional[CompetitionSession]:
        """获取当前届次"""
        pass
    
    @abstractmethod
    def get_session_by_key(self, session_key: str) -> Optional[CompetitionSession]:
        """通过届次标识获取届次"""
        pass
    
    @abstractmethod
    def create_session(self, session: CompetitionSession) -> int:
        """创建届次"""
        pass
    
    @abstractmethod
    def update_session_phase(self, session_id: int, phase: str) -> None:
        """更新届次阶段"""
        pass
    
    @abstractmethod
    def register_alliance(self, registration: CompetitionRegistration) -> int:
        """联盟报名"""
        pass
    
    @abstractmethod
    def get_registration(self, session_id: int, alliance_id: int) -> Optional[CompetitionRegistration]:
        """获取联盟报名信息"""
        pass
    
    @abstractmethod
    def signup_member(self, signup: CompetitionSignup) -> int:
        """成员签到"""
        pass
    
    @abstractmethod
    def get_signup(self, session_id: int, alliance_id: int, user_id: int) -> Optional[CompetitionSignup]:
        """获取成员签到信息"""
        pass
    
    @abstractmethod
    def get_alliance_signups(self, session_id: int, alliance_id: int) -> List[CompetitionSignup]:
        """获取联盟所有签到成员"""
        pass
    
    @abstractmethod
    def get_team_signups(self, session_id: int, team_key: str) -> List[CompetitionSignup]:
        """获取战队所有签到成员"""
        pass
    
    @abstractmethod
    def set_team_member_order(self, team_member: CompetitionTeamMember) -> int:
        """设置战队成员出战顺序"""
        pass
    
    @abstractmethod
    def get_team_members(self, session_id: int, alliance_id: int, team_key: str) -> List[CompetitionTeamMember]:
        """获取战队成员列表"""
        pass
    
    @abstractmethod
    def update_team_score(self, score: CompetitionScore) -> None:
        """更新战队积分"""
        pass
    
    @abstractmethod
    def get_team_score(self, session_id: int, alliance_id: int, team_key: str) -> Optional[CompetitionScore]:
        """获取战队积分"""
        pass
    
    @abstractmethod
    def update_personal_score(self, score: CompetitionPersonalScore) -> None:
        """更新个人积分"""
        pass
    
    @abstractmethod
    def get_personal_score(self, session_id: int, user_id: int) -> Optional[CompetitionPersonalScore]:
        """获取个人积分"""
        pass
    
    @abstractmethod
    def get_team_rankings(self, session_id: int, team_key: str, limit: int = 10) -> List[CompetitionScore]:
        """获取战队排行榜"""
        pass
    
    @abstractmethod
    def get_personal_rankings(self, session_id: int, limit: int = 10) -> List[CompetitionPersonalScore]:
        """获取个人排行榜"""
        pass
    
    @abstractmethod
    def get_alliance_prestige(self, session_id: int, alliance_id: int) -> Optional[Dict]:
        """获取联盟威望"""
        pass
    
    @abstractmethod
    def get_alliance_prestige_rankings(self, session_id: int, limit: int = 10, offset: int = 0) -> List[Dict]:
        """获取联盟威望排行榜"""
        pass
    
    @abstractmethod
    def count_alliance_prestige_rankings(self, session_id: int) -> int:
        """获取联盟威望排行榜总数"""
        pass
    
    @abstractmethod
    def get_alliance_battles(self, session_id: int, alliance_id: int, team_key: Optional[str] = None) -> List[Dict]:
        """获取联盟战斗记录"""
        pass
    
    @abstractmethod
    def get_elite_top8_count(self, session_id: int, alliance_id: int) -> int:
        """获取联盟进入8强的精英数量"""
        pass
