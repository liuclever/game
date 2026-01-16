"""
联盟精英争霸赛 MySQL 实现
"""
from datetime import datetime
from typing import Optional, List, Dict
from infrastructure.db.connection import execute_query, execute_update, execute_insert
from domain.repositories.competition_repo import (
    ICompetitionRepo,
    CompetitionSession,
    CompetitionRegistration,
    CompetitionSignup,
    CompetitionTeamMember,
    CompetitionScore,
    CompetitionPersonalScore,
)

class MySQLCompetitionRepo(ICompetitionRepo):
    """争霸赛 MySQL 实现"""
    
    def get_current_session(self) -> Optional[CompetitionSession]:
        """获取当前届次"""
        now = datetime.now()
        sql = """
            SELECT * FROM alliance_competition_sessions
            WHERE registration_start <= %s AND battle_end >= %s
            ORDER BY id DESC
            LIMIT 1
        """
        rows = execute_query(sql, (now, now))
        if not rows:
            return None
        return self._row_to_session(rows[0])
    
    def get_session_by_key(self, session_key: str) -> Optional[CompetitionSession]:
        """通过届次标识获取届次"""
        sql = "SELECT * FROM alliance_competition_sessions WHERE session_key = %s"
        rows = execute_query(sql, (session_key,))
        if not rows:
            return None
        return self._row_to_session(rows[0])
    
    def create_session(self, session: CompetitionSession) -> int:
        """创建届次"""
        sql = """
            INSERT INTO alliance_competition_sessions
            (session_key, session_name, phase, registration_start, registration_end,
             signup_start, signup_end, battle_date, battle_start, battle_end)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        return execute_insert(sql, (
            session.session_key,
            session.session_name,
            session.phase,
            session.registration_start,
            session.registration_end,
            session.signup_start,
            session.signup_end,
            session.battle_date,
            session.battle_start,
            session.battle_end,
        ))
    
    def update_session_phase(self, session_id: int, phase: str) -> None:
        """更新届次阶段"""
        sql = "UPDATE alliance_competition_sessions SET phase = %s WHERE id = %s"
        execute_update(sql, (phase, session_id))
    
    def register_alliance(self, registration: CompetitionRegistration) -> int:
        """联盟报名"""
        sql = """
            INSERT INTO alliance_competition_registrations
            (session_id, alliance_id, registered_by, registered_at, status)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            registered_by = VALUES(registered_by),
            registered_at = VALUES(registered_at),
            status = VALUES(status)
        """
        return execute_insert(sql, (
            registration.session_id,
            registration.alliance_id,
            registration.registered_by,
            registration.registered_at,
            registration.status,
        ))
    
    def get_registration(self, session_id: int, alliance_id: int) -> Optional[CompetitionRegistration]:
        """获取联盟报名信息"""
        sql = """
            SELECT * FROM alliance_competition_registrations
            WHERE session_id = %s AND alliance_id = %s
        """
        rows = execute_query(sql, (session_id, alliance_id))
        if not rows:
            return None
        return self._row_to_registration(rows[0])
    
    def signup_member(self, signup: CompetitionSignup) -> int:
        """成员签到"""
        sql = """
            INSERT INTO alliance_competition_signups
            (session_id, alliance_id, user_id, team_key, signed_at, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            team_key = VALUES(team_key),
            signed_at = VALUES(signed_at),
            status = VALUES(status)
        """
        return execute_insert(sql, (
            signup.session_id,
            signup.alliance_id,
            signup.user_id,
            signup.team_key,
            signup.signed_at,
            signup.status,
        ))
    
    def get_signup(self, session_id: int, alliance_id: int, user_id: int) -> Optional[CompetitionSignup]:
        """获取成员签到信息"""
        sql = """
            SELECT * FROM alliance_competition_signups
            WHERE session_id = %s AND alliance_id = %s AND user_id = %s
        """
        rows = execute_query(sql, (session_id, alliance_id, user_id))
        if not rows:
            return None
        return self._row_to_signup(rows[0])
    
    def get_alliance_signups(self, session_id: int, alliance_id: int) -> List[CompetitionSignup]:
        """获取联盟所有签到成员"""
        sql = """
            SELECT * FROM alliance_competition_signups
            WHERE session_id = %s AND alliance_id = %s AND status = 1
            ORDER BY signed_at
        """
        rows = execute_query(sql, (session_id, alliance_id))
        return [self._row_to_signup(row) for row in rows]
    
    def get_team_signups(self, session_id: int, team_key: str) -> List[CompetitionSignup]:
        """获取战队所有签到成员"""
        sql = """
            SELECT * FROM alliance_competition_signups
            WHERE session_id = %s AND team_key = %s AND status = 1
            ORDER BY signed_at
        """
        rows = execute_query(sql, (session_id, team_key))
        return [self._row_to_signup(row) for row in rows]
    
    def set_team_member_order(self, team_member: CompetitionTeamMember) -> int:
        """设置战队成员出战顺序"""
        sql = """
            INSERT INTO alliance_competition_team_members
            (session_id, alliance_id, team_key, user_id, battle_order, adjusted_by, adjusted_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            battle_order = VALUES(battle_order),
            adjusted_by = VALUES(adjusted_by),
            adjusted_at = VALUES(adjusted_at)
        """
        return execute_insert(sql, (
            team_member.session_id,
            team_member.alliance_id,
            team_member.team_key,
            team_member.user_id,
            team_member.battle_order,
            team_member.adjusted_by,
            team_member.adjusted_at,
        ))
    
    def get_team_members(self, session_id: int, alliance_id: int, team_key: str) -> List[CompetitionTeamMember]:
        """获取战队成员列表"""
        sql = """
            SELECT * FROM alliance_competition_team_members
            WHERE session_id = %s AND alliance_id = %s AND team_key = %s
            ORDER BY battle_order
        """
        rows = execute_query(sql, (session_id, alliance_id, team_key))
        return [self._row_to_team_member(row) for row in rows]
    
    def update_team_score(self, score: CompetitionScore) -> None:
        """更新战队积分"""
        sql = """
            INSERT INTO alliance_competition_scores
            (session_id, alliance_id, team_key, team_score, team_rank, team_final_rank)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            team_score = VALUES(team_score),
            team_rank = VALUES(team_rank),
            team_final_rank = VALUES(team_final_rank)
        """
        execute_update(sql, (
            score.session_id,
            score.alliance_id,
            score.team_key,
            score.team_score,
            score.team_rank,
            score.team_final_rank,
        ))
    
    def get_team_score(self, session_id: int, alliance_id: int, team_key: str) -> Optional[CompetitionScore]:
        """获取战队积分"""
        sql = """
            SELECT * FROM alliance_competition_scores
            WHERE session_id = %s AND alliance_id = %s AND team_key = %s
        """
        rows = execute_query(sql, (session_id, alliance_id, team_key))
        if not rows:
            return None
        return self._row_to_score(rows[0])
    
    def update_personal_score(self, score: CompetitionPersonalScore) -> None:
        """更新个人积分"""
        sql = """
            INSERT INTO alliance_competition_personal_scores
            (session_id, user_id, alliance_id, team_key, personal_score, personal_rank, eliminated_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            personal_score = VALUES(personal_score),
            personal_rank = VALUES(personal_rank),
            eliminated_count = VALUES(eliminated_count)
        """
        execute_update(sql, (
            score.session_id,
            score.user_id,
            score.alliance_id,
            score.team_key,
            score.personal_score,
            score.personal_rank,
            score.eliminated_count,
        ))
    
    def get_personal_score(self, session_id: int, user_id: int) -> Optional[CompetitionPersonalScore]:
        """获取个人积分"""
        sql = """
            SELECT * FROM alliance_competition_personal_scores
            WHERE session_id = %s AND user_id = %s
        """
        rows = execute_query(sql, (session_id, user_id))
        if not rows:
            return None
        return self._row_to_personal_score(rows[0])
    
    def get_team_rankings(self, session_id: int, team_key: str, limit: int = 10) -> List[CompetitionScore]:
        """获取战队排行榜"""
        sql = """
            SELECT * FROM alliance_competition_scores
            WHERE session_id = %s AND team_key = %s
            ORDER BY team_score DESC, team_rank ASC
            LIMIT %s
        """
        rows = execute_query(sql, (session_id, team_key, limit))
        return [self._row_to_score(row) for row in rows]
    
    def get_personal_rankings(self, session_id: int, limit: int = 10, offset: int = 0) -> List[CompetitionPersonalScore]:
        """获取个人排行榜"""
        sql = """
            SELECT * FROM alliance_competition_personal_scores
            WHERE session_id = %s
            ORDER BY personal_score DESC, personal_rank ASC
            LIMIT %s OFFSET %s
        """
        rows = execute_query(sql, (session_id, limit, offset))
        return [self._row_to_personal_score(row) for row in rows]
    
    def count_personal_rankings(self, session_id: int) -> int:
        """获取个人排行榜总数"""
        sql = """
            SELECT COUNT(*) as cnt FROM alliance_competition_personal_scores
            WHERE session_id = %s
        """
        rows = execute_query(sql, (session_id,))
        if rows:
            return rows[0].get('cnt', 0)
        return 0
    
    def get_alliance_prestige(self, session_id: int, alliance_id: int) -> Optional[Dict]:
        """获取联盟威望"""
        sql = """
            SELECT * FROM alliance_competition_prestige
            WHERE session_id = %s AND alliance_id = %s
        """
        rows = execute_query(sql, (session_id, alliance_id))
        if not rows:
            return None
        return rows[0]
    
    def get_alliance_prestige_rankings(self, session_id: int, limit: int = 10, offset: int = 0) -> List[Dict]:
        """获取联盟威望排行榜"""
        sql = """
            SELECT * FROM alliance_competition_prestige
            WHERE session_id = %s
            ORDER BY prestige DESC, alliance_rank ASC
            LIMIT %s OFFSET %s
        """
        rows = execute_query(sql, (session_id, limit, offset))
        return rows
    
    def count_alliance_prestige_rankings(self, session_id: int) -> int:
        """获取联盟威望排行榜总数"""
        sql = """
            SELECT COUNT(*) as cnt FROM alliance_competition_prestige
            WHERE session_id = %s
        """
        rows = execute_query(sql, (session_id,))
        if rows:
            return rows[0].get('cnt', 0)
        return 0
    
    def get_alliance_battles(self, session_id: int, alliance_id: int, team_key: Optional[str] = None) -> List[Dict]:
        """获取联盟战斗记录"""
        if team_key:
            sql = """
                SELECT 
                    b.id,
                    b.round,
                    b.team_key,
                    b.opponent_alliance_id,
                    b.battle_result,
                    b.battle_time,
                    a.name as opponent_alliance_name
                FROM alliance_competition_battles b
                LEFT JOIN alliances a ON b.opponent_alliance_id = a.id
                WHERE b.session_id = %s 
                    AND b.alliance_id = %s 
                    AND b.team_key = %s
                    AND b.battle_result != 'pending'
                ORDER BY b.round ASC, b.battle_time ASC
            """
            rows = execute_query(sql, (session_id, alliance_id, team_key))
        else:
            sql = """
                SELECT 
                    b.id,
                    b.round,
                    b.team_key,
                    b.opponent_alliance_id,
                    b.battle_result,
                    b.battle_time,
                    a.name as opponent_alliance_name
                FROM alliance_competition_battles b
                LEFT JOIN alliances a ON b.opponent_alliance_id = a.id
                WHERE b.session_id = %s 
                    AND b.alliance_id = %s
                    AND b.battle_result != 'pending'
                ORDER BY b.round ASC, b.battle_time ASC
            """
            rows = execute_query(sql, (session_id, alliance_id))
        return rows
    
    def get_elite_top8_count(self, session_id: int, alliance_id: int) -> int:
        """获取联盟进入8强的精英数量"""
        sql = """
            SELECT COUNT(DISTINCT ps.user_id) as cnt
            FROM alliance_competition_personal_scores ps
            WHERE ps.session_id = %s 
                AND ps.alliance_id = %s
                AND ps.personal_rank IS NOT NULL
                AND ps.personal_rank <= 8
        """
        rows = execute_query(sql, (session_id, alliance_id))
        if rows:
            return rows[0].get('cnt', 0)
        return 0
    
    # 辅助方法：将数据库行转换为对象
    def _row_to_session(self, row: Dict) -> CompetitionSession:
        return CompetitionSession(
            id=row['id'],
            session_key=row['session_key'],
            session_name=row['session_name'],
            phase=row['phase'],
            registration_start=row['registration_start'],
            registration_end=row['registration_end'],
            signup_start=row['signup_start'],
            signup_end=row['signup_end'],
            battle_date=row['battle_date'],
            battle_start=row['battle_start'],
            battle_end=row['battle_end'],
            result_published_at=row.get('result_published_at'),
        )
    
    def _row_to_registration(self, row: Dict) -> CompetitionRegistration:
        return CompetitionRegistration(
            id=row['id'],
            session_id=row['session_id'],
            alliance_id=row['alliance_id'],
            registered_by=row['registered_by'],
            registered_at=row['registered_at'],
            status=row['status'],
        )
    
    def _row_to_signup(self, row: Dict) -> CompetitionSignup:
        return CompetitionSignup(
            id=row['id'],
            session_id=row['session_id'],
            alliance_id=row['alliance_id'],
            user_id=row['user_id'],
            team_key=row['team_key'],
            signed_at=row['signed_at'],
            status=row['status'],
        )
    
    def _row_to_team_member(self, row: Dict) -> CompetitionTeamMember:
        return CompetitionTeamMember(
            id=row['id'],
            session_id=row['session_id'],
            alliance_id=row['alliance_id'],
            team_key=row['team_key'],
            user_id=row['user_id'],
            battle_order=row['battle_order'],
            adjusted_by=row.get('adjusted_by'),
            adjusted_at=row.get('adjusted_at'),
        )
    
    def _row_to_score(self, row: Dict) -> CompetitionScore:
        return CompetitionScore(
            id=row['id'],
            session_id=row['session_id'],
            alliance_id=row['alliance_id'],
            team_key=row['team_key'],
            team_score=row['team_score'],
            team_rank=row.get('team_rank'),
            team_final_rank=row.get('team_final_rank'),
        )
    
    def _row_to_personal_score(self, row: Dict) -> CompetitionPersonalScore:
        return CompetitionPersonalScore(
            id=row['id'],
            session_id=row['session_id'],
            user_id=row['user_id'],
            alliance_id=row['alliance_id'],
            team_key=row['team_key'],
            personal_score=row['personal_score'],
            personal_rank=row.get('personal_rank'),
            eliminated_count=row.get('eliminated_count', 0),
        )
