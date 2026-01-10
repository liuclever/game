from flask import Blueprint, request, jsonify, session

from interfaces.web_api.bootstrap import services
from application.services.refine_pot_service import RefinePotError


refine_pot_bp = Blueprint("refine_pot", __name__, url_prefix="/refine-pot")


def get_current_user_id() -> int:
    return session.get('user_id', 0)


@refine_pot_bp.post("/refine")
def refine():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "未登录"}), 401

    data = request.get_json(silent=True) or {}
    main_id = data.get("main_beast_id")
    material_id = data.get("material_beast_id")
    attr_type = data.get("attr_type")

    if not main_id or not material_id or not attr_type:
        return jsonify({"ok": False, "error": "参数不完整"}), 400

    try:
        main_id = int(main_id)
        material_id = int(material_id)
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "幻兽ID必须为整数"}), 400

    try:
        result = services.refine_pot_service.refine(
            user_id=user_id,
            main_id=main_id,
            material_id=material_id,
            attr_type=str(attr_type),
        )
        return jsonify({"ok": True, "data": result})
    except RefinePotError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
