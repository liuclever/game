"""
MySQL版玩家仓库
"""
from typing import List, Optional
from datetime import datetime, timedelta
from domain.entities.player import Player, ZhenyaoFloor
from domain.repositories.player_repo import IPlayerRepo, IZhenyaoRepo
from infrastructure.db.connection import execute_query, execute_update, execute_insert


class MySQLPlayerRepo(IPlayerRepo):
    """MySQL版玩家存储"""
    
    def get_by_id(self, user_id: int) -> Optional[Player]:
        """获取玩家信息"""
        sql = """
            SELECT user_id, username, nickname, level, exp, gold, silver_diamond, yuanbao, dice, 
                   enhancement_stone, energy, prestige, crystal_tower, charm, location, 
                   vip_level, vip_exp, last_energy_recovery_time, last_signin_date, 
                   consecutive_signin_days, created_at, updated_at,
                   cultivation_start_time, cultivation_duration, cultivation_area, cultivation_dungeon
            FROM player WHERE user_id = %s
        """
        rows = execute_query(sql, (user_id,))
        if rows:
            row = rows[0]
            return Player(
                user_id=row['user_id'],
                username=row.get('username') or "",
                nickname=row.get('nickname') or "",
                level=row.get('level') or 1,
                exp=row.get('exp') or 0,
                gold=row.get('gold') or 0,
                copper=row.get('gold') or 0,  # copper 映射到 gold
                silver_diamond=row.get('silver_diamond') or 0,
                yuanbao=row.get('yuanbao') or 0,
                dice=row.get('dice') or 0,
                enhancement_stone=row.get('enhancement_stone') or 0,
                energy=row.get('energy') or 0,
                prestige=row.get('prestige') or 0,
                crystal_tower=row.get('crystal_tower') or 0,
                charm=row.get('charm') or 0,
                location=row.get('location') or "落龙镇",
                vip_level=row.get('vip_level') or 0,
                vip_exp=row.get('vip_exp') or 0,
                last_energy_recovery_time=row.get('last_energy_recovery_time'),
                last_signin_date=row.get('last_signin_date'),
                signin_streak=int(row.get('consecutive_signin_days') or 0),
                created_at=row.get('created_at'),
                updated_at=row.get('updated_at'),
                cultivation_start_time=row.get('cultivation_start_time'),
                cultivation_duration=row.get('cultivation_duration'),
                cultivation_area=row.get('cultivation_area'),
                cultivation_dungeon=row.get('cultivation_dungeon'),
            )
        return None
    
    def get_by_username(self, username: str) -> Optional[Player]:
        """根据账号获取玩家"""
        sql = """
            SELECT user_id, username, nickname, level, exp, gold, silver_diamond, yuanbao, dice, 
                   enhancement_stone, energy, prestige, crystal_tower, charm, location, 
                   vip_level, vip_exp, last_energy_recovery_time, last_signin_date, 
                   consecutive_signin_days, created_at, updated_at,
                   cultivation_start_time, cultivation_duration, cultivation_area, cultivation_dungeon
            FROM player WHERE username = %s
        """
        rows = execute_query(sql, (username,))
        if rows:
            row = rows[0]
            return Player(
                user_id=row['user_id'],
                username=row.get('username') or "",
                nickname=row.get('nickname') or "",
                level=row.get('level') or 1,
                exp=row.get('exp') or 0,
                gold=row.get('gold') or 0,
                copper=row.get('gold') or 0,
                silver_diamond=row.get('silver_diamond') or 0,
                yuanbao=row.get('yuanbao') or 0,
                dice=row.get('dice') or 0,
                enhancement_stone=row.get('enhancement_stone') or 0,
                energy=row.get('energy') or 0,
                prestige=row.get('prestige') or 0,
                crystal_tower=row.get('crystal_tower') or 0,
                charm=row.get('charm') or 0,
                location=row.get('location') or "落龙镇",
                vip_level=row.get('vip_level') or 0,
                vip_exp=row.get('vip_exp') or 0,
                last_energy_recovery_time=row.get('last_energy_recovery_time'),
                last_signin_date=row.get('last_signin_date'),
                signin_streak=int(row.get('consecutive_signin_days') or 0),
                created_at=row.get('created_at'),
                updated_at=row.get('updated_at'),
                cultivation_start_time=row.get('cultivation_start_time'),
                cultivation_duration=row.get('cultivation_duration'),
                cultivation_area=row.get('cultivation_area'),
                cultivation_dungeon=row.get('cultivation_dungeon'),
            )
        return None
    
    def verify_login(self, username: str, password: str) -> Optional[Player]:
        """验证登录"""
        sql = """
            SELECT user_id, username, nickname, level, exp, gold, silver_diamond, yuanbao, dice, 
                   enhancement_stone, energy, prestige, crystal_tower, charm, location, 
                   vip_level, vip_exp, last_energy_recovery_time, last_signin_date, 
                   consecutive_signin_days, created_at, updated_at,
                   cultivation_start_time, cultivation_duration, cultivation_area, cultivation_dungeon
            FROM player WHERE username = %s AND password = %s
        """
        rows = execute_query(sql, (username, password))
        if rows:
            row = rows[0]
            return Player(
                user_id=row['user_id'],
                username=row.get('username') or "",
                nickname=row.get('nickname') or "",
                level=row.get('level') or 1,
                exp=row.get('exp') or 0,
                gold=row.get('gold') or 0,
                copper=row.get('gold') or 0,
                silver_diamond=row.get('silver_diamond') or 0,
                yuanbao=row.get('yuanbao') or 0,
                dice=row.get('dice') or 0,
                enhancement_stone=row.get('enhancement_stone') or 0,
                energy=row.get('energy') or 0,
                prestige=row.get('prestige') or 0,
                crystal_tower=row.get('crystal_tower') or 0,
                charm=row.get('charm') or 0,
                location=row.get('location') or "落龙镇",
                vip_level=row.get('vip_level') or 0,
                vip_exp=row.get('vip_exp') or 0,
                last_energy_recovery_time=row.get('last_energy_recovery_time'),
                last_signin_date=row.get('last_signin_date'),
                signin_streak=int(row.get('consecutive_signin_days') or 0),
                created_at=row.get('created_at'),
                updated_at=row.get('updated_at'),
                cultivation_start_time=row.get('cultivation_start_time'),
                cultivation_duration=row.get('cultivation_duration'),
                cultivation_area=row.get('cultivation_area'),
                cultivation_dungeon=row.get('cultivation_dungeon'),
            )
        return None
    
    def save(self, player: Player) -> None:
        """保存玩家信息"""
        # 获取保存前的等级，用于检查是否升级
        old_level = None
        try:
            old_player = self.get_by_id(player.user_id)
            if old_player:
                old_level = old_player.level
        except Exception:
            pass  # 如果获取失败，忽略，不影响保存
        
        # 兼容老库：last_signin_date / consecutive_signin_days 字段可能不存在
        sql = """
            UPDATE player 
            SET nickname = %s, level = %s, exp = %s, gold = %s, silver_diamond = %s, 
                yuanbao = %s, dice = %s, enhancement_stone = %s, energy = %s, 
                prestige = %s, crystal_tower = %s, charm = %s, location = %s, 
                vip_level = %s, vip_exp = %s, last_energy_recovery_time = %s, 
                last_signin_date = %s, consecutive_signin_days = %s,
                cultivation_start_time = %s, cultivation_duration = %s, 
                cultivation_area = %s, cultivation_dungeon = %s
            WHERE user_id = %s
        """
        params = (
            player.nickname, player.level, player.exp, player.gold, player.silver_diamond,
            player.yuanbao, player.dice, player.enhancement_stone, player.energy,
            player.prestige, player.crystal_tower, player.charm, player.location,
            player.vip_level, player.vip_exp, player.last_energy_recovery_time,
            getattr(player, "last_signin_date", None),
            int(getattr(player, "signin_streak", 0) or 0),
            player.cultivation_start_time, player.cultivation_duration,
            player.cultivation_area, player.cultivation_dungeon,
            player.user_id
        )
        saved = False
        try:
            execute_update(sql, params)
            saved = True
        except Exception:
            # 再兜底：可能既没有 last_signin_date，也没有 copper
            sql = """
                UPDATE player 
                SET nickname = %s, level = %s, exp = %s, gold = %s, copper = %s, silver_diamond = %s, yuanbao = %s, dice = %s, enhancement_stone = %s, energy = %s, prestige = %s, crystal_tower = %s, charm = %s, location = %s, vip_level = %s, vip_exp = %s, last_energy_recovery_time = %s,
                    cultivation_start_time = %s, cultivation_duration = %s, cultivation_area = %s, cultivation_dungeon = %s
                WHERE user_id = %s
            """
            params = (
                player.nickname, player.level, player.exp, player.gold, player.copper, player.silver_diamond, player.yuanbao, player.dice, player.enhancement_stone,
                player.energy, player.prestige, player.crystal_tower, player.charm, player.location, player.vip_level, player.vip_exp, player.last_energy_recovery_time,
                player.cultivation_start_time, player.cultivation_duration, player.cultivation_area, player.cultivation_dungeon,
                player.user_id
            )
            try:
                execute_update(sql, params)
                saved = True
            except Exception:
                sql = """
                    UPDATE player 
                    SET nickname = %s, level = %s, exp = %s, gold = %s, silver_diamond = %s, yuanbao = %s, dice = %s, enhancement_stone = %s, energy = %s, prestige = %s, crystal_tower = %s, charm = %s, location = %s, vip_level = %s, vip_exp = %s, last_energy_recovery_time = %s,
                        cultivation_start_time = %s, cultivation_duration = %s, cultivation_area = %s, cultivation_dungeon = %s
                    WHERE user_id = %s
                """
                params = (
                    player.nickname, player.level, player.exp, player.gold, player.silver_diamond, player.yuanbao, player.dice, player.enhancement_stone,
                    player.energy, player.prestige, player.crystal_tower, player.charm, player.location, player.vip_level, player.vip_exp, player.last_energy_recovery_time,
                    player.cultivation_start_time, player.cultivation_duration, player.cultivation_area, player.cultivation_dungeon,
                    player.user_id
                )
                execute_update(sql, params)
                saved = True
        
        # 如果保存成功且等级发生变化，同步联盟军队类型
        if saved and old_level is not None and player.level is not None and old_level != player.level:
            self._sync_alliance_army_on_level_change(player.user_id, old_level, player.level)
    
    def _sync_alliance_army_on_level_change(self, user_id: int, old_level: int, new_level: int) -> None:
        """当玩家等级变化时，同步联盟军队类型"""
        # 使用延迟导入避免循环依赖
        try:
            # 检查是否需要重新分配军队（40级及以下伏虎军，40级以上飞龙军）
            old_army_type = 1 if old_level > 40 else 2  # 1=飞龙军, 2=伏虎军
            new_army_type = 1 if new_level > 40 else 2
            
            # 如果军队类型发生变化，同步到数据库
            if old_army_type != new_army_type:
                # 延迟导入 services 避免循环依赖
                import sys
                from pathlib import Path
                project_root = Path(__file__).resolve().parent.parent.parent
                if str(project_root) not in sys.path:
                    sys.path.insert(0, str(project_root))
                
                from interfaces.web_api.bootstrap import services
                # 调用联盟服务的同步方法
                services.alliance_service.sync_member_army_by_user_id(user_id)
        except Exception:
            # 如果同步失败，不影响玩家保存，只记录错误
            pass
    
    def create(self, player: Player) -> None:
        """创建新玩家"""
        sql = """
            INSERT INTO player (user_id, nickname, level, exp, gold, silver_diamond, yuanbao, dice, location, vip_level, vip_exp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        execute_insert(sql, (
            player.user_id, player.nickname, player.level, player.exp, player.gold, 
            player.silver_diamond, player.yuanbao, player.dice,
            player.location, player.vip_level, player.vip_exp
        ))
    
    def create_with_auth(self, username: str, password: str, player: Player) -> Optional[int]:
        """创建带账号密码的新玩家，返回user_id"""
        sql = """
            INSERT INTO player (username, password, nickname, level, exp, gold, silver_diamond, location, vip_level, vip_exp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        user_id = execute_insert(sql, (
            username, password, player.nickname, player.level, player.exp, player.gold, 
            player.silver_diamond, player.location, player.vip_level, player.vip_exp
        ))
        return user_id


class MySQLZhenyaoRepo(IZhenyaoRepo):
    """MySQL版镇妖存储"""

    def _ensure_floors_exist(self, floors: List[int]) -> None:
        if not floors:
            return
        sql = (
            "INSERT IGNORE INTO zhenyao_floor "
            "(floor, occupant_id, occupant_name, occupy_time, expire_time, rewarded) "
            "VALUES (%s, NULL, '', NULL, NULL, 0)"
        )
        for f in floors:
            try:
                execute_insert(sql, (int(f),))
            except Exception:
                pass
    
    def get_floor(self, floor: int) -> Optional[ZhenyaoFloor]:
        """获取某层信息"""
        self._ensure_floors_exist([floor])
        sql = """
            SELECT id, floor, occupant_id, occupant_name, occupy_time, expire_time, rewarded
            FROM zhenyao_floor WHERE floor = %s
        """
        rows = execute_query(sql, (floor,))
        if rows:
            row = rows[0]
            return ZhenyaoFloor(
                id=row['id'],
                floor=row['floor'],
                occupant_id=row['occupant_id'],
                occupant_name=row['occupant_name'] or '',
                occupy_time=row.get('occupy_time'),
                expire_time=row.get('expire_time'),
                rewarded=bool(row.get('rewarded', 0)),
            )
        return None
    
    def get_floors_in_range(self, start: int, end: int) -> List[ZhenyaoFloor]:
        """获取指定范围的层信息"""
        if start <= end:
            self._ensure_floors_exist(list(range(int(start), int(end) + 1)))
        sql = """
            SELECT id, floor, occupant_id, occupant_name, occupy_time, expire_time, rewarded
            FROM zhenyao_floor 
            WHERE floor >= %s AND floor <= %s
            ORDER BY floor DESC
        """
        rows = execute_query(sql, (start, end))
        return [
            ZhenyaoFloor(
                id=row['id'],
                floor=row['floor'],
                occupant_id=row['occupant_id'],
                occupant_name=row['occupant_name'] or '',
                occupy_time=row.get('occupy_time'),
                expire_time=row.get('expire_time'),
                rewarded=bool(row.get('rewarded', 0)),
            )
            for row in rows
        ]
    
    def occupy_floor(self, floor: int, user_id: int, nickname: str, duration_minutes: int) -> bool:
        """占领某层"""
        self._ensure_floors_exist([floor])
        now = datetime.now()
        expire_time = now + timedelta(minutes=duration_minutes)
        sql = """
            UPDATE zhenyao_floor 
            SET occupant_id = %s, occupant_name = %s, occupy_time = %s, expire_time = %s, rewarded = 0
            WHERE floor = %s
        """
        affected = execute_update(sql, (user_id, nickname, now, expire_time, floor))
        return affected > 0
    
    def release_floor(self, floor: int) -> bool:
        """释放某层"""
        self._ensure_floors_exist([floor])
        sql = """
            UPDATE zhenyao_floor 
            SET occupant_id = NULL, occupant_name = '', occupy_time = NULL, expire_time = NULL, rewarded = 0
            WHERE floor = %s
        """
        affected = execute_update(sql, (floor,))
        return affected > 0
    
    def get_floors_by_occupant(self, user_id: int) -> List[ZhenyaoFloor]:
        """获取某玩家占领的所有层"""
        sql = """
            SELECT id, floor, occupant_id, occupant_name, occupy_time, expire_time, rewarded
            FROM zhenyao_floor 
            WHERE occupant_id = %s AND expire_time > NOW()
            ORDER BY floor DESC
        """
        rows = execute_query(sql, (user_id,))
        return [
            ZhenyaoFloor(
                id=row['id'],
                floor=row['floor'],
                occupant_id=row['occupant_id'],
                occupant_name=row['occupant_name'] or '',
                occupy_time=row.get('occupy_time'),
                expire_time=row.get('expire_time'),
                rewarded=bool(row.get('rewarded', 0)),
            )
            for row in rows
        ]

    def mark_floor_rewarded(self, floor: int) -> bool:
        """标记某层已发放奖励"""
        self._ensure_floors_exist([floor])
        sql = "UPDATE zhenyao_floor SET rewarded = 1 WHERE floor = %s"
        affected = execute_update(sql, (floor,))
        return affected > 0


# ========== 模块级便捷函数 ==========
_player_repo = MySQLPlayerRepo()


def get_player_by_id(user_id: int) -> Optional[dict]:
    """根据ID获取玩家，返回字典格式"""
    player = _player_repo.get_by_id(user_id)
    if player:
        return {
            'user_id': player.user_id,
            'username': player.username,
            'nickname': player.nickname,
            'level': player.level,
            'exp': player.exp,
            'gold': player.gold,
            'enhancement_stone': player.enhancement_stone,
            'vip_level': player.vip_level,
        }
    return None


def update_gold(user_id: int, delta: int) -> bool:
    """更新玩家铜钱（增加或减少）"""
    sql = "UPDATE player SET gold = gold + %s WHERE user_id = %s"
    affected = execute_update(sql, (delta, user_id))
    return affected > 0
