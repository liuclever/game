from typing import List, Optional
from datetime import datetime
from domain.entities.manor import ManorLand, PlayerManor
from domain.repositories.manor_repo import IManorRepo
from infrastructure.db.connection import execute_query, execute_update, execute_insert

class MySQLManorRepo(IManorRepo):
    """MySQL版庄园仓库"""

    def get_user_lands(self, user_id: int) -> List[ManorLand]:
        """获取玩家所有土地信息"""
        sql = """
            SELECT id, user_id, land_index, status, tree_type, plant_time, created_at, updated_at
            FROM manor_land WHERE user_id = %s
            ORDER BY land_index ASC
        """
        rows = execute_query(sql, (user_id,))
        return [
            ManorLand(
                id=row['id'],
                user_id=row['user_id'],
                land_index=row['land_index'],
                status=row['status'],
                tree_type=row['tree_type'],
                plant_time=row['plant_time'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            ) for row in rows
        ]

    def get_land(self, user_id: int, land_index: int) -> Optional[ManorLand]:
        """获取特定土地信息"""
        sql = """
            SELECT id, user_id, land_index, status, tree_type, plant_time, created_at, updated_at
            FROM manor_land WHERE user_id = %s AND land_index = %s
        """
        rows = execute_query(sql, (user_id, land_index))
        if rows:
            row = rows[0]
            return ManorLand(
                id=row['id'],
                user_id=row['user_id'],
                land_index=row['land_index'],
                status=row['status'],
                tree_type=row['tree_type'],
                plant_time=row['plant_time'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
        return None

    def open_land(self, user_id: int, land_index: int) -> bool:
        """开启土地"""
        # 如果已存在且状态为未开启，更新为开启状态
        existing = self.get_land(user_id, land_index)
        if existing:
            if existing.status == 0:
                sql = "UPDATE manor_land SET status = 1 WHERE user_id = %s AND land_index = %s"
                affected = execute_update(sql, (user_id, land_index))
                return affected > 0
            return True # 已经开启了
        
        # 否则插入新记录，状态为1（空闲/开启）
        sql = "INSERT INTO manor_land (user_id, land_index, status) VALUES (%s, %s, 1)"
        affected = execute_insert(sql, (user_id, land_index))
        return affected is not None

    def start_planting(self, user_id: int, land_index: int, tree_type: int, plant_time: datetime) -> bool:
        """开始种植"""
        existing = self.get_land(user_id, land_index)
        if not existing or existing.status != 1:
            return False

        # 规则：每块土地只能种一种东西（首次种植决定 tree_type 后锁定；后续必须种同一种）
        if existing.tree_type and existing.tree_type != tree_type:
            return False

        sql = """
            UPDATE manor_land 
            SET status = 2, tree_type = %s, plant_time = %s 
            WHERE user_id = %s AND land_index = %s AND status = 1
        """
        affected = execute_update(sql, (tree_type, plant_time, user_id, land_index))
        return affected > 0

    def reset_land(self, user_id: int, land_index: int) -> bool:
        """收获后重置土地状态"""
        sql = """
            UPDATE manor_land 
            SET status = 1, plant_time = NULL 
            WHERE user_id = %s AND land_index = %s AND status = 2
        """
        affected = execute_update(sql, (user_id, land_index))
        return affected > 0

    def get_player_manor(self, user_id: int) -> Optional[PlayerManor]:
        """获取玩家庄园扩展信息"""
        sql = """
            SELECT user_id, total_harvest_count, total_gold_earned, created_at, updated_at
            FROM player_manor WHERE user_id = %s
        """
        rows = execute_query(sql, (user_id,))
        if rows:
            row = rows[0]
            return PlayerManor(
                user_id=row['user_id'],
                total_harvest_count=row['total_harvest_count'],
                total_gold_earned=row['total_gold_earned'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
        return None

    def update_player_manor(self, player_manor: PlayerManor) -> bool:
        """更新玩家庄园扩展信息"""
        sql = """
            UPDATE player_manor 
            SET total_harvest_count = %s, total_gold_earned = %s 
            WHERE user_id = %s
        """
        affected = execute_update(sql, (
            player_manor.total_harvest_count, 
            player_manor.total_gold_earned, 
            player_manor.user_id
        ))
        return affected > 0

    def create_player_manor_if_not_exists(self, user_id: int) -> bool:
        """如果不存在则创建玩家庄园信息"""
        existing = self.get_player_manor(user_id)
        if existing:
            return True
        sql = "INSERT INTO player_manor (user_id) VALUES (%s)"
        affected = execute_insert(sql, (user_id,))
        return affected is not None
