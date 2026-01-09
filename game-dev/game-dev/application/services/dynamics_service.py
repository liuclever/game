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
        """
        获取用户动态列表（分页）
        整合所有对战类型的记录：擂台、镇妖、古战场、联盟对战等
        
        Args:
            user_id: 用户ID
            page: 页码（从1开始）
            page_size: 每页数量
        
        Returns:
            动态列表和分页信息
        """
        offset = (page - 1) * page_size
        
        # 获取所有类型的战斗记录
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
            # 如果表不存在或其他错误，跳过镇妖记录
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
        
        # 4. 联盟对战记录（如果有）
        try:
            alliance_logs = self._get_alliance_battles(user_id, limit=page_size * 5)
            for log in alliance_logs:
                dynamic = self._format_alliance_dynamic(log, user_id)
                if dynamic:
                    dynamic['battle_type'] = 'alliance'
                    all_dynamics.append(dynamic)
        except Exception as e:
            print(f"获取联盟对战记录失败: {e}")
        
        # 5. 切磋记录
        try:
            spar_logs = self._get_spar_battles(user_id, limit=page_size * 5)
            for log in spar_logs:
                dynamic = self._format_spar_dynamic(log, user_id)
                if dynamic:
                    dynamic['battle_type'] = 'spar'
                    all_dynamics.append(dynamic)
        except Exception as e:
            print(f"获取切磋记录失败: {e}")
        
        # 按时间排序（最新的在前）
        all_dynamics.sort(key=lambda x: self._parse_time(x['time']), reverse=True)
        
        # 分页
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
        """解析时间字符串为datetime对象用于排序"""
        try:
            # 格式: MM-DD HH:MM
            current_year = datetime.now().year
            dt_str = f"{current_year}-{time_str}"
            return datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        except:
            return datetime.min
    
    def _format_arena_dynamic(self, log, user_id: int) -> Dict:
        """
        格式化擂台动态
        
        格式示例：
        - "在黄金场战胜 XXX 成功守擂，连胜X场 查看"
        - "在普通场率先抢占擂台"
        """
        if not log.created_at:
            return None
        
        # 格式化时间 (MM-DD HH:MM)，例如：01-06 22:01
        if isinstance(log.created_at, datetime):
            time_str = log.created_at.strftime("%m-%d %H:%M")
        elif isinstance(log.created_at, str):
            try:
                dt = datetime.strptime(log.created_at[:19], '%Y-%m-%d %H:%M:%S')
                time_str = dt.strftime("%m-%d %H:%M")
            except:
                time_str = log.created_at[5:16].replace('-', '-').replace(' ', ' ') if len(log.created_at) > 16 else log.created_at
        else:
            time_str = str(log.created_at)[5:16].replace('-', '-').replace(' ', ' ') if len(str(log.created_at)) > 16 else str(log.created_at)
        
        # 场次类型
        type_name = "黄金场" if log.arena_type == "gold" else "普通场"
        
        # 判断用户是挑战者还是擂主
        is_challenger = log.challenger_id == user_id
        is_champion = log.champion_id == user_id
        
        # 获取连胜场次
        # 从battle_data中获取，如果没有则根据战斗结果推断
        consecutive_wins = 0
        if log.battle_data and isinstance(log.battle_data, dict):
            # battle_data可能包含new_consecutive_wins或consecutive_wins
            consecutive_wins = log.battle_data.get('new_consecutive_wins') or log.battle_data.get('consecutive_wins', 0)
        
        # 如果battle_data中没有，根据战斗结果推断
        if consecutive_wins == 0:
            if is_champion and not log.is_challenger_win:
                # 守擂成功，尝试从arena表获取当前连胜（战斗后的）
                consecutive_wins = self._get_arena_consecutive_wins(log.arena_type, log.rank_name, log.champion_id)
                # 如果还是0，可能是首次守擂，设为1
                if consecutive_wins == 0:
                    consecutive_wins = 1
            elif is_challenger and log.is_challenger_win:
                # 挑战成功成为新擂主，首次抢占，连胜为1
                consecutive_wins = 1
        
        # 构建动态文本（按照用户要求的格式）
        if is_challenger:
            # 用户是挑战者
            if log.is_challenger_win:
                # 挑战成功
                if consecutive_wins == 1:
                    # 首次抢占擂台
                    text = f"在{type_name}率先抢占擂台"
                elif consecutive_wins > 1:
                    # 成功守擂（挑战成功后继续守擂）
                    text = f"在{type_name}战胜 {log.champion_name} 成功守擂，连胜{consecutive_wins}场"
                else:
                    # 默认情况（首次抢占）
                    text = f"在{type_name}率先抢占擂台"
            else:
                # 挑战失败
                text = f"在{type_name}惜败 {log.champion_name}"
        else:
            # 用户是擂主
            if log.is_challenger_win:
                # 被挑战失败（不显示在"我的动态"中，因为这是失败）
                # 但为了完整性，还是显示
                text = f"在{type_name}被 {log.challenger_name} 挑战失败"
            else:
                # 守擂成功
                if consecutive_wins > 0:
                    text = f"在{type_name}战胜 {log.challenger_name} 成功守擂，连胜{consecutive_wins}场"
                else:
                    text = f"在{type_name}战胜 {log.challenger_name} 成功守擂"
        
        return {
            "id": log.id,
            "time": time_str,
            "text": text,
            "battle_id": log.id,
            "has_detail": True,
        }
    
    def _get_arena_consecutive_wins(self, arena_type: str, rank_name: str, user_id: int) -> int:
        """从arena表获取当前连胜场次"""
        try:
            rows = execute_query(
                "SELECT consecutive_wins FROM arena WHERE arena_type = %s AND rank_name = %s AND champion_user_id = %s",
                (arena_type, rank_name, user_id)
            )
            if rows:
                return rows[0].get('consecutive_wins', 0)
        except Exception:
            pass
        return 0
    
    def _format_zhenyao_dynamic(self, log, user_id: int) -> Dict:
        """格式化镇妖动态"""
        if not log.created_at:
            return None
        
        # 格式化时间
        if isinstance(log.created_at, datetime):
            time_str = log.created_at.strftime("%m-%d %H:%M")
        else:
            try:
                dt = datetime.strptime(str(log.created_at)[:19], '%Y-%m-%d %H:%M:%S')
                time_str = dt.strftime("%m-%d %H:%M")
            except:
                time_str = str(log.created_at)[5:16] if len(str(log.created_at)) > 16 else str(log.created_at)
        
        # 判断用户是攻击者还是防守者
        is_attacker = log.attacker_id == user_id
        
        if is_attacker:
            if log.is_success:
                text = f"在镇妖塔第{log.floor}层战胜 {log.defender_name} 成功占领"
            else:
                text = f"在镇妖塔第{log.floor}层挑战 {log.defender_name} 失败"
        else:
            if log.is_success:
                text = f"在镇妖塔第{log.floor}层被 {log.attacker_name} 挑战失败"
            else:
                text = f"在镇妖塔第{log.floor}层成功防守 {log.attacker_name} 的挑战"
        
        return {
            "id": log.id,
            "time": time_str,
            "text": text,
            "battle_id": log.id,
            "has_detail": True,
        }
    
    def _get_battlefield_battles(self, user_id: int, limit: int) -> List[Dict]:
        """获取古战场战斗记录"""
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
        """格式化古战场动态"""
        if not log.get('created_at'):
            return None
        
        # 格式化时间
        try:
            dt = datetime.strptime(str(log['created_at'])[:19], '%Y-%m-%d %H:%M:%S')
            time_str = dt.strftime("%m-%d %H:%M")
        except:
            time_str = str(log['created_at'])[5:16] if len(str(log['created_at'])) > 16 else str(log['created_at'])
        
        battlefield_type = "猛虎战场" if log.get('battlefield_type') == 'tiger' else "飞鹤战场"
        is_first = log.get('first_user_id') == user_id
        
        if is_first:
            opponent_name = log.get('second_user_name', '未知')
            is_win = bool(log.get('is_first_win'))
        else:
            opponent_name = log.get('first_user_name', '未知')
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
        }
    
    def _get_alliance_battles(self, user_id: int, limit: int) -> List[Dict]:
        """获取联盟对战记录"""
        try:
            rows = execute_query(
                """SELECT id, attacker_signup_id, defender_signup_id, attacker_result, log_data, created_at
                   FROM alliance_land_battle_duel
                   WHERE attacker_signup_id IN (
                       SELECT id FROM alliance_army_signup WHERE user_id = %s
                   ) OR defender_signup_id IN (
                       SELECT id FROM alliance_army_signup WHERE user_id = %s
                   )
                   ORDER BY created_at DESC
                   LIMIT %s""",
                (user_id, user_id, limit)
            )
            return rows
        except Exception:
            return []
    
    def _format_alliance_dynamic(self, log: Dict, user_id: int) -> Dict:
        """格式化联盟对战动态"""
        if not log.get('created_at'):
            return None
        
        # 格式化时间
        try:
            dt = datetime.strptime(str(log['created_at'])[:19], '%Y-%m-%d %H:%M:%S')
            time_str = dt.strftime("%m-%d %H:%M")
        except:
            time_str = str(log['created_at'])[5:16] if len(str(log['created_at'])) > 16 else str(log['created_at'])
        
        # 简化显示，因为需要查询联盟信息比较复杂
        text = f"参与联盟对战"
        
        return {
            "id": log['id'],
            "time": time_str,
            "text": text,
            "battle_id": log['id'],
            "has_detail": False,  # 联盟对战详情暂时不支持
        }
    
    def _get_spar_battles(self, user_id: int, limit: int) -> List[Dict]:
        """获取切磋战斗记录"""
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
        """格式化切磋动态"""
        if not log.get('created_at'):
            return None
        
        # 格式化时间
        try:
            dt = datetime.strptime(str(log['created_at'])[:19], '%Y-%m-%d %H:%M:%S')
            time_str = dt.strftime("%m-%d %H:%M")
        except:
            time_str = str(log['created_at'])[5:16] if len(str(log['created_at'])) > 16 else str(log['created_at'])
        
        is_attacker = log.get('attacker_id') == user_id
        
        if is_attacker:
            opponent_name = log.get('defender_name', '未知')
            is_win = bool(log.get('is_attacker_win'))
            text = f"与 {opponent_name} 切磋，{'完美胜利' if is_win else '失败'}"
        else:
            opponent_name = log.get('attacker_name', '未知')
            is_win = not bool(log.get('is_attacker_win'))
            text = f"与 {opponent_name} 切磋，{'完美胜利' if is_win else '失败'}"
        
        return {
            "id": log['id'],
            "time": time_str,
            "text": text,
            "battle_id": log['id'],
            "has_detail": True,
        }
