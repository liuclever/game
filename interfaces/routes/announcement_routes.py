# interfaces/routes/announcement_routes.py
"""开服活动路由"""

from flask import Blueprint, request, jsonify, session

from application.services.announcement_service import AnnouncementService
from interfaces.web_api.bootstrap import services

announcement_bp = Blueprint('announcement', __name__, url_prefix='/api/announcement')


def get_current_user_id() -> int:
    return session.get('user_id', 0)


def _get_service() -> AnnouncementService:
    """获取公告服务实例"""
    return AnnouncementService(
        inventory_service=services.inventory_service,
        player_repo=services.player_repo
    )


# ==================== 新人战力榜排行 ====================

@announcement_bp.get("/power-ranking/<int:level_bracket>")
def get_power_ranking(level_bracket: int):
    """获取指定等级段的战力排行"""
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 10, type=int)
    
    svc = _get_service()
    result = svc.get_power_ranking(level_bracket, page, size)
    
    # 添加当前玩家排名
    user_id = get_current_user_id()
    if user_id and result.get("ok"):
        my_rank = _get_my_power_rank(user_id, level_bracket)
        result["my_rank"] = my_rank
    
    # 添加是否已结算
    result["is_finalized"] = svc.check_power_ranking_finalized(level_bracket)
    result["is_activity_ended"] = svc.is_activity_ended("power_ranking")
    
    return jsonify(result)


def _get_my_power_rank(user_id: int, level_bracket: int) -> int:
    """获取当前玩家在指定等级段的排名"""
    from infrastructure.db.connection import execute_query
    
    level_ranges = {
        29: (20, 29),
        39: (30, 39),
        49: (40, 49),
        59: (50, 59),
    }
    if level_bracket not in level_ranges:
        return 0
    
    min_level, max_level = level_ranges[level_bracket]
    
    # 获取玩家战力
    power_sql = """
        SELECT COALESCE(SUM(b.combat_power), 0) as power, p.level
        FROM player p
        LEFT JOIN player_beast b ON p.user_id = b.user_id AND b.is_in_team = 1
        WHERE p.user_id = %s
        GROUP BY p.user_id
    """
    rows = execute_query(power_sql, (user_id,))
    if not rows:
        return 0
    
    my_power = rows[0].get('power', 0)
    my_level = rows[0].get('level', 0)
    
    # 不在该等级段
    if not (min_level <= my_level <= max_level):
        return 0
    
    # 计算排名
    rank_sql = """
        SELECT COUNT(*) + 1 as `rank` FROM (
            SELECT p.user_id, COALESCE(SUM(b.combat_power), 0) as power
            FROM player p
            LEFT JOIN player_beast b ON p.user_id = b.user_id AND b.is_in_team = 1
            WHERE p.level BETWEEN %s AND %s
            GROUP BY p.user_id
        ) t
        WHERE t.power > %s
    """
    rank_rows = execute_query(rank_sql, (min_level, max_level, my_power))
    return rank_rows[0]['rank'] if rank_rows else 0


@announcement_bp.post("/power-ranking/<int:level_bracket>/finalize")
def finalize_power_ranking(level_bracket: int):
    """结算战力榜并发放奖励（仅活动结束后可调用）"""
    svc = _get_service()
    
    # 检查活动是否已结束
    if not svc.is_activity_ended("power_ranking"):
        return jsonify({"ok": False, "error": "活动尚未结束，无法结算"})
    
    result = svc.finalize_power_ranking(level_bracket)
    return jsonify(result)


@announcement_bp.get("/power-ranking/status")
def get_power_ranking_status():
    """获取战力榜活动状态"""
    svc = _get_service()
    
    status = {
        "ok": True,
        "is_active": svc.is_activity_active("power_ranking"),
        "is_ended": svc.is_activity_ended("power_ranking"),
        "brackets": []
    }
    
    for level in [29, 39, 49, 59]:
        status["brackets"].append({
            "level": level,
            "is_finalized": svc.check_power_ranking_finalized(level)
        })
    
    return jsonify(status)


# ==================== 轮盘抽奖 ====================

