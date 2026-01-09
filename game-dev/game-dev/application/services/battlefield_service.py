from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
import random

from infrastructure.db.connection import execute_query, execute_update
from infrastructure.db.player_beast_repo_mysql import MySQLPlayerBeastRepo, PlayerBeastData
from infrastructure.db.battlefield_repo_mysql import MySQLBattlefieldBattleRepo
from domain.repositories.player_repo import IPlayerRepo
from domain.services.pvp_battle_engine import PvpBeast, PvpPlayer, run_pvp_battle
from domain.services.skill_system import apply_buff_debuff_skills
from application.services.beast_pvp_service import BeastPvpService


# 与 tests/test_battlefield.py 中保持一致的战场类型配置
BATTLEFIELD_TYPES: Dict[str, Dict] = {
    "tiger": {"name": "猛虎战场", "level_range": (20, 39), "title": "猛虎战王"},
    "crane": {"name": "飞鹤战场", "level_range": (40, 100), "title": "飞鹤战王"},
}


@dataclass
class BattlefieldParticipant:
    """报名参与战场的玩家快照（不直接暴露给前端）。"""

    user_id: int
    nickname: str
    level: int
    team: str = ""  # "red" / "blue"


class BattlefieldService:
    """古战场自动匹配 + 战报生成服务。

    主要职责：
    - 根据战场类型，自动筛选符合等级范围的玩家作为参赛者（后续可改为真正的“报名表”）。
    - 按淘汰赛规则自动匹配对战，使用统一 PVP+技能战斗引擎决出胜负。
    - 为每一场对战生成与镇妖/擂台相同结构的 battle_data，并写入 battlefield_battle_log。
    - 根据战报统计上一期的战王和玩家个人战绩，用于战场首页展示。
    """

    def __init__(
        self,
        *,
        player_repo: IPlayerRepo,
        player_beast_repo: MySQLPlayerBeastRepo,
        beast_pvp_service: BeastPvpService | None = None,
        battle_repo: Optional[MySQLBattlefieldBattleRepo] = None,
    ) -> None:
        self.player_repo = player_repo
        self.player_beast_repo = player_beast_repo
        self.beast_pvp_service = beast_pvp_service
        self.battle_repo = battle_repo or MySQLBattlefieldBattleRepo()

    # ------------------------------------------------------------------
    # 对外主入口
    # ------------------------------------------------------------------

    def run_tournament(self, battlefield_type: str) -> Dict:
        """为指定战场类型运行一整期淘汰赛并写入所有战报。

        返回简单汇总信息：期数、参赛人数、冠军等。
        """

        cfg = BATTLEFIELD_TYPES.get(battlefield_type)
        if not cfg:
            raise ValueError(f"未知战场类型: {battlefield_type}")

        participants = self._get_participants_for_type(battlefield_type)
        if len(participants) < 2:
            return {"ok": False, "error": "参赛玩家不足，至少需要2人"}

        # 分配阵营（简单按人数对半分红/蓝）
        random.shuffle(participants)
        half = len(participants) // 2
        for idx, p in enumerate(participants):
            p.team = "red" if idx < half else "blue"

        last_period = self.battle_repo.get_latest_period(battlefield_type) or 0
        period = last_period + 1

        remaining: List[BattlefieldParticipant] = participants[:]
        next_round: List[BattlefieldParticipant] = []

        round_num = 0
        wins_count: Dict[int, int] = defaultdict(int)

        while len(remaining) > 1:
            round_num += 1
            match_num = 0
            next_round.clear()

            # 处理轮空：若为奇数人，随机挑一人直接晋级
            temp_players = remaining[:]
            bye_player: Optional[BattlefieldParticipant] = None
            if len(temp_players) % 2 == 1:
                bye_index = random.randint(0, len(temp_players) - 1)
                bye_player = temp_players.pop(bye_index)
                next_round.append(bye_player)

            random.shuffle(temp_players)

            for i in range(0, len(temp_players), 2):
                p1 = temp_players[i]
                p2 = temp_players[i + 1]
                match_num += 1

                battle_result = self._run_single_battle(
                    battlefield_type=battlefield_type,
                    period=period,
                    round_num=round_num,
                    match_num=match_num,
                    first=p1,
                    second=p2,
                )

                winner = battle_result["winner"]
                wins_count[winner.user_id] += 1
                next_round.append(winner)

            remaining = next_round[:]

        champion = remaining[0]
        champion_wins = wins_count.get(champion.user_id, 0)

        # 本期结束后清理当日该战场类型的报名记录
        try:
            execute_update(
                "DELETE FROM battlefield_signup WHERE battlefield_type = %s AND signup_date = CURDATE()",
                (battlefield_type,),
            )
        except Exception:
            # 清理失败不影响战报生成
            pass

        return {
            "ok": True,
            "battlefield_type": battlefield_type,
            "period": period,
            "total_players": len(participants),
            "total_rounds": round_num,
            "champion_id": champion.user_id,
            "champion_name": champion.nickname,
            "champion_team": champion.team,
            "champion_wins": champion_wins,
        }

    # ------------------------------------------------------------------
    # 战场首页信息聚合
    # ------------------------------------------------------------------

    def get_last_and_my_result(self, user_id: int) -> Tuple[Dict, Dict]:
        """根据 battlefield_battle_log 汇总上一期战王和当前玩家战绩。

        返回 (last_result, my_result)：
        last_result: {
            period: int,
            tigerKing: { name, team, kills },
            craneKing: { name, team, kills },
            kingReward: str,
        }

        my_result: {
            period: int,
            team: str,
            won: bool,
            kills: int,
            campReward: str,
            killReward: str,
        }
        """

        last_periods: Dict[str, Optional[int]] = {}
        champions: Dict[str, Dict] = {}
        user_stats: Dict[str, Dict] = {}

        for bf_type in ("tiger", "crane"):
            period = self.battle_repo.get_latest_period(bf_type)
            last_periods[bf_type] = period
            if not period:
                continue

            logs = self.battle_repo.get_matches_for_period(bf_type, period)
            if not logs:
                continue

            # 统计每个玩家的胜场数
            wins = defaultdict(int)
            team_by_user: Dict[int, str] = {}
            for log in logs:
                winner_id = log.first_user_id if log.is_first_win else log.second_user_id
                wins[winner_id] += 1
                team_by_user[log.first_user_id] = log.first_user_team or ""
                team_by_user[log.second_user_id] = log.second_user_team or ""

            if not wins:
                continue

            champ_id = max(wins.keys(), key=lambda uid: wins[uid])
            champ_name = None
            for log in logs:
                if log.first_user_id == champ_id:
                    champ_name = log.first_user_name
                    break
                if log.second_user_id == champ_id:
                    champ_name = log.second_user_name
                    break

            champions[bf_type] = {
                "name": champ_name or f"玩家{champ_id}",
                "team": team_by_user.get(champ_id, ""),
                "kills": wins[champ_id],
            }

            # 当前玩家数据
            if user_id:
                kills = wins.get(user_id, 0)
                user_team = team_by_user.get(user_id, "")
                user_stats[bf_type] = {
                    "period": period,
                    "team": user_team,
                    "kills": kills,
                }

        # last_result：取任一已有期数（优先 tiger），否则为 0
        period = last_periods.get("tiger") or last_periods.get("crane") or 0

        last_result = {
            "period": period or 0,
            "tigerKing": champions.get("tiger", {"name": "", "team": "", "kills": 0}),
            "craneKing": champions.get("crane", {"name": "", "team": "", "kills": 0}),
            "kingReward": "战王宝藏",
        }

        # 个人战绩：优先使用猛虎战场的数据
        my_type = "tiger" if "tiger" in user_stats else "crane" if "crane" in user_stats else None
        if my_type is None:
            my_result = {
                "period": period or 0,
                "team": "",
                "won": False,
                "kills": 0,
                "campReward": "",
                "killReward": "",
            }
        else:
            s = user_stats[my_type]
            # 简单规则：和冠军同队则阵营胜利
            champ = champions.get(my_type, {})
            camp_win = bool(s.get("team") and champ and s.get("team") == champ.get("team"))

            # 奖励描述可以后续接入真实配置，这里先给示例文本
            camp_reward = "胜利阵营奖励" if camp_win else "失败阵营安慰奖"
            kill_reward = f"击杀{ s['kills'] }人，获得杀戮礼包" if s["kills"] > 0 else "无杀戮奖励"

            my_result = {
                "period": s["period"],
                "team": s.get("team", ""),
                "won": camp_win,
                "kills": s["kills"],
                "campReward": camp_reward,
                "killReward": kill_reward,
            }

        return last_result, my_result

    # ------------------------------------------------------------------
    # 内部工具：筛选玩家、转换幻兽、单场对战
    # ------------------------------------------------------------------

    def _get_participants_for_type(self, battlefield_type: str) -> List[BattlefieldParticipant]:
        """根据战场类型筛选符合等级范围的玩家作为参赛者。

        目前简单按 player.level 落在对应区间的所有玩家视为“已报名”。
        后续如有单独报名表，可在此替换为从报名表读取。
        """

        cfg = BATTLEFIELD_TYPES[battlefield_type]
        min_lv, max_lv = cfg["level_range"]

        rows = execute_query(
            """
            SELECT p.user_id, p.nickname, p.level
            FROM battlefield_signup s
            JOIN player p ON p.user_id = s.user_id
            WHERE s.battlefield_type = %s
              AND s.signup_date = CURDATE()
              AND p.level BETWEEN %s AND %s
            """,
            (battlefield_type, min_lv, max_lv),
        )
        participants: List[BattlefieldParticipant] = []
        for row in rows:
            participants.append(
                BattlefieldParticipant(
                    user_id=row["user_id"],
                    nickname=row.get("nickname") or f"玩家{row['user_id']}",
                    level=row.get("level", 1),
                )
            )
        return participants


    def _build_battle_data(self, pvp_result, attacker_player: PvpPlayer, defender_player: PvpPlayer) -> Dict:
        """根据 PvpBattleResult 构建战报数据结构（与擂台/镇妖保持一致）。"""

        attacker_name = attacker_player.name or str(attacker_player.player_id)
        defender_name = defender_player.name or str(defender_player.player_id)

        def get_player_name(pid: int) -> str:
            return attacker_name if pid == attacker_player.player_id else defender_name

        def get_side_flag(pid: int) -> str:
            return "attacker" if pid == attacker_player.player_id else "defender"

        def build_battle_segment(battle_index: int, seg_logs):
            if not seg_logs:
                return {
                    "battle_num": battle_index,
                    "attacker_beast": "",
                    "defender_beast": "",
                    "winner": "defender",
                    "rounds": [],
                    "result": "",
                }

            rounds = []
            for idx, log in enumerate(seg_logs, start=1):
                rounds.append({
                    "round": idx,
                    "action": log.description,
                    "a_hp": log.attacker_hp_after,
                    "d_hp": log.defender_hp_after,
                })

            beast_state: Dict[Tuple[int, int], Tuple[str, int]] = {}
            for log in seg_logs:
                if log.attacker_beast_id != 0:
                    beast_state[(log.attacker_player_id, log.attacker_beast_id)] = (
                        log.attacker_name,
                        log.attacker_hp_after,
                    )
                if log.defender_beast_id != 0:
                    beast_state[(log.defender_player_id, log.defender_beast_id)] = (
                        log.defender_name,
                        log.defender_hp_after,
                    )

            winner_player_id = pvp_result.winner_player_id
            loser_player_id = (
                attacker_player.player_id
                if winner_player_id == defender_player.player_id
                else defender_player.player_id
            )
            winner_beast_name = ""
            loser_beast_name = ""
            winner_hp = 0

            keys = list(beast_state.keys())
            if keys:
                if len(keys) == 1:
                    keys = keys * 2
                (p1, b1), (p2, b2) = keys[0], keys[1]
                name1, hp1 = beast_state[(p1, b1)]
                name2, hp2 = beast_state[(p2, b2)]

                if hp1 > 0 and hp2 <= 0:
                    winner_player_id, loser_player_id = p1, p2
                    winner_beast_name, winner_hp = name1, hp1
                    loser_beast_name = name2
                elif hp2 > 0 and hp1 <= 0:
                    winner_player_id, loser_player_id = p2, p1
                    winner_beast_name, winner_hp = name2, hp2
                    loser_beast_name = name1
                elif hp1 != hp2:
                    if hp1 > hp2:
                        winner_player_id, loser_player_id = p1, p2
                        winner_beast_name, winner_hp = name1, hp1
                        loser_beast_name = name2
                    else:
                        winner_player_id, loser_player_id = p2, p1
                        winner_beast_name, winner_hp = name2, hp2
                        loser_beast_name = name1

            winner_player_name = get_player_name(winner_player_id)
            winner_flag = get_side_flag(winner_player_id)

            if winner_beast_name and loser_beast_name:
                result_text = f"『{winner_player_name}』的{winner_beast_name}获胜，剩余气血{winner_hp}"
            else:
                result_text = f"『{winner_player_name}』获胜"

            return {
                "battle_num": battle_index,
                "attacker_beast": "",
                "defender_beast": "",
                "winner": winner_flag,
                "rounds": rounds,
                "result": result_text,
            }

        battles = []
        current_pair = None
        current_logs = []

        for log in pvp_result.logs:
            if log.attacker_beast_id == 0 and current_pair is not None:
                current_logs.append(log)
                continue

            pair = frozenset({log.attacker_beast_id, log.defender_beast_id})

            if current_pair is None:
                current_pair = pair
                current_logs.append(log)
            elif pair == current_pair:
                current_logs.append(log)
            else:
                battles.append(build_battle_segment(len(battles) + 1, current_logs))
                current_pair = pair
                current_logs = [log]

        if current_logs:
            battles.append(build_battle_segment(len(battles) + 1, current_logs))

        is_victory = pvp_result.winner_player_id == attacker_player.player_id
        attacker_wins = 1 if is_victory else 0
        defender_wins = 1 - attacker_wins

        return {
            "is_victory": is_victory,
            "attacker_wins": attacker_wins,
            "defender_wins": defender_wins,
            "battles": battles,
        }

    def _run_single_battle(
        self,
        *,
        battlefield_type: str,
        period: int,
        round_num: int,
        match_num: int,
        first: BattlefieldParticipant,
        second: BattlefieldParticipant,
    ) -> Dict:
        """执行一场玩家 vs 玩家 对战，并写入 battlefield_battle_log。

        返回 winner 这个 BattlefieldParticipant。
        """

        beasts1 = self.player_beast_repo.get_team_beasts(first.user_id)
        beasts2 = self.player_beast_repo.get_team_beasts(second.user_id)

        # 若某一方没有出战幻兽，则判为直接失败
        if not beasts1 and not beasts2:
            # 都没有，直接随机一方胜利
            winner = random.choice([first, second])
            loser = second if winner is first else first
            is_first_win = winner is first
            battle_data = {
                "is_victory": is_first_win,
                "attacker_wins": 1 if is_first_win else 0,
                "defender_wins": 0 if is_first_win else 1,
                "battles": [],
            }
        elif not beasts1:
            winner = second
            loser = first
            is_first_win = False
            battle_data = {
                "is_victory": False,
                "attacker_wins": 0,
                "defender_wins": 1,
                "battles": [],
            }
        elif not beasts2:
            winner = first
            loser = second
            is_first_win = True
            battle_data = {
                "is_victory": True,
                "attacker_wins": 1,
                "defender_wins": 0,
                "battles": [],
            }
        else:
            pvp_beasts1 = self.beast_pvp_service.to_pvp_beasts(beasts1)
            pvp_beasts2 = self.beast_pvp_service.to_pvp_beasts(beasts2)

            attacker_player = PvpPlayer(
                player_id=first.user_id,
                level=first.level,
                beasts=pvp_beasts1,
                name=first.nickname,
            )
            defender_player = PvpPlayer(
                player_id=second.user_id,
                level=second.level,
                beasts=pvp_beasts2,
                name=second.nickname,
            )

            pvp_result = run_pvp_battle(attacker_player, defender_player, max_log_turns=50)
            is_first_win = pvp_result.winner_player_id == first.user_id
            winner = first if is_first_win else second
            loser = second if is_first_win else first

            battle_data = self._build_battle_data(pvp_result, attacker_player, defender_player)

        # 胜负标签：先简单用 “胜利/失败”，后续可根据剩余血量细分小胜/完美胜利
        result_label = "胜利" if is_first_win else "失败"

        # 写入战报表
        self.battle_repo.save_battle(
            battlefield_type=battlefield_type,
            period=period,
            round_num=round_num,
            match_num=match_num,
            first_user_id=first.user_id,
            first_user_name=first.nickname,
            second_user_id=second.user_id,
            second_user_name=second.nickname,
            first_user_team=first.team,
            second_user_team=second.team,
            is_first_win=is_first_win,
            result_label=result_label,
            battle_data=battle_data,
        )

        return {"winner": winner, "loser": loser, "is_first_win": is_first_win}
