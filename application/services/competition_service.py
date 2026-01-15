"""
联盟精英争霸赛服务
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from domain.repositories.competition_repo import ICompetitionRepo
from domain.repositories.competition_repo import ICompetitionRepo, CompetitionSession, CompetitionRegistration, CompetitionSignup
from domain.repositories.alliance_repo import IAllianceRepo
from domain.repositories.player_repo import IPlayerRepo
from domain.rules.alliance_rules import AllianceRules

class CompetitionService:
    """联盟精英争霸赛服务"""
    
    # 战队等级对应关系
    TEAM_LEVEL_MAP = {
        'calf_tiger': (1, 39),
        'white_tiger': (40, 49),
        'azure_dragon': (50, 59),
        'vermillion_bird': (60, 69),
        'black_tortoise': (70, 79),
        'god_of_war': (80, 100),
    }
    
    # 积分规则
    SCORE_RULES = {
        'champion': 20,  # 冠军
        'final': 15,     # 2强
        'semi': 10,      # 4强
        'quarter': 5,    # 8强
        'eliminate': 2,  # 淘汰对手
    }
    
    def __init__(
        self,
        competition_repo: ICompetitionRepo,
        alliance_repo: IAllianceRepo,
        player_repo: IPlayerRepo,
    ):
        self.competition_repo = competition_repo
        self.alliance_repo = alliance_repo
        self.player_repo = player_repo
    
    def _get_current_week_monday(self) -> datetime:
        """获取当前周的周一0点"""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        days_since_monday = today.weekday()
        monday = today - timedelta(days=days_since_monday)
        return monday
    
    def _get_current_session_key(self) -> str:
        """获取当前届次标识（当前周的周一日期）"""
        monday = self._get_current_week_monday()
        return monday.strftime('%Y-%m-%d')
    
    def _get_team_by_level(self, level: int) -> Optional[str]:
        """根据等级获取战队"""
        for team_key, (min_level, max_level) in self.TEAM_LEVEL_MAP.items():
            if min_level <= level <= max_level:
                return team_key
        return None
    
    def get_current_session(self) -> Optional[CompetitionSession]:
        """获取当前届次"""
        session = self.competition_repo.get_current_session()
        if session:
            return session
        
        # 如果没有当前届次，创建新的届次
        return self._create_new_session()
    
    def _create_new_session(self) -> CompetitionSession:
        """创建新的届次"""
        monday = self._get_current_week_monday()
        session_key = monday.strftime('%Y-%m-%d')
        session_name = f"第{session_key}届"
        
        # 报名时间：周一0点至周三23:59
        registration_start = monday
        registration_end = monday + timedelta(days=2, hours=23, minutes=59)
        
        # 签到时间：周四0点-周日20:00
        signup_start = monday + timedelta(days=3)
        signup_end = monday + timedelta(days=6, hours=20)
        
        # 战斗时间：周日20点-22点
        battle_date = monday + timedelta(days=6)
        battle_start = battle_date.replace(hour=20, minute=0, second=0)
        battle_end = battle_date.replace(hour=22, minute=0, second=0)
        
        # 确定当前阶段
        now = datetime.now()
        if now < registration_end:
            phase = 'registration'
        elif now < signup_end:
            phase = 'signup'
        elif now < battle_end:
            phase = 'battle'
        else:
            phase = 'finished'
        
        session = CompetitionSession(
            id=0,
            session_key=session_key,
            session_name=session_name,
            phase=phase,
            registration_start=registration_start,
            registration_end=registration_end,
            signup_start=signup_start,
            signup_end=signup_end,
            battle_date=battle_date,
            battle_start=battle_start,
            battle_end=battle_end,
        )
        
        session_id = self.competition_repo.create_session(session)
        session.id = session_id
        return session
    
    def get_competition_info(self, user_id: int) -> Dict:
        """获取争霸赛信息"""
        session = self.get_current_session()
        if not session:
            return {"ok": False, "error": "无法获取当前届次"}
        
        # 获取用户联盟信息
        member = self.alliance_repo.get_member(user_id)
        if not member:
            return {
                "ok": True,
                "session": session.session_key,
                "phase": session.phase,
                "zones": {key: {"registered": False} for key in self.TEAM_LEVEL_MAP.keys()},
                "personalSignup": {"registered": False, "team": None},
            }
        
        alliance_id = member.alliance_id
        
        # 检查联盟是否已报名
        registration = self.competition_repo.get_registration(session.id, alliance_id)
        is_registered = registration is not None and registration.status == 1
        
        # 获取各区域报名状态
        zones = {}
        for team_key in self.TEAM_LEVEL_MAP.keys():
            # 这里简化处理，实际应该检查该联盟在该战队的报名情况
            zones[team_key] = {"registered": is_registered}
        
        # 获取个人签到状态
        personal_signup = None
        if is_registered:
            signup = self.competition_repo.get_signup(session.id, alliance_id, user_id)
            if signup:
                personal_signup = {
                    "registered": signup.status == 1,
                    "team": signup.team_key,
                }
        
        if not personal_signup:
            personal_signup = {"registered": False, "team": None}
        
        return {
            "ok": True,
            "session": session.session_key,
            "phase": session.phase,
            "zones": zones,
            "personalSignup": personal_signup,
        }
    
    def register_alliance(self, user_id: int, team_keys: List[str]) -> Dict:
        """联盟报名（盟主或副盟主）"""
        # 检查权限
        member = self.alliance_repo.get_member(user_id)
        if not member:
            return {"ok": False, "error": "未加入联盟"}
        
        if member.role not in [AllianceRules.ROLE_LEADER, AllianceRules.ROLE_VICE_LEADER]:
            return {"ok": False, "error": "只有盟主和副盟主可以报名"}
        
        # 获取当前届次
        session = self.get_current_session()
        if not session:
            return {"ok": False, "error": "无法获取当前届次"}
        
        # 检查是否在报名时间内
        now = datetime.now()
        if now < session.registration_start or now > session.registration_end:
            return {"ok": False, "error": "不在报名时间内"}
        
        # 检查是否已报名
        existing = self.competition_repo.get_registration(session.id, member.alliance_id)
        if existing and existing.status == 1:
            return {"ok": False, "error": "联盟已报名"}
        
        # 创建报名记录
        registration = CompetitionRegistration(
            id=0,
            session_id=session.id,
            alliance_id=member.alliance_id,
            registered_by=user_id,
            registered_at=now,
            status=1,
        )
        
        self.competition_repo.register_alliance(registration)
        
        return {"ok": True, "message": "报名成功"}
    
    def signup_member(self, user_id: int) -> Dict:
        """成员签到"""
        # 检查是否在联盟中
        member = self.alliance_repo.get_member(user_id)
        if not member:
            return {"ok": False, "error": "未加入联盟"}
        
        # 获取当前届次
        session = self.get_current_session()
        if not session:
            return {"ok": False, "error": "无法获取当前届次"}
        
        # 检查是否在签到时间内
        now = datetime.now()
        if now < session.signup_start or now > session.signup_end:
            return {"ok": False, "error": "不在签到时间内"}
        
        # 检查联盟是否已报名
        registration = self.competition_repo.get_registration(session.id, member.alliance_id)
        if not registration or registration.status != 1:
            return {"ok": False, "error": "联盟未报名"}
        
        # 检查是否已签到
        existing = self.competition_repo.get_signup(session.id, member.alliance_id, user_id)
        if existing and existing.status == 1:
            return {"ok": False, "error": "已签到"}
        
        # 获取玩家等级
        player = self.player_repo.get_by_id(user_id)
        if not player:
            return {"ok": False, "error": "玩家信息不存在"}
        
        # 根据等级确定战队
        team_key = self._get_team_by_level(player.level)
        if not team_key:
            return {"ok": False, "error": "等级不符合参赛要求"}
        
        # 创建签到记录
        signup = CompetitionSignup(
            id=0,
            session_id=session.id,
            alliance_id=member.alliance_id,
            user_id=user_id,
            team_key=team_key,
            signed_at=now,
            status=1,
        )
        
        self.competition_repo.signup_member(signup)
        
        return {"ok": True, "message": "签到成功", "team": team_key}
    
    def get_team_rankings(self, team_key: str, stage: str = 'all') -> Dict:
        """获取战队排行榜"""
        session = self.get_current_session()
        if not session:
            return {"ok": False, "error": "无法获取当前届次"}
        
        # 获取战队排行榜
        rankings = self.competition_repo.get_team_rankings(session.id, team_key, limit=100)
        
        # 根据阶段筛选
        if stage != 'all':
            filtered_rankings = []
            for rank in rankings:
                if stage == 'champion' and rank.team_final_rank == 1:
                    filtered_rankings.append(rank)
                elif stage == 'final' and rank.team_final_rank == 2:
                    filtered_rankings.append(rank)
                elif stage == 'semi' and rank.team_final_rank == 4:
                    filtered_rankings.append(rank)
                elif stage == 'quarter' and rank.team_final_rank == 8:
                    filtered_rankings.append(rank)
            rankings = filtered_rankings
        
        # 获取联盟名称
        result_list = []
        honor_text = None
        
        for rank in rankings:
            alliance = self.alliance_repo.get_alliance_by_id(rank.alliance_id)
            alliance_name = alliance.name if alliance else f"联盟{rank.alliance_id}"
            
            result_list.append({
                "id": rank.id,
                "alliance_id": rank.alliance_id,
                "alliance_name": alliance_name,
                "team_score": rank.team_score,
                "rank": rank.team_rank,
                "final_rank": rank.team_final_rank,
            })
        
        # 获取当前区域的荣誉文本（显示第一个有最终排名的）
        if result_list and result_list[0].get('final_rank'):
            final_rank = result_list[0]['final_rank']
            team_name = self._get_team_name(team_key)
            if final_rank == 1:
                honor_text = f"{team_name}战队荣誉获得冠军"
            elif final_rank == 2:
                honor_text = f"{team_name}战队荣誉晋级2强"
            elif final_rank == 4:
                honor_text = f"{team_name}战队荣誉晋级4强"
            elif final_rank == 8:
                honor_text = f"{team_name}战队荣誉晋级8强"
        
        return {
            "ok": True,
            "session": session.session_key,
            "team_key": team_key,
            "team_name": self._get_team_name(team_key),
            "honorText": honor_text,
            "rankings": result_list,
        }
    
    def _get_team_name(self, team_key: str) -> str:
        """获取战队名称"""
        team_names = {
            'calf_tiger': '犊虎',
            'white_tiger': '白虎',
            'azure_dragon': '青龙',
            'vermillion_bird': '朱雀',
            'black_tortoise': '玄武',
            'god_of_war': '战神',
        }
        return team_names.get(team_key, team_key)
    
    def get_elite_rankings(self, page: int = 1, page_size: int = 10) -> Dict:
        """获取精英排行榜（个人积分排行）"""
        session = self.get_current_session()
        if not session:
            return {"ok": False, "error": "无法获取当前届次"}
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 获取排行榜数据
        rankings = self.competition_repo.get_personal_rankings(session.id, limit=page_size, offset=offset)
        total_count = self.competition_repo.count_personal_rankings(session.id)
        total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1
        
        # 获取玩家昵称和联盟名称
        result_list = []
        for idx, rank in enumerate(rankings):
            # 获取玩家信息
            player = self.player_repo.get_by_id(rank.user_id)
            nickname = player.nickname if player else f"玩家{rank.user_id}"
            
            # 获取联盟信息
            alliance_name = ""
            if rank.alliance_id:
                alliance = self.alliance_repo.get_alliance_by_id(rank.alliance_id)
                alliance_name = alliance.name if alliance else ""
            
            # 计算实际排名（考虑分页）
            actual_rank = offset + idx + 1
            
            result_list.append({
                "id": rank.id,
                "rank": actual_rank,
                "user_id": rank.user_id,
                "nickname": nickname,
                "alliance_id": rank.alliance_id,
                "alliance_name": alliance_name,
                "score": rank.personal_score,
                "team_key": rank.team_key,
            })
        
        return {
            "ok": True,
            "session": session.session_key,
            "rankings": result_list,
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": total_pages,
        }
    
    def get_alliance_prestige_rankings(self, user_id: int, page: int = 1, page_size: int = 10) -> Dict:
        """获取联盟积分排行（联盟威望排行）"""
        session = self.get_current_session()
        if not session:
            return {"ok": False, "error": "无法获取当前届次"}
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 获取总数
        total_count = self.competition_repo.count_alliance_prestige_rankings(session.id)
        total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1
        
        # 获取用户联盟信息
        user_alliance_id = None
        user_alliance_rank = None
        member = self.alliance_repo.get_member(user_id)
        if member:
            user_alliance_id = member.alliance_id
        
        # 获取分页的联盟威望排行榜
        rankings_data = self.competition_repo.get_alliance_prestige_rankings(
            session.id, 
            limit=page_size, 
            offset=offset
        )
        
        # 如果需要查找用户联盟排名，需要查询全部数据
        if user_alliance_id:
            all_rankings = self.competition_repo.get_alliance_prestige_rankings(session.id, limit=1000, offset=0)
            for idx, rank_data in enumerate(all_rankings):
                if rank_data.get('alliance_id') == user_alliance_id:
                    user_alliance_rank = idx + 1
                    break
        
        # 获取联盟名称并构建结果列表
        result_list = []
        for idx, rank_data in enumerate(rankings_data):
            alliance_id = rank_data.get('alliance_id')
            alliance = self.alliance_repo.get_alliance_by_id(alliance_id)
            alliance_name = alliance.name if alliance else f"联盟{alliance_id}"
            
            # 计算排名（考虑分页偏移）
            actual_rank = offset + idx + 1
            
            result_list.append({
                "rank": actual_rank,
                "alliance_id": alliance_id,
                "alliance_name": alliance_name,
                "prestige": rank_data.get('prestige', 0),
            })
        
        return {
            "ok": True,
            "session": session.session_key,
            "rankings": result_list,
            "my_rank": user_alliance_rank,
            "my_alliance_id": user_alliance_id,
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": total_pages,
        }
    
    def get_past_records(self, user_id: int, session_key: Optional[str] = None) -> Dict:
        """获取往届战绩"""
        # 获取指定届次或当前届次
        if session_key:
            session = self.competition_repo.get_session_by_key(session_key)
        else:
            session = self.get_current_session()
        
        if not session:
            return {"ok": False, "error": "无法获取届次信息"}
        
        # 获取用户联盟信息
        member = self.alliance_repo.get_member(user_id)
        if not member:
            return {"ok": False, "error": "未加入联盟"}
        
        alliance_id = member.alliance_id
        
        # 获取联盟威望和排名
        prestige_data = self.competition_repo.get_alliance_prestige(session.id, alliance_id)
        alliance_prestige = prestige_data.get('prestige', 0) if prestige_data else 0
        alliance_rank = prestige_data.get('alliance_rank') if prestige_data else None
        
        # 获取各战队最终排名
        team_records = []
        for team_key in self.TEAM_LEVEL_MAP.keys():
            score = self.competition_repo.get_team_score(session.id, alliance_id, team_key)
            if score and score.team_final_rank:
                team_name = self._get_team_name(team_key)
                final_rank = score.team_final_rank
                if final_rank == 1:
                    honor_text = f"{team_name}队荣誉获得冠军"
                elif final_rank == 2:
                    honor_text = f"{team_name}队荣誉晋级2强"
                elif final_rank == 4:
                    honor_text = f"{team_name}队荣誉晋级4强"
                elif final_rank == 8:
                    honor_text = f"{team_name}队荣誉晋级8强"
                else:
                    honor_text = f"{team_name}队"
                
                team_records.append({
                    "team_key": team_key,
                    "team_name": team_name,
                    "final_rank": final_rank,
                    "honor_text": honor_text,
                })
        
        # 获取精英战绩（进入8强的数量）
        elite_top8_count = self.competition_repo.get_elite_top8_count(session.id, alliance_id)
        
        # 获取所有战斗记录（按战队分组）
        all_battles = self.competition_repo.get_alliance_battles(session.id, alliance_id)
        
        # 按战队分组战斗记录
        battles_by_team = {}
        for battle in all_battles:
            team_key = battle.get('team_key')
            if team_key not in battles_by_team:
                battles_by_team[team_key] = []
            
            battles_by_team[team_key].append({
                "id": battle.get('id'),
                "round": battle.get('round'),
                "team_key": team_key,
                "opponent_alliance_id": battle.get('opponent_alliance_id'),
                "opponent_alliance_name": battle.get('opponent_alliance_name') or f"联盟{battle.get('opponent_alliance_id')}",
                "battle_result": battle.get('battle_result'),
                "battle_time": battle.get('battle_time'),
                "is_win": battle.get('battle_result') == 'win',
            })
        
        return {
            "ok": True,
            "session": session.session_key,
            "session_name": session.session_name,
            "alliance_prestige": alliance_prestige,
            "alliance_rank": alliance_rank,
            "team_records": team_records,
            "elite_top8_count": elite_top8_count,
            "battles_by_team": battles_by_team,
        }