from __future__ import annotations

import json
from datetime import date
from typing import Optional, Dict, Any

from infrastructure.db.connection import execute_query, execute_update
from domain.entities.dragonpalace import DragonPalaceDailyState, DragonPalaceStageState
from domain.repositories.dragonpalace_repo import IDragonPalaceRepo


def _dump(obj: Any) -> Optional[str]:
    if obj is None:
        return None
    return json.dumps(obj, ensure_ascii=False)


def _load(text: Any) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    if isinstance(text, (dict, list)):
        # 某些驱动可能自动反序列化
        return text  # type: ignore[return-value]
    try:
        return json.loads(str(text))
    except Exception:
        return None


class MySQLDragonPalaceRepo(IDragonPalaceRepo):
    def get_daily_state(self, user_id: int, play_date: date) -> Optional[DragonPalaceDailyState]:
        rows = execute_query(
            """
            SELECT
              user_id, play_date,
              resets_used, status, current_stage,
              stage1_success, stage1_report_json, stage1_reward_item_id, stage1_reward_claimed,
              stage2_success, stage2_report_json, stage2_reward_item_id, stage2_reward_claimed,
              stage3_success, stage3_report_json, stage3_reward_item_id, stage3_reward_claimed
            FROM dragonpalace_daily_state
            WHERE user_id = %s AND play_date = %s
            """,
            (user_id, play_date),
        )
        if not rows:
            return None
        r = rows[0]
        st = DragonPalaceDailyState(
            user_id=int(r["user_id"]),
            play_date=r["play_date"],
            resets_used=int(r.get("resets_used", 0) or 0),
            status=str(r.get("status") or "not_started"),
            current_stage=int(r.get("current_stage", 1) or 1),
        )
        st.stage1 = DragonPalaceStageState(
            stage=1,
            success=bool(r.get("stage1_success", 0)),
            report=_load(r.get("stage1_report_json")),
            reward_item_id=(int(r["stage1_reward_item_id"]) if r.get("stage1_reward_item_id") is not None else None),
            reward_claimed=bool(r.get("stage1_reward_claimed", 0)),
        )
        st.stage2 = DragonPalaceStageState(
            stage=2,
            success=bool(r.get("stage2_success", 0)),
            report=_load(r.get("stage2_report_json")),
            reward_item_id=(int(r["stage2_reward_item_id"]) if r.get("stage2_reward_item_id") is not None else None),
            reward_claimed=bool(r.get("stage2_reward_claimed", 0)),
        )
        st.stage3 = DragonPalaceStageState(
            stage=3,
            success=bool(r.get("stage3_success", 0)),
            report=_load(r.get("stage3_report_json")),
            reward_item_id=(int(r["stage3_reward_item_id"]) if r.get("stage3_reward_item_id") is not None else None),
            reward_claimed=bool(r.get("stage3_reward_claimed", 0)),
        )
        return st

    def upsert_daily_state(self, state: DragonPalaceDailyState) -> None:
        execute_update(
            """
            INSERT INTO dragonpalace_daily_state (
              user_id, play_date,
              resets_used, status, current_stage,
              stage1_success, stage1_report_json, stage1_reward_item_id, stage1_reward_claimed,
              stage2_success, stage2_report_json, stage2_reward_item_id, stage2_reward_claimed,
              stage3_success, stage3_report_json, stage3_reward_item_id, stage3_reward_claimed,
              updated_at
            )
            VALUES (
              %s, %s,
              %s, %s, %s,
              %s, %s, %s, %s,
              %s, %s, %s, %s,
              %s, %s, %s, %s,
              NOW()
            )
            ON DUPLICATE KEY UPDATE
              resets_used = VALUES(resets_used),
              status = VALUES(status),
              current_stage = VALUES(current_stage),
              stage1_success = VALUES(stage1_success),
              stage1_report_json = VALUES(stage1_report_json),
              stage1_reward_item_id = VALUES(stage1_reward_item_id),
              stage1_reward_claimed = VALUES(stage1_reward_claimed),
              stage2_success = VALUES(stage2_success),
              stage2_report_json = VALUES(stage2_report_json),
              stage2_reward_item_id = VALUES(stage2_reward_item_id),
              stage2_reward_claimed = VALUES(stage2_reward_claimed),
              stage3_success = VALUES(stage3_success),
              stage3_report_json = VALUES(stage3_report_json),
              stage3_reward_item_id = VALUES(stage3_reward_item_id),
              stage3_reward_claimed = VALUES(stage3_reward_claimed),
              updated_at = NOW()
            """,
            (
                state.user_id,
                state.play_date,
                int(state.resets_used or 0),
                str(state.status or "not_started"),
                int(state.current_stage or 1),
                1 if state.stage1.success else 0,
                _dump(state.stage1.report),
                state.stage1.reward_item_id,
                1 if state.stage1.reward_claimed else 0,
                1 if state.stage2.success else 0,
                _dump(state.stage2.report),
                state.stage2.reward_item_id,
                1 if state.stage2.reward_claimed else 0,
                1 if state.stage3.success else 0,
                _dump(state.stage3.report),
                state.stage3.reward_item_id,
                1 if state.stage3.reward_claimed else 0,
            ),
        )


