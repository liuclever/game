from flask import Blueprint, request, jsonify

from interfaces.web_api.bootstrap import services


handbook_bp = Blueprint("handbook", __name__, url_prefix="/api/handbook")


@handbook_bp.get("/index")
def handbook_index():
    """图鉴列表页（独立模块，无需登录）。"""
    pacename = request.args.get("pacename", type=int) or 1
    page = request.args.get("page", type=int) or 1
    page_size = request.args.get("pageSize", type=int) or 10
    result = services.handbook_service.get_index(pacename=pacename, page=page, page_size=page_size)
    return jsonify(result)


@handbook_bp.get("/pets/<int:pet_id>")
def handbook_pet_detail(pet_id: int):
    """图鉴详情页（独立模块，无需登录）。"""
    evolution = request.args.get("evolution", type=int) or 0
    result = services.handbook_service.get_pet_detail(pet_id=pet_id, evolution=evolution)
    status = 200 if result.get("ok") else 404
    return jsonify(result), status


@handbook_bp.get("/skills/<skill_key>")
def handbook_skill_detail(skill_key: str):
    """技能说明页（独立模块，无需登录）。"""
    result = services.handbook_service.get_skill_detail(skill_key=skill_key)
    status = 200 if result.get("ok") else 404
    return jsonify(result), status


