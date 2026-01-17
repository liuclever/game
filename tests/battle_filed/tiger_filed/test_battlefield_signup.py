"""古战场集成测试：使用真实数据库玩家 + 幻兽，验证 31 人报名的完整流程。
python -m pytest tests/battle_filed/tiger_filed/test_battlefield_signup.py -vv

行为：
    - 从数据库中选出 31 名在猛虎战场等级范围内、且拥有出战幻兽的真实玩家。
    - 写入 battlefield_signup 报名表（tiger）。
    - 调用 BattlefieldService.run_tournament("tiger") 使用统一 PVP+技能规则完成一整期比赛。
    - 从 battlefield_battle_log 读取本期全部战报，并在 tests/battle_filed/battle_report 目录下生成文本战报文件。

注意：
    - 需要数据库中至少有 31 个满足条件的玩家和对应的出战幻兽。
    - 本测试会清空当日猛虎战场的报名记录，并删除该战场已有的战报记录，请勿在生产库执行。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from infrastructure.db.connection import execute_query, execute_update
from infrastructure.db.player_beast_repo_mysql import MySQLPlayerBeastRepo
from infrastructure.db.player_repo_mysql import MySQLPlayerRepo
from infrastructure.db.battlefield_repo_mysql import MySQLBattlefieldBattleRepo
from application.services.battlefield_service import BattlefieldService, BATTLEFIELD_TYPES

REPORT_DIR = Path(__file__).parent / "battle_report"

# 额外需要加入的前端登录玩家（等级30，已有两只幻兽）
EXTRA_USER_IDS = [2031]


def _pick_real_players_with_beasts(limit: int = 31, battlefield_type: str = "tiger") -> List[int]:
    """选出满足等级且有出战幻兽的玩家，尽量包含前端登录玩家。"""

    cfg = BATTLEFIELD_TYPES[battlefield_type]
    min_lv, max_lv = cfg["level_range"]

    rows = execute_query(
        """
        SELECT DISTINCT p.user_id
        FROM player p
        JOIN player_beast b ON p.user_id = b.user_id
        WHERE b.is_in_team = 1
          AND p.level BETWEEN %s AND %s
        ORDER BY p.user_id ASC
        """,
        (min_lv, max_lv),
    )

    all_ids = [row["user_id"] for row in rows]

    picked: List[int] = []
    for uid in all_ids:
        if uid in EXTRA_USER_IDS:
            picked.append(uid)
    for uid in all_ids:
        if uid in picked:
            continue
        if len(picked) < limit:
            picked.append(uid)
    return picked


def test_31_players_signup_and_tournament_with_real_data():
    """使用真实玩家 + 幻兽，跑一整期 31+1 人猛虎战场，并生成文本战报。"""

    battlefield_type = "tiger"
    min_lv, max_lv = BATTLEFIELD_TYPES[battlefield_type]["level_range"]

    # 1. 选出 31 名符合条件的真实玩家 + 额外前端玩家
    user_ids = _pick_real_players_with_beasts(31, battlefield_type)
    assert len(user_ids) >= 31, (
        f"需要至少 31 名 {min_lv}-{max_lv} 级且有出战幻兽的玩家，当前仅找到 {len(user_ids)} 名，"
        "请先在数据库中准备好足够的测试玩家和幻兽。"
    )

    # 确保额外玩家在列表末尾（如果存在）
    for uid in EXTRA_USER_IDS:
        if uid in user_ids:
            user_ids = [x for x in user_ids if x != uid] + [uid]

    beast_repo = MySQLPlayerBeastRepo()
    for uid in user_ids:
        beasts = beast_repo.get_team_beasts(uid)
        assert beasts, f"玩家 {uid} 没有出战幻兽，请先在 player_beast 表中为其配置 is_in_team=1 的幻兽。"

    # 2. 清空当日报名（仅测试账号与额外账号）和旧战报（仅 tiger 战场）
    execute_update(
        "DELETE FROM battlefield_signup WHERE battlefield_type = %s AND signup_date = CURDATE() AND user_id BETWEEN %s AND %s",
        (battlefield_type, 2000, 2030),
    )
    if EXTRA_USER_IDS:
        placeholders = ",".join(["%s"] * len(EXTRA_USER_IDS))
        execute_update(
            f"DELETE FROM battlefield_signup WHERE battlefield_type = %s AND signup_date = CURDATE() AND user_id IN ({placeholders})",
            (battlefield_type, *EXTRA_USER_IDS),
        )
    execute_update(
        "DELETE FROM battlefield_battle_log WHERE battlefield_type = %s",
        (battlefield_type,),
    )

    # 3. 为玩家写入今日猛虎战场报名记录（包含额外玩家）
    for uid in user_ids:
        execute_update(
            """
            INSERT INTO battlefield_signup (user_id, battlefield_type, signup_date)
            VALUES (%s, %s, CURDATE())
            ON DUPLICATE KEY UPDATE signup_time = NOW()
            """,
            (uid, battlefield_type),
        )

    # 4. 使用真正的 BattlefieldService 运行一整期比赛（PVP+技能规则）
    player_repo = MySQLPlayerRepo()
    battle_repo = MySQLBattlefieldBattleRepo()
    service = BattlefieldService(
        player_repo=player_repo,
        player_beast_repo=beast_repo,
        battle_repo=battle_repo,
    )

    result = service.run_tournament(battlefield_type)
    assert result["ok"], f"古战场运行失败: {result}"

    period = result["period"]
    total_players = result["total_players"]
    assert total_players >= 31

    # 5. 读取本期所有战报记录
    logs = battle_repo.get_matches_for_period(battlefield_type, period)
    # 单败淘汰应有 n-1 场对战
    assert len(logs) == total_players - 1, f"{total_players} 人单淘汰应有 {total_players - 1} 场对战，实际 {len(logs)} 场"

    # 6. 在 tests/battle_filed/battle_report 目录下生成文本战报文件
    REPORT_DIR.mkdir(exist_ok=True, parents=True)

    for log in logs:
        filename = (
            f"period{period}_round{log.round_num}_match{log.match_num}_id{log.id}.txt"
        )
        path = REPORT_DIR / filename

        data = log.battle_data or {}
        battles = data.get("battles", [])

        with path.open("w", encoding="utf-8") as f:
            f.write(
                f"期数: {log.period}\n"
                f"战场: {log.battlefield_type}\n"
                f"轮次: 第{log.round_num}轮 第{log.match_num}场\n"
                f"对阵: {log.first_user_name} VS {log.second_user_name}\n"
                f"结果: {'胜利' if log.is_first_win else '失败'} (针对左侧玩家)\n\n"
            )

            for battle in battles:
                f.write(f"[第{battle.get('battle_num', 1)}战] {battle.get('result', '')}\n")
                for r in battle.get("rounds", []):
                    f.write(f"[回合{r.get('round')}]: {r.get('action')}\n")
                f.write("\n")

    # 简单校验：至少有一个战报文件包含技能描述关键字（例如“使用”）
    any_skill_line = False
    for txt_path in REPORT_DIR.glob(f"period{period}_*.txt"):
        content = txt_path.read_text(encoding="utf-8")
        if "使用" in content:
            any_skill_line = True
            break

    assert any_skill_line, "战报文件中未检测到技能描述，请检查 PVP+技能战斗集成是否正常。"
