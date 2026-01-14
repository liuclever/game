"""
世界聊天路由
"""
from flask import Blueprint, request, jsonify, session
from interfaces.web_api.bootstrap import services
from application.services.world_chat_service import WorldChatError

world_chat_bp = Blueprint('world_chat', __name__, url_prefix='/api/world-chat')


def get_current_user_id() -> int:
    """获取当前登录用户ID"""
    return session.get('user_id', 0)


@world_chat_bp.post('/send')
def send_message():
    """发送世界聊天消息"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    data = request.get_json() or {}
    content = data.get('content', '').strip()
    message_type = data.get('message_type', 'normal')
    
    if not content:
        return jsonify({"ok": False, "error": "消息内容不能为空"}), 400
    
    try:
        result = services.world_chat_service.send_message(
            user_id=user_id, content=content, message_type=message_type
        )
        return jsonify(result)
    except WorldChatError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": f"发送失败：{str(e)}"}), 500


@world_chat_bp.get('/messages')
def get_messages():
    """获取世界聊天消息列表（分页）"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 50:
        page_size = 10
    
    result = services.world_chat_service.get_messages(
        page=page, page_size=page_size, exclude_alliance=True, exclude_system=True
    )
    return jsonify(result)


@world_chat_bp.get('/homepage')
def get_homepage_messages():
    """获取首页显示的喊话消息（最多3条）"""
    try:
        messages = services.world_chat_service.get_homepage_messages(limit=3)
        return jsonify({"ok": True, "messages": messages})
    except Exception as e:
        # 记录错误但不中断服务
        import traceback
        print(f"获取首页消息失败: {e}")
        print(traceback.format_exc())
        return jsonify({"ok": True, "messages": []})


@world_chat_bp.get('/pinned')
def get_pinned_message():
    """获取置顶的召唤之王消息"""
    try:
        message = services.world_chat_service.get_pinned_message()
        return jsonify({"ok": True, "message": message})
    except Exception as e:
        # 记录错误但不中断服务
        import traceback
        print(f"获取置顶消息失败: {e}")
        print(traceback.format_exc())
        return jsonify({"ok": True, "message": None})


@world_chat_bp.get('/horn-count')
def get_horn_count():
    """获取玩家小喇叭数量"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    count = services.world_chat_service.get_horn_count(user_id)
    return jsonify({"ok": True, "count": count})


@world_chat_bp.get('/is-summon-king')
def check_is_summon_king():
    """检查当前玩家是否是召唤之王"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    is_king = services.world_chat_service._is_summon_king(user_id)
    return jsonify({"ok": True, "is_summon_king": is_king})
