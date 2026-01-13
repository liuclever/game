"""
魔魂仓库 - MySQL实现
"""
from typing import List, Optional, Dict
from infrastructure.db.connection import get_connection
from domain.entities.mosoul import MoSoul, MoSoulGrade, BeastMoSoulSlot, SoulStorage, HuntingState, GlobalPityCounter
from domain.repositories.mosoul_repo import IMoSoulRepo, ISoulStorageRepo, IBeastMoSoulRepo, IHuntingStateRepo, IGlobalPityRepo


def get_mosoul_by_id(mosoul_id: int) -> Optional[Dict]:
    """根据ID获取魔魂"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM player_mosoul WHERE id = %s",
                (mosoul_id,)
            )
            return cursor.fetchone()
    finally:
        conn.close()


def get_mosouls_by_user(user_id: int) -> List[Dict]:
    """获取玩家所有魔魂"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM player_mosoul WHERE user_id = %s ORDER BY id",
                (user_id,)
            )
            return cursor.fetchall()
    finally:
        conn.close()


def get_mosouls_by_beast(beast_id: int) -> List[Dict]:
    """获取幻兽已装备的魔魂"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM player_mosoul WHERE beast_id = %s ORDER BY id",
                (beast_id,)
            )
            return cursor.fetchall()
    finally:
        conn.close()


def get_unequipped_mosouls(user_id: int) -> List[Dict]:
    """获取玩家未装备的魔魂（储魂器中的）"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM player_mosoul WHERE user_id = %s AND beast_id IS NULL ORDER BY id",
                (user_id,)
            )
            return cursor.fetchall()
    finally:
        conn.close()


