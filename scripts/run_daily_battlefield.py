"""每日定时开赛脚本（生产/测试可用）。

建议由系统定时任务在 00:05 左右执行一次，负责在战斗时间窗口
（默认 00:00-06:00）内自动触发飞鹤/猛虎战场开赛并生成战报。

运行示例（项目根目录）：
    python scripts/run_daily_battlefield.py          # 同时跑 tiger + crane
    python scripts/run_daily_battlefield.py --type crane

说明：
    - 仅在有当日报名数据时才会开赛；若报名不足 2 人则跳过。
    - 通过环境变量 BATTLEFIELD_ALLOW_TIME_BYPASS=true 可跳过时间窗口校验（测试用）。
    - 运行成功后，battlefield_signup 当日记录会被 run_tournament 清空。
"""

import argparse
import os
import sys
from datetime import datetime
from typing import Iterable, List

from infrastructure.db.connection import execute_query
from infrastructure.db.player_beast_repo_mysql import MySQLPlayerBeastRepo
from infrastructure.db.player_repo_mysql import MySQLPlayerRepo
from infrastructure.db.battlefield_repo_mysql import MySQLBattlefieldBattleRepo
from application.services.battlefield_service import BattlefieldService

# 与接口保持一致的时间窗口（小时，24h）
FIGHT_START_HOUR = 0
FIGHT_END_HOUR = 6


def _allow_time_window_bypass() -> bool:
    return os.getenv("BATTLEFIELD_ALLOW_TIME_BYPASS", "").lower() in ("1", "true", "yes")


def _is_now_in_window(start_hour: int, end_hour: int) -> bool:
    now_hour = datetime.now().hour
    return start_hour <= now_hour < end_hour


def _has_signup_today(battlefield_type: str) -> bool:
    rows = execute_query(
        """
        SELECT COUNT(*) AS cnt
        FROM battlefield_signup
        WHERE battlefield_type = %s AND signup_date = CURDATE()
        """,
        (battlefield_type,),
    )
    cnt = rows[0]["cnt"] if rows else 0
    return cnt >= 2  # 至少两人才能开赛


def _run_once(battlefield_type: str) -> None:
    if not _allow_time_window_bypass() and not _is_now_in_window(FIGHT_START_HOUR, FIGHT_END_HOUR):
        print(f"[{battlefield_type}] 当前不在战斗时间窗口，跳过")
        return

    if not _has_signup_today(battlefield_type):
        print(f"[{battlefield_type}] 当日报名人数不足 2 人，跳过")
        return

    player_repo = MySQLPlayerRepo()
    beast_repo = MySQLPlayerBeastRepo()
    battle_repo = MySQLBattlefieldBattleRepo()

    service = BattlefieldService(
        player_repo=player_repo,
        player_beast_repo=beast_repo,
        battle_repo=battle_repo,
    )

    print(f"[{battlefield_type}] 开始运行淘汰赛...")
    result = service.run_tournament(battlefield_type)
    if not result.get("ok"):
        raise RuntimeError(f"[{battlefield_type}] 开赛失败: {result}")

    print(
        f"[{battlefield_type}] 完成：period={result['period']}, "
        f"players={result['total_players']}, rounds={result['total_rounds']}, "
        f"champion={result['champion_name']}({result['champion_id']})"
    )


def main(types: Iterable[str]) -> None:
    for t in types:
        try:
            _run_once(t)
        except Exception as e:
            print(f"[{t}] 失败：{e}", file=sys.stderr)
            # 保持其他战场继续尝试


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="每日自动开赛脚本")
    parser.add_argument(
        "--type",
        choices=["tiger", "crane"],
        help="仅运行指定战场（默认两个战场都跑）",
    )
    args = parser.parse_args()

    targets: List[str] = [args.type] if args.type else ["tiger", "crane"]
    main(targets)

