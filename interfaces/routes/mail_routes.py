"""
信件路由
处理私信和好友请求
"""
from flask import Blueprint, request, jsonify, session
from interfaces.web_api.bootstrap import services
from application.services.mail_service import MailService

mail_bp = Blueprint('mail', __name__, url_prefix='/api/mail')


def get_current_user_id() -> int:
    """获取当前登录用户ID"""
    return session.get('user_id', 0)


def get_current_user_name() -> str:
    """获取当前登录用户昵称"""
    try:
        user_id = get_current_user_id()
        if user_id:
            player = services.player_repo.get_by_id(user_id)
            if player:
                return player.nickname or f"玩家{user_id}"
    except Exception:
        pass
    return "未知"


@mail_bp.get('/private-message/senders')
def get_private_message_senders():
    """获取私信发送者列表"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    mail_service = MailService()
    senders = mail_service.get_private_message_senders(user_id)
    return jsonify({"ok": True, "senders": senders})


@mail_bp.get('/private-message/conversation')
def get_conversation():
    """获取与某个玩家的聊天记录"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    target_id = int(request.args.get('target_id', 0))
    if not target_id:
        return jsonify({"ok": False, "error": "缺少目标用户ID"}), 400
    
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))
    
    mail_service = MailService()
    result = mail_service.get_conversation_messages(
        user_id=user_id, target_id=target_id, page=page, page_size=page_size
    )
    return jsonify(result)


@mail_bp.post('/private-message/send')
def send_private_message():
    """发送私信"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    data = request.get_json() or {}
    target_id = int(data.get('target_id', 0))
    content = data.get('content', '').strip()
    
    if not target_id:
        return jsonify({"ok": False, "error": "缺少目标用户ID"}), 400
    if not content:
        return jsonify({"ok": False, "error": "消息内容不能为空"}), 400
    
    try:
        target_player = services.player_repo.get_by_id(target_id)
        if not target_player:
            return jsonify({"ok": False, "error": "目标用户不存在"}), 404
        receiver_name = target_player.nickname or f"玩家{target_id}"
    except Exception:
        return jsonify({"ok": False, "error": "获取目标用户信息失败"}), 500
    
    sender_name = get_current_user_name()
    
    mail_service = MailService()
    result = mail_service.send_private_message(
        sender_id=user_id, sender_name=sender_name,
        receiver_id=target_id, receiver_name=receiver_name, content=content
    )
    status = 200 if result.get('ok') else 400
    return jsonify(result), status


@mail_bp.delete('/private-message/conversation')
def delete_conversation():
    """删除与某个玩家的所有私信"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    target_id = int(request.args.get('target_id', 0))
    if not target_id:
        return jsonify({"ok": False, "error": "缺少目标用户ID"}), 400
    
    mail_service = MailService()
    result = mail_service.delete_conversation(user_id, target_id)
    status = 200 if result.get('ok') else 400
    return jsonify(result), status


@mail_bp.get('/friend-request/list')
def get_friend_requests():
    """获取好友请求列表"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    
    mail_service = MailService()
    result = mail_service.get_friend_requests(user_id=user_id, page=page, page_size=page_size)
    return jsonify(result)


@mail_bp.post('/friend-request/send')
def send_friend_request():
    """发送好友请求"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    data = request.get_json() or {}
    target_id = int(data.get('target_id', 0))
    
    if not target_id:
        return jsonify({"ok": False, "error": "缺少目标用户ID"}), 400
    
    try:
        target_player = services.player_repo.get_by_id(target_id)
        if not target_player:
            return jsonify({"ok": False, "error": "目标用户不存在"}), 404
        receiver_name = target_player.nickname or f"玩家{target_id}"
    except Exception:
        return jsonify({"ok": False, "error": "获取目标用户信息失败"}), 500
    
    requester_name = get_current_user_name()
    
    mail_service = MailService()
    result = mail_service.send_friend_request(
        requester_id=user_id, requester_name=requester_name,
        receiver_id=target_id, receiver_name=receiver_name
    )
    status = 200 if result.get('ok') else 400
    return jsonify(result), status


@mail_bp.post('/friend-request/accept')
def accept_friend_request():
    """接受好友请求"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    data = request.get_json() or {}
    request_id = int(data.get('request_id', 0))
    
    if not request_id:
        return jsonify({"ok": False, "error": "缺少请求ID"}), 400
    
    mail_service = MailService()
    result = mail_service.accept_friend_request(request_id, user_id)
    status = 200 if result.get('ok') else 400
    return jsonify(result), status


@mail_bp.post('/friend-request/reject')
def reject_friend_request():
    """拒绝好友请求"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    data = request.get_json() or {}
    request_id = int(data.get('request_id', 0))
    
    if not request_id:
        return jsonify({"ok": False, "error": "缺少请求ID"}), 400
    
    mail_service = MailService()
    result = mail_service.reject_friend_request(request_id, user_id)
    status = 200 if result.get('ok') else 400
    return jsonify(result), status
