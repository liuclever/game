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
    
    # 检查奖励领取状态
    reward_claim_status = {
        "can_claim": False,
        "king_claimed": False,
        "camp_claimed": False,
        "kill_claimed": False,
    }
    
    if last_result.get("period"):
        claim_rows = execute_query(
            """SELECT * FROM battlefield_reward_claims 
               WHERE user_id = %s AND battlefield_type = %s AND period = %s""",
            (user_id, battlefield_type, last_result["period"])
        )
        
        if claim_rows:
            record = claim_rows[0]
            reward_claim_status["king_claimed"] = bool(record.get("king_reward_claimed"))
            reward_claim_status["camp_claimed"] = bool(record.get("camp_reward_claimed"))
            reward_claim_status["kill_claimed"] = bool(record.get("kill_reward_claimed"))
            
            # 如果有任何一项未领取，则可以领取
            reward_claim_status["can_claim"] = not (
                reward_claim_status["king_claimed"] and 
                reward_claim_status["camp_claimed"] and 
                reward_claim_status["kill_claimed"]
            )
        else:
            # 如果玩家参与了战场但没有领取记录，说明可以领取
            if my_result.get("kills", 0) > 0 or my_result.get("team"):
                reward_claim_status["can_claim"] = True

    return jsonify({
        "ok": True,
        "battlefield": battlefield,
        "lastResult": last_result,
        "myResult": my_result,
        "isSignedUp": is_signed_up,
        "rewardClaimStatus": reward_claim_status,
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


@battlefield_bp.post("/claim_rewards")
def claim_battlefield_rewards():
    """领取战场奖励
    
    body: { 
        "type": "tiger" | "crane",
        "period": int (可选，不传则使用最新期数)
    }
    
    返回: {
        "ok": true,
        "claimed": {
            "king_reward": {...},  # 战王奖励（如果是战王）
            "camp_reward": {...},  # 阵营奖励
            "kill_reward": {...}   # 杀敌奖励
        },
        "total_gold": int,
        "total_items": [...]
    }
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    data = request.get_json() or {}
    battlefield_type = data.get("type", "tiger")
    period = data.get("period")
    
    # 如果没有指定期数，使用最新期数
    if period is None:
        period = BATTLEFIELD_REPO.get_latest_period(battlefield_type)
        if period is None:
            return jsonify({"ok": False, "error": "暂无战报，无法领取奖励"})
    
    try:
        from infrastructure.config.battlefield_reward_config import BattlefieldRewardConfig
        reward_config = BattlefieldRewardConfig()
        
        # 检查是否已领取
        claim_record = execute_query(
            """SELECT * FROM battlefield_reward_claims 
               WHERE user_id = %s AND battlefield_type = %s AND period = %s""",
            (user_id, battlefield_type, period)
        )
        
        if claim_record:
            record = claim_record[0]
            if record.get("king_reward_claimed") and record.get("camp_reward_claimed") and record.get("kill_reward_claimed"):
                return jsonify({"ok": False, "error": "本期奖励已全部领取"})
        
        # 获取玩家战绩
        logs = BATTLEFIELD_REPO.get_matches_for_period(battlefield_type, period)
        if not logs:
            return jsonify({"ok": False, "error": "本期暂无战报"})
        
        # 统计玩家数据
        from collections import defaultdict
        wins = defaultdict(int)
        team_by_user = {}
        
        for log in logs:
            winner_id = log.first_user_id if log.is_first_win else log.second_user_id
            wins[winner_id] += 1
            team_by_user[log.first_user_id] = log.first_user_team or ""
            team_by_user[log.second_user_id] = log.second_user_team or ""
        
        # 检查玩家是否参与了本期战场
        if user_id not in team_by_user:
            return jsonify({"ok": False, "error": "您未参与本期战场，无法领取奖励"})
        
        user_kills = wins.get(user_id, 0)
        user_team = team_by_user.get(user_id, "")
        
        # 找出战王
        king_id = max(wins.keys(), key=lambda uid: wins[uid]) if wins else None
        is_king = (user_id == king_id)
        
        # 判断阵营胜利
        king_team = team_by_user.get(king_id, "") if king_id else ""
        is_camp_winner = (user_team == king_team) if user_team and king_team else False
        
        # 准备发放的奖励
        claimed_rewards = {}
        total_gold = 0
        total_items = []
        
        # 创建或更新领取记录
        if not claim_record:
            execute_update(
                """INSERT INTO battlefield_reward_claims 
                   (user_id, battlefield_type, period, is_king, camp_team, kills)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (user_id, battlefield_type, period, is_king, user_team, user_kills)
            )
            claim_record = execute_query(
                """SELECT * FROM battlefield_reward_claims 
                   WHERE user_id = %s AND battlefield_type = %s AND period = %s""",
                (user_id, battlefield_type, period)
            )
        
        record = claim_record[0] if claim_record else {}
        
        # 1. 战王奖励
        if is_king and not record.get("king_reward_claimed"):
            king_reward = reward_config.get_king_reward()
            if king_reward:
                gold = king_reward.get("gold", 0)
                items = king_reward.get("items", [])
                
                # 发放铜钱
                if gold > 0:
                    execute_update(
                        "UPDATE player SET gold = gold + %s WHERE user_id = %s",
                        (gold, user_id)
                    )
                    total_gold += gold
                
                # 发放道具
                for item in items:
                    services.inventory_service.add_item(
                        user_id, item["item_id"], item["quantity"]
                    )
                    total_items.append(item)
                
                # 标记已领取
                execute_update(
                    """UPDATE battlefield_reward_claims 
                       SET king_reward_claimed = 1 
                       WHERE user_id = %s AND battlefield_type = %s AND period = %s""",
                    (user_id, battlefield_type, period)
                )
                
                claimed_rewards["king_reward"] = king_reward
        
        # 2. 阵营奖励
        if not record.get("camp_reward_claimed"):
            camp_reward = reward_config.get_camp_reward(is_camp_winner)
            if camp_reward:
                gold = camp_reward.get("gold", 0)
                items = camp_reward.get("items", [])
                
                # 发放铜钱
                if gold > 0:
                    execute_update(
                        "UPDATE player SET gold = gold + %s WHERE user_id = %s",
                        (gold, user_id)
                    )
                    total_gold += gold
                
                # 发放道具
                for item in items:
                    services.inventory_service.add_item(
                        user_id, item["item_id"], item["quantity"]
                    )
                    total_items.append(item)
                
                # 标记已领取
                execute_update(
                    """UPDATE battlefield_reward_claims 
                       SET camp_reward_claimed = 1 
                       WHERE user_id = %s AND battlefield_type = %s AND period = %s""",
                    (user_id, battlefield_type, period)
                )
                
                claimed_rewards["camp_reward"] = camp_reward
        
        # 3. 杀敌奖励
        if not record.get("kill_reward_claimed") and user_kills > 0:
            kill_reward = reward_config.get_kill_reward(user_kills)
            if kill_reward:
                gold = kill_reward.get("gold", 0)
                items = kill_reward.get("items", [])
                
                # 发放铜钱
                if gold > 0:
                    execute_update(
                        "UPDATE player SET gold = gold + %s WHERE user_id = %s",
                        (gold, user_id)
                    )
                    total_gold += gold
                
                # 发放道具
                for item in items:
                    services.inventory_service.add_item(
                        user_id, item["item_id"], item["quantity"]
                    )
                    total_items.append(item)
                
                # 标记已领取
                execute_update(
                    """UPDATE battlefield_reward_claims 
                       SET kill_reward_claimed = 1 
                       WHERE user_id = %s AND battlefield_type = %s AND period = %s""",
                    (user_id, battlefield_type, period)
                )
                
                claimed_rewards["kill_reward"] = kill_reward
        
        if not claimed_rewards:
            return jsonify({"ok": False, "error": "没有可领取的奖励"})
        
        return jsonify({
            "ok": True,
            "claimed": claimed_rewards,
            "total_gold": total_gold,
            "total_items": total_items,
            "message": f"成功领取奖励：铜钱+{total_gold}，道具×{len(total_items)}"
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"ok": False, "error": f"领取奖励失败: {str(e)}"}), 500
