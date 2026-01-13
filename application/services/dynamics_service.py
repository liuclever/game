"""
动态服务
整合所有动态数据来源（擂台、镇妖、古战场、联盟对战等）
"""
from typing import List, Dict
from datetime import datetime
from infrastructure.db.connection import execute_query
from infrastructure.db.arena_battle_repo_mysql import MySQLArenaBattleRepo
from infrastructure.db.zhenyao_battle_repo_mysql import MySQLZhenyaoBattleRepo
from infrastructure.db.battlefield_repo_mysql import MySQLBattlefieldBattleRepo


class DynamicsService:
    """动态服务"""
    
    def __init__(self):
        self.arena_battle_repo = MySQLArenaBattleRepo()
        self.zhenyao_battle_repo = MySQLZhenyaoBattleRepo()
        self.battlefield_battle_repo = MySQLBattlefieldBattleRepo()
    
    def get_user_dynamics(
        self, 
        user_id: int, 
        page: int = 1, 
        page_size: int = 10
    ) -> Dict:
        """获取用户动态列表（分页）"""
        offset = (page - 1) * page_size
        all_dynamics = []
        
        # 1. 擂台战斗记录
        arena_logs = self.arena_battle_repo.get_user_battles(user_id, limit=page_size * 5)
        for log in arena_logs:
            dynamic = self._format_arena_dynamic(log, user_id)
            if dynamic:
                dynamic['battle_type'] = 'arena'
                all_dynamics.append(dynamic)
        
        # 2. 镇妖战斗记录
        try:
            zhenyao_logs = self.zhenyao_battle_repo.get_user_battles(user_id, limit=page_size * 5)
            for log in zhenyao_logs:
                dynamic = self._format_zhenyao_dynamic(log, user_id)
                if dynamic:
                    dynamic['battle_type'] = 'zhenyao'
                    all_dynamics.append(dynamic)
        except Exception as e:
            print(f"获取镇妖记录失败: {e}")
        
        # 3. 古战场战斗记录
        try:
            battlefield_logs = self._get_battlefield_battles(user_id, limit=page_size * 5)
            for log in battlefield_logs:
                dynamic = self._format_battlefield_dynamic(log, user_id)
                if dynamic:
                    dynamic['battle_type'] = 'battlefield'
                    all_dynamics.append(dynamic)
        except Exception as e:
            print(f"获取古战场记录失败: {e}")
        
        # 4. 切磋记录
        try:
            spar_logs = self._get_spar_battles(user_id, limit=page_size * 5)
            for log in spar_logs:
                dynamic = self._format_spar_dynamic(log, user_id)
                if dynamic:
                    dynamic['battle_type'] = 'spar'
                    all_dynamics.append(dynamic)
        except Exception as e:
            print(f"获取切磋记录失败: {e}")
        
        # 按时间排序
        all_dynamics.sort(key=lambda x: self._parse_time(x['time']), reverse=True)
        
        total = len(all_dynamics)
        total_pages = max(1, (total + page_size - 1) // page_size)
        paginated_dynamics = all_dynamics[offset:offset + page_size]
        
        return {
            "ok": True,
            "dynamics": paginated_dynamics,
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
        }
    
    def _parse_time(self, time_str: str) -> datetime:
        try:
            current_year = datetime.now().year
            dt_str = f"{current_year}-{time_str}"
            return datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        except:
            return datetime.min
    
    def _format_arena_dynamic(self, log, user_id: int) -> Dict:
        if not log.created_at:
            return None
        
        if isinstance(log.created_at, datetime):
            time_str = log.created_at.strftime("%m-%d %H:%M")
        else:
            try:
                dt = datetime.strptime(str(log.created_at)[:19], '%Y-%m-%d %H:%M:%S')
                time_str = dt.strftime("%m-%d %H:%M")
            except:
                time_str = str(log.created_at)[5:16]
        
        type_name = "黄金场" if log.arena_type == "gold" else "普通场"
        is_challenger = log.challenger_id == user_id
        
        consecutive_wins = 0
        if log.battle_data and isinstance(log.battle_data, dict):
            consecutive_wins = log.battle_data.get('new_consecutive_wins') or log.battle_data.get('consecutive_wins', 0)
        
        if is_challenger:
            if log.is_challenger_win:
                if consecutive_wins <= 1:
                    text = f"在{type_name}率先抢占擂台"
                    opponent_id = None
                    opponent_name = None
                else:
                    text = f"在{type_name}战胜 {log.champion_name} 成功守擂，连胜{consecutive_wins}场"
                    opponent_id = log.champion_id
                    opponent_name = log.champion_name
            else:
                text = f"在{type_name}惜败 {log.champion_name}"
                opponent_id = log.champion_id
                opponent_name = log.champion_name
        else:
            if log.is_challenger_win:
                text = f"在{type_name}被 {log.challenger_name} 挑战失败"
                opponent_id = log.challenger_id
                opponent_name = log.challenger_name
            else:
                if consecutive_wins > 0:
                    text = f"在{type_name}战胜 {log.challenger_name} 成功守擂，连胜{consecutive_wins}场"
                else:
                    text = f"在{type_name}战胜 {log.challenger_name} 成功守擂"
                opponent_id = log.challenger_id
                opponent_name = log.challenger_name
        
        return {
            "id": log.id,
            "time": time_str,
            "text": text,
            "battle_id": log.id,
            "has_detail": True,
            "opponent_id": opponent_id,
            "opponent_name": opponent_name,
        }
    
    def _format_zhenyao_dynamic(self, log, user_id: int) -> Dict:
        if not log.created_at:
            return None
        
        if isinstance(log.created_at, datetime):
            time_str = log.created_at.strftime("%m-%d %H:%M")
        else:
            try:
                dt = datetime.strptime(str(log.created_at)[:19], '%Y-%m-%d %H:%M:%S')
                time_str = dt.strftime("%m-%d %H:%M")
            except:
                time_str = str(log.created_at)[5:16]
        
        is_attacker = log.attacker_id == user_id
        
        if is_attacker:
            if log.is_success:
                text = f"在镇妖塔第{log.floor}层战胜 {log.defender_name} 成功占领"
                opponent_id = log.defender_id
                opponent_name = log.defender_name
            else:
                text = f"在镇妖塔第{log.floor}层挑战 {log.defender_name} 失败"
                opponent_id = log.defender_id
                opponent_name = log.defender_name
        else:
            if log.is_success:
                text = f"在镇妖塔第{log.floor}层被 {log.attacker_name} 挑战失败"
                opponent_id = log.attacker_id
                opponent_name = log.attacker_name
            else:
                text = f"在镇妖塔第{log.floor}层成功防守 {log.attacker_name} 的挑战"
                opponent_id = log.attacker_id
                opponent_name = log.attacker_name
        
        return {
            "id": log.id,
            "time": time_str,
            "text": text,
            "battle_id": log.id,
            "has_detail": True,
            "opponent_id": opponent_id,
            "opponent_name": opponent_name,
        }
    
    def _get_battlefield_battles(self, user_id: int, limit: int) -> List[Dict]:
        try:
            rows = execute_query(
                """SELECT id, battlefield_type, period, round_num, match_num,
                          first_user_id, first_user_name, second_user_id, second_user_name,
                          is_first_win, result_label, battle_data, created_at
                   FROM battlefield_battle_log
                   WHERE first_user_id = %s OR second_user_id = %s
                   ORDER BY created_at DESC
                   LIMIT %s""",
                (user_id, user_id, limit)
            )
            return rows
        except Exception:
            return []
    
    def _format_battlefield_dynamic(self, log: Dict, user_id: int) -> Dict:
        if not log.get('created_at'):
            return None
        
        try:
            dt = datetime.strptime(str(log['created_at'])[:19], '%Y-%m-%d %H:%M:%S')
            time_str = dt.strftime("%m-%d %H:%M")
        except:
            time_str = str(log['created_at'])[5:16]
        
        battlefield_type = "猛虎战场" if log.get('battlefield_type') == 'tiger' else "飞鹤战场"
        is_first = log.get('first_user_id') == user_id
        
        if is_first:
            opponent_name = log.get('second_user_name', '未知')
            opponent_id = log.get('second_user_id')
            is_win = bool(log.get('is_first_win'))
        else:
            opponent_name = log.get('first_user_name', '未知')
            opponent_id = log.get('first_user_id')
            is_win = not bool(log.get('is_first_win'))
        
        result_label = log.get('result_label', '')
        if result_label:
            text = f"在{battlefield_type}第{log.get('period', 0)}期与 {opponent_name} 对战，{result_label}"
        else:
            text = f"在{battlefield_type}第{log.get('period', 0)}期与 {opponent_name} 对战，{'胜利' if is_win else '失败'}"
        
        return {
            "id": log['id'],
            "time": time_str,
            "text": text,
            "battle_id": log['id'],
            "has_detail": True,
            "opponent_id": opponent_id,
            "opponent_name": opponent_name,
        }
    
    def _get_spar_battles(self, user_id: int, limit: int) -> List[Dict]:
        try:
            rows = execute_query(
                """SELECT id, attacker_id, attacker_name, defender_id, defender_name, 
                          is_attacker_win, battle_data, created_at
                   FROM spar_battle_log
                   WHERE attacker_id = %s OR defender_id = %s
                   ORDER BY created_at DESC
                   LIMIT %s""",
                (user_id, user_id, limit)
            )
            return rows
        except Exception:
            return []
    
    def _format_spar_dynamic(self, log: Dict, user_id: int) -> Dict:
        if not log.get('created_at'):
            return None
        
        try:
            dt = datetime.strptime(str(log['created_at'])[:19], '%Y-%m-%d %H:%M:%S')
            time_str = dt.strftime("%m-%d %H:%M")
        except:
            time_str = str(log['created_at'])[5:16]
        
        is_attacker = log.get('attacker_id') == user_id
        
        if is_attacker:
            opponent_name = log.get('defender_name', '未知')
            opponent_id = log.get('defender_id')
            is_win = bool(log.get('is_attacker_win'))
        else:
            opponent_name = log.get('attacker_name', '未知')
            opponent_id = log.get('attacker_id')
            is_win = not bool(log.get('is_attacker_win'))
        
        text = f"与 {opponent_name} 切磋，{'完美胜利' if is_win else '失败'}"
        
        return {
            "id": log['id'],
            "time": time_str,
            "text": text,
            "battle_id": log['id'],
            "has_detail": True,
            "opponent_id": opponent_id,
            "opponent_name": opponent_name,
        }
