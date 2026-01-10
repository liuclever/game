from __future__ import annotations

from dataclasses import asdict
from datetime import date, datetime
from typing import Any, Dict, List, Optional
import random

from domain.entities.dragonpalace import DragonPalaceDailyState, DragonPalaceStageState
from domain.repositories.dragonpalace_repo import IDragonPalaceRepo
from domain.rules.dragonpalace_rules import is_dragonpalace_open, pick_dragonpalace_reward_item_id
from domain.services.pvp_battle_engine import PvpPlayer, PvpBeast, run_pvp_battle
from domain.services.skill_system import apply_buff_debuff_skills
from infrastructure.config.dragonpalace_config import get_dragonpalace_config


class DragonPalaceError(Exception):
    pass


def _to_pvp_beasts_from_config(config_beasts: list) -> List[PvpBeast]:
    """将配置中的敌方幻兽转换为 PvpBeast。"""
    beasts: List[PvpBeast] = []
    for i, b in enumerate(config_beasts):
        stats = b.get("stats", {}) or {}
        attack_type = (b.get("attack_type", "physical") or "physical").strip()
        if attack_type == "magical":
            attack_type = "magic"

        hp = int(stats.get("hp", 0) or 0)
        atk = int(stats.get("atk", 0) or 0)
        pd = int(stats.get("def", 0) or 0)
        md = int(stats.get("mdef", 0) or 0)
        spd = int(stats.get("speed", 0) or 0)
        skills = b.get("skills", []) or []

        pa = atk if attack_type == "physical" else 0
        ma = atk if attack_type == "magic" else 0

        (f_hp, f_pa, f_ma, f_pd, f_md, f_spd, spec) = apply_buff_debuff_skills(
            skills=skills,
            attack_type=attack_type,
            raw_hp=hp,
            raw_physical_attack=pa,
            raw_magic_attack=ma,
            raw_physical_defense=pd,
            raw_magic_defense=md,
            raw_speed=spd,
        )

        beasts.append(
            PvpBeast(
                id=-(i + 1),
                name=str(b.get("name") or f"敌人{i+1}"),
                hp_max=f_hp,
                hp_current=f_hp,
                physical_attack=f_pa,
                magic_attack=f_ma,
                physical_defense=f_pd,
                magic_defense=f_md,
                speed=f_spd,
                attack_type=attack_type,
                skills=skills,
                poison_enhance=spec.get("poison_enhance", 0.0),
                critical_resist=spec.get("critical_resist", 0.0),
                immune_counter=bool(spec.get("immune_counter", False)),
                poison_resist=spec.get("poison_resist", 0.0),
            )
        )
    return beasts


def _format_battle_result(pvp_result, attacker_name: str, defender_name: str) -> List[Dict[str, Any]]:
    """将 PvpBattleResult 转换为前端“详细战报”页使用的 battles 结构（复用 DungeonDetailReportPage 的展示）。"""

    def build_segment(battle_idx: int, logs: list) -> Optional[Dict[str, Any]]:
        if not logs:
            return None
        rounds = []
        for idx, log in enumerate(logs, start=1):
            rounds.append(
                {
                    "round": idx,
                    "action": log.description,
                    "a_hp": log.attacker_hp_after,
                    "d_hp": log.defender_hp_after,
                }
            )
        last = logs[-1]
        log_attacker_owner = attacker_name if last.attacker_player_id != 0 else defender_name
        log_defender_owner = attacker_name if last.defender_player_id != 0 else defender_name
        if last.defender_hp_after <= 0:
            res_text = f"『{log_defender_owner}』的{last.defender_name}阵亡，『{log_attacker_owner}』的{last.attacker_name}获胜"
        else:
            res_text = f"『{log_attacker_owner}』的{last.attacker_name}阵亡，『{log_defender_owner}』的{last.defender_name}获胜"
        return {"battle_num": battle_idx, "winner": "", "rounds": rounds, "result": res_text}

    battles: List[Dict[str, Any]] = []
    current_pair = None
    current_logs = []
    for log in pvp_result.logs:
        pair = frozenset({log.attacker_beast_id, log.defender_beast_id})
        if current_pair is None:
            current_pair = pair
            current_logs.append(log)
        elif pair == current_pair:
            current_logs.append(log)
        else:
            seg = build_segment(len(battles) + 1, current_logs)
            if seg:
                battles.append(seg)
            current_pair = pair
            current_logs = [log]
    if current_logs:
        seg = build_segment(len(battles) + 1, current_logs)
        if seg:
            battles.append(seg)
    return battles


