"""
动态路由
"""
from flask import Blueprint, request, jsonify, session
from application.services.dynamics_service import DynamicsService

dynamics_bp = Blueprint('dynamics', __name__, url_prefix='/api/dynamics')


def get_current_user_id() -> int:
    """获取当前登录用户ID"""
    return session.get('user_id', 0)


@dynamics_bp.get('/my-dynamics')
def get_my_dynamics():
    """获取我的动态列表（分页）"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 50:
        page_size = 10
    
    dynamics_service = DynamicsService()
    result = dynamics_service.get_user_dynamics(
        user_id=user_id, page=page, page_size=page_size
    )
    return jsonify(result)