def create_mosoul(user_id: int, template_id: int, level: int = 1, exp: int = 0) -> int:
    """创建魔魂，返回新魔魂ID"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """INSERT INTO player_mosoul (user_id, template_id, level, exp)
                   VALUES (%s, %s, %s, %s)""",
                (user_id, template_id, level, exp)
            )
            conn.commit()
            return cursor.lastrowid
    finally:
        conn.close()


_UNSET = object()  # 用于区分"未传参"和"传了None"

def update_mosoul(mosoul_id: int, level: int = None, exp: int = None, beast_id = _UNSET) -> bool:
    """更新魔魂信息
    
    beast_id: 传入None表示清除装备状态，不传表示不更新
    """
    updates = []
    params = []
    
    if level is not None:
        updates.append("level = %s")
        params.append(level)
    if exp is not None:
        updates.append("exp = %s")
        params.append(exp)
    if beast_id is not _UNSET:
        # 显式传入了beast_id（包括None）
        updates.append("beast_id = %s")
        params.append(beast_id)
    
    if not updates:
        return False
    
    params.append(mosoul_id)
    
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f"UPDATE player_mosoul SET {', '.join(updates)} WHERE id = %s",
                tuple(params)
            )
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()


def equip_mosoul(mosoul_id: int, beast_id: int) -> bool:
    """装备魔魂到幻兽"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE player_mosoul SET beast_id = %s WHERE id = %s",
                (beast_id, mosoul_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()


def equip_mosoul_with_slot(mosoul_id: int, beast_id: int, slot_index: int) -> bool:
    """装备魔魂到幻兽指定槽位"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE player_mosoul SET beast_id = %s, slot_index = %s WHERE id = %s",
                (beast_id, slot_index, mosoul_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()


def unequip_mosoul(mosoul_id: int) -> bool:
    """卸下魔魂"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE player_mosoul SET beast_id = NULL, slot_index = NULL WHERE id = %s",
                (mosoul_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()


def delete_mosoul(mosoul_id: int) -> bool:
    """删除魔魂"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM player_mosoul WHERE id = %s",
                (mosoul_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()


def count_beast_mosouls(beast_id: int) -> int:
    """统计幻兽已装备的魔魂数量"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) as count FROM player_mosoul WHERE beast_id = %s",
                (beast_id,)
            )
            result = cursor.fetchone()
            return result['count'] if result else 0
    finally:
        conn.close()


class MySQLMoSoulRepo(IMoSoulRepo):
    """魔魂实例仓库"""

    def _row_to_entity(self, row: Dict) -> MoSoul:
        return MoSoul(
            id=row['id'],
            user_id=row['user_id'],
            template_id=row['template_id'],
            level=row['level'],
            exp=row['exp'],
            beast_id=row['beast_id']
        )

    def get_by_id(self, soul_id: int) -> Optional[MoSoul]:
        row = get_mosoul_by_id(soul_id)
        return self._row_to_entity(row) if row else None

    def get_by_user_id(self, user_id: int) -> List[MoSoul]:
        rows = get_mosouls_by_user(user_id)
        return [self._row_to_entity(row) for row in rows]

    def get_equipped_by_beast_id(self, beast_id: int) -> List[MoSoul]:
        rows = get_mosouls_by_beast(beast_id)
        return [self._row_to_entity(row) for row in rows]

    def save(self, soul: MoSoul) -> MoSoul:
        if soul.id:
            update_mosoul(soul.id, soul.level, soul.exp, soul.beast_id)
        else:
            soul.id = create_mosoul(soul.user_id, soul.template_id, soul.level, soul.exp)
        return soul

    def delete(self, soul_id: int) -> None:
        delete_mosoul(soul_id)

    def delete_batch(self, soul_ids: List[int]) -> None:
        if not soul_ids:
            return
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                format_strings = ','.join(['%s'] * len(soul_ids))
                cursor.execute(
                    f"DELETE FROM player_mosoul WHERE id IN ({format_strings})",
                    tuple(soul_ids)
                )
                conn.commit()
        finally:
            conn.close()


class MySQLBeastMoSoulRepo(IBeastMoSoulRepo):
    """幻兽魔魂装备仓库"""

    def __init__(self, mosoul_repo: IMoSoulRepo = None):
        self.mosoul_repo = mosoul_repo or MySQLMoSoulRepo()

    def get_by_beast_id(self, beast_id: int) -> Optional[BeastMoSoulSlot]:
        equipped_souls = self.mosoul_repo.get_equipped_by_beast_id(beast_id)
        # 获取幻兽等级
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT level FROM player_beast WHERE id = %s", (beast_id,))
                row = cursor.fetchone()
                level = row['level'] if row else 1
        finally:
            conn.close()
        
        return BeastMoSoulSlot(
            beast_id=beast_id,
            beast_level=level,
            equipped_souls=equipped_souls
        )

    def get_by_user_id(self, user_id: int) -> List[BeastMoSoulSlot]:
        # 获取该玩家所有幻兽ID
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM player_beast WHERE user_id = %s", (user_id,))
                rows = cursor.fetchall()
                beast_ids = [row['id'] for row in rows]
        finally:
            conn.close()
        
        return [self.get_by_beast_id(bid) for bid in beast_ids]

    def save(self, slot: BeastMoSoulSlot) -> None:
        # 其实装备信息是存在 player_mosoul 表的 beast_id 字段
        # 这里我们同步保存所有装备的魔魂
        for soul in slot.equipped_souls:
            self.mosoul_repo.save(soul)

    def equip_soul(self, beast_id: int, soul_id: int) -> bool:
        return equip_mosoul(soul_id, beast_id)

    def unequip_soul(self, beast_id: int, soul_id: int) -> bool:
        return unequip_mosoul(soul_id)


class MySQLSoulStorageRepo(ISoulStorageRepo):
    """储魂器仓库实现"""

    def __init__(self, mosoul_repo: IMoSoulRepo = None):
        self.mosoul_repo = mosoul_repo or MySQLMoSoulRepo()

    def get_by_user_id(self, user_id: int) -> Optional[SoulStorage]:
        # 获取玩家VIP等级（用于计算容量）
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT vip_level FROM player WHERE user_id = %s", (user_id,))
                row = cursor.fetchone()
                vip_level = row['vip_level'] if row else 0
        finally:
            conn.close()

        # 获取未装备的魔魂
        souls = self.mosoul_repo.get_by_user_id(user_id)
        storage_souls = [s for s in souls if s.beast_id is None]

        return SoulStorage(
            user_id=user_id,
            vip_level=vip_level,
            souls=storage_souls
        )

    def save(self, storage: SoulStorage) -> None:
        # 储魂器状态主要由魔魂实例的 beast_id 决定
        for soul in storage.souls:
            self.mosoul_repo.save(soul)

    def get_soul_count(self, user_id: int) -> int:
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) as count FROM player_mosoul WHERE user_id = %s AND beast_id IS NULL",
                    (user_id,)
                )
                row = cursor.fetchone()
                return row['count'] if row else 0
        finally:
            conn.close()


