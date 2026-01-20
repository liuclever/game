"""
MySQL版玩家幻兽仓库
"""

from typing import List, Optional
import json

from infrastructure.db.connection import execute_query, execute_update, execute_insert


class PlayerBeastData:
    """玩家幻兽数据"""

    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 0)
        self.user_id = kwargs.get('user_id', 0)
        self.template_id = kwargs.get('template_id', 0)
        self.name = kwargs.get('name', '')
        self.nickname = kwargs.get('nickname', self.name)
        self.realm = kwargs.get('realm', '')
        self.race = kwargs.get('race', '')
        self.level = kwargs.get('level', 1)
        self.exp = kwargs.get('exp', 0)  # 当前经验
        self.nature = kwargs.get('nature', '物系')
        self.personality = kwargs.get('personality', '')
        self.hp = kwargs.get('hp', 0)
        self.physical_attack = kwargs.get('physical_attack', 0)
        self.magic_attack = kwargs.get('magic_attack', 0)
        self.physical_defense = kwargs.get('physical_defense', 0)
        self.magic_defense = kwargs.get('magic_defense', 0)
        self.speed = kwargs.get('speed', 0)
        self.combat_power = kwargs.get('combat_power', 0)
        self.growth_rate = kwargs.get('growth_rate', 0)
        self.hp_aptitude = kwargs.get('hp_aptitude', 0)
        self.speed_aptitude = kwargs.get('speed_aptitude', 0)

        # 资质兼容
        self.physical_atk_aptitude = kwargs.get('physical_atk_aptitude', kwargs.get('physical_attack_aptitude', 0))
        self.magic_atk_aptitude = kwargs.get('magic_atk_aptitude', kwargs.get('magic_attack_aptitude', 0))
        self.physical_def_aptitude = kwargs.get('physical_def_aptitude', kwargs.get('physical_defense_aptitude', 0))
        self.magic_def_aptitude = kwargs.get('magic_def_aptitude', kwargs.get('magic_defense_aptitude', 0))
        
        # 历史逻辑兼容
        self.physical_attack_aptitude = self.physical_atk_aptitude
        self.magic_attack_aptitude = self.magic_atk_aptitude
        self.physical_defense_aptitude = self.physical_def_aptitude
        self.magic_defense_aptitude = self.magic_def_aptitude

        self.lifespan = kwargs.get('lifespan', '10000/10000')
        self.counters = kwargs.get('counters', '')
        self.countered_by = kwargs.get('countered_by', '')
        self.is_in_team = kwargs.get('is_in_team', 0)
        self.is_main = kwargs.get('is_main', self.is_in_team)
        self.team_position = kwargs.get('team_position', 0)
        self.attack_type = kwargs.get('attack_type', 'physical')
        # 兼容历史值：magical 统一归一化为 magic
        if self.attack_type == 'magical':
            self.attack_type = 'magic'

        # 技能列表
        skills = kwargs.get('skills', '[]')
        if isinstance(skills, str):
            try:
                self.skills = json.loads(skills)
            except Exception:
                self.skills = []
        else:
            self.skills = skills or []

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'template_id': self.template_id,
            'name': self.name,
            'nickname': self.nickname,
            'realm': self.realm,
            'race': self.race,
            'level': self.level,
            'exp': self.exp,
            'nature': self.nature,
            'personality': self.personality,
            'hp': self.hp,
            'physical_attack': self.physical_attack,
            'magic_attack': self.magic_attack,
            'physical_defense': self.physical_defense,
            'magic_defense': self.magic_defense,
            'speed': self.speed,
            'combat_power': self.combat_power,
            'growth_rate': self.growth_rate,
            'hp_aptitude': self.hp_aptitude,
            'speed_aptitude': self.speed_aptitude,
            'physical_attack_aptitude': self.physical_attack_aptitude,
            'magic_attack_aptitude': self.magic_attack_aptitude,
            'physical_defense_aptitude': self.physical_defense_aptitude,
            'magic_defense_aptitude': self.magic_defense_aptitude,
            'lifespan': self.lifespan,
            'skills': self.skills,
            'counters': self.counters,
            'countered_by': self.countered_by,
            'is_main': self.is_main,
            'attack_type': self.attack_type,
        }

    def exp_to_next_level(self) -> int:
        """从当前等级升到下一等级所需经验。默认公式 level * 50"""
        return self.level * 50

    def add_exp(self, amount: int, max_level: Optional[int] = None) -> bool:
        """增加经验并处理升级（可选：限制最高等级）。

        - 当传入 max_level 时：幻兽等级最多升级到 max_level，达到后会将 exp 置 0（不保留溢出经验）。
        - 返回值：本次是否至少升级 1 级。
        """
        if amount <= 0:
            return False

        # 兜底：max_level 非法时当作不限制
        eff_max = None
        if max_level is not None:
            try:
                eff_max = int(max_level)
            except (TypeError, ValueError):
                eff_max = None
            if eff_max is not None and eff_max <= 0:
                eff_max = None

        self.exp += int(amount)
        leveled_up = False

        while True:
            # 到达上限：不再升级，经验清零（与旧逻辑保持一致：不允许囤经验越过上限）
            if eff_max is not None and int(self.level or 1) >= eff_max:
                self.level = eff_max
                self.exp = 0
                break

            need = int(self.exp_to_next_level() or 0)
            if need <= 0:
                break

            if int(self.exp or 0) < need:
                break

            self.exp -= need
            self.level += 1
            leveled_up = True

        return leveled_up


