import json
from datetime import datetime
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
        sql = """
            INSERT INTO alliance_members (alliance_id, user_id, role, contribution)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE alliance_id = VALUES(alliance_id), role = VALUES(role)
        """
        execute_update(sql, (
            member.alliance_id,
            member.user_id,
            member.role,
            member.contribution
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
            INSERT INTO alliance_training_rooms (alliance_id, creator_user_id, title, status, max_participants)
            VALUES (%s, %s, %s, %s, %s)
        """
        return execute_insert(sql, (
            room.alliance_id,
            room.creator_user_id,
            room.title,
            room.status,
            room.max_participants,
        ))

    def get_training_rooms(self, alliance_id: int) -> List[AllianceTrainingRoom]:
        sql = """
            SELECT id, alliance_id, creator_user_id, title, status, max_participants, created_at, completed_at
            FROM alliance_training_rooms
            WHERE alliance_id = %s
            ORDER BY status DESC, created_at DESC
        """
        rows = execute_query(sql, (alliance_id,))
        return [self._map_row_to_training_room(row) for row in rows]

    def get_training_room_by_id(self, room_id: int) -> Optional[AllianceTrainingRoom]:
        sql = """
            SELECT id, alliance_id, creator_user_id, title, status, max_participants, created_at, completed_at
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

    def update_alliance_resources(self, alliance_id: int, funds_delta: int = 0, prosperity_delta: int = 0) -> None:
        sql = "UPDATE alliances SET funds = GREATEST(0, funds + %s), prosperity = GREATEST(0, prosperity + %s) WHERE id = %s"
        execute_update(sql, (funds_delta, prosperity_delta, alliance_id))

    def update_member_contribution(self, user_id: int, delta: int) -> None:
        sql = "UPDATE alliance_members SET contribution = contribution + %s WHERE user_id = %s"
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
        sql = """
            SELECT a.id, a.name, a.level, 
                   COALESCE(SUM(r.cost), 0) as total_merit
            FROM alliances a
            JOIN alliance_land_registration r ON a.id = r.alliance_id
            WHERE r.registration_time >= %s
            GROUP BY a.id, a.name, a.level
            ORDER BY total_merit DESC
            LIMIT %s OFFSET %s
        """
        return execute_query(sql, (since, limit, offset))

    def count_alliance_war_leaderboard(self, since: datetime) -> int:
        sql = """
            SELECT COUNT(DISTINCT alliance_id) as cnt
            FROM alliance_land_registration
            WHERE registration_time >= %s
        """
        rows = execute_query(sql, (since,))
        return rows[0]['cnt'] if rows else 0

    def get_alliance_war_leaderboard_entry(self, alliance_id: int, since: datetime) -> Optional[Dict]:
        # 该条目用于“盟战排行榜：指定联盟的名次与分数”
        sql = """
            SELECT
                t.alliance_id,
                t.name,
                t.score,
                DENSE_RANK() OVER (ORDER BY t.score DESC, t.alliance_id ASC) AS rank
            FROM (
                SELECT
                    a.id AS alliance_id,
                    a.name,
                    COALESCE(SUM(r.cost), 0) AS score
                FROM alliances a
                JOIN alliance_land_registration r ON a.id = r.alliance_id
                WHERE r.registration_time >= %s
                GROUP BY a.id, a.name
            ) t
            WHERE t.alliance_id = %s
        """
        rows = execute_query(sql, (since, alliance_id))
        if not rows:
            return None
        row = rows[0]
        return {
            "rank": row["rank"],
            "alliance_id": row["alliance_id"],
            "alliance_name": row["name"],
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
