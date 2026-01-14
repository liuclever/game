"""
MySQL版战骨仓库
"""
from typing import List, Optional

from domain.entities.bone import BeastBone
from domain.repositories.bone_repo import IBoneRepo
from infrastructure.db.connection import execute_query, execute_update, execute_insert


class MySQLBoneRepo(IBoneRepo):
    """MySQL版战骨存储"""

    def get_by_user_id(self, user_id: int) -> List[BeastBone]:
        """获取玩家所有战骨"""
        sql = """
            SELECT id, user_id, beast_id, template_id, slot, level, stage,
                   hp_flat, attack_flat, physical_defense_flat, magic_defense_flat, speed_flat
            FROM beast_bone WHERE user_id = %s
        """
        rows = execute_query(sql, (user_id,))
        return [self._row_to_bone(row) for row in rows]

    def get_by_id(self, bone_id: int) -> Optional[BeastBone]:
        """根据ID获取战骨"""
        sql = """
            SELECT id, user_id, beast_id, template_id, slot, level, stage,
                   hp_flat, attack_flat, physical_defense_flat, magic_defense_flat, speed_flat
            FROM beast_bone WHERE id = %s
        """
        rows = execute_query(sql, (bone_id,))
        if rows:
            return self._row_to_bone(rows[0])
        return None

    def get_by_beast_id(self, beast_id: int) -> List[BeastBone]:
        """获取某只幻兽装备的所有战骨"""
        sql = """
            SELECT id, user_id, beast_id, template_id, slot, level, stage,
                   hp_flat, attack_flat, physical_defense_flat, magic_defense_flat, speed_flat
            FROM beast_bone WHERE beast_id = %s
        """
        rows = execute_query(sql, (beast_id,))
        return [self._row_to_bone(row) for row in rows]

    def save(self, bone: BeastBone) -> None:
        """保存战骨（新增或更新）"""
        if bone.id is None:
            # 新增
            sql = """
                INSERT INTO beast_bone 
                (user_id, beast_id, template_id, slot, level, stage,
                 hp_flat, attack_flat, physical_defense_flat, magic_defense_flat, speed_flat)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            bone.id = execute_insert(sql, (
                bone.user_id,
                bone.beast_id,
                bone.template_id,
                bone.slot,
                bone.level,
                bone.stage,
                bone.hp_flat,
                bone.attack_flat,
                bone.physical_defense_flat,
                bone.magic_defense_flat,
                bone.speed_flat,
            ))
        else:
            # 更新
            sql = """
                UPDATE beast_bone SET
                    user_id = %s,
                    beast_id = %s,
                    template_id = %s,
                    slot = %s,
                    level = %s,
                    stage = %s,
                    hp_flat = %s,
                    attack_flat = %s,
                    physical_defense_flat = %s,
                    magic_defense_flat = %s,
                    speed_flat = %s
                WHERE id = %s
            """
            execute_update(sql, (
                bone.user_id,
                bone.beast_id,
                bone.template_id,
                bone.slot,
                bone.level,
                bone.stage,
                bone.hp_flat,
                bone.attack_flat,
                bone.physical_defense_flat,
                bone.magic_defense_flat,
                bone.speed_flat,
                bone.id,
            ))

    def delete(self, bone_id: int) -> None:
        """删除战骨"""
        sql = "DELETE FROM beast_bone WHERE id = %s"
        execute_update(sql, (bone_id,))

    def _row_to_bone(self, row: dict) -> BeastBone:
        """将数据库行转换为BeastBone实体"""
        return BeastBone(
            id=row['id'],
            user_id=row['user_id'],
            beast_id=row['beast_id'],
            template_id=row['template_id'],
            slot=row['slot'],
            level=row['level'],
            stage=row['stage'],
            hp_flat=row['hp_flat'],
            attack_flat=row['attack_flat'],
            physical_defense_flat=row['physical_defense_flat'],
            magic_defense_flat=row['magic_defense_flat'],
            speed_flat=row['speed_flat'],
        )



