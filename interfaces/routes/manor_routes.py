# interfaces/routes/manor_routes.py
"""庄园系统路由：土地扩建、种植、收获"""

from flask import Blueprint, request, jsonify, session
from interfaces.web_api.bootstrap import services

manor_bp = Blueprint('manor', __name__, url_prefix='/api')

def get_current_user_id() -> int:
    return session.get('user_id', 0)

@manor_bp.get("/manor/status")
def get_manor_status():
    """获取所有土地状态"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    info = services.manor_service.get_manor_info(user_id)
    return jsonify({"ok": True, **info})

@manor_bp.post("/manor/expand")
def expand_land():
    """扩建土地"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    data = request.get_json() or {}
    land_index = data.get("land_index")
    
    if land_index is None:
        return jsonify({"ok": False, "error": "缺少土地索引"})
        
    success, msg = services.manor_service.expand_land(user_id, int(land_index))
    return jsonify({"ok": success, "message": msg})

@manor_bp.post("/manor/plant")
def plant_tree():
    """种植（支持单选或全选）"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    data = request.get_json() or {}
    land_indices = data.get("land_indices", [])
    tree_type = data.get("tree_type")
    
    if not land_indices:
        return jsonify({"ok": False, "error": "请选择要种植的土地"})
    if not tree_type:
        return jsonify({"ok": False, "error": "请选择树种"})
        
    success, msg = services.manor_service.plant_tree(user_id, [int(i) for i in land_indices], int(tree_type))
    return jsonify({"ok": success, "message": msg})

@manor_bp.post("/manor/harvest")
def harvest_all():
    """一键收获"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
        
    success, msg, result = services.manor_service.harvest_all(user_id)
    return jsonify({"ok": success, "message": msg, "result": result})