class MySQLPlayerBeastRepo:
    """MySQL版玩家幻兽仓库"""

    def get_team_beasts(self, user_id: int) -> List[PlayerBeastData]:
        """获取用户战斗队幻兽（按位置排序）"""
        sql = """
            SELECT * FROM player_beast
            WHERE user_id = %s AND is_in_team = 1
            ORDER BY team_position ASC
        """
        rows = execute_query(sql, (user_id,))
        return [PlayerBeastData(**row) for row in rows]

    def get_by_id(self, beast_id: int) -> Optional[PlayerBeastData]:
        """根据ID获取幻兽"""
        sql = "SELECT * FROM player_beast WHERE id = %s"
        rows = execute_query(sql, (beast_id,))
        if rows:
            return PlayerBeastData(**rows[0])
        return None

    def get_by_user_and_id(self, user_id: int, beast_id: int) -> Optional[PlayerBeastData]:
        """根据玩家和幻兽ID获取"""
        sql = "SELECT * FROM player_beast WHERE id = %s AND user_id = %s"
        rows = execute_query(sql, (beast_id, user_id))
        if rows:
            return PlayerBeastData(**rows[0])
        return None

    def get_all_by_user(self, user_id: int) -> List[PlayerBeastData]:
        """获取用户所有幻兽"""
        sql = "SELECT * FROM player_beast WHERE user_id = %s ORDER BY id"
        rows = execute_query(sql, (user_id,))
        return [PlayerBeastData(**row) for row in rows]

    def get_by_user_id(self, user_id: int) -> List[PlayerBeastData]:
        """获取用户所有幻兽（接口兼容）"""
        return self.get_all_by_user(user_id)

    def get_main_beast(self, user_id: int) -> Optional[PlayerBeastData]:
        """获取主幻兽（接口兼容）"""
        sql = "SELECT * FROM player_beast WHERE user_id = %s AND is_in_team = 1 LIMIT 1"
        rows = execute_query(sql, (user_id,))
        if rows:
            return PlayerBeastData(**rows[0])
        return None

    def update_beast(self, beast: PlayerBeastData) -> None:
        """更新幻兽数据"""
        sql = """
              UPDATE player_beast SET
                  level = %s, exp = %s, hp = %s, physical_attack = %s, magic_attack = %s,
                  physical_defense = %s, magic_defense = %s, speed = %s,
                  combat_power = %s, growth_rate = %s, is_in_team = %s, team_position = %s,
                  skills = %s, realm = %s, race = %s,
                  hp_aptitude = %s, speed_aptitude = %s,
                  physical_attack_aptitude = %s, magic_attack_aptitude = %s,
                  physical_defense_aptitude = %s, magic_defense_aptitude = %s,
                  template_id = %s, nickname = %s, attack_type = %s
              WHERE id = %s
        """

        # 属性名适配
        hp_apt = getattr(beast, "hp_aptitude", 0)
        speed_apt = getattr(beast, "speed_aptitude", 0)
        p_atk_apt = getattr(beast, "physical_atk_aptitude", getattr(beast, "physical_attack_aptitude", 0))
        m_atk_apt = getattr(beast, "magic_atk_aptitude", getattr(beast, "magic_attack_aptitude", 0))
        p_def_apt = getattr(beast, "physical_def_aptitude", getattr(beast, "physical_defense_aptitude", 0))
        m_def_apt = getattr(beast, "magic_def_aptitude", getattr(beast, "magic_defense_aptitude", 0))
        
        is_in_team = 1 if getattr(beast, "is_main", False) or getattr(beast, "is_in_team", 0) else 0
        nickname = getattr(beast, "nickname", getattr(beast, "name", ""))
        template_id = getattr(beast, "template_id", 0)
        attack_type = getattr(beast, "attack_type", "physical")
        if attack_type == "magical":
            attack_type = "magic"
        race = getattr(beast, "race", "")
        realm = getattr(beast, "realm", "")

        # 增加对基础属性的防御性获取，防止 domain Beast 对象缺少这些字段
        hp = getattr(beast, "hp", 0)
        p_attack = getattr(beast, "physical_attack", 0)
        m_attack = getattr(beast, "magic_attack", 0)
        p_def = getattr(beast, "physical_defense", 0)
        m_def = getattr(beast, "magic_defense", 0)
        speed = getattr(beast, "speed", 0)
        cp = getattr(beast, "combat_power", 0)
        gr = getattr(beast, "growth_rate", 0)

        skills_json = json.dumps(beast.skills or [], ensure_ascii=False)
        execute_update(
            sql,
            (
                beast.level, beast.exp, hp, p_attack, m_attack,
                p_def, m_def, speed,
                cp, gr, is_in_team, getattr(beast, "team_position", 0),
                skills_json,
                realm, race,
                hp_apt, speed_apt,
                p_atk_apt, m_atk_apt, p_def_apt, m_def_apt,
                template_id, nickname, attack_type,
                beast.id,
            ),
        )

    def create_beast(self, beast: PlayerBeastData) -> int:
        """创建新幻兽，返回新幻兽ID"""
        sql = """
            INSERT INTO player_beast (
                user_id, name, realm, race, level, exp, nature, personality,
                hp, physical_attack, magic_attack, physical_defense, magic_defense, speed,
                combat_power, growth_rate,
                hp_aptitude, speed_aptitude,
                physical_attack_aptitude, magic_attack_aptitude,
                physical_defense_aptitude, magic_defense_aptitude,
                lifespan, skills, counters, countered_by,
                is_in_team, team_position, template_id, nickname, attack_type
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s,
                %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s, %s
            )
        """

        # 属性名适配
        hp_apt = getattr(beast, "hp_aptitude", 0)
        speed_apt = getattr(beast, "speed_aptitude", 0)
        p_atk_apt = getattr(beast, "physical_atk_aptitude", getattr(beast, "physical_attack_aptitude", 0))
        m_atk_apt = getattr(beast, "magic_atk_aptitude", getattr(beast, "magic_attack_aptitude", 0))
        p_def_apt = getattr(beast, "physical_def_aptitude", getattr(beast, "physical_defense_aptitude", 0))
        m_def_apt = getattr(beast, "magic_def_aptitude", getattr(beast, "magic_defense_aptitude", 0))
        
        is_in_team = 1 if getattr(beast, "is_main", False) or getattr(beast, "is_in_team", 0) else 0
        nickname = getattr(beast, "nickname", getattr(beast, "name", ""))
        template_id = getattr(beast, "template_id", 0)
        attack_type = getattr(beast, "attack_type", "physical")
        if attack_type == "magical":
            attack_type = "magic"
        race = getattr(beast, "race", "")
        realm = getattr(beast, "realm", "")

        # 增加对基础属性的防御性获取，防止 domain Beast 对象缺少这些字段
        hp = getattr(beast, "hp", 0)
        p_attack = getattr(beast, "physical_attack", 0)
        m_attack = getattr(beast, "magic_attack", 0)
        p_def = getattr(beast, "physical_defense", 0)
        m_def = getattr(beast, "magic_defense", 0)
        speed = getattr(beast, "speed", 0)
        cp = getattr(beast, "combat_power", 0)
        gr = getattr(beast, "growth_rate", 0)
        pers = getattr(beast, "personality", "")

        skills_json = json.dumps(beast.skills or [], ensure_ascii=False)
        # 使用 nickname 作为 name 字段（Beast 领域实体只有 nickname）
        name = nickname or getattr(beast, "name", "")
        new_id = execute_insert(
            sql,
            (
                beast.user_id, name, realm, race, beast.level, beast.exp,
                getattr(beast, "nature", "物系"), pers,
                hp, p_attack, m_attack,
                p_def, m_def, speed,
                cp, gr,
                hp_apt, speed_apt,
                p_atk_apt, m_atk_apt, p_def_apt, m_def_apt,
                getattr(beast, "lifespan", "10000/10000"), skills_json, getattr(beast, "counters", ""), getattr(beast, "countered_by", ""),
                is_in_team, getattr(beast, "team_position", 0),
                template_id, nickname, attack_type
            ),
        )
        beast.id = new_id
        return new_id

    def count_by_user(self, user_id: int) -> int:
        """统计用户幻兽数量"""
        sql = "SELECT COUNT(*) as cnt FROM player_beast WHERE user_id = %s"
        rows = execute_query(sql, (user_id,))
        if rows:
            return rows[0].get('cnt', 0)
        return 0

    def delete_beast(self, beast_id: int, user_id: int) -> bool:
        """删除幻兽（放生）"""
        sql = "DELETE FROM player_beast WHERE id = %s AND user_id = %s"
        affected = execute_update(sql, (beast_id, user_id))
        return affected > 0

    def delete(self, beast_id: int) -> None:
        """删除幻兽（接口兼容）"""
        sql = "DELETE FROM player_beast WHERE id = %s"
        execute_update(sql, (beast_id,))

    def save(self, beast: PlayerBeastData) -> None:
        """保存（插入或更新）幻兽数据"""
        if getattr(beast, "id", None) is None:
            self.create_beast(beast)
        else:
            self.update_beast(beast)


# ========== 模块级便捷函数 ==========
_repo = MySQLPlayerBeastRepo()


def get_beast_by_id(beast_id: int) -> Optional[dict]:
    """根据ID获取幻兽，返回字典格式"""
    beast = _repo.get_by_id(beast_id)
    if beast:
        result = beast.to_dict()
        result['user_id'] = beast.user_id
        result['nickname'] = beast.nickname or beast.name  # 兼容 mosoul_routes 的字段
        return result
    return None


def get_beasts_by_user(user_id: int) -> List[dict]:
    """获取用户所有幻兽，返回字典列表"""
    beasts = _repo.get_all_by_user(user_id)
    result = []
    for beast in beasts:
        d = beast.to_dict()
        d['user_id'] = beast.user_id
        d['nickname'] = beast.nickname or beast.name
        result.append(d)
    return result
