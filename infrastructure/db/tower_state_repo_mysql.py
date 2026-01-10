"""
MySQL版闯塔状态仓库
"""
from typing import Optional
from datetime import date

from domain.entities.tower import TowerState
from domain.repositories.tower_repo import ITowerStateRepo
from infrastructure.db.connection import execute_query, execute_update


class MySQLTowerStateRepo(ITowerStateRepo):
    """MySQL版闯塔状态存储"""
    
    def get_by_user_id(self, user_id: int, tower_type: str) -> Optional[TowerState]:
        """获取用户的闯塔状态"""
        sql = """
            SELECT user_id, tower_type, current_floor, max_floor_record, 
                   today_count, last_challenge_date
            FROM tower_state 
            WHERE user_id = %s AND tower_type = %s
        """
        rows = execute_query(sql, (user_id, tower_type))
        
        if rows:
            row = rows[0]
            return TowerState(
                user_id=row['user_id'],
                tower_type=row['tower_type'],
                current_floor=row['current_floor'],
                max_floor_record=row['max_floor_record'],
                today_count=row['today_count'],
                last_challenge_date=row['last_challenge_date'],
            )
        else:
            # 创建默认状态并保存
            state = TowerState(user_id=user_id, tower_type=tower_type)
            self.save(state)
            return state
    
    def save(self, state: TowerState) -> None:
        """保存闯塔状态（插入或更新）"""
        sql = """
            INSERT INTO tower_state 
                (user_id, tower_type, current_floor, max_floor_record, today_count, last_challenge_date)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                current_floor = VALUES(current_floor),
                max_floor_record = VALUES(max_floor_record),
                today_count = VALUES(today_count),
                last_challenge_date = VALUES(last_challenge_date)
        """
        execute_update(sql, (
            state.user_id,
            state.tower_type,
            state.current_floor,
            state.max_floor_record,
            state.today_count,
            state.last_challenge_date,
        ))