class MySQLHuntingStateRepo(IHuntingStateRepo):
    """猎魂状态仓库实现"""

    def get_by_user_id(self, user_id: int) -> Optional[HuntingState]:
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM mosoul_hunting_state WHERE user_id = %s", (user_id,))
                row = cursor.fetchone()
                if not row:
                    return HuntingState(user_id=user_id)

                import json
                state = HuntingState(
                    user_id=user_id,
                    field_type=row['field_type'],
                    normal_available_npcs=json.loads(row['normal_available_npcs']),
                    advanced_available_npcs=json.loads(row['advanced_available_npcs']),
                    soul_charm_consumed=row.get('soul_charm_consumed', 0),
                    copper_consumed=row.get('copper_consumed', 0)
                )
                return state
        finally:
            conn.close()

    def save(self, state: HuntingState) -> None:
        conn = get_connection()
        import json
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO mosoul_hunting_state 
                       (user_id, field_type, normal_available_npcs, advanced_available_npcs, soul_charm_consumed, copper_consumed)
                       VALUES (%s, %s, %s, %s, %s, %s)
                       ON DUPLICATE KEY UPDATE 
                       field_type = VALUES(field_type),
                       normal_available_npcs = VALUES(normal_available_npcs),
                       advanced_available_npcs = VALUES(advanced_available_npcs),
                       soul_charm_consumed = VALUES(soul_charm_consumed),
                       copper_consumed = VALUES(copper_consumed)""",
                    (
                        state.user_id,
                        state.field_type,
                        json.dumps(state.normal_available_npcs),
                        json.dumps(state.advanced_available_npcs),
                        state.soul_charm_consumed,
                        state.copper_consumed
                    )
                )
                conn.commit()
        finally:
            conn.close()

    def reset(self, user_id: int, field_type: str = "normal") -> None:
        state = self.get_by_user_id(user_id)
        if field_type == "normal":
            state.reset_normal_field()
        else:
            state.reset_advanced_field()
        self.save(state)


class MySQLGlobalPityRepo(IGlobalPityRepo):
    """全服保底仓库实现"""

    def get(self, counter_key: str = "kevin_adv_pity") -> GlobalPityCounter:
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM mosoul_global_pity WHERE counter_key = %s", (counter_key,))
                row = cursor.fetchone()
                if not row:
                    return GlobalPityCounter(counter_key=counter_key)

                return GlobalPityCounter(
                    counter_key=row['counter_key'],
                    count=row['count'],
                    pity_threshold=row['pity_threshold'],
                    soul_charm_consumed_global=row.get('soul_charm_consumed_global', 0)
                )
        finally:
            conn.close()

    def increment(self, counter_key: str = "kevin_adv_pity") -> bool:
        # 这个方法现在不直接用了，改为在业务层计算后保存
        state = self.get(counter_key)
        triggered = state.increment()
        self.save(state)
        return triggered

    def save(self, counter: GlobalPityCounter) -> None:
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO mosoul_global_pity (counter_key, count, pity_threshold, soul_charm_consumed_global)
                       VALUES (%s, %s, %s, %s)
                       ON DUPLICATE KEY UPDATE 
                       count = VALUES(count),
                       pity_threshold = VALUES(pity_threshold),
                       soul_charm_consumed_global = VALUES(soul_charm_consumed_global)""",
                    (counter.counter_key, counter.count, counter.pity_threshold, counter.soul_charm_consumed_global)
                )
                conn.commit()
        finally:
            conn.close()

    def reset(self, counter_key: str = "kevin_adv_pity") -> None:
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE mosoul_global_pity SET count = 0, soul_charm_consumed_global = 0 WHERE counter_key = %s",
                    (counter_key,)
                )
                conn.commit()
        finally:
            conn.close()
