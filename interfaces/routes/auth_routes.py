# interfaces/routes/auth_routes.py
"""认证相关路由：登录、注册、登出"""

from datetime import datetime
from flask import Blueprint, request, jsonify, session
from interfaces.web_api.bootstrap import services
from application.services.auth_service import is_test_mode
from infrastructure.db.connection import execute_query

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def get_current_user_id() -> int:
    """获取当前登录用户ID，未登录返回0"""
    return session.get('user_id', 0)


@auth_bp.post("/login")
def login():
    """登录"""
    data = request.get_json() or {}
    username = data.get("username", "").strip()  # 去除首尾空格
    password = data.get("password", "").strip()  # 去除首尾空格
    
    result = services.auth_service.login(username, password)
    
    if result.success:
        session['user_id'] = result.user_id
        session['nickname'] = result.nickname
        return jsonify({
            "ok": True,
            "user_id": result.user_id,
            "nickname": result.nickname,
            "level": result.level,
            "rank_name": result.rank_name,
        })
    else:
        return jsonify({"ok": False, "error": result.error})


@auth_bp.post("/register")
def register():
    """注册"""
    data = request.get_json() or {}
    username = data.get("username", "")
    password = data.get("password", "")
    nickname = data.get("nickname", "")
    
    result = services.auth_service.register(username, password, nickname)
    
    if result.success:
        session['user_id'] = result.user_id
        session['nickname'] = result.nickname
        return jsonify({
            "ok": True,
            "user_id": result.user_id,
            "nickname": result.nickname,
            "level": result.level,
            "rank_name": result.rank_name,
        })
    else:
        return jsonify({"ok": False, "error": result.error})


@auth_bp.post("/logout")
def logout():
    """登出"""
    session.clear()
    return jsonify({"ok": True})


@auth_bp.get("/game-config")
def game_config():
    """获取游戏配置（如模式）"""
    return jsonify({
        "ok": True,
        "is_test_mode": is_test_mode(),
    })


@auth_bp.get("/status")
def auth_status():
    """获取登录状态"""
    user_id = get_current_user_id()
    if user_id:
        player = services.player_repo.get_by_id(user_id)
        if player:
            # 处理活力恢复与上限检查
            if player.recover_energy():
                services.player_repo.save(player)
                
            beasts = services.player_beast_repo.get_team_beasts(user_id)
            battle_power = 0
            if beasts:
                # 与 /api/beast/list 保持一致：先重算每只出战幻兽的属性/战力并回写
                from interfaces.routes.beast_routes import _calc_beast_stats, _calc_total_combat_power_with_equipment

                for b in beasts:
                    b = _calc_beast_stats(b)
                    services.player_beast_repo.update_beast(b)
                    battle_power += int(_calc_total_combat_power_with_equipment(b) or 0)
            
            return jsonify({
                "ok": True,
                "logged_in": True,
                "user_id": user_id,
                "nickname": player.nickname,
                "level": player.level,
                "exp": player.exp,
                "vip_level": player.vip_level,
                "max_energy": player.max_energy,
                "rank_name": player.get_rank_name(),
                "battle_power": battle_power,
                "crystal_tower": player.crystal_tower,
                "energy": player.energy,
                "prestige": player.prestige,
                # 金币/铜钱字段历史遗留较多：这里保持语义清晰
                "gold": player.gold,
                "copper": player.copper,
                "spirit_stone": player.spirit_stone,
                "yuanbao": player.yuanbao,
                "silver_diamond": getattr(player, "silver_diamond", 0),
                "last_signin_date": (
                    player.last_signin_date.date().isoformat() if isinstance(player.last_signin_date, datetime) else (player.last_signin_date.isoformat() if getattr(player, "last_signin_date", None) else None)
                ),
                "signin_streak": int(getattr(player, "signin_streak", 0) or 0),
            })
    return jsonify({"ok": True, "logged_in": False})