@announcement_bp.get("/lottery/status")
def get_lottery_status():
    """获取抽奖状态"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    svc = _get_service()
    
    # 检查活动是否有效
    if not svc.is_activity_active("wheel_lottery"):
        return jsonify({"ok": False, "error": "活动未开启或已结束"})
    
    status = svc.get_lottery_status(user_id)
    
    # 获取玩家元宝
    player = services.player_repo.get_by_id(user_id)
    yuanbao = getattr(player, 'yuanbao', 0) or 0 if player else 0
    
    return jsonify({
        "ok": True,
        "draw_count": status.get("draw_count", 0),
        "fragment_count": status.get("fragment_count", 0),
        "round_count": status.get("round_count", 0),
        "yuanbao": yuanbao,
        "single_cost": 600,
        "ten_cost": 5000,
    })


@announcement_bp.post("/lottery/draw")
def do_lottery():
    """执行抽奖"""
    print("[路由] 收到抽奖请求")
    user_id = get_current_user_id()
    print(f"[路由] user_id={user_id}")
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    data = request.get_json() or {}
    draw_type = data.get("draw_type", "single")  # single/ten
    print(f"[路由] draw_type={draw_type}")
    
    svc = _get_service()
    result = svc.do_lottery(user_id, draw_type)
    print(f"[路由] 抽奖结果: {result}")
    
    # 返回最新元宝
    if result.get("ok"):
        player = services.player_repo.get_by_id(user_id)
        result["yuanbao"] = getattr(player, 'yuanbao', 0) or 0 if player else 0
    
    print(f"[路由] 返回结果: {result}")
    return jsonify(result)


@announcement_bp.post("/lottery/exchange")
def exchange_fragment():
    """碎片兑换"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    data = request.get_json() or {}
    exchange_type = data.get("exchange_type", "")  # earth/fire/water/wood/gold/god
    
    svc = _get_service()
    result = svc.exchange_fragment(user_id, exchange_type)
    return jsonify(result)


# ==================== 铜钱圣典 ====================

@announcement_bp.get("/copper-book/status")
def get_copper_book_status():
    """获取铜钱圣典状态"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    svc = _get_service()
    
    if not svc.is_activity_active("copper_book"):
        return jsonify({"ok": False, "error": "活动未开启或已结束"})
    
    ann = svc.get_announcement("copper_book")
    daily_limit = ann.get("daily_limit", 4) if ann else 4
    
    # 获取今日购买次数
    from datetime import date
    bought_today = svc._get_daily_claim_count(user_id, "copper_book", "buy", date.today())
    
    # 获取玩家元宝
    player = services.player_repo.get_by_id(user_id)
    yuanbao = getattr(player, 'yuanbao', 0) or 0 if player else 0
    
    return jsonify({
        "ok": True,
        "bought_today": bought_today,
        "daily_limit": daily_limit,
        "can_buy": bought_today < daily_limit,
        "yuanbao": yuanbao,
        "price": ann.get("price", 2188) if ann else 2188,
        "reward_copper": ann.get("reward_copper", 2880000) if ann else 2880000,
    })


@announcement_bp.post("/copper-book/buy")
def buy_copper_book():
    """购买铜钱圣典礼盒"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    svc = _get_service()
    result = svc.buy_copper_book(user_id)
    
    # 返回最新货币
    if result.get("ok"):
        player = services.player_repo.get_by_id(user_id)
        result["yuanbao"] = getattr(player, 'yuanbao', 0) or 0 if player else 0
        result["copper"] = getattr(player, 'gold', 0) or 0 if player else 0
    
    return jsonify(result)


# ==================== 声望助力庆典 ====================

@announcement_bp.get("/prestige/status")
def get_prestige_status():
    """获取声望助力状态"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    svc = _get_service()
    
    if not svc.is_activity_active("prestige_boost"):
        return jsonify({"ok": False, "error": "活动未开启或已结束"})
    
    # 获取免费声望石领取状态
    free_claimed = svc._get_claim_count(user_id, "prestige_boost", "free_prestige_stone") > 0
    
    # 获取今日购买次数
    from datetime import date
    bought_today = svc._get_daily_claim_count(user_id, "prestige_boost", "buy_box", date.today())
    
    # 获取玩家信息
    player = services.player_repo.get_by_id(user_id)
    yuanbao = getattr(player, 'yuanbao', 0) or 0 if player else 0
    level = player.level if player else 0
    
    return jsonify({
        "ok": True,
        "free_claimed": free_claimed,
        "can_claim_free": not free_claimed,
        "bought_today": bought_today,
        "daily_limit": 4,
        "can_buy": bought_today < 4 and level <= 50,
        "yuanbao": yuanbao,
        "level": level,
    })


@announcement_bp.post("/prestige/claim-free")
def claim_prestige_free():
    """领取免费声望石"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    svc = _get_service()
    result = svc.claim_prestige_free(user_id)
    return jsonify(result)


