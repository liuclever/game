# interfaces/routes/map_routes.py
"""地图系统路由"""

import math
from datetime import datetime
import json
import os
from flask import Blueprint, request, jsonify, session
from infrastructure.db.connection import execute_query, execute_update

map_bp = Blueprint('map', __name__, url_prefix='/api/map')

TELEPORT_ITEM_ID = 6018
MOVE_COOLDOWN_SECONDS = 60


def load_maps_config():
    config_path = os.path.join(os.path.dirname(__file__), '../../configs/maps.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_current_user_id() -> int:
    return session.get('user_id', 0)


def _find_city_index(maps: list, city_name: str) -> int:
    for i, m in enumerate(maps):
        if m.get('name') == city_name:
            return i
    return -1


def _get_remaining_move_seconds(maps: list, start_city: str, target_city: str, started_at) -> int:
    if not isinstance(started_at, datetime):
        return 0
    start_index = _find_city_index(maps, start_city)
    target_index = _find_city_index(maps, target_city)
    if start_index < 0 or target_index < 0:
        return 0
    distance = abs(target_index - start_index)
    total_seconds = distance * MOVE_COOLDOWN_SECONDS
    elapsed = (datetime.now() - started_at).total_seconds()
    remaining = int(math.ceil(total_seconds - elapsed))
    return max(0, remaining)


@map_bp.get("/info")
def get_map_info():
    """获取地图信息"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    rows = execute_query(
        "SELECT level, location, moving_to, last_map_move_at FROM player WHERE user_id = %s",
        (user_id,),
    )
    if not rows:
        return jsonify({"ok": False, "error": "玩家不存在"})

    row = rows[0]
    current_location = row.get('location') or '落龙镇'
    moving_to = row.get('moving_to')
    started_at = row.get('last_map_move_at')

    moving = False
    remaining_seconds = 0

    if moving_to:
        maps = load_maps_config()
        remaining_seconds = _get_remaining_move_seconds(maps, current_location, moving_to, started_at)
        if remaining_seconds <= 0:
            execute_update(
                "UPDATE player SET location = %s, moving_to = NULL, last_map_move_at = NULL WHERE user_id = %s",
                (moving_to, user_id),
            )
            current_location = moving_to
            moving_to = None
        else:
            moving = True

    return jsonify({
        "ok": True,
        "current_location": current_location,
        "level": row.get('level', 1),
        "moving": moving,
        "moving_to": moving_to,
        "remaining_seconds": remaining_seconds,
    })


@map_bp.post("/move")
def map_move():
    """移动到相邻城市"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    data = request.get_json() or {}
    city = data.get("city", "")

    rows = execute_query(
        "SELECT level, location, moving_to, last_map_move_at FROM player WHERE user_id = %s",
        (user_id,),
    )
    if not rows:
        return jsonify({"ok": False, "error": "玩家不存在"})

    player_level = rows[0]['level']
    current_city = rows[0].get('location') or '落龙镇'
    moving_to = rows[0].get('moving_to')
    started_at = rows[0].get('last_map_move_at')

    maps = load_maps_config()
    if moving_to:
        remaining = _get_remaining_move_seconds(maps, current_city, moving_to, started_at)
        if remaining > 0:
            return jsonify({"ok": False, "error": f"移动中，请等待{remaining}秒"})
        execute_update(
            "UPDATE player SET location = %s, moving_to = NULL, last_map_move_at = NULL WHERE user_id = %s",
            (moving_to, user_id),
        )
        current_city = moving_to
        moving_to = None
        started_at = None

    current_index = _find_city_index(maps, current_city)
    target_index = _find_city_index(maps, city)
    if target_index < 0:
        return jsonify({"ok": False, "error": "无效城市"})
    if current_index < 0:
        return jsonify({"ok": False, "error": "当前位置无效"})
    if target_index == current_index:
        return jsonify({"ok": True, "message": f"已在{city}"})

    target_map = maps[target_index]

    if target_map and player_level < target_map['min_level']:
        return jsonify({"ok": False, "error": f"等级不足，需要{target_map['min_level']}级才能前往{city}"})

    distance = abs(target_index - current_index)
    total_seconds = distance * MOVE_COOLDOWN_SECONDS
    execute_update(
        "UPDATE player SET moving_to = %s, last_map_move_at = NOW() WHERE user_id = %s",
        (city, user_id),
    )

    return jsonify({"ok": True, "message": f"开始移动，预计{total_seconds}秒后到达{city}"})


@map_bp.post("/teleport")
def map_teleport():
    """传送到城市"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    data = request.get_json() or {}
    city = data.get("city", "")

    rows = execute_query(
        "SELECT level, location, moving_to, last_map_move_at FROM player WHERE user_id = %s",
        (user_id,),
    )
    if not rows:
        return jsonify({"ok": False, "error": "玩家不存在"})

    player_level = rows[0]['level']
    current_city = rows[0].get('location') or '落龙镇'
    moving_to = rows[0].get('moving_to')
    started_at = rows[0].get('last_map_move_at')

    maps = load_maps_config()
    if moving_to:
        remaining = _get_remaining_move_seconds(maps, current_city, moving_to, started_at)
        if remaining > 0:
            execute_update(
                "UPDATE player SET moving_to = NULL, last_map_move_at = NULL WHERE user_id = %s",
                (user_id,),
            )
            moving_to = None
            started_at = None

    target_map = next((m for m in maps if m['name'] == city), None)
    if not target_map:
        return jsonify({"ok": False, "error": "无效城市"})

    if target_map and player_level < target_map['min_level']:
        return jsonify({"ok": False, "error": f"等级不足，需要{target_map['min_level']}级才能前往{city}"})

    affected = execute_update(
        "UPDATE player_inventory "
        "SET quantity = quantity - 1 "
        "WHERE user_id = %s AND item_id = %s AND is_temporary = 0 AND quantity >= 1",
        (user_id, TELEPORT_ITEM_ID),
    )
    if affected <= 0:
        return jsonify({"ok": False, "error": "传送符不足！"})

    execute_update(
        "UPDATE player SET location = %s, moving_to = NULL, last_map_move_at = NULL WHERE user_id = %s",
        (city, user_id),
    )

    return jsonify({"ok": True, "message": f"已传送到{city}"})


@map_bp.get("/teleport-count")
def get_teleport_count():
    """获取传送符数量"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    rows = execute_query(
        "SELECT quantity FROM player_inventory WHERE user_id = %s AND item_id = %s AND is_temporary = 0",
        (user_id, TELEPORT_ITEM_ID),
    )
    count = rows[0].get('quantity', 0) if rows else 0
    return jsonify({"ok": True, "count": count})
