# interfaces/routes/battlefield_routes.py
"""古战场（战场）相关接口

目前提供：
- GET /api/battlefield/info        战场基础信息（暂为简单示例数据）
- GET /api/battlefield/yesterday   昨日战况列表
- GET /api/battlefield/battle/<id> 单场详细战报

战斗详情 battle_data 的结构与镇妖 / 擂台战报保持一致：
{
  "is_victory": bool,          # 以前置玩家视角
  "battles": [
    {
      "battle_num": 1,
      "rounds": [
        {"round": 1, "action": "..."},
        ...
      ],
      "result": "..."
    },
    ...
  ]
}
"""

import os
from datetime import datetime

from flask import Blueprint, jsonify, request, session

from infrastructure.db.battlefield_repo_mysql import MySQLBattlefieldBattleRepo
from infrastructure.db.connection import execute_query, execute_update
from interfaces.web_api.bootstrap import services


battlefield_bp = Blueprint("battlefield", __name__, url_prefix="/api/battlefield")


def get_current_user_id() -> int:
    return session.get("user_id", 0)


BATTLEFIELD_TYPES = {
    "tiger": {
        "name": "猛虎战场",
        "level_range": (20, 39),
    },
    "crane": {
        "name": "飞鹤战场",
        "level_range": (40, 100),
    },
}


BATTLEFIELD_REPO = MySQLBattlefieldBattleRepo()

# 报名/战斗时间窗口（小时，24h 制）
SIGNUP_START_HOUR = 6   # 06:00 起
SIGNUP_END_HOUR = 20    # 20:00 止
FIGHT_START_HOUR = 0    # 00:00 起
FIGHT_END_HOUR = 6      # 06:00 止


def _allow_time_window_bypass() -> bool:
    """用于测试/预发布环境的时间窗口旁路开关。

    仅当显式设置环境变量时才允许跳过时间限制：
    - BATTLEFIELD_ALLOW_TIME_BYPASS=1/true/yes

    注意：正式逻辑默认必须在报名/战斗时间窗口内才能操作。
    """
    return os.getenv("BATTLEFIELD_ALLOW_TIME_BYPASS", "").lower() in ("1", "true", "yes")


def _is_now_in_window(start_hour: int, end_hour: int) -> bool:
    """判断当前时间是否在 [start_hour, end_hour) 区间。"""
    now_hour = datetime.now().hour
    return start_hour <= now_hour < end_hour


@battlefield_bp.get("/info")
def get_battlefield_info():
    """战场信息接口（目前返回简单示例数据，后续可接入真实报名/战绩）"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    battlefield_type = request.args.get("type", "tiger")
    cfg = BATTLEFIELD_TYPES.get(battlefield_type, BATTLEFIELD_TYPES["tiger"])

    # 今日报名人数
    rows = execute_query(
        """
        SELECT COUNT(*) AS cnt
        FROM battlefield_signup
        WHERE battlefield_type = %s AND signup_date = CURDATE()
        """,
        (battlefield_type,),
    )
    count = rows[0].get("cnt", 0) if rows else 0
    red_count = (count + 1) // 2
    blue_count = count // 2

    min_lv, max_lv = cfg["level_range"]
    battlefield = {
        "period": 0,
        "levelRange": f"{min_lv}-{max_lv}",
        "signUpTime": "6点-20点",
        "redCount": red_count,
        "blueCount": blue_count,
    }

    last_result, my_result = services.battlefield_service.get_last_and_my_result(user_id)

    # 使用上一期期数填充当前展示期数（如果有）
    if last_result.get("period"):
        battlefield["period"] = last_result["period"]

    # 判断当前玩家是否已报名今日该战场
    signup_rows = execute_query(
        """
        SELECT 1 FROM battlefield_signup
        WHERE user_id = %s AND battlefield_type = %s AND signup_date = CURDATE()
        LIMIT 1
        """,
        (user_id, battlefield_type),
    )
    is_signed_up = bool(signup_rows)

    return jsonify({
        "ok": True,
        "battlefield": battlefield,
        "lastResult": last_result,
        "myResult": my_result,
        "isSignedUp": is_signed_up,
    })


@battlefield_bp.post("/signup")
def battlefield_signup():
    """报名参加古战场。

    body: { "type": "tiger" | "crane" }
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    data = request.get_json() or {}
    battlefield_type = data.get("type", "tiger")
    cfg = BATTLEFIELD_TYPES.get(battlefield_type)
    if not cfg:
        return jsonify({"ok": False, "error": "无效的战场类型"})

    # 报名时间窗口：默认 06:00-20:00，允许通过环境变量跳过（测试用途）
    if not _allow_time_window_bypass() and not _is_now_in_window(SIGNUP_START_HOUR, SIGNUP_END_HOUR):
        return jsonify({"ok": False, "error": "当前不在报名时间（06:00-20:00）"}), 400

    # 等级限制
    rows = execute_query(
        "SELECT level, nickname FROM player WHERE user_id = %s",
        (user_id,),
    )
    if not rows:
        return jsonify({"ok": False, "error": "玩家不存在"})

    level = rows[0].get("level", 1)
    nickname = rows[0].get("nickname", "玩家")
    min_lv, max_lv = cfg["level_range"]
    if not (min_lv <= level <= max_lv):
        return jsonify({"ok": False, "error": f"仅{min_lv}-{max_lv}级玩家可参加{cfg['name']}"})

    # 写入报名表（同一玩家同一天同一战场只保留一条）
    execute_update(
        """
        INSERT INTO battlefield_signup (user_id, battlefield_type, signup_date)
        VALUES (%s, %s, CURDATE())
        ON DUPLICATE KEY UPDATE signup_time = NOW()
        """,
        (user_id, battlefield_type),
    )

    return jsonify({
        "ok": True,
        "message": f"已成功报名{cfg['name']}，请等待系统匹配对战。",
        "nickname": nickname,
    })


