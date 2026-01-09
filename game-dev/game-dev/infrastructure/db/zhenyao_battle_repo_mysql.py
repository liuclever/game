"""
镇妖战斗记录仓库 - MySQL实现
"""
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime
import json

from infrastructure.db.connection import execute_query, execute_insert, execute_update


@dataclass
class ZhenyaoBattleLog:
    """镇妖战斗记录"""
    id: int
    floor: int
    attacker_id: int
    attacker_name: str
    defender_id: int
    defender_name: str
    is_success: bool
    remaining_seconds: int
    battle_data: dict
    created_at: datetime
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "floor": self.floor,
            "attacker_id": self.attacker_id,
            "attacker_name": self.attacker_name,
            "defender_id": self.defender_id,
            "defender_name": self.defender_name,
            "is_success": self.is_success,
            "remaining_seconds": self.remaining_seconds,
            "battle_data": self.battle_data,
            "created_at": self.created_at.strftime("%Y年%m月%d日 %H:%M") if self.created_at else "",
        }


class MySQLZhenyaoBattleRepo:
    """镇妖战斗记录仓库"""
    
    def save_battle(
        self,
        floor: int,
        attacker_id: int,
        attacker_name: str,
        defender_id: int,
        defender_name: str,
        is_success: bool,
        remaining_seconds: int,
        battle_data: dict
    ) -> int:
        """保存战斗记录，返回记录ID"""
        sql = """
            INSERT INTO zhenyao_battle_log 
            (floor, attacker_id, attacker_name, defender_id, defender_name, 
             is_success, remaining_seconds, battle_data)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        battle_json = json.dumps(battle_data, ensure_ascii=False)
        return execute_insert(sql, (
            floor, attacker_id, attacker_name, defender_id, defender_name,
            1 if is_success else 0, remaining_seconds, battle_json
        ))
    
    def get_by_id(self, battle_id: int) -> Optional[ZhenyaoBattleLog]:
        """根据ID获取战斗记录"""
        sql = """
            SELECT id, floor, attacker_id, attacker_name, defender_id, defender_name,
                   is_success, remaining_seconds, battle_data, created_at
            FROM zhenyao_battle_log WHERE id = %s
        """
        rows = execute_query(sql, (battle_id,))
        if rows:
            row = rows[0]
            battle_data = {}
            if row['battle_data']:
                try:
                    battle_data = json.loads(row['battle_data'])
                except:
                    pass
            return ZhenyaoBattleLog(
                id=row['id'],
                floor=row['floor'],
                attacker_id=row['attacker_id'],
                attacker_name=row['attacker_name'],
                defender_id=row['defender_id'],
                defender_name=row['defender_name'],
                is_success=bool(row['is_success']),
                remaining_seconds=row['remaining_seconds'],
                battle_data=battle_data,
                created_at=row['created_at'],
            )
        return None
    
    def get_recent_battles(self, limit: int = 20) -> List[ZhenyaoBattleLog]:
        """获取最近的战斗记录（全服动态）"""
        sql = """
            SELECT id, floor, attacker_id, attacker_name, defender_id, defender_name,
                   is_success, remaining_seconds, battle_data, created_at
            FROM zhenyao_battle_log 
            ORDER BY created_at DESC
            LIMIT %s
        """
        rows = execute_query(sql, (limit,))
        result = []
        for row in rows:
            battle_data = {}
            if row['battle_data']:
                try:
                    battle_data = json.loads(row['battle_data'])
                except:
                    pass
            result.append(ZhenyaoBattleLog(
                id=row['id'],
                floor=row['floor'],
                attacker_id=row['attacker_id'],
                attacker_name=row['attacker_name'],
                defender_id=row['defender_id'],
                defender_name=row['defender_name'],
                is_success=bool(row['is_success']),
                remaining_seconds=row['remaining_seconds'],
                battle_data=battle_data,
                created_at=row['created_at'],
            ))
        return result
    
    def get_user_battles(self, user_id: int, limit: int = 20) -> List[ZhenyaoBattleLog]:
        """获取某玩家相关的战斗记录（个人动态）"""
        sql = """
            SELECT id, floor, attacker_id, attacker_name, defender_id, defender_name,
                   is_success, remaining_seconds, battle_data, created_at
            FROM zhenyao_battle_log 
            WHERE attacker_id = %s OR defender_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        rows = execute_query(sql, (user_id, user_id, limit))
        result = []
        for row in rows:
            battle_data = {}
            if row['battle_data']:
                try:
                    battle_data = json.loads(row['battle_data'])
                except:
                    pass
            result.append(ZhenyaoBattleLog(
                id=row['id'],
                floor=row['floor'],
                attacker_id=row['attacker_id'],
                attacker_name=row['attacker_name'],
                defender_id=row['defender_id'],
                defender_name=row['defender_name'],
                is_success=bool(row['is_success']),
                remaining_seconds=row['remaining_seconds'],
                battle_data=battle_data,
                created_at=row['created_at'],
            ))
        return result


class MySQLZhenyaoDailyCountRepo:
    """镇妖每日次数仓库"""
    
    def get_today_count(self, user_id: int) -> tuple:
        """获取今日次数，返回(trial_count, hell_count)"""
        sql = """
            SELECT trial_count, hell_count FROM zhenyao_daily_count
            WHERE user_id = %s AND count_date = CURDATE()
        """
        rows = execute_query(sql, (user_id,))
        if rows:
            return (rows[0]['trial_count'], rows[0]['hell_count'])
        return (0, 0)
    
    def increment_trial(self, user_id: int) -> bool:
        """增加试炼层次数"""
        # 尝试更新
        sql_update = """
            UPDATE zhenyao_daily_count 
            SET trial_count = trial_count + 1
            WHERE user_id = %s AND count_date = CURDATE()
        """
        affected = execute_update(sql_update, (user_id,))
        
        if affected == 0:
            # 不存在则插入
            sql_insert = """
                INSERT INTO zhenyao_daily_count (user_id, trial_count, hell_count, count_date)
                VALUES (%s, 1, 0, CURDATE())
            """
            execute_insert(sql_insert, (user_id,))
        
        return True
    
    def increment_hell(self, user_id: int) -> bool:
        """增加炼狱层次数"""
        sql_update = """
            UPDATE zhenyao_daily_count 
            SET hell_count = hell_count + 1
            WHERE user_id = %s AND count_date = CURDATE()
        """
        affected = execute_update(sql_update, (user_id,))
        
        if affected == 0:
            sql_insert = """
                INSERT INTO zhenyao_daily_count (user_id, trial_count, hell_count, count_date)
                VALUES (%s, 0, 1, CURDATE())
            """
            execute_insert(sql_insert, (user_id,))
        
        return True
