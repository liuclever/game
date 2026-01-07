"""MySQL 版玩家幻兽仓库（实现 IBeastRepo，持久化 domain.entities.Beast）

表结构示例（需在 game_tower 库中手动创建 user_beast 表）：

CREATE TABLE user_beast (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    template_id INT NOT NULL,
    nickname VARCHAR(50) DEFAULT '',
    level INT NOT NULL DEFAULT 1,
    exp INT NOT NULL DEFAULT 0,
    is_main TINYINT(1) NOT NULL DEFAULT 0,
    attack_type VARCHAR(20) DEFAULT '',
    realm VARCHAR(20) DEFAULT '',
    hp_aptitude INT NOT NULL DEFAULT 0,
    speed_aptitude INT NOT NULL DEFAULT 0,
    physical_atk_aptitude INT NOT NULL DEFAULT 0,
    magic_atk_aptitude INT NOT NULL DEFAULT 0,
    physical_def_aptitude INT NOT NULL DEFAULT 0,
    magic_def_aptitude INT NOT NULL DEFAULT 0,
    skills JSON NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

注意：
- 若实际表名或字段名不同，请相应调整 SQL 和本文件中的列名。
"""

from typing import List, Optional
import json

from domain.entities.beast import Beast
from domain.repositories.beast_repo import IBeastRepo
from infrastructure.db.connection import execute_query, execute_update, execute_insert


class MySQLBeastRepo(IBeastRepo):
    """使用 user_beast 表持久化 Beast 实例的仓库实现。"""

    TABLE_NAME = "user_beast"

    # ------------- 读取 -------------

    def get_by_user_id(self, user_id: int) -> List[Beast]:
        sql = f"SELECT * FROM {self.TABLE_NAME} WHERE user_id = %s ORDER BY id"
        rows = execute_query(sql, (user_id,))
        return [self._row_to_beast(row) for row in rows]

    def get_by_id(self, beast_id: int) -> Optional[Beast]:
        sql = f"SELECT * FROM {self.TABLE_NAME} WHERE id = %s"
        rows = execute_query(sql, (beast_id,))
        if rows:
            return self._row_to_beast(rows[0])
        return None

    def get_main_beast(self, user_id: int) -> Optional[Beast]:
        sql = f"SELECT * FROM {self.TABLE_NAME} WHERE user_id = %s AND is_main = 1 LIMIT 1"
        rows = execute_query(sql, (user_id,))
        if rows:
            return self._row_to_beast(rows[0])
        return None

    # ------------- 写入 / 更新 -------------

    def save(self, beast: Beast) -> None:
        """插入或更新一只幻兽。"""
        if beast.id is None:
            # 插入
            sql = f"""
                INSERT INTO {self.TABLE_NAME} (
                    user_id, template_id, nickname,
                    level, exp, is_main,
                    attack_type, realm,
                    hp_aptitude, speed_aptitude,
                    physical_atk_aptitude, magic_atk_aptitude,
                    physical_def_aptitude, magic_def_aptitude,
                    skills
                ) VALUES (
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s,
                    %s, %s,
                    %s, %s,
                    %s, %s,
                    %s
                )
            """
            skills_json = json.dumps(beast.skills or [], ensure_ascii=False)
            new_id = execute_insert(sql, (
                beast.user_id,
                beast.template_id,
                beast.nickname or "",
                beast.level,
                beast.exp,
                1 if beast.is_main else 0,
                beast.attack_type or "",
                beast.realm or "",
                beast.hp_aptitude,
                beast.speed_aptitude,
                beast.physical_atk_aptitude,
                beast.magic_atk_aptitude,
                beast.physical_def_aptitude,
                beast.magic_def_aptitude,
                skills_json,
            ))
            beast.id = new_id
        else:
            # 更新
            sql = f"""
                UPDATE {self.TABLE_NAME} SET
                    user_id = %s,
                    template_id = %s,
                    nickname = %s,
                    level = %s,
                    exp = %s,
                    is_main = %s,
                    attack_type = %s,
                    realm = %s,
                    hp_aptitude = %s,
                    speed_aptitude = %s,
                    physical_atk_aptitude = %s,
                    magic_atk_aptitude = %s,
                    physical_def_aptitude = %s,
                    magic_def_aptitude = %s,
                    skills = %s
                WHERE id = %s
            """
            skills_json = json.dumps(beast.skills or [], ensure_ascii=False)
            execute_update(sql, (
                beast.user_id,
                beast.template_id,
                beast.nickname or "",
                beast.level,
                beast.exp,
                1 if beast.is_main else 0,
                beast.attack_type or "",
                beast.realm or "",
                beast.hp_aptitude,
                beast.speed_aptitude,
                beast.physical_atk_aptitude,
                beast.magic_atk_aptitude,
                beast.physical_def_aptitude,
                beast.magic_def_aptitude,
                skills_json,
                beast.id,
            ))

    def delete(self, beast_id: int) -> None:
        sql = f"DELETE FROM {self.TABLE_NAME} WHERE id = %s"
        execute_update(sql, (beast_id,))

    # ------------- 工具方法 -------------

    def _row_to_beast(self, row: dict) -> Beast:
        """将一行数据库记录转换为 Beast 实例。"""
        # skills 存的是 JSON 字符串
        raw_skills = row.get("skills")
        if isinstance(raw_skills, str):
            try:
                skills = json.loads(raw_skills)
            except Exception:
                skills = []
        else:
            skills = raw_skills or []

        return Beast(
            id=row.get("id"),
            user_id=row.get("user_id", 0),
            template_id=row.get("template_id", 0),
            nickname=row.get("nickname", ""),
            level=row.get("level", 1),
            exp=row.get("exp", 0),
            is_main=bool(row.get("is_main", 0)),
            attack_type=row.get("attack_type", ""),
            realm=row.get("realm", ""),
            hp_aptitude=row.get("hp_aptitude", 0),
            speed_aptitude=row.get("speed_aptitude", 0),
            physical_atk_aptitude=row.get("physical_atk_aptitude", 0),
            magic_atk_aptitude=row.get("magic_atk_aptitude", 0),
            physical_def_aptitude=row.get("physical_def_aptitude", 0),
            magic_def_aptitude=row.get("magic_def_aptitude", 0),
            skills=skills,
        )