@announcement_bp.post("/prestige/buy-box")
def buy_prestige_box():
    """购买声望礼盒"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    svc = _get_service()
    result = svc.buy_prestige_box(user_id)
    
    # 返回最新货币
    if result.get("ok"):
        player = services.player_repo.get_by_id(user_id)
        result["yuanbao"] = getattr(player, 'yuanbao', 0) or 0 if player else 0
    
    return jsonify(result)


# ==================== 霸王龙预登场 ====================

@announcement_bp.get("/tyrannosaurus/status")
def get_tyrannosaurus_status():
    """获取霸王龙预登场状态"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    svc = _get_service()
    
    if not svc.is_activity_active("tyrannosaurus_preview"):
        return jsonify({"ok": False, "error": "活动未开启或已结束"})
    
    ann = svc.get_announcement("tyrannosaurus_preview")
    required_gems = ann.get("required_gems", 300) if ann else 300
    
    # 获取领取状态
    claimed = svc._get_claim_count(user_id, "tyrannosaurus_preview", "claim_ball") > 0
    
    # 获取玩家累计赞助宝石（实际充值，不含赠送），以及玩家等级
    player = services.player_repo.get_by_id(user_id)
    total_gems = svc._get_total_sponsored_gems(user_id)
    level = player.level if player else 0
    
    return jsonify({
        "ok": True,
        "claimed": claimed,
        "can_claim": not claimed and total_gems >= required_gems,
        "total_gems": total_gems,
        "required_gems": required_gems,
        "level": level,
    })


@announcement_bp.post("/tyrannosaurus/claim")
def claim_tyrannosaurus_ball():
    """领取霸王龙召唤球"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    data = request.get_json() or {}
    ball_level = data.get("ball_level", 0)
    
    try:
        ball_level = int(ball_level)
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "无效的召唤球等级"})
    
    svc = _get_service()
    result = svc.claim_tyrannosaurus_ball(user_id, ball_level)
    return jsonify(result)


# ==================== 元宝返利 ====================

@announcement_bp.get("/rebate/status")
def get_rebate_status():
    """获取元宝返利状态"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    svc = _get_service()
    
    if not svc.is_activity_active("yuanbao_rebate"):
        return jsonify({"ok": False, "error": "活动未开启或已结束"})
    
    ann = svc.get_announcement("yuanbao_rebate")
    tiers = ann.get("tiers", []) if ann else []
    
    # 获取玩家今日赞助宝石（实际充值，不含赠送）
    from datetime import date
    today = date.today()
    today_gems = svc._get_today_sponsored_gems(user_id, today)
    
    # 获取今日各档位领取状态
    tier_status = []
    for tier in tiers:
        gems_required = tier.get("gems_required", 0)
        yuanbao_reward = tier.get("yuanbao_reward", 0)
        claim_key = f"rebate_{gems_required}"
        claimed = svc._get_daily_claim_count(user_id, "yuanbao_rebate", claim_key, today) > 0
        tier_status.append({
            "gems_required": gems_required,
            "yuanbao_reward": yuanbao_reward,
            "claimed": claimed,
            "can_claim": not claimed and today_gems >= gems_required,
        })
    
    return jsonify({
        "ok": True,
        # 兼容字段名：这里返回的是“今日赞助宝石”，以匹配活动文案（每天刷新）
        "total_gems": today_gems,
        "today_gems": today_gems,
        "tiers": tier_status,
    })


@announcement_bp.post("/rebate/claim")
def claim_rebate():
    """领取元宝返利"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    data = request.get_json() or {}
    tier_gems = data.get("tier_gems", 0)
    
    try:
        tier_gems = int(tier_gems)
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "无效的档位"})
    
    svc = _get_service()
    result = svc.claim_yuanbao_rebate(user_id, tier_gems)
    
    # 返回最新元宝
    if result.get("ok"):
        player = services.player_repo.get_by_id(user_id)
        result["yuanbao"] = getattr(player, 'yuanbao', 0) or 0 if player else 0
    
    return jsonify(result)