class DragonPalaceService:
    def __init__(
        self,
        dragonpalace_repo: IDragonPalaceRepo,
        player_repo,
        player_beast_repo,
        beast_pvp_service,
        inventory_service,
        item_repo,
    ):
        self.repo = dragonpalace_repo
        self.player_repo = player_repo
        self.player_beast_repo = player_beast_repo
        self.beast_pvp_service = beast_pvp_service
        self.inventory_service = inventory_service
        self.item_repo = item_repo

    def _get_or_init_today(self, user_id: int, today: date) -> DragonPalaceDailyState:
        st = self.repo.get_daily_state(user_id, today)
        if st is not None:
            return st
        return DragonPalaceDailyState(user_id=user_id, play_date=today)

    def get_status(self, user_id: int, now: Optional[datetime] = None) -> Dict[str, Any]:
        if now is None:
            now = datetime.now()
        cfg = get_dragonpalace_config()
        today = now.date()

        open_ok = is_dragonpalace_open(now)
        st = self._get_or_init_today(user_id, today)

        stages = cfg.get("stages", []) or []
        max_resets = int(cfg.get("max_resets_per_day", 2) or 2)
        reset_cost = int(cfg.get("reset_cost_yuanbao", 200) or 200)

        # 今日挑战：按示例固定显示 1 次免费（分母=1）
        today_used = 1 if st.status != "not_started" else 0

        def stage_line(s: DragonPalaceStageState) -> Dict[str, Any]:
            reward_name = ""
            if s.reward_item_id:
                item = self.item_repo.get_by_id(int(s.reward_item_id))
                reward_name = getattr(item, "name", "") if item else ""
            return {
                "stage": s.stage,
                "success": bool(s.success),
                "reward_claimed": bool(s.reward_claimed),
                "can_claim": bool(s.success and (not s.reward_claimed) and s.reward_item_id),
                "has_report": bool(s.report),
                "reward_item_name": reward_name,
            }

        return {
            "ok": True,
            "open": bool(open_ok),
            "open_time_text": "10:00-24:00",
            "today_used": int(today_used),
            "today_free": 1,
            "resets_used": int(st.resets_used),
            "max_resets": int(max_resets),
            "reset_cost_yuanbao": int(reset_cost),
            "status": str(st.status),
            "current_stage": int(st.current_stage),
            "stages": [
                {"stage": int(x.get("stage")), "recommend_level": int(x.get("recommend_level")), "name": str(x.get("name"))}
                for x in stages
            ],
            "history": [stage_line(st.stage1), stage_line(st.stage2), stage_line(st.stage3)],
        }

    def reset_today(self, user_id: int, now: Optional[datetime] = None) -> Dict[str, Any]:
        if now is None:
            now = datetime.now()
        if not is_dragonpalace_open(now):
            raise DragonPalaceError("活动未开放（10:00-24:00）")

        cfg = get_dragonpalace_config()
        max_resets = int(cfg.get("max_resets_per_day", 2) or 2)
        reset_cost = int(cfg.get("reset_cost_yuanbao", 200) or 200)

        today = now.date()
        st = self._get_or_init_today(user_id, today)

        if st.resets_used >= max_resets:
            raise DragonPalaceError("今日重置次数已达上限")

        player = self.player_repo.get_by_id(user_id)
        if player is None:
            raise DragonPalaceError("玩家不存在")
        if int(getattr(player, "yuanbao", 0) or 0) < reset_cost:
            raise DragonPalaceError("元宝不足")

        player.yuanbao = int(getattr(player, "yuanbao", 0) or 0) - reset_cost
        self.player_repo.save(player)

        st.resets_used = int(st.resets_used) + 1
        st.status = "not_started"
        st.current_stage = 1
        st.stage1 = DragonPalaceStageState(stage=1)
        st.stage2 = DragonPalaceStageState(stage=2)
        st.stage3 = DragonPalaceStageState(stage=3)
        self.repo.upsert_daily_state(st)

        return {"ok": True, "message": "重置成功", "yuanbao": int(getattr(player, "yuanbao", 0) or 0)}

    def challenge(self, user_id: int, now: Optional[datetime] = None) -> Dict[str, Any]:
        if now is None:
            now = datetime.now()
        if not is_dragonpalace_open(now):
            raise DragonPalaceError("活动未开放（10:00-24:00）")

        cfg = get_dragonpalace_config()
        today = now.date()
        st = self._get_or_init_today(user_id, today)

        # 每日免费一次；若失败/完成后再挑战，必须先重置（付费）
        if st.status in ("failed", "completed"):
            raise DragonPalaceError("今日挑战已结束，请重置次数后再进入")

        # 首次进入：开始挑战
        if st.status == "not_started":
            st.status = "in_progress"
            st.current_stage = 1

        stage_no = int(st.current_stage or 1)
        if stage_no < 1 or stage_no > 3:
            raise DragonPalaceError("关卡状态异常")

        # 取关卡配置
        stage_cfg = None
        for s in (cfg.get("stages", []) or []):
            if int(s.get("stage", 0) or 0) == stage_no:
                stage_cfg = s
                break
        if not isinstance(stage_cfg, dict):
            raise DragonPalaceError("关卡配置缺失")

        player = self.player_repo.get_by_id(user_id)
        if player is None:
            raise DragonPalaceError("玩家不存在")

        raw_beasts = self.player_beast_repo.get_team_beasts(user_id)
        if not raw_beasts:
            raise DragonPalaceError("你没有出战幻兽，请先在幻兽仓库设置出战")

        attacker_pvp_beasts = self.beast_pvp_service.to_pvp_beasts(raw_beasts)
        defender_pvp_beasts = _to_pvp_beasts_from_config(stage_cfg.get("enemies", []) or [])

        attacker_player = PvpPlayer(player_id=user_id, level=int(getattr(player, "level", 1) or 1), beasts=attacker_pvp_beasts, name=player.nickname)
        defender_player = PvpPlayer(player_id=0, level=int(stage_cfg.get("recommend_level", 1) or 1), beasts=defender_pvp_beasts, name=str(stage_cfg.get("name") or "龙宫之谜"))

        pvp_result = run_pvp_battle(attacker_player, defender_player)
        is_victory = (pvp_result.winner_player_id == user_id)

        battles = _format_battle_result(pvp_result, player.nickname, defender_player.name)

        battle_data = {
            "is_victory": bool(is_victory),
            "rating": "S" if is_victory else "C",
            "victory_text": "挑战成功！调整状态准备下一场战斗吧！" if is_victory else "挑战失败",
            "battles": battles,
            "player_name": player.nickname,
            "player_beast": raw_beasts[0].name if raw_beasts else "",
            "dungeon_name": defender_player.name,
            "floor": stage_no,
            "beasts": [
                {"name": str(x.get("name") or ""), "level": int(x.get("level", 1) or 1), "stats": x.get("stats", {})}
                for x in (stage_cfg.get("enemies", []) or [])
            ],
        }

        stage_state = st.get_stage_state(stage_no)
        stage_state.report = {"battles": battle_data["battles"]}
        stage_state.success = bool(is_victory)

        if is_victory:
            # 掉落龙宫宝箱（领奖一次）
            # 领奖时发放“探索礼包”（礼包打开后再按概率掉落进化材料）
            stage_state.reward_item_id = 93001
            stage_state.reward_claimed = False
            st.current_stage = stage_no + 1
            if st.current_stage > 3:
                st.status = "completed"
        else:
            st.status = "failed"

        # 写回对应 stage 对象
        if stage_no == 1:
            st.stage1 = stage_state
        elif stage_no == 2:
            st.stage2 = stage_state
        else:
            st.stage3 = stage_state

        self.repo.upsert_daily_state(st)

        return {"ok": True, "battle_data": battle_data, "message": battle_data["victory_text"]}

    def get_report(self, user_id: int, stage: int, today: Optional[date] = None) -> Dict[str, Any]:
        if today is None:
            today = date.today()
        st = self._get_or_init_today(user_id, today)
        s = st.get_stage_state(int(stage))
        if not s.report:
            raise DragonPalaceError("暂无战报")
        return {"ok": True, "report": s.report}

    def claim_reward(self, user_id: int, stage: int, today: Optional[date] = None) -> Dict[str, Any]:
        if today is None:
            today = date.today()
        st = self._get_or_init_today(user_id, today)
        s = st.get_stage_state(int(stage))
        if not s.success:
            raise DragonPalaceError("该关卡未挑战成功")
        if s.reward_claimed:
            raise DragonPalaceError("奖励已领取")
        if not s.reward_item_id:
            raise DragonPalaceError("暂无可领取奖励")

        item_id = int(s.reward_item_id)
        # 约定：领奖后礼包进入“背包-临时”分类，便于用户立刻看到并打开。
        self.inventory_service.add_item_to_temp(user_id, item_id, 1)
        s.reward_claimed = True
        if int(stage) == 1:
            st.stage1 = s
        elif int(stage) == 2:
            st.stage2 = s
        else:
            st.stage3 = s
        self.repo.upsert_daily_state(st)

        item = self.item_repo.get_by_id(item_id)
        name = getattr(item, "name", f"物品{item_id}") if item else f"物品{item_id}"
        return {"ok": True, "message": f"领取成功，获得{name}", "item_id": item_id, "item_name": name}


