import json
from datetime import datetime, date
from typing import List, Optional, Dict, Tuple
from domain.entities.alliance import (
    Alliance,
    AllianceMember,
    AllianceArmyAssignment,
    AllianceChatMessage,
    AllianceTalentResearch,
    PlayerTalentLevel,
    AllianceBeastStorage,
    AllianceItemStorage,
    AllianceTrainingRoom,
    AllianceTrainingParticipant,
    AllianceActivity,
    AllianceBuilding,
)
from domain.entities.alliance_registration import AllianceRegistration
from domain.entities.alliance_battle import (
    AllianceArmySignup,
    AllianceLandBattle,
    AllianceLandBattleRound,
    AllianceLandBattleDuel,
)
from domain.repositories.alliance_repo import IAllianceRepo
from infrastructure.db.connection import execute_query, execute_update, execute_insert

class MySQLAllianceRepo(IAllianceRepo):
    def create_alliance(self, alliance: Alliance) -> int:
        sql = """
            INSERT INTO alliances (
                name,
                leader_id,
                level,
                exp,
                funds,
                crystals,
                prosperity,
                war_honor,
                war_honor_history,
                notice
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        return execute_insert(sql, (
            alliance.name,
            alliance.leader_id,
            alliance.level,
            alliance.exp,
            alliance.funds,
            alliance.crystals,
            alliance.prosperity,
            getattr(alliance, "war_honor", 0),
            getattr(alliance, "war_honor_history", 0),
            alliance.notice
        ))

    def get_alliance_by_id(self, alliance_id: int) -> Optional[Alliance]:
        sql = "SELECT * FROM alliances WHERE id = %s"
        rows = execute_query(sql, (alliance_id,))
        if not rows:
            return None
        return self._map_row_to_alliance(rows[0])

    def get_alliance_by_name(self, name: str) -> Optional[Alliance]:
        sql = "SELECT * FROM alliances WHERE name = %s"
        rows = execute_query(sql, (name,))
        if not rows:
            return None
        return self._map_row_to_alliance(rows[0])

    def list_alliances(self, keyword: Optional[str], limit: int, offset: int) -> List[Dict]:
        kw = (keyword or "").strip()
        where_sql = ""
        params: Tuple = ()
        if kw:
            where_sql = "WHERE a.name LIKE %s"
            params = (f"%{kw}%",)

        sql = f"""
            SELECT
                a.id,
                a.name,
                a.level,
                a.notice,
                a.leader_id,
                COALESCE(m.member_count, 0) AS member_count
            FROM alliances a
            LEFT JOIN (
                SELECT alliance_id, COUNT(1) AS member_count
                FROM alliance_members
                GROUP BY alliance_id
            ) m ON m.alliance_id = a.id
            {where_sql}
            ORDER BY a.level DESC, a.id DESC
            LIMIT %s OFFSET %s
        """
        rows = execute_query(sql, params + (int(limit), int(offset)))
        return list(rows or [])

    def count_alliances(self, keyword: Optional[str]) -> int:
        kw = (keyword or "").strip()
        if kw:
            rows = execute_query("SELECT COUNT(1) AS cnt FROM alliances WHERE name LIKE %s", (f"%{kw}%",))
        else:
            rows = execute_query("SELECT COUNT(1) AS cnt FROM alliances", ())
        if not rows:
            return 0
        return int(rows[0].get("cnt", 0) or 0)

    def count_members(self, alliance_id: int) -> int:
        rows = execute_query("SELECT COUNT(1) AS cnt FROM alliance_members WHERE alliance_id = %s", (alliance_id,))
        if not rows:
            return 0
        return int(rows[0].get("cnt", 0) or 0)

    def add_member(self, member: AllianceMember) -> None:
        # 重要：添加成员时，如果 total_contribution 未设置，使用 contribution 作为初始值
        # 但如果成员已存在，不要覆盖 total_contribution（保护历史总贡献点）
        sql = """
            INSERT INTO alliance_members (alliance_id, user_id, role, contribution, total_contribution)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                alliance_id = VALUES(alliance_id), 
                role = VALUES(role),
                contribution = VALUES(contribution)
                -- 注意：不更新 total_contribution，保护历史总贡献点不被覆盖
        """
        execute_update(sql, (
            member.alliance_id,
            member.user_id,
            member.role,
            member.contribution,
            getattr(member, 'total_contribution', member.contribution)
        ))

    def get_member(self, user_id: int) -> Optional[AllianceMember]:
        sql = """
            SELECT m.*, p.nickname, p.level, bp.power AS battle_power
            FROM alliance_members m
            LEFT JOIN player p ON m.user_id = p.user_id
            LEFT JOIN (
                SELECT user_id, SUM(combat_power) AS power
                FROM player_beast
                WHERE is_in_team = 1
                GROUP BY user_id
            ) bp ON bp.user_id = m.user_id
            WHERE m.user_id = %s
        """
        rows = execute_query(sql, (user_id,))
        if not rows:
            return None
        row = rows[0]
        return AllianceMember(
            alliance_id=row['alliance_id'],
            user_id=row['user_id'],
            role=row['role'],
            contribution=row['contribution'],
            total_contribution=row.get('total_contribution', row.get('contribution', 0)),
            army_type=row.get('army_type', 0),
            joined_at=row['joined_at'],
            nickname=row.get('nickname'),
            level=row.get('level'),
            battle_power=row.get('battle_power'),
        )

    def get_alliance_members(self, alliance_id: int) -> List[AllianceMember]:
        sql = """
            SELECT m.*, p.nickname, p.level, bp.power AS battle_power
            FROM alliance_members m
            LEFT JOIN player p ON m.user_id = p.user_id
            LEFT JOIN (
                SELECT user_id, SUM(combat_power) AS power
                FROM player_beast
                WHERE is_in_team = 1
                GROUP BY user_id
            ) bp ON bp.user_id = m.user_id
            WHERE m.alliance_id = %s
        """
        rows = execute_query(sql, (alliance_id,))
        return [
            AllianceMember(
                alliance_id=row['alliance_id'],
                user_id=row['user_id'],
                role=row['role'],
                contribution=row['contribution'],
                total_contribution=row.get('total_contribution', row.get('contribution', 0)),
                army_type=row.get('army_type', 0),
                joined_at=row['joined_at'],
                nickname=row.get('nickname'),
                level=row.get('level'),
                battle_power=row.get('battle_power'),
            )
            for row in rows
        ]

    def get_members_by_army(self, alliance_id: int, army_type: int) -> List[AllianceMember]:
        sql = """
            SELECT m.*, p.nickname, p.level, bp.power AS battle_power
            FROM alliance_members m
            LEFT JOIN player p ON m.user_id = p.user_id
            LEFT JOIN (
                SELECT user_id, SUM(combat_power) AS power
                FROM player_beast
                WHERE is_in_team = 1
                GROUP BY user_id
            ) bp ON bp.user_id = m.user_id
            WHERE m.alliance_id = %s AND m.army_type = %s
        """
        rows = execute_query(sql, (alliance_id, army_type))
        return [
            AllianceMember(
                alliance_id=row['alliance_id'],
                user_id=row['user_id'],
                role=row['role'],
                contribution=row['contribution'],
                total_contribution=row.get('total_contribution', row.get('contribution', 0)),
                army_type=row.get('army_type', 0),
                joined_at=row['joined_at'],
                nickname=row.get('nickname'),
                level=row.get('level'),
                battle_power=row.get('battle_power'),
            )
            for row in rows
        ]

    def update_member_role(self, user_id: int, role: int) -> None:
        sql = "UPDATE alliance_members SET role = %s WHERE user_id = %s"
        execute_update(sql, (role, user_id))

    def update_member_army(self, user_id: int, army_type: int) -> None:
        sql = "UPDATE alliance_members SET army_type = %s WHERE user_id = %s"
        execute_update(sql, (army_type, user_id))

    def remove_member(self, user_id: int) -> None:
        sql = "DELETE FROM alliance_members WHERE user_id = %s"
        execute_update(sql, (user_id,))

    def record_quit_time(self, user_id: int, quit_at: datetime) -> None:
        """记录玩家退出联盟的时间"""
        try:
            sql = """
                INSERT INTO alliance_quit_records (user_id, quit_at)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE quit_at = %s
            """
            execute_update(sql, (user_id, quit_at, quit_at))
        except Exception as e:
            # 如果表不存在，记录错误但不影响主流程
            error_str = str(e).lower()
            if 'table' in error_str and "doesn't exist" in error_str:
                import traceback
                print(f"Warning: alliance_quit_records table doesn't exist: {e}")
                print(traceback.format_exc())
            else:
                raise

    def get_quit_time(self, user_id: int) -> Optional[datetime]:
        """获取玩家最后一次退出联盟的时间，如果从未退出过则返回None"""
        try:
            sql = "SELECT quit_at FROM alliance_quit_records WHERE user_id = %s"
            rows = execute_query(sql, (user_id,))
            if not rows:
                return None
            return rows[0].get('quit_at')
        except Exception as e:
            # 如果表不存在，返回None（允许加入）
            error_str = str(e).lower()
            if 'table' in error_str and "doesn't exist" in error_str:
                import traceback
                print(f"Warning: alliance_quit_records table doesn't exist: {e}")
                print(traceback.format_exc())
                return None
            else:
                raise

    # 兵营相关
    def get_army_assignments(self, alliance_id: int) -> List[AllianceArmyAssignment]:
        sql = """
            SELECT a.alliance_id, a.user_id, a.army, a.signed_at,
                   p.nickname, p.level
            FROM alliance_army_assignments a
            LEFT JOIN player p ON p.user_id = a.user_id
            WHERE a.alliance_id = %s
            ORDER BY a.signed_at ASC
        """
        rows = execute_query(sql, (alliance_id,))
        return [
            AllianceArmyAssignment(
                alliance_id=row["alliance_id"],
                user_id=row["user_id"],
                army=row["army"],
                signed_at=row.get("signed_at"),
                nickname=row.get("nickname"),
                level=row.get("level"),
            )
            for row in rows
        ]

    def upsert_army_assignment(self, alliance_id: int, user_id: int, army: str) -> None:
        sql = """
            INSERT INTO alliance_army_assignments (alliance_id, user_id, army, signed_at)
            VALUES (%s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE army = VALUES(army), signed_at = NOW()
        """
        execute_update(sql, (alliance_id, user_id, army))

    def update_notice(self, alliance_id: int, notice: str) -> None:
        sql = "UPDATE alliances SET notice = %s WHERE id = %s"
        execute_update(sql, (notice, alliance_id))

    def update_alliance_name(self, alliance_id: int, name: str) -> None:
        sql = "UPDATE alliances SET name = %s WHERE id = %s"
        execute_update(sql, (name, alliance_id))

    def update_alliance_level(self, alliance_id: int, level: int) -> None:
        sql = "UPDATE alliances SET level = %s WHERE id = %s"
        execute_update(sql, (level, alliance_id))

    def add_chat_message(self, message: AllianceChatMessage) -> int:
        sql = """
            INSERT INTO alliance_chat_messages (alliance_id, user_id, content)
            VALUES (%s, %s, %s)
        """
        return execute_insert(sql, (
            message.alliance_id,
            message.user_id,
            message.content
        ))

    def get_chat_messages(self, alliance_id: int, limit: int = 50) -> List[AllianceChatMessage]:
        sql = """
            SELECT m.*, p.nickname 
            FROM alliance_chat_messages m
            LEFT JOIN player p ON m.user_id = p.user_id
            WHERE m.alliance_id = %s
            ORDER BY m.created_at DESC
            LIMIT %s
        """
        rows = execute_query(sql, (alliance_id, limit))
        # 先倒序取最近的消息，再正序返回给前端显示
        messages = [
            AllianceChatMessage(
                id=row['id'],
                alliance_id=row['alliance_id'],
                user_id=row['user_id'],
                content=row['content'],
                created_at=row['created_at'],
                nickname=row.get('nickname')
            )
            for row in rows
        ]
        return messages[::-1]

    def add_activity(self, activity: AllianceActivity) -> int:
        sql = """
            INSERT INTO alliance_activities (
                alliance_id,
                event_type,
                actor_user_id,
                actor_name,
                target_user_id,
                target_name,
                item_name,
                item_quantity,
                created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, COALESCE(%s, NOW()))
        """
        return execute_insert(sql, (
            activity.alliance_id,
            activity.event_type,
            activity.actor_user_id,
            activity.actor_name,
            activity.target_user_id,
            activity.target_name,
            activity.item_name,
            activity.item_quantity,
            activity.created_at,
        ))

    def list_activities(self, alliance_id: int, limit: int = 20) -> List[AllianceActivity]:
        sql = """
            SELECT
                id,
                alliance_id,
                event_type,
                actor_user_id,
                actor_name,
                target_user_id,
                target_name,
                item_name,
                item_quantity,
                created_at
            FROM alliance_activities
            WHERE alliance_id = %s
            ORDER BY created_at DESC, id DESC
            LIMIT %s
        """
        rows = execute_query(sql, (alliance_id, limit))
        return [self._map_row_to_activity(row) for row in rows]

    def get_alliance_talent_research(self, alliance_id: int) -> List[AllianceTalentResearch]:
        sql = "SELECT alliance_id, talent_key, research_level FROM alliance_talents WHERE alliance_id = %s"
        rows = execute_query(sql, (alliance_id,))
        return [
            AllianceTalentResearch(
                alliance_id=row["alliance_id"],
                talent_key=row["talent_key"],
                research_level=row["research_level"],
            )
            for row in rows
        ]

    def update_alliance_talent_research(self, alliance_id: int, talent_key: str, level: int) -> None:
        sql = """
            INSERT INTO alliance_talents (alliance_id, talent_key, research_level)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE research_level = VALUES(research_level)
        """
        execute_update(sql, (alliance_id, talent_key, level))

    def get_player_talent_levels(self, user_id: int) -> List[PlayerTalentLevel]:
        sql = "SELECT user_id, talent_key, level FROM player_talent_levels WHERE user_id = %s"
        rows = execute_query(sql, (user_id,))
        return [
            PlayerTalentLevel(
                user_id=row["user_id"],
                talent_key=row["talent_key"],
                level=row["level"],
            )
            for row in rows
        ]

    def update_player_talent_level(self, user_id: int, talent_key: str, level: int) -> None:
        sql = """
            INSERT INTO player_talent_levels (user_id, talent_key, level)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE level = VALUES(level)
        """
        execute_update(sql, (user_id, talent_key, level))

    def get_beast_storage(self, alliance_id: int) -> List[AllianceBeastStorage]:
        sql = """
            SELECT id, alliance_id, beast_id, owner_user_id, stored_at
            FROM alliance_beast_storage
            WHERE alliance_id = %s
            ORDER BY stored_at ASC, id ASC
        """
        rows = execute_query(sql, (alliance_id,))
        return [self._map_row_to_storage(row) for row in rows]

    def add_beast_storage(self, storage: AllianceBeastStorage) -> int:
        sql = """
            INSERT INTO alliance_beast_storage (alliance_id, owner_user_id, beast_id, stored_at)
            VALUES (%s, %s, %s, NOW())
        """
        return execute_insert(sql, (storage.alliance_id, storage.owner_user_id, storage.beast_id))

    def remove_beast_storage(self, storage_id: int) -> None:
        sql = "DELETE FROM alliance_beast_storage WHERE id = %s"
        execute_update(sql, (storage_id,))

    def get_beast_storage_by_id(self, storage_id: int) -> Optional[AllianceBeastStorage]:
        sql = """
            SELECT id, alliance_id, beast_id, owner_user_id, stored_at
            FROM alliance_beast_storage
            WHERE id = %s
        """
        rows = execute_query(sql, (storage_id,))
        if not rows:
            return None
        return self._map_row_to_storage(rows[0])

    def get_beast_storage_by_beast(self, beast_id: int) -> Optional[AllianceBeastStorage]:
        sql = """
            SELECT id, alliance_id, beast_id, owner_user_id, stored_at
            FROM alliance_beast_storage
            WHERE beast_id = %s
        """
        rows = execute_query(sql, (beast_id,))
        if not rows:
            return None
        return self._map_row_to_storage(rows[0])

    def count_beast_storage(self, alliance_id: int) -> int:
        sql = "SELECT COUNT(*) AS cnt FROM alliance_beast_storage WHERE alliance_id = %s"
        rows = execute_query(sql, (alliance_id,))
        if not rows:
            return 0
        return rows[0].get("cnt", 0)

    def get_beast_storage_by_owner(self, owner_user_id: int) -> List[AllianceBeastStorage]:
        sql = """
            SELECT id, alliance_id, beast_id, owner_user_id, stored_at
            FROM alliance_beast_storage
            WHERE owner_user_id = %s
            ORDER BY stored_at ASC, id ASC
        """
        rows = execute_query(sql, (owner_user_id,))
        return [self._map_row_to_storage(row) for row in rows]

    def get_item_storage(self, alliance_id: int) -> List[AllianceItemStorage]:
        sql = """
            SELECT id, alliance_id, item_id, quantity, owner_user_id, stored_at
            FROM alliance_item_storage
            WHERE alliance_id = %s
            ORDER BY stored_at ASC, id ASC
        """
        rows = execute_query(sql, (alliance_id,))
        return [self._map_row_to_item_storage(row) for row in rows]

    def get_item_storage_slots(self, alliance_id: int, owner_user_id: int, item_id: int) -> List[AllianceItemStorage]:
        sql = """
            SELECT id, alliance_id, item_id, quantity, owner_user_id, stored_at
            FROM alliance_item_storage
            WHERE alliance_id = %s AND owner_user_id = %s AND item_id = %s
            ORDER BY stored_at ASC, id ASC
        """
        rows = execute_query(sql, (alliance_id, owner_user_id, item_id))
        return [self._map_row_to_item_storage(row) for row in rows]

    def add_item_storage(self, storage: AllianceItemStorage) -> int:
        sql = """
            INSERT INTO alliance_item_storage (alliance_id, owner_user_id, item_id, quantity, stored_at)
            VALUES (%s, %s, %s, %s, NOW())
        """
        return execute_insert(sql, (
            storage.alliance_id,
            storage.owner_user_id,
            storage.item_id,
            storage.quantity,
        ))

    def update_item_storage_quantity(self, storage_id: int, quantity: int) -> None:
        sql = "UPDATE alliance_item_storage SET quantity = %s WHERE id = %s"
        execute_update(sql, (quantity, storage_id))

    def remove_item_storage(self, storage_id: int) -> None:
        sql = "DELETE FROM alliance_item_storage WHERE id = %s"
        execute_update(sql, (storage_id,))

    def count_item_storage(self, alliance_id: int) -> int:
        sql = "SELECT COUNT(*) AS cnt FROM alliance_item_storage WHERE alliance_id = %s"
        rows = execute_query(sql, (alliance_id,))
        if not rows:
            return 0
        return rows[0].get("cnt", 0)

    def get_item_storage_by_owner(self, alliance_id: int, owner_user_id: int) -> List[AllianceItemStorage]:
        sql = """
            SELECT id, alliance_id, item_id, quantity, owner_user_id, stored_at
            FROM alliance_item_storage
            WHERE alliance_id = %s AND owner_user_id = %s
            ORDER BY stored_at ASC, id ASC
        """
        rows = execute_query(sql, (alliance_id, owner_user_id))
        return [self._map_row_to_item_storage(row) for row in rows]

    def get_item_storage_by_id(self, storage_id: int) -> Optional[AllianceItemStorage]:
        sql = """
            SELECT id, alliance_id, item_id, quantity, owner_user_id, stored_at
            FROM alliance_item_storage
            WHERE id = %s
        """
        rows = execute_query(sql, (storage_id,))
        if not rows:
            return None
        return self._map_row_to_item_storage(rows[0])

    def update_alliance_crystals(self, alliance_id: int, delta: int) -> None:
        sql = "UPDATE alliances SET crystals = GREATEST(0, crystals + %s) WHERE id = %s"
        execute_update(sql, (delta, alliance_id))

    def create_training_room(self, room: AllianceTrainingRoom) -> int:
        sql = """
            INSERT INTO alliance_training_rooms (alliance_id, creator_user_id, title, status, max_participants, duration_hours)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        return execute_insert(sql, (
            room.alliance_id,
            room.creator_user_id,
            room.title,
            room.status,
            room.max_participants,
            getattr(room, "duration_hours", 2) or 2,  # 兼容旧数据，默认2小时
        ))

    def get_training_rooms(self, alliance_id: int) -> List[AllianceTrainingRoom]:
        sql = """
            SELECT id, alliance_id, creator_user_id, title, status, max_participants, duration_hours, created_at, completed_at
            FROM alliance_training_rooms
            WHERE alliance_id = %s
            ORDER BY status DESC, created_at DESC
        """
        rows = execute_query(sql, (alliance_id,))
        return [self._map_row_to_training_room(row) for row in rows]

    def get_training_room_by_id(self, room_id: int) -> Optional[AllianceTrainingRoom]:
        sql = """
            SELECT id, alliance_id, creator_user_id, title, status, max_participants, duration_hours, created_at, completed_at
            FROM alliance_training_rooms
            WHERE id = %s
        """
        rows = execute_query(sql, (room_id,))
        if not rows:
            return None
        return self._map_row_to_training_room(rows[0])

    def add_training_participant(self, participant: AllianceTrainingParticipant) -> int:
        sql = """
            INSERT INTO alliance_training_participants (room_id, user_id, reward_amount)
            VALUES (%s, %s, %s)
        """
        return execute_insert(sql, (
            participant.room_id,
            participant.user_id,
            participant.reward_amount,
        ))

    def get_training_participant(self, participant_id: int) -> Optional[AllianceTrainingParticipant]:
        sql = """
            SELECT p.id, p.room_id, p.user_id, p.joined_at, p.claimed_at, p.reward_amount, pl.nickname
            FROM alliance_training_participants p
            LEFT JOIN player pl ON p.user_id = pl.user_id
            WHERE p.id = %s
        """
        rows = execute_query(sql, (participant_id,))
        if not rows:
            return None
        return self._map_row_to_training_participant(rows[0])

    def get_training_participant_by_room(self, room_id: int, user_id: int) -> Optional[AllianceTrainingParticipant]:
        sql = """
            SELECT p.id, p.room_id, p.user_id, p.joined_at, p.claimed_at, p.reward_amount, pl.nickname
            FROM alliance_training_participants p
            LEFT JOIN player pl ON p.user_id = pl.user_id
            WHERE p.room_id = %s AND p.user_id = %s
        """
        rows = execute_query(sql, (room_id, user_id))
        if not rows:
            return None
        return self._map_row_to_training_participant(rows[0])

    def get_training_participants(self, room_id: int) -> List[AllianceTrainingParticipant]:
        sql = """
            SELECT p.id, p.room_id, p.user_id, p.joined_at, p.claimed_at, p.reward_amount, pl.nickname
            FROM alliance_training_participants p
            LEFT JOIN player pl ON p.user_id = pl.user_id
            WHERE room_id = %s
            ORDER BY p.joined_at ASC
        """
        rows = execute_query(sql, (room_id,))
        return [self._map_row_to_training_participant(row) for row in rows]

    def get_training_participation_today(self, alliance_id: int, user_id: int) -> Optional[AllianceTrainingParticipant]:
        sql = """
            SELECT p.*, pl.nickname
            FROM alliance_training_participants p
            JOIN alliance_training_rooms r ON p.room_id = r.id
            LEFT JOIN player pl ON p.user_id = pl.user_id
            WHERE r.alliance_id = %s
              AND p.user_id = %s
              AND DATE(p.joined_at) = CURDATE()
            ORDER BY p.joined_at DESC
            LIMIT 1
        """
        rows = execute_query(sql, (alliance_id, user_id))
        if not rows:
            return None
        return self._map_row_to_training_participant(rows[0])

    def mark_training_claimed(self, participant_id: int, reward_amount: int) -> None:
        sql = """
            UPDATE alliance_training_participants
            SET claimed_at = NOW(), reward_amount = %s
            WHERE id = %s
        """
        execute_update(sql, (reward_amount, participant_id))

    def update_training_room_status(self, room_id: int, status: str) -> None:
        sql = """
            UPDATE alliance_training_rooms
            SET status = %s,
                completed_at = CASE WHEN %s = 'completed' THEN NOW() ELSE completed_at END
            WHERE id = %s
        """
        execute_update(sql, (status, status, room_id))

    def has_claimed_fire_ore_today(self, user_id: int) -> bool:
        """检查玩家今日是否已领取火能原石（使用数据库日期确保时区一致）"""
        try:
            # 使用数据库的CURDATE()来比较，确保时区一致
            sql = """
                SELECT last_fire_ore_claim_date
                FROM player
                WHERE user_id = %s
                AND last_fire_ore_claim_date = CURDATE()
            """
            rows = execute_query(sql, (user_id,))
            # 如果查询到记录，说明今日已领取
            return len(rows) > 0
        except Exception:
            # 如果字段不存在或其他错误，返回 False
            return False

    def record_fire_ore_claim(self, user_id: int) -> bool:
        """记录火能原石领取（使用条件更新，确保原子性）
        返回True表示更新成功（今日首次领取），False表示今日已领取过
        """
        # 更新 player 表的 last_fire_ore_claim_date 字段
        # 只有当今日未领取时才更新，防止并发问题
        try:
            sql = """
                UPDATE player
                SET last_fire_ore_claim_date = CURDATE()
                WHERE user_id = %s
                AND (last_fire_ore_claim_date IS NULL OR last_fire_ore_claim_date < CURDATE())
            """
            affected_rows = execute_update(sql, (user_id,))
            # 如果影响行数>0，说明更新成功（今日首次领取）
            # 如果影响行数=0，说明今日已领取过
            return affected_rows > 0
        except Exception as e:
            # 如果字段不存在，记录错误
            import logging
            logging.warning(f"Failed to update last_fire_ore_claim_date for user {user_id}: {e}")
            # 返回False，表示无法记录（可能是字段不存在）
            return False

    def update_alliance_resources(self, alliance_id: int, funds_delta: int = 0, prosperity_delta: int = 0) -> None:
        sql = "UPDATE alliances SET funds = GREATEST(0, funds + %s), prosperity = GREATEST(0, prosperity + %s) WHERE id = %s"
        execute_update(sql, (funds_delta, prosperity_delta, alliance_id))

    def update_member_contribution(self, user_id: int, delta: int) -> None:
        # 更新现有贡献点，如果是增加则同时更新历史总贡献点
        # 历史总贡献点只增不减，永远不会减少
        if delta > 0:
            # 增加贡献点：同时更新现有贡献点和历史总贡献点
            # 历史总贡献点 = max(原历史总贡献点 + 增量, 新的现有贡献点)
            # 确保历史总贡献点只增不减，且至少等于新的现有贡献点
            sql = """
                UPDATE alliance_members 
                SET contribution = contribution + %s,
                    total_contribution = GREATEST(
                        COALESCE(total_contribution, 0) + %s,
                        contribution + %s
                    )
                WHERE user_id = %s
            """
            execute_update(sql, (delta, delta, delta, user_id))
        else:
            # 减少贡献点：只更新现有贡献点，历史总贡献点保持不变（只增不减）
            # 注意：不显式设置 total_contribution，MySQL 会自动保持原值不变
            # 这样触发器也不需要处理这种情况，避免任何潜在的问题
            sql = """
                UPDATE alliance_members 
                SET contribution = GREATEST(0, contribution + %s)
                WHERE user_id = %s
            """
            execute_update(sql, (delta, user_id))

    def get_alliance_war_points(self, alliance_id: int) -> Tuple[int, int]:
        sql = "SELECT war_honor, war_honor_history FROM alliances WHERE id = %s"
        rows = execute_query(sql, (alliance_id,))
        if not rows:
            return 0, 0
        row = rows[0]
        return row.get("war_honor", 0) or 0, row.get("war_honor_history", 0) or 0

    def update_alliance_war_points(self, alliance_id: int, delta: int) -> None:
        sql = """
            UPDATE alliances
            SET
                war_honor = GREATEST(0, war_honor + %s),
                war_honor_history = war_honor_history + CASE WHEN %s > 0 THEN %s ELSE 0 END
            WHERE id = %s
        """
        execute_update(sql, (delta, delta, delta, alliance_id))

    def list_top_alliance_names_by_war_honor_history(self, limit: int) -> List[str]:
        """盟战排行榜：按历史累计战功倒序取前 N 个联盟名字。"""
        sql = """
            SELECT name
            FROM alliances
            ORDER BY war_honor_history DESC, id ASC
            LIMIT %s
        """
        rows = execute_query(sql, (int(limit or 0),))
        return [str(r.get("name") or "").strip() for r in (rows or []) if str(r.get("name") or "").strip()]

    def get_active_honor_effects(self, alliance_id: int) -> List[Dict]:
        sql = """
            SELECT id, alliance_id, effect_key, effect_type, cost, started_at, expires_at, created_by
            FROM alliance_war_honor_effects
            WHERE alliance_id = %s AND expires_at > NOW()
            ORDER BY expires_at ASC
        """
        return execute_query(sql, (alliance_id,))

    def insert_honor_effect(
        self,
        alliance_id: int,
        effect_key: str,
        effect_type: str,
        cost: int,
        started_at: datetime,
        expires_at: datetime,
        created_by: int,
    ) -> int:
        sql = """
            INSERT INTO alliance_war_honor_effects (
                alliance_id,
                effect_key,
                effect_type,
                cost,
                started_at,
                expires_at,
                created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        return execute_insert(sql, (
            alliance_id,
            effect_key,
            effect_type,
            cost,
            started_at,
            expires_at,
            created_by,
        ))

    def increment_alliance_war_score(self, alliance_id: int, season_key: str, delta: int = 1) -> None:
        sql = """
            INSERT INTO alliance_war_scores (alliance_id, season_key, score)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                score = score + VALUES(score),
                updated_at = CURRENT_TIMESTAMP
        """
        execute_update(sql, (alliance_id, season_key, delta))

    def list_alliance_war_leaderboard(self, since: datetime, limit: int, offset: int) -> List[Dict]:
        """排行榜基于alliances表的war_honor字段（当前战功），与联盟内显示保持一致"""
        sql = """
            SELECT 
                a.id AS alliance_id,
                a.name AS alliance_name,
                COALESCE(a.war_honor, 0) AS score
            FROM alliances a
            WHERE a.war_honor > 0
            ORDER BY a.war_honor DESC, a.id ASC
            LIMIT %s OFFSET %s
        """
        return execute_query(sql, (limit, offset))

    def count_alliance_war_leaderboard(self, since: datetime) -> int:
        """统计排行榜数量，基于alliances表的war_honor字段"""
        sql = """
            SELECT COUNT(*) as cnt
            FROM alliances
            WHERE war_honor > 0
        """
        rows = execute_query(sql)
        return rows[0]['cnt'] if rows else 0

    def get_alliance_war_leaderboard_entry(self, alliance_id: int, since: datetime) -> Optional[Dict]:
        """获取指定联盟在排行榜中的条目，基于alliances表的war_honor字段"""
        sql = """
            SELECT
                t.alliance_id,
                t.alliance_name,
                t.score,
                DENSE_RANK() OVER (ORDER BY t.score DESC, t.alliance_id ASC) AS rank
            FROM (
                SELECT
                    a.id AS alliance_id,
                    a.name AS alliance_name,
                    COALESCE(a.war_honor, 0) AS score
                FROM alliances a
                WHERE a.war_honor > 0
            ) t
            WHERE t.alliance_id = %s
        """
        rows = execute_query(sql, (alliance_id,))
        if not rows:
            return None
        row = rows[0]
        return {
            "rank": row["rank"],
            "alliance_id": row["alliance_id"],
            "alliance_name": row["alliance_name"],
            "score": row["score"],
        }

    # === 土地报名 ===
    def get_land_registration(self, alliance_id: int, land_id: int) -> Optional[AllianceRegistration]:
        sql = """
            SELECT id, alliance_id, land_id, army, registration_time, cost, status, created_at,
                   bye_waiting_round, last_bye_round
            FROM alliance_land_registration
            WHERE alliance_id = %s AND land_id = %s
            LIMIT 1
        """
        rows = execute_query(sql, (alliance_id, land_id))
        if not rows:
            return None
        return self._map_land_registration(rows[0])

    # === 军团报名玩家 ===
    def add_army_signups(self, signups: List[AllianceArmySignup]) -> None:
        if not signups:
            return
        sql = """
            INSERT INTO alliance_army_signups (
                registration_id, alliance_id, army, user_id, signup_order, hp_state, status, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        for signup in signups:
            hp_json = json.dumps(signup.hp_state, ensure_ascii=False) if signup.hp_state else None
            new_id = execute_insert(
                sql,
                (
                    signup.registration_id,
                    signup.alliance_id,
                    signup.army,
                    signup.user_id,
                    signup.signup_order,
                    hp_json,
                    signup.status,
                    signup.created_at or None,
                ),
            )
            signup.id = new_id

    def _map_army_signup(self, row: dict) -> AllianceArmySignup:
        """将数据库行映射为AllianceArmySignup对象"""
        hp_state = None
        if row.get('hp_state'):
            if isinstance(row['hp_state'], str):
                hp_state = json.loads(row['hp_state'])
            else:
                hp_state = row['hp_state']
        
        return AllianceArmySignup(
            id=row.get('id'),
            registration_id=row.get('registration_id', 0),
            alliance_id=row.get('alliance_id', 0),
            army=row.get('army', ''),
            user_id=row.get('user_id', 0),
            signup_order=row.get('signup_order', 0),
            hp_state=hp_state,
            status=row.get('status', 1),
            created_at=row.get('created_at'),
        )
    
    def list_army_signups(self, registration_id: int) -> List[AllianceArmySignup]:
        sql = """
            SELECT id, registration_id, alliance_id, army, user_id, signup_order, hp_state, status, created_at
            FROM alliance_army_signups
            WHERE registration_id = %s
            ORDER BY signup_order ASC, id ASC
        """
        rows = execute_query(sql, (registration_id,))
        return [self._map_army_signup(row) for row in rows]

    def update_army_signup_state(self, signup_id: int, status: int, hp_state: Optional[dict]) -> None:
        sql = """
            UPDATE alliance_army_signups
            SET status = %s,
                hp_state = %s
            WHERE id = %s
        """
        hp_json = json.dumps(hp_state, ensure_ascii=False) if hp_state else None
        execute_update(sql, (status, hp_json, signup_id))

    # === 土地战斗 ===
    def create_land_battle(self, battle: AllianceLandBattle) -> int:
        sql = """
            INSERT INTO alliance_land_battle (
                land_id, left_registration_id, right_registration_id, phase, current_round, started_at, finished_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        new_id = execute_insert(
            sql,
            (
                battle.land_id,
                battle.left_registration_id,
                battle.right_registration_id,
                battle.phase,
                battle.current_round,
                battle.started_at,
                battle.finished_at,
            ),
        )
        battle.id = new_id
        return new_id

    def update_land_battle(self, battle: AllianceLandBattle) -> None:
        if not battle.id:
            raise ValueError("Battle ID required for update")
        sql = """
            UPDATE alliance_land_battle
            SET land_id = %s,
                left_registration_id = %s,
                right_registration_id = %s,
                phase = %s,
                current_round = %s,
                started_at = %s,
                finished_at = %s
            WHERE id = %s
        """
        execute_update(
            sql,
            (
                battle.land_id,
                battle.left_registration_id,
                battle.right_registration_id,
                battle.phase,
                battle.current_round,
                battle.started_at,
                battle.finished_at,
                battle.id,
            ),
        )

    def get_land_battle_by_id(self, battle_id: int) -> Optional[AllianceLandBattle]:
        sql = """
            SELECT id, land_id, left_registration_id, right_registration_id, phase, current_round, started_at, finished_at
            FROM alliance_land_battle
            WHERE id = %s
        """
        rows = execute_query(sql, (battle_id,))
        if not rows:
            return None
        return self._map_land_battle(rows[0])

    def get_active_battle_by_land(self, land_id: int) -> Optional[AllianceLandBattle]:
        sql = """
            SELECT id, land_id, left_registration_id, right_registration_id, phase, current_round, started_at, finished_at
            FROM alliance_land_battle
            WHERE land_id = %s AND phase IN (0, 1)
            ORDER BY id DESC
            LIMIT 1
        """
        rows = execute_query(sql, (land_id,))
        if not rows:
            return None
        return self._map_land_battle(rows[0])

    def list_alliance_battles(self, alliance_id: int) -> List[AllianceLandBattle]:
        sql = """
            SELECT b.id,
                   b.land_id,
                   b.left_registration_id,
                   b.right_registration_id,
                   b.phase,
                   b.current_round,
                   b.started_at,
                   b.finished_at
            FROM alliance_land_battle b
            INNER JOIN alliance_land_registration lreg ON lreg.id = b.left_registration_id
            INNER JOIN alliance_land_registration rreg ON rreg.id = b.right_registration_id
            WHERE lreg.alliance_id = %s OR rreg.alliance_id = %s
            ORDER BY b.id DESC
        """
        rows = execute_query(sql, (alliance_id, alliance_id))
        return [self._map_land_battle(row) for row in rows]

    # === 战斗轮次 ===
    def create_battle_round(self, battle_round: AllianceLandBattleRound) -> int:
        sql = """
            INSERT INTO alliance_land_battle_round (
                battle_id, round_no, left_alive, right_alive, status, started_at, finished_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        new_id = execute_insert(
            sql,
            (
                battle_round.battle_id,
                battle_round.round_no,
                battle_round.left_alive,
                battle_round.right_alive,
                battle_round.status,
                battle_round.started_at,
                battle_round.finished_at,
            ),
        )
        battle_round.id = new_id
        return new_id

    def update_battle_round(self, battle_round: AllianceLandBattleRound) -> None:
        if not battle_round.id:
            raise ValueError("Battle round ID required for update")
        sql = """
            UPDATE alliance_land_battle_round
            SET battle_id = %s,
                round_no = %s,
                left_alive = %s,
                right_alive = %s,
                status = %s,
                started_at = %s,
                finished_at = %s
            WHERE id = %s
        """
        execute_update(
            sql,
            (
                battle_round.battle_id,
                battle_round.round_no,
                battle_round.left_alive,
                battle_round.right_alive,
                battle_round.status,
                battle_round.started_at,
                battle_round.finished_at,
                battle_round.id,
            ),
        )

    def list_battle_rounds(self, battle_id: int) -> List[AllianceLandBattleRound]:
        sql = """
            SELECT id, battle_id, round_no, left_alive, right_alive, status, started_at, finished_at
            FROM alliance_land_battle_round
            WHERE battle_id = %s
            ORDER BY round_no ASC, id ASC
        """
        rows = execute_query(sql, (battle_id,))
        return [self._map_battle_round(row) for row in rows]

    def get_battle_round_by_id(self, round_id: int) -> Optional[AllianceLandBattleRound]:
        sql = """
            SELECT id, battle_id, round_no, left_alive, right_alive, status, started_at, finished_at
            FROM alliance_land_battle_round
            WHERE id = %s
            LIMIT 1
        """
        rows = execute_query(sql, (round_id,))
        if not rows:
            return None
        return self._map_battle_round(rows[0])

    # === 战斗对战日志 ===
    def add_battle_duels(self, duels: List[AllianceLandBattleDuel]) -> None:
        if not duels:
            return
        sql = """
            INSERT INTO alliance_land_battle_duel (
                round_id, attacker_signup_id, defender_signup_id, attacker_result, log_json, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        for duel in duels:
            log_json = json.dumps(duel.log_data or {}, ensure_ascii=False)
            new_id = execute_insert(
                sql,
                (
                    duel.round_id,
                    duel.attacker_signup_id,
                    duel.defender_signup_id,
                    duel.attacker_result,
                    log_json,
                    duel.created_at or None,
                ),
            )
            duel.id = new_id

    def list_duels_by_round(self, round_id: int) -> List[AllianceLandBattleDuel]:
        sql = """
            SELECT id, round_id, attacker_signup_id, defender_signup_id, attacker_result, log_json, created_at
            FROM alliance_land_battle_duel
            WHERE round_id = %s
            ORDER BY id ASC
        """
        rows = execute_query(sql, (round_id,))
        return [self._map_battle_duel(row) for row in rows]

    def save_land_registration(self, registration: AllianceRegistration) -> int:
        if registration.id:
            sql = """
                UPDATE alliance_land_registration
                SET army = %s,
                    registration_time = %s,
                    cost = %s,
                    status = %s,
                    bye_waiting_round = %s,
                    last_bye_round = %s
                WHERE id = %s
            """
            execute_update(sql, (
                registration.army,
                registration.registration_time,
                registration.cost,
                registration.status,
                registration.bye_waiting_round,
                registration.last_bye_round,
                registration.id,
            ))
            return registration.id

        sql = """
            INSERT INTO alliance_land_registration (
                land_id, alliance_id, army, registration_time, cost, status, created_at,
                bye_waiting_round, last_bye_round
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        new_id = execute_insert(sql, (
            registration.land_id,
            registration.alliance_id,
            registration.army,
            registration.registration_time,
            registration.cost,
            registration.status,
            registration.created_at,
            registration.bye_waiting_round,
            registration.last_bye_round,
        ))
        registration.id = new_id
        return new_id

    def get_active_land_registration_by_range(
        self, alliance_id: int, land_ids: List[int]
    ) -> Optional[AllianceRegistration]:
        if not land_ids:
            return None
        placeholders = ", ".join(["%s"] * len(land_ids))
        sql = f"""
            SELECT id, alliance_id, land_id, army, registration_time, cost, status, created_at,
                   bye_waiting_round, last_bye_round
            FROM alliance_land_registration
            WHERE alliance_id = %s
              AND land_id IN ({placeholders})
              AND status IN (1, 2, 3, 4)
            ORDER BY registration_time DESC
            LIMIT 1
        """
        params = [alliance_id, *land_ids]
        rows = execute_query(sql, tuple(params))
        if not rows:
            return None
        return self._map_land_registration(rows[0])

    def list_land_registrations_by_land(
        self, land_id: int, statuses: Optional[List[int]] = None
    ) -> List[AllianceRegistration]:
        sql = """
            SELECT id, alliance_id, land_id, army, registration_time, cost, status, created_at,
                   bye_waiting_round, last_bye_round
            FROM alliance_land_registration
            WHERE land_id = %s
        """
        params: List = [land_id]
        if statuses:
            placeholders = ", ".join(["%s"] * len(statuses))
            sql += f" AND status IN ({placeholders})"
            params.extend(statuses)
        sql += " ORDER BY registration_time ASC, id ASC"
        rows = execute_query(sql, tuple(params))
        return [self._map_land_registration(row) for row in rows]

    def get_land_registration_by_id(self, registration_id: int) -> Optional[AllianceRegistration]:
        sql = """
            SELECT id, alliance_id, land_id, army, registration_time, cost, status, created_at,
                   bye_waiting_round, last_bye_round
            FROM alliance_land_registration
            WHERE id = %s
            LIMIT 1
        """
        rows = execute_query(sql, (registration_id,))
        if not rows:
            return None
        return self._map_land_registration(rows[0])

    def get_alliance_buildings(self, alliance_id: int) -> List[AllianceBuilding]:
        sql = """
            SELECT alliance_id, building_key, level
            FROM alliance_buildings
            WHERE alliance_id = %s
        """
        rows = execute_query(sql, (alliance_id,))
        return [self._map_row_to_building(row) for row in rows]

    def get_alliance_building(self, alliance_id: int, building_key: str) -> Optional[AllianceBuilding]:
        sql = """
            SELECT alliance_id, building_key, level
            FROM alliance_buildings
            WHERE alliance_id = %s AND building_key = %s
        """
        rows = execute_query(sql, (alliance_id, building_key))
        if not rows:
            return None
        return self._map_row_to_building(rows[0])

    def set_alliance_building_level(self, alliance_id: int, building_key: str, level: int) -> None:
        sql = """
            INSERT INTO alliance_buildings (alliance_id, building_key, level)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE level = VALUES(level)
        """
        execute_update(sql, (alliance_id, building_key, level))

    def _map_row_to_alliance(self, row: dict) -> Alliance:
        return Alliance(
            id=row['id'],
            name=row['name'],
            leader_id=row['leader_id'],
            level=row['level'],
            exp=row['exp'],
            funds=row['funds'],
            crystals=row['crystals'],
            prosperity=row['prosperity'],
            notice=row['notice'],
            created_at=row['created_at']
        )

    def _map_row_to_storage(self, row: dict) -> AllianceBeastStorage:
        return AllianceBeastStorage(
            id=row.get("id"),
            alliance_id=row.get("alliance_id"),
            beast_id=row.get("beast_id"),
            owner_user_id=row.get("owner_user_id"),
            stored_at=row.get("stored_at"),
        )

    def _map_row_to_training_room(self, row: dict) -> AllianceTrainingRoom:
        return AllianceTrainingRoom(
            id=row.get("id"),
            alliance_id=row.get("alliance_id"),
            creator_user_id=row.get("creator_user_id"),
            title=row.get("title"),
            status=row.get("status"),
            max_participants=row.get("max_participants"),
            duration_hours=row.get("duration_hours", 2) or 2,  # 兼容旧数据，默认2小时
            created_at=row.get("created_at"),
            completed_at=row.get("completed_at"),
        )

    def _map_row_to_training_participant(self, row: dict) -> AllianceTrainingParticipant:
        return AllianceTrainingParticipant(
            id=row.get("id"),
            room_id=row.get("room_id"),
            user_id=row.get("user_id"),
            joined_at=row.get("joined_at"),
            claimed_at=row.get("claimed_at"),
            reward_amount=row.get("reward_amount"),
            nickname=row.get("nickname"),
        )

    def _map_row_to_item_storage(self, row: dict) -> AllianceItemStorage:
        return AllianceItemStorage(
            id=row.get("id"),
            alliance_id=row.get("alliance_id"),
            item_id=row.get("item_id"),
            quantity=row.get("quantity"),
            owner_user_id=row.get("owner_user_id"),
            stored_at=row.get("stored_at"),
        )

    def _map_row_to_building(self, row: dict) -> AllianceBuilding:
        return AllianceBuilding(
            alliance_id=row.get("alliance_id"),
            building_key=row.get("building_key"),
            level=row.get("level"),
        )

    def _map_row_to_activity(self, row: dict) -> AllianceActivity:
        return AllianceActivity(
            id=row.get("id"),
            alliance_id=row.get("alliance_id"),
            event_type=row.get("event_type"),
            actor_user_id=row.get("actor_user_id"),
            actor_name=row.get("actor_name"),
            target_user_id=row.get("target_user_id"),
            target_name=row.get("target_name"),
            item_name=row.get("item_name"),
            item_quantity=row.get("item_quantity"),
            created_at=row.get("created_at"),
        )

    def _map_land_registration(self, row: dict) -> AllianceRegistration:
        return AllianceRegistration(
            id=row.get("id"),
            alliance_id=row.get("alliance_id"),
            land_id=row.get("land_id"),
            army=row.get("army"),
            registration_time=row.get("registration_time"),
            cost=row.get("cost"),
            status=row.get("status"),
            created_at=row.get("created_at"),
            bye_waiting_round=row.get("bye_waiting_round"),
            last_bye_round=row.get("last_bye_round"),
        )

    def _map_land_battle(self, row: dict) -> AllianceLandBattle:
        return AllianceLandBattle(
            id=row.get("id"),
            land_id=row.get("land_id"),
            left_registration_id=row.get("left_registration_id"),
            right_registration_id=row.get("right_registration_id"),
            phase=row.get("phase", 0),
            current_round=row.get("current_round", 0),
            started_at=row.get("started_at"),
            finished_at=row.get("finished_at"),
        )

    def _map_battle_round(self, row: dict) -> AllianceLandBattleRound:
        return AllianceLandBattleRound(
            id=row.get("id"),
            battle_id=row.get("battle_id"),
            round_no=row.get("round_no"),
            left_alive=row.get("left_alive", 0),
            right_alive=row.get("right_alive", 0),
            status=row.get("status", 0),
            started_at=row.get("started_at"),
            finished_at=row.get("finished_at"),
        )

    def _map_battle_duel(self, row: dict) -> AllianceLandBattleDuel:
        log_raw = row.get("log_json")
        log_data = {}
        if isinstance(log_raw, str) and log_raw:
            try:
                log_data = json.loads(log_raw)
            except Exception:
                log_data = {}
        elif isinstance(log_raw, dict):
            log_data = log_raw
        return AllianceLandBattleDuel(
            id=row.get("id"),
            round_id=row.get("round_id"),
            attacker_signup_id=row.get("attacker_signup_id"),
            defender_signup_id=row.get("defender_signup_id"),
            attacker_result=row.get("attacker_result", 0),
            log_data=log_data,
            created_at=row.get("created_at"),
        )

    # === 盟战签到 ===
    def has_war_checkin(self, alliance_id: int, user_id: int, war_phase: str, war_weekday: int, checkin_date: date) -> bool:
        if isinstance(checkin_date, str):
            checkin_date = datetime.strptime(checkin_date, "%Y-%m-%d").date()
        sql = """
            SELECT 1 FROM alliance_war_checkin
            WHERE alliance_id = %s AND user_id = %s AND war_phase = %s AND war_weekday = %s AND checkin_date = %s
            LIMIT 1
        """
        rows = execute_query(sql, (alliance_id, user_id, war_phase, war_weekday, checkin_date))
        return len(rows) > 0

    def add_war_checkin(self, alliance_id: int, user_id: int, war_phase: str, war_weekday: int, checkin_date: date, copper_reward: int) -> int:
        if isinstance(checkin_date, str):
            checkin_date = datetime.strptime(checkin_date, "%Y-%m-%d").date()
        sql = """
            INSERT INTO alliance_war_checkin (alliance_id, user_id, war_phase, war_weekday, checkin_date, copper_reward)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        return execute_insert(sql, (alliance_id, user_id, war_phase, war_weekday, checkin_date, copper_reward))

    # === 盟战战绩 ===
    def add_war_battle_record(self, alliance_id: int, opponent_alliance_id: int, land_id: int, army_type: str, war_phase: str, war_date: date, battle_result: str, honor_gained: int, battle_id: Optional[int] = None) -> int:
        if isinstance(war_date, str):
            war_date = datetime.strptime(war_date, "%Y-%m-%d").date()
        sql = """
            INSERT INTO alliance_war_battle_records 
            (battle_id, alliance_id, opponent_alliance_id, land_id, army_type, war_phase, war_date, battle_result, honor_gained)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        return execute_insert(sql, (battle_id, alliance_id, opponent_alliance_id, land_id, army_type, war_phase, war_date, battle_result, honor_gained))

    def list_war_battle_records(self, alliance_id: int, limit: int = 50) -> List[Dict]:
        sql = """
            SELECT 
                r.id,
                r.battle_id,
                r.alliance_id,
                r.opponent_alliance_id,
                a1.name AS alliance_name,
                a2.name AS opponent_alliance_name,
                r.land_id,
                l.name AS land_name,
                r.army_type,
                r.war_phase,
                r.war_date,
                r.battle_result,
                r.honor_gained,
                r.created_at
            FROM alliance_war_battle_records r
            LEFT JOIN alliances a1 ON a1.id = r.alliance_id
            LEFT JOIN alliances a2 ON a2.id = r.opponent_alliance_id
            LEFT JOIN lands l ON l.id = r.land_id
            WHERE r.alliance_id = %s
            ORDER BY r.war_date DESC, r.created_at DESC
            LIMIT %s
        """
        return execute_query(sql, (alliance_id, limit))

    # === 战功兑换 ===
    def add_war_honor_exchange(self, alliance_id: int, user_id: int, exchange_type: str, honor_cost: int, item_id: int, item_name: str, item_quantity: int) -> int:
        sql = """
            INSERT INTO alliance_war_honor_exchange 
            (alliance_id, user_id, exchange_type, honor_cost, item_id, item_name, item_quantity)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        return execute_insert(sql, (alliance_id, user_id, exchange_type, honor_cost, item_id, item_name, item_quantity))

    def list_war_honor_exchanges(self, alliance_id: int, limit: int = 50) -> List[Dict]:
        sql = """
            SELECT 
                e.id,
                e.alliance_id,
                e.user_id,
                p.nickname AS user_name,
                e.exchange_type,
                e.honor_cost,
                e.item_id,
                e.item_name,
                e.item_quantity,
                e.exchanged_at
            FROM alliance_war_honor_exchange e
            LEFT JOIN player p ON p.user_id = e.user_id
            WHERE e.alliance_id = %s
            ORDER BY e.exchanged_at DESC
            LIMIT %s
        """
        return execute_query(sql, (alliance_id, limit))

    # === 赛季奖励 ===
    def get_season_reward(self, alliance_id: int, season_key: str) -> Optional[Dict]:
        sql = """
            SELECT id, alliance_id, season_key, rank, copper_reward, items_json, distributed_at, created_at
            FROM alliance_season_rewards
            WHERE alliance_id = %s AND season_key = %s
        """
        rows = execute_query(sql, (alliance_id, season_key))
        return rows[0] if rows else None

    def add_season_reward(self, alliance_id: int, season_key: str, rank: int, copper_reward: int, items_json: str) -> int:
        sql = """
            INSERT INTO alliance_season_rewards (alliance_id, season_key, rank, copper_reward, items_json)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE rank = VALUES(rank), copper_reward = VALUES(copper_reward), items_json = VALUES(items_json)
        """
        return execute_insert(sql, (alliance_id, season_key, rank, copper_reward, items_json))

    def distribute_season_rewards(self, season_key: str) -> List[Dict]:
        """发放赛季奖励，返回发放记录列表"""
        # 获取前三名
        sql = """
            SELECT 
                aws.alliance_id,
                a.name AS alliance_name,
                aws.score,
                DENSE_RANK() OVER (ORDER BY aws.score DESC, aws.alliance_id ASC) AS rank
            FROM alliance_war_scores aws
            INNER JOIN alliances a ON a.id = aws.alliance_id
            WHERE aws.season_key = %s AND aws.score > 0
            ORDER BY aws.score DESC, aws.alliance_id ASC
            LIMIT 3
        """
        top3 = execute_query(sql, (season_key,))
        
        distributed = []
        for row in top3:
            rank = row["rank"]
            alliance_id = row["alliance_id"]
            # 检查是否已发放
            existing = self.get_season_reward(alliance_id, season_key)
            if existing and existing.get("distributed_at"):
                continue  # 已发放，跳过
            
            # 获取奖励配置
            from application.services.alliance_service import AllianceService
            reward_config = AllianceService.SEASON_REWARD_RULES.get(rank, {})
            copper_reward = reward_config.get("copper", 0)
            items = reward_config.get("items", [])
            items_json = json.dumps(items, ensure_ascii=False)
            
            # 记录奖励
            self.add_season_reward(alliance_id, season_key, rank, copper_reward, items_json)
            
            # 标记为已发放
            update_sql = """
                UPDATE alliance_season_rewards 
                SET distributed_at = NOW()
                WHERE alliance_id = %s AND season_key = %s
            """
            execute_update(update_sql, (alliance_id, season_key))
            
            distributed.append({
                "alliance_id": alliance_id,
                "alliance_name": row["alliance_name"],
                "rank": rank,
                "copper_reward": copper_reward,
                "items": items,
            })
        
        return distributed

    # === 土地占领 ===
    def get_land_occupation(self, land_id: int) -> Optional[Dict]:
        sql = """
            SELECT 
                o.id,
                o.land_id,
                o.alliance_id,
                a.name AS alliance_name,
                o.occupied_at,
                o.war_phase,
                o.war_date
            FROM alliance_land_occupation o
            INNER JOIN alliances a ON a.id = o.alliance_id
            WHERE o.land_id = %s
            ORDER BY o.occupied_at DESC
            LIMIT 1
        """
        rows = execute_query(sql, (land_id,))
        return rows[0] if rows else None

    def set_land_occupation(self, land_id: int, alliance_id: int, war_phase: str, war_date: date) -> int:
        if isinstance(war_date, str):
            war_date = datetime.strptime(war_date, "%Y-%m-%d").date()
        # 先删除旧记录
        delete_sql = "DELETE FROM alliance_land_occupation WHERE land_id = %s"
        execute_update(delete_sql, (land_id,))
        # 插入新记录
        sql = """
            INSERT INTO alliance_land_occupation (land_id, alliance_id, war_phase, war_date)
            VALUES (%s, %s, %s, %s)
        """
        return execute_insert(sql, (land_id, alliance_id, war_phase, war_date))
