from __future__ import annotations

import random
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol, Tuple

from domain.entities.alliance import AllianceArmyAssignment
from domain.entities.alliance_battle import (
    AllianceArmySignup,
    AllianceLandBattle,
    AllianceLandBattleDuel,
    AllianceLandBattleRound,
)
from domain.entities.alliance_registration import (
    AllianceRegistration,
    STATUS_CONFIRMED,
    STATUS_ELIMINATED,
    STATUS_IN_BATTLE,
    STATUS_VICTOR,
)
from domain.repositories.alliance_repo import IAllianceRepo
from domain.repositories.player_repo import IPlayerRepo
from domain.services.pvp_battle_engine import PvpPlayer, run_pvp_battle
from application.services.beast_pvp_service import BeastPvpService


class PlayerBeastRepoProtocol(Protocol):
    def get_team_beasts(self, user_id: int) -> List[Any]:
        ...


SIGNUP_STATUS_READY = 1
SIGNUP_STATUS_ENGAGED = 2
SIGNUP_STATUS_ELIMINATED = 3
SIGNUP_STATUS_ADVANCED = 4


class AllianceBattleService:
    """Handles land battle preparation, pairing, and round progression."""

    def __init__(
        self,
        alliance_repo: IAllianceRepo,
        player_repo: IPlayerRepo,
        player_beast_repo: PlayerBeastRepoProtocol,
        beast_pvp_service: BeastPvpService,
    ) -> None:
        self.alliance_repo = alliance_repo
        self.player_repo = player_repo
        self.player_beast_repo = player_beast_repo
        self.beast_pvp_service = beast_pvp_service

    def lock_and_pair_land(self, land_id: int, seed: Optional[int] = None) -> dict:
        """Lock confirmed registrations on a land and pair them into battles.
        
        注意：会同时接受 STATUS_CONFIRMED (3) 和 STATUS_REGISTERED (1) 状态的报名，
        因为报名后可能直接是已报名状态，需要兼容处理。
        """
        from domain.entities.alliance_registration import STATUS_REGISTERED
        # 同时接受已确认和已报名的状态（兼容不同流程）
        registrations = self.alliance_repo.list_land_registrations_by_land(
            land_id, statuses=[STATUS_CONFIRMED, STATUS_REGISTERED]
        )
        waiting_regs = [r for r in registrations if r.bye_waiting_round is not None]
        ready_regs = [r for r in registrations if r.bye_waiting_round is None]

        if len(registrations) < 2:
            return {
                "ok": False,
                "error": "至少需要两个联盟报名才可配对",
                "bye_registrations": [
                    {
                        "registration_id": reg.id,
                        "alliance_id": reg.alliance_id,
                        "bye_waiting_round": reg.bye_waiting_round,
                        "last_bye_round": reg.last_bye_round,
                    }
                    for reg in waiting_regs
                ],
            }

        # Reactivate waiting registrations so they join the next pairing batch.
        if waiting_regs:
            for reg in waiting_regs:
                reg.bye_waiting_round = None
                self.alliance_repo.save_land_registration(reg)

        pool = ready_regs + waiting_regs

        rng = random.Random(seed if seed is not None else datetime.utcnow().timestamp())
        rng.shuffle(pool)

        bye_summary = None
        if len(pool) % 2 == 1:
            recent_bye_round = max((reg.last_bye_round or 0) for reg in pool)
            candidates = [reg for reg in pool if (reg.last_bye_round or 0) < recent_bye_round]
            if not candidates:
                candidates = pool
            bye_registration = rng.choice(candidates)
            pool.remove(bye_registration)

            next_bye_round = (max((reg.last_bye_round or 0) for reg in registrations) or 0) + 1
            bye_registration.bye_waiting_round = next_bye_round
            bye_registration.last_bye_round = next_bye_round
            self.alliance_repo.save_land_registration(bye_registration)

            bye_summary = {
                "registration_id": bye_registration.id,
                "alliance_id": bye_registration.alliance_id,
                "bye_waiting_round": bye_registration.bye_waiting_round,
            }

        battle_summaries = []
        now = datetime.utcnow()

        for idx in range(0, len(pool), 2):
            left = pool[idx]
            right = pool[idx + 1]

            battle = AllianceLandBattle(
                id=None,
                land_id=land_id,
                left_registration_id=left.id or 0,
                right_registration_id=right.id or 0,
                phase=0,
                current_round=1,
                started_at=None,
                finished_at=None,
            )
            battle_id = self.alliance_repo.create_land_battle(battle)

            left_signups = self._build_army_signups(left, now)
            right_signups = self._build_army_signups(right, now)
            
            # 检查是否有足够的参战成员
            if len(left_signups) == 0:
                raise ValueError(f"联盟 {left.alliance_id} 的 {left.army} 军队没有已签到的成员，无法参战")
            if len(right_signups) == 0:
                raise ValueError(f"联盟 {right.alliance_id} 的 {right.army} 军队没有已签到的成员，无法参战")
            
            self.alliance_repo.add_army_signups(left_signups + right_signups)

            round_record = AllianceLandBattleRound(
                id=None,
                battle_id=battle_id,
                round_no=1,
                left_alive=len(left_signups),
                right_alive=len(right_signups),
                status=0,
                started_at=now,
                finished_at=None,
            )
            self.alliance_repo.create_battle_round(round_record)

            left.status = STATUS_IN_BATTLE
            right.status = STATUS_IN_BATTLE
            self.alliance_repo.save_land_registration(left)
            self.alliance_repo.save_land_registration(right)

            battle_summaries.append(
                {
                    "battle_id": battle_id,
                    "left_alliance_id": left.alliance_id,
                    "right_alliance_id": right.alliance_id,
                    "left_count": len(left_signups),
                    "right_count": len(right_signups),
                }
            )

        result = {"ok": True, "battles": battle_summaries}
        if bye_summary:
            result["bye_allocation"] = bye_summary
        return result

    def advance_round(self, battle_id: int) -> dict:
        """Simulate the next battle round for the given battle."""

        battle = self.alliance_repo.get_land_battle_by_id(battle_id)
        if not battle:
            return {"ok": False, "error": "未找到战斗"}
        if battle.phase >= 2:
            return {"ok": False, "error": "战斗已结束"}

        rounds = self.alliance_repo.list_battle_rounds(battle_id)
        current_round = next((r for r in rounds if r.status == 0), None)
        if not current_round:
            return {"ok": False, "error": "没有进行中的回合"}

        left_registration = self.alliance_repo.get_land_registration_by_id(
            battle.left_registration_id
        )
        right_registration = self.alliance_repo.get_land_registration_by_id(
            battle.right_registration_id
        )
        if not left_registration or not right_registration:
            return {"ok": False, "error": "报名记录缺失，无法推进"}

        left_signups = self.alliance_repo.list_army_signups(left_registration.id or 0)
        right_signups = self.alliance_repo.list_army_signups(right_registration.id or 0)

        duels: List[AllianceLandBattleDuel] = []
        duel_summaries: List[dict] = []

        while True:
            left_signup = self._next_available_signup(left_signups)
            right_signup = self._next_available_signup(right_signups)
            if not left_signup or not right_signup:
                break

            duel_result = self._conduct_duel(left_signup, right_signup)
            duels.append(duel_result["entity"])
            duel_summaries.append(duel_result["summary"])

        if duels:
            self.alliance_repo.add_battle_duels(duels)

        now = datetime.utcnow()
        current_round.left_alive = self._count_alive(left_signups)
        current_round.right_alive = self._count_alive(right_signups)
        current_round.status = 1
        current_round.finished_at = now
        self.alliance_repo.update_battle_round(current_round)

        battle_started = battle.started_at or now
        if not battle.started_at:
            battle.started_at = battle_started

        round_result = {
            "round_no": current_round.round_no,
            "left_alive": current_round.left_alive,
            "right_alive": current_round.right_alive,
            "duel_count": len(duels),
            "duels": duel_summaries,
        }

        if current_round.left_alive == 0 or current_round.right_alive == 0:
            # Battle finished
            battle.phase = 2
            battle.finished_at = now
            self.alliance_repo.update_land_battle(battle)

            battle_id = battle.id or 0
            if current_round.left_alive > current_round.right_alive:
                self._finalize_registration(left_registration, STATUS_VICTOR, battle_id, right_registration.alliance_id)
                self._finalize_registration(right_registration, STATUS_ELIMINATED, battle_id, left_registration.alliance_id)
            elif current_round.right_alive > current_round.left_alive:
                self._finalize_registration(left_registration, STATUS_ELIMINATED, battle_id, right_registration.alliance_id)
                self._finalize_registration(right_registration, STATUS_VICTOR, battle_id, left_registration.alliance_id)
            else:
                # 双方同时战败
                self._finalize_registration(left_registration, STATUS_ELIMINATED, battle_id, right_registration.alliance_id)
                self._finalize_registration(right_registration, STATUS_ELIMINATED, battle_id, left_registration.alliance_id)

            return {"ok": True, "battle_finished": True, "round": round_result}

        # Prepare next round
        next_round = AllianceLandBattleRound(
            id=None,
            battle_id=battle_id,
            round_no=current_round.round_no + 1,
            left_alive=current_round.left_alive,
            right_alive=current_round.right_alive,
            status=0,
            started_at=now,
            finished_at=None,
        )
        self._reset_ready_state(left_signups)
        self._reset_ready_state(right_signups)
        self.alliance_repo.create_battle_round(next_round)

        battle.current_round = next_round.round_no
        self.alliance_repo.update_land_battle(battle)

        return {"ok": True, "battle_finished": False, "round": round_result}

    # ---------------------- Query helpers ---------------------- #

    def get_land_battle_overview(self, land_id: int) -> dict:
        battle = self.alliance_repo.get_active_battle_by_land(land_id)
        if not battle:
            return {"ok": False, "error": "当前土地没有进行中的战斗"}

        rounds = self.alliance_repo.list_battle_rounds(battle.id or 0)
        latest_round = rounds[-1] if rounds else None
        registrations = self.alliance_repo.list_land_registrations_by_land(battle.land_id)
        bye_registrations = [
            {
                "registration_id": reg.id,
                "alliance_id": reg.alliance_id,
                "bye_waiting_round": reg.bye_waiting_round,
                "last_bye_round": reg.last_bye_round,
            }
            for reg in registrations
            if reg.bye_waiting_round is not None or reg.last_bye_round
        ]

        overview = {
            "battle_id": battle.id,
            "land_id": battle.land_id,
            "phase": battle.phase,
            "current_round": battle.current_round,
            "left_registration_id": battle.left_registration_id,
            "right_registration_id": battle.right_registration_id,
            "started_at": battle.started_at.isoformat() if battle.started_at else None,
            "finished_at": battle.finished_at.isoformat() if battle.finished_at else None,
            "rounds": [
                {
                    "round_id": r.id,
                    "round_no": r.round_no,
                    "left_alive": r.left_alive,
                    "right_alive": r.right_alive,
                    "status": r.status,
                    "started_at": r.started_at.isoformat() if r.started_at else None,
                    "finished_at": r.finished_at.isoformat() if r.finished_at else None,
                }
                for r in rounds
            ],
            "bye_registrations": bye_registrations,
        }

        if latest_round:
            overview["left_alive"] = latest_round.left_alive
            overview["right_alive"] = latest_round.right_alive
        else:
            overview["left_alive"] = overview["right_alive"] = 0

        return {"ok": True, "battle": overview}

    def get_round_duels(
        self, *, battle_id: Optional[int] = None, round_no: Optional[int] = None, round_id: Optional[int] = None
    ) -> dict:
        if round_id is None:
            if battle_id is None or round_no is None:
                return {"ok": False, "error": "缺少 round_id 或 (battle_id, round_no)"}
            rounds = self.alliance_repo.list_battle_rounds(battle_id)
            target = next((r for r in rounds if r.round_no == round_no), None)
            if not target:
                return {"ok": False, "error": "指定回合不存在"}
            round_id = target.id
        else:
            target = self.alliance_repo.get_battle_round_by_id(round_id)
            if not target:
                return {"ok": False, "error": "指定回合不存在"}

        duels = self.alliance_repo.list_duels_by_round(round_id)
        formatted = []
        for duel in duels:
            log_data = duel.log_data or {}
            formatted.append(
                {
                    "duel_id": duel.id,
                    "attacker_signup_id": duel.attacker_signup_id,
                    "defender_signup_id": duel.defender_signup_id,
                    "attacker_result": duel.attacker_result,
                    "logs": log_data.get("logs", []),
                    "reason": log_data.get("reason", ""),
                    "created_at": duel.created_at.isoformat() if duel.created_at else None,
                }
            )

        return {
            "ok": True,
            "round": {
                "round_id": round_id,
                "battle_id": target.battle_id,
                "round_no": target.round_no,
                "left_alive": target.left_alive,
                "right_alive": target.right_alive,
                "status": target.status,
            },
            "duels": formatted,
        }

    # ---------------------- Internal helpers ---------------------- #

    def _build_army_signups(
        self, registration: AllianceRegistration, timestamp: datetime
    ) -> List[AllianceArmySignup]:
        """构建参战成员列表，只包含已签到的成员"""
        assignments = self.alliance_repo.get_army_assignments(registration.alliance_id)
        filtered: List[AllianceArmyAssignment] = [
            assign for assign in assignments if assign.army == registration.army
        ]
        
        # 检查成员是否已签到（根据规则，只有已签到的成员才能参战）
        now = datetime.utcnow()
        weekday = now.weekday()
        war_phase = "first" if weekday <= 2 else "second"  # 周一-周三为第一次，周四-周六为第二次
        checkin_date = now.date()
        
        checked_in_assignments: List[AllianceArmyAssignment] = []
        for assign in filtered:
            # 检查该成员是否已签到
            if self.alliance_repo.has_war_checkin(
                registration.alliance_id, 
                assign.user_id, 
                war_phase, 
                weekday, 
                checkin_date
            ):
                checked_in_assignments.append(assign)
        
        signups: List[AllianceArmySignup] = []
        for order, assign in enumerate(checked_in_assignments, start=1):
            signups.append(
                AllianceArmySignup(
                    id=None,
                    registration_id=registration.id or 0,
                    alliance_id=registration.alliance_id,
                    army=registration.army or "",
                    user_id=assign.user_id,
                    signup_order=order,
                    hp_state=None,
                    status=SIGNUP_STATUS_READY,
                    created_at=timestamp,
                )
            )
        return signups

    def _next_available_signup(
        self, signups: List[AllianceArmySignup]
    ) -> Optional[AllianceArmySignup]:
        ready = [
            s
            for s in signups
            if s.status in (SIGNUP_STATUS_READY, SIGNUP_STATUS_ADVANCED)
        ]
        ready.sort(key=lambda s: (s.signup_order, s.id or 0))
        if not ready:
            return None
        signup = ready[0]
        self._update_signup_state(signup, SIGNUP_STATUS_ENGAGED, signup.hp_state)
        return signup

    def _conduct_duel(
        self, left_signup: AllianceArmySignup, right_signup: AllianceArmySignup
    ) -> Dict[str, Any]:
        left_player = self._build_pvp_player(left_signup)
        right_player = self._build_pvp_player(right_signup)

        if not left_player["beasts"] and not right_player["beasts"]:
            # 双方无兵，随机判负
            winner = random.choice(["left", "right"])
            loser = "right" if winner == "left" else "left"
            return self._finalize_duel(
                left_signup,
                right_signup,
                winner_side=winner,
                logs=[],
                reason="双方无参战幻兽，随机判负",
            )

        if not left_player["beasts"]:
            return self._finalize_duel(
                left_signup,
                right_signup,
                winner_side="right",
                logs=[],
                reason="对手无人参战，直接获胜",
            )

        if not right_player["beasts"]:
            return self._finalize_duel(
                left_signup,
                right_signup,
                winner_side="left",
                logs=[],
                reason="对手无人参战，直接获胜",
            )

        pvp_result = run_pvp_battle(
            left_player["pvp_player"],
            right_player["pvp_player"],
            max_log_turns=50,
        )
        winner_side = (
            "left"
            if pvp_result.winner_player_id == left_player["pvp_player"].player_id
            else "right"
        )

        logs_payload = [log.__dict__ for log in pvp_result.logs]
        return self._finalize_duel(
            left_signup,
            right_signup,
            winner_side=winner_side,
            logs=logs_payload,
            reason="",
        )

    def _finalize_duel(
        self,
        left_signup: AllianceArmySignup,
        right_signup: AllianceArmySignup,
        *,
        winner_side: str,
        logs: List[dict],
        reason: str,
    ) -> Dict[str, Any]:
        winner_signup = left_signup if winner_side == "left" else right_signup
        loser_signup = right_signup if winner_side == "left" else left_signup

        winner_state = self._capture_hp_state(winner_signup)
        loser_state = self._capture_hp_state(loser_signup)

        self._update_signup_state(winner_signup, SIGNUP_STATUS_ADVANCED, winner_state)
        self._update_signup_state(loser_signup, SIGNUP_STATUS_ELIMINATED, loser_state)

        duel_entity = AllianceLandBattleDuel(
            id=None,
            round_id=0,  # 将在仓储层 INSERT 时自动关联
            attacker_signup_id=left_signup.id or 0,
            defender_signup_id=right_signup.id or 0,
            attacker_result=1 if winner_side == "left" else 2,
            log_data={"logs": logs, "reason": reason},
            created_at=datetime.utcnow(),
        )

        duel_summary = {
            "winner_signup_id": winner_signup.id,
            "winner_user_id": winner_signup.user_id,
            "loser_signup_id": loser_signup.id,
            "logs": logs,
            "reason": reason,
        }
        return {"entity": duel_entity, "summary": duel_summary}

    def _capture_hp_state(self, signup: AllianceArmySignup) -> Dict[str, Any]:
        # After combat, the PvpPlayer objects have updated HP. We store the latest HP snapshot.
        state = signup.hp_state or {}
        beasts_state = state.get("beasts", [])
        return {"beasts": beasts_state}

    def _build_pvp_player(self, signup: AllianceArmySignup) -> Dict[str, Any]:
        player = self.player_repo.get_by_id(signup.user_id)
        if not player:
            return {"beasts": [], "pvp_player": PvpPlayer(player_id=signup.user_id, level=1, beasts=[])}

        team_beasts = self.player_beast_repo.get_team_beasts(signup.user_id)
        pvp_beasts = self.beast_pvp_service.to_pvp_beasts(team_beasts)

        hp_map = {}
        if signup.hp_state and "beasts" in signup.hp_state:
            hp_map = {item["id"]: item.get("hp", 0) for item in signup.hp_state["beasts"]}
        beasts_state: List[dict] = []
        for beast in pvp_beasts:
            if hp_map:
                stored_hp = hp_map.get(beast.id)
                if stored_hp is not None:
                    beast.hp_current = max(0, min(beast.hp_max, stored_hp))
                    if beast.hp_current == 0:
                        beast.is_dead = True
            beasts_state.append({"id": beast.id, "hp": beast.hp_current})

        signup.hp_state = {"beasts": beasts_state}
        return {
            "beasts": pvp_beasts,
            "pvp_player": PvpPlayer(
                player_id=player.user_id,
                level=player.level or 1,
                beasts=pvp_beasts,
                name=player.nickname or f"玩家{player.user_id}",
            ),
        }

    def _update_signup_state(
        self, signup: AllianceArmySignup, status: int, hp_state: Optional[dict]
    ) -> None:
        signup.status = status
        signup.hp_state = hp_state
        if signup.id:
            self.alliance_repo.update_army_signup_state(signup.id, status, hp_state or {})

    def _count_alive(self, signups: List[AllianceArmySignup]) -> int:
        return sum(1 for s in signups if s.status != SIGNUP_STATUS_ELIMINATED)

    def _reset_ready_state(self, signups: List[AllianceArmySignup]) -> None:
        for signup in signups:
            if signup.status == SIGNUP_STATUS_ADVANCED:
                self._update_signup_state(signup, SIGNUP_STATUS_READY, signup.hp_state)

    def _finalize_registration(self, registration: AllianceRegistration, status: int, battle_id: Optional[int] = None, opponent_alliance_id: Optional[int] = None) -> None:
        registration.status = status
        self.alliance_repo.save_land_registration(registration)
        if status == STATUS_VICTOR:
            # 记录战绩
            now = datetime.utcnow()
            war_date = now.date()
            # 判断是第一次还是第二次盟战
            weekday = now.weekday()
            if weekday <= 2:  # 周一-周三
                war_phase = "first"
            else:  # 周四-周六
                war_phase = "second"
            
            if battle_id and opponent_alliance_id:
                army_type = registration.army or "dragon"
                self.alliance_repo.add_war_battle_record(
                    registration.alliance_id, opponent_alliance_id, registration.land_id,
                    army_type, war_phase, war_date, "win", 1, battle_id
                )
                
                # 记录失败方战绩
                self.alliance_repo.add_war_battle_record(
                    opponent_alliance_id, registration.alliance_id, registration.land_id,
                    army_type, war_phase, war_date, "lose", 0, battle_id
                )
            
            # 每场对战胜利都获得1个联盟战功（规则②：A联盟和B联盟对战，胜利的联盟获得1个联盟战功）
            from infrastructure.db.connection import execute_update
            execute_update(
                "UPDATE alliances SET war_honor = war_honor + 1, war_honor_history = war_honor_history + 1 WHERE id = %s",
                (registration.alliance_id,)
            )
            
            # 检查是否是最终胜利者（该土地/据点没有其他活跃的报名或胜利者）
            all_registrations = self.alliance_repo.list_land_registrations_by_land(registration.land_id)
            active_registrations = [r for r in all_registrations if (r.is_active() or r.status == STATUS_VICTOR) and r.id != registration.id]
            
            # 如果没有其他活跃的报名或胜利者，说明是最终胜利者（规则③：最终胜利者占领土地）
            # 注意：这个检查在 run_land_battle 中也会进行，这里作为备用检查
            # 如果 run_land_battle 正确执行，这里不会触发（因为会有多个胜利者）
            if not active_registrations:
                # 更新赛季积分
                season_key = datetime.utcnow().strftime("%Y-%m")
                self.alliance_repo.increment_alliance_war_score(registration.alliance_id, season_key, 1)
                
                # 设置土地占领（只有最终胜利者才能占领）
                self.alliance_repo.set_land_occupation(registration.land_id, registration.alliance_id, war_phase, war_date)
