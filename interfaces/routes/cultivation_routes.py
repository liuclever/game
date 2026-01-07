# interfaces/routes/cultivation_routes.py
"""
修行系统路由
"""
from flask import Blueprint, request, jsonify, session
from interfaces.web_api.bootstrap import services
from application.services.cultivation_service import CultivationError
from domain.rules.cultivation_rules import load_cultivation_config
import os
import json
from datetime import datetime
import math
from infrastructure.db.connection import execute_query, execute_update
import logging

cultivation_bp = Blueprint('cultivation', __name__, url_prefix='/api/cultivation')

logger = logging.getLogger(__name__)


def get_current_user_id() -> int:
    return session.get('user_id', 0)


def _load_maps_config():
    config_path = os.path.join(os.path.dirname(__file__), '../../configs/maps.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


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
    total_seconds = distance * 60
    elapsed = (datetime.now() - started_at).total_seconds()
    remaining = int(math.ceil(total_seconds - elapsed))
    return max(0, remaining)


def _settle_player_location_if_arrived(user_id: int):
    rows = execute_query(
        "SELECT location, moving_to, last_map_move_at FROM player WHERE user_id = %s",
        (user_id,),
    )
    if not rows:
        return None
    row = rows[0]
    current_location = (row.get('location') or '落龙镇').strip()
    moving_to = row.get('moving_to')
    if isinstance(moving_to, str):
        moving_to = moving_to.strip()
    started_at = row.get('last_map_move_at')

    if not moving_to:
        return {"moving": False, "remaining": 0, "location": current_location}

    maps = _load_maps_config()
    remaining = _get_remaining_move_seconds(maps, current_location, moving_to, started_at)
    if remaining <= 0:
        execute_update(
            "UPDATE player SET location = %s, moving_to = NULL, last_map_move_at = NULL WHERE user_id = %s",
            (moving_to, user_id),
        )
        return {"moving": False, "remaining": 0, "location": moving_to}

    return {"moving": True, "remaining": remaining, "location": current_location, "moving_to": moving_to}


@cultivation_bp.route('/status', methods=['GET'])
def get_cultivation_status():
    """获取当前修行状态"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    try:
        status = services.cultivation_service.get_status(user_id)
        return jsonify({"ok": True, **status})
    except CultivationError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@cultivation_bp.route('/start', methods=['POST'])
def start_cultivation():
    """开始修行"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    settle = _settle_player_location_if_arrived(user_id)
    if settle and settle.get('moving'):
        return jsonify({"ok": False, "error": f"移动中，无法开始修行（剩余{settle.get('remaining', 0)}秒）"}), 400
    
    data = request.get_json() or {}
    area_name = data.get('area_name')
    dungeon_name = data.get('dungeon_name')
    duration_hours = data.get('duration_hours', data.get('hours', 2))

    try:
        raw_body = request.get_data(as_text=True)
        logger.info(
            "[cultivation.start] user_id=%s path=%s content_type=%s raw_body=%s json=%s duration_hours_field=%s hours_field=%s parsed_duration_hours=%s",
            user_id,
            request.path,
            request.content_type,
            raw_body,
            data,
            data.get('duration_hours'),
            data.get('hours'),
            duration_hours,
        )
    except Exception:
        pass
    
    if not area_name or not dungeon_name:
        return jsonify({"ok": False, "error": "请指定修行区域和副本"}), 400
    
    try:
        result = services.cultivation_service.start(user_id, area_name, dungeon_name, duration_hours)
        return jsonify(result)
    except CultivationError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@cultivation_bp.route('/end', methods=['POST'])
def end_cultivation():
    """结束修行并领取奖励"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    try:
        result = services.cultivation_service.end(user_id)
        return jsonify(result)
    except CultivationError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@cultivation_bp.route('/harvest', methods=['POST'])
def harvest_cultivation():
    """领取修行奖励（end的别名）"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    try:
        result = services.cultivation_service.end(user_id)
        return jsonify(result)
    except CultivationError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@cultivation_bp.route('/stop', methods=['POST'])
def stop_cultivation():
    """终止修行（不领取奖励）"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    try:
        result = services.cultivation_service.stop(user_id)
        return jsonify(result)
    except CultivationError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@cultivation_bp.route('/options', methods=['GET'])
def get_cultivation_options():
    """获取当前位置可修行的副本选项"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    settle = _settle_player_location_if_arrived(user_id)
    if settle and settle.get('moving'):
        return jsonify({
            "ok": True,
            "options": [],
            "areas": [],
            "moving": True,
            "remaining_seconds": settle.get('remaining', 0),
            "current_location": settle.get('location'),
        })
    
    player = services.player_repo.get_by_id(user_id)
    if not player:
        return jsonify({"ok": False, "error": "玩家不存在"}), 404
    
    raw_location = player.location
    current_location = (raw_location or '').strip() or '落龙镇'
    config = load_cultivation_config()
    
    # 查找当前位置对应的修行配置
    area_config = next((a for a in config.get("areas", []) if a["name"] == current_location), None)
    
    if not area_config or not area_config.get("can_cultivate", False):
        return jsonify({
            "ok": True,
            "options": [],
            "areas": [],
            "current_location": current_location,
            "raw_location": raw_location,
        })
    
    # 返回当前位置的修行选项
    areas = [{
        "name": current_location,
        "dungeons": [{"name": d["name"]} for d in area_config.get("dungeons", [])]
    }]
    
    return jsonify({
        "ok": True,
        "options": areas,
        "areas": areas,
        "current_location": current_location,
        "raw_location": raw_location,
    })


@cultivation_bp.route('/maps', methods=['GET'])
def get_cultivation_maps():
    """获取所有可修行地图及其副本配置"""
    config = load_cultivation_config()
    
    # 只返回可修行的区域
    cultivable_areas = []
    for area in config.get("areas", []):
        if area.get("can_cultivate", False):
            cultivable_areas.append({
                "name": area["name"],
                "prestige_rate": area.get("prestige_rate", 0),
                "beast_exp_rate": area.get("beast_exp_rate", 0),
                "stone_rate": area.get("stone_rate", 0),
                "dungeons": [
                    {
                        "name": d["name"],
                        "capture_balls": d.get("capture_balls", [])
                    }
                    for d in area.get("dungeons", [])
                ]
            })
    
    return jsonify({
        "ok": True,
        "areas": cultivable_areas
    })


@cultivation_bp.route('/available-dungeons', methods=['GET'])
def get_available_dungeons():
    """
    根据玩家当前所在地图，返回可修行的副本列表
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    settle = _settle_player_location_if_arrived(user_id)
    if settle and settle.get('moving'):
        return jsonify({
            "ok": True,
            "can_cultivate": False,
            "message": f"移动中，无法修行（剩余{settle.get('remaining', 0)}秒）",
            "dungeons": [],
            "current_location": settle.get('location'),
        })
    
    player = services.player_repo.get_by_id(user_id)
    if not player:
        return jsonify({"ok": False, "error": "玩家不存在"}), 404

    raw_location = player.location
    current_location = (raw_location or '').strip() or '落龙镇'
    config = load_cultivation_config()
    
    # 查找当前位置对应的修行配置
    area_config = next((a for a in config.get("areas", []) if a["name"] == current_location), None)
    
    if not area_config:
        return jsonify({
            "ok": True,
            "can_cultivate": False,
            "message": f"{current_location} 不支持修行，只有定老城及以上地图才能修行",
            "dungeons": [],
            "current_location": current_location,
            "area_name": current_location,
            "raw_location": raw_location,
        })
    
    if not area_config.get("can_cultivate", False):
        return jsonify({
            "ok": True,
            "can_cultivate": False,
            "message": f"{current_location} 不支持修行，只有定老城及以上地图才能修行",
            "dungeons": [],
            "current_location": current_location,
            "area_name": current_location,
            "raw_location": raw_location,
        })
    
    dungeons = []
    for d in area_config.get("dungeons", []):
        dungeons.append({
            "name": d["name"],
            "capture_balls": d.get("capture_balls", [])
        })
    
    return jsonify({
        "ok": True,
        "can_cultivate": True,
        "area_name": current_location,
        "current_location": current_location,
        "raw_location": raw_location,
        "prestige_rate": area_config.get("prestige_rate", 0),
        "beast_exp_rate": area_config.get("beast_exp_rate", 0),
        "stone_rate": area_config.get("stone_rate", 0),
        "dungeons": dungeons
    })