@battlefield_bp.get("/yesterday")
def get_battlefield_yesterday():
    """昨日战况列表。

    前端通常按轮数分组显示：
    - ?type=tiger|crane
    - 可选 ?period=xxx（不传则取最新期数）

    返回：
    {
      ok: true,
      battlefieldType: "tiger",
      period: 338,
      matches: [
        {
          id: 1,
          round: 1,
          match: 1,
          firstPlayer: "我有回来啦",
          secondPlayer: "づ午夜卍…",
          resultLabel: "失败",      # 针对 firstPlayer 的结果
          isFirstWin: false,
        },
        ...
      ]
    }
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    battlefield_type = request.args.get("type", "tiger")
    period_param = request.args.get("period")
    period = int(period_param) if period_param else None

    logs = BATTLEFIELD_REPO.get_matches_for_period(battlefield_type, period)
    if not logs:
        return jsonify({
            "ok": True,
            "battlefieldType": battlefield_type,
            "period": period or 0,
            "matches": [],
        })

    # 所有log的period应该一致，取第一个
    effective_period = logs[0].period

    matches = []
    for log in logs:
        matches.append({
            "id": log.id,
            "round": log.round_num,
            "match": log.match_num,
            "firstPlayer": log.first_user_name,
            "secondPlayer": log.second_user_name,
            "resultLabel": log.result_label,
            "isFirstWin": log.is_first_win,
        })

    return jsonify({
        "ok": True,
        "battlefieldType": battlefield_type,
        "period": effective_period,
        "matches": matches,
    })


@battlefield_bp.get("/battle/<int:battle_id>")
def get_battlefield_battle_detail(battle_id: int):
    """单场古战场详细战报。

    返回结构与擂台战报类似：{"ok": True, "battle": {...}}，其中
    battle.battle_data 为多战 + 多回合日志，前端按镇妖风格渲染。
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    log = BATTLEFIELD_REPO.get_by_id(battle_id)
    if not log:
        return jsonify({"ok": False, "error": "战报不存在"}), 404

    return jsonify({"ok": True, "battle": log.to_dict()})


@battlefield_bp.post("/run")
def run_battlefield_tournament():
    """手动触发一次古战场淘汰赛（调试/定时任务入口）。

    body: { "type": "tiger" | "crane" }
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    data = request.get_json() or {}
    battlefield_type = data.get("type", "tiger")

    # 战斗时间窗口：默认 00:00-06:00，允许通过环境变量跳过（测试用途）
    if not _allow_time_window_bypass() and not _is_now_in_window(FIGHT_START_HOUR, FIGHT_END_HOUR):
        return jsonify({"ok": False, "error": "当前不在战斗时间（00:00-06:00）"}), 400

    try:
        result = services.battlefield_service.run_tournament(battlefield_type)
        return jsonify(result)
    except Exception as e:  # pragma: no cover - 调试用
        return jsonify({"ok": False, "error": str(e)}), 500
