# interfaces/routes/bone_routes.py
"""战骨相关路由：升级、进阶、查询、创建"""

from flask import Blueprint, jsonify, session, request
from interfaces.web_api.bootstrap import services
from application.services.bone_service import BoneError

bone_bp = Blueprint('bone', __name__, url_prefix='/api/bone')


def get_current_user_id() -> int:
    return session.get('user_id', 0)


@bone_bp.post("/create")
def create_bone():
    """创建战骨（测试用）"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    data = request.get_json() or {}
    template_id = int(data.get("template_id", 0))
    stage = int(data.get("stage", 1))
    level = int(data.get("level", 1))

    if template_id == 0:
        return jsonify({"ok": False, "error": "template_id 必填"})

    try:
        bone_info = services.bone_service.create_bone(
            user_id=user_id,
            template_id=template_id,
            stage=stage,
            level=level
        )
        return jsonify({"ok": True, "bone": bone_info.to_dict()})
    except BoneError as e:
        return jsonify({"ok": False, "error": str(e)})
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)})


@bone_bp.get("/list")
def get_bone_list():
    """获取玩家所有战骨"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    bones = services.bone_service.get_bones(user_id)
    return jsonify({
        "ok": True,
        "bones": [b.to_dict() for b in bones],
    })


@bone_bp.get("/<int:bone_id>")
def get_bone_detail(bone_id: int):
    """获取单个战骨详情"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    bone_info = services.bone_service.get_bone(user_id, bone_id)
    if bone_info is None:
        return jsonify({"ok": False, "error": "战骨不存在"}), 404

    return jsonify({
        "ok": True,
        "bone": bone_info.to_dict(),
    })


@bone_bp.get("/<int:bone_id>/upgrade-cost")
def get_upgrade_cost(bone_id: int):
    """查询升级消耗"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    try:
        cost = services.bone_service.get_upgrade_cost(user_id, bone_id)
        return jsonify({"ok": True, **cost})
    except BoneError as e:
        return jsonify({"ok": False, "error": str(e)})


@bone_bp.post("/<int:bone_id>/upgrade")
def upgrade_bone(bone_id: int):
    """升级战骨"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    try:
        bone_info = services.bone_service.upgrade_bone(user_id, bone_id)
        return jsonify({
            "ok": True,
            "message": "升级成功",
            "bone": bone_info.to_dict(),
        })
    except BoneError as e:
        return jsonify({"ok": False, "error": str(e)})


@bone_bp.get("/<int:bone_id>/refine-cost")
def get_refine_cost(bone_id: int):
    """查询进阶消耗"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    try:
        cost = services.bone_service.get_refine_cost(user_id, bone_id)
        return jsonify({"ok": True, **cost})
    except BoneError as e:
        return jsonify({"ok": False, "error": str(e)})


@bone_bp.get("/<int:bone_id>/refine-preview")
def get_refine_preview(bone_id: int):
    """获取炼制预览信息（包含当前属性、进阶后属性、材料需求）"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    try:
        # 获取战骨信息
        bone_info = services.bone_service.get_bone(user_id, bone_id)
        if bone_info is None:
            return jsonify({"ok": False, "error": "战骨不存在"}), 404

        bone = bone_info.bone
        current_stage = bone.stage
        current_level = bone.level
        to_stage = current_stage + 1

        # 获取配置
        from infrastructure.config.bone_system_config import get_bone_system_config
        config = get_bone_system_config()

        # 获取当前阶段和下一阶段配置
        current_stage_cfg = config.get_stage_config(current_stage)
        next_stage_cfg = config.get_stage_config(to_stage)

        if next_stage_cfg is None:
            return jsonify({
                "ok": False,
                "error": "已达最高阶段",
                "isMaxStage": True,
            })

        # 获取炼制消耗
        refine_cost = services.bone_service.get_refine_cost(user_id, bone_id)

        # 计算进阶后的属性（进阶后等级为下一阶段的起始等级）
        next_level = next_stage_cfg.get("min_level", current_level)
        next_stats = config.calc_bone_stats(to_stage, bone.slot, next_level)

        # 战骨阶段名称
        stage_names = {
            1: "原始", 2: "碎空", 3: "猎魔", 4: "龙炎", 5: "奔雷",
            6: "凌霄", 7: "麒麟", 8: "武神", 9: "弑天", 10: "毁灭",
        }

        current_stage_name = stage_names.get(current_stage, "原始")
        next_stage_name = stage_names.get(to_stage, "")

        # 构建返回数据
        return jsonify({
            "ok": True,
            "bone": {
                "id": bone.id,
                "slot": bone.slot,
                "currentName": f"{current_stage_name}{bone.slot}",
                "nextName": f"{next_stage_name}{bone.slot}",
                "currentStage": current_stage,
                "nextStage": to_stage,
                "currentStars": current_stage_cfg.get("stars", 0),
                "nextStars": next_stage_cfg.get("stars", 0),
                "currentLevel": current_level,
                "nextLevel": next_level,
                # 当前属性
                "currentStats": {
                    "hp": bone.hp_flat,
                    "attack": bone.attack_flat,
                    "physicalDefense": bone.physical_defense_flat,
                    "magicDefense": bone.magic_defense_flat,
                    "speed": bone.speed_flat,
                },
                # 进阶后属性
                "nextStats": {
                    "hp": next_stats.get("hp", 0),
                    "attack": max(int(next_stats.get("physical_attack", 0) or 0), int(next_stats.get("magic_attack", 0) or 0)),
                    "physicalDefense": next_stats.get("physical_defense", 0),
                    "magicDefense": next_stats.get("magic_defense", 0),
                    "speed": next_stats.get("speed", 0),
                },
            },
            "requiredLevel": next_stage_cfg.get("min_player_level", 1),
            "materials": refine_cost.get("materials", []),
            "canRefine": refine_cost.get("can_refine", False),
            "reason": refine_cost.get("reason", ""),
        })
    except BoneError as e:
        return jsonify({"ok": False, "error": str(e)})


@bone_bp.post("/<int:bone_id>/refine")
def refine_bone(bone_id: int):
    """进阶/炼制战骨"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    try:
        bone_info = services.bone_service.refine_bone(user_id, bone_id)
        return jsonify({
            "ok": True,
            "message": "进阶成功",
            "bone": bone_info.to_dict(),
        })
    except BoneError as e:
        return jsonify({"ok": False, "error": str(e)})


@bone_bp.get("/beast/<int:beast_id>/equipped")
def get_beast_equipped_bones(beast_id: int):
    """获取指定幻兽的已装备战骨"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    # 获取该幻兽装备的所有战骨
    bones = services.bone_repo.get_by_beast_id(beast_id)
    
    # 槽位名称映射
    slot_names = {
        "头骨": "头",
        "胸骨": "胸",
        "臂骨": "臂",
        "手骨": "手",
        "腿骨": "腿",
        "尾骨": "尾",
        "元魂": "魂",
    }
    
    # 战骨阶段名称
    stage_names = {
        1: "原始",
        2: "碎空",
        3: "猎魔",
        4: "龙炎",
        5: "奔雷",
        6: "凌霄",
        7: "麒麟",
        8: "武神",
        9: "弑天",
        10: "毁灭",
    }
    
    # 构建槽位数据
    slots_data = {}
    for bone in bones:
        slot_display = slot_names.get(bone.slot, bone.slot)
        stage_name = stage_names.get(bone.stage, "原始")
        slots_data[slot_display] = {
            "id": bone.id,
            "name": f"{stage_name}{bone.slot}",
            "slot": bone.slot,
            "level": bone.level,
            "stage": bone.stage,
            "stageName": stage_name,
        }
    
    return jsonify({
        "ok": True,
        "beastId": beast_id,
        "slots": slots_data,
    })


@bone_bp.get("/page-data")
def get_bone_page_data():
    """获取战骨页面所需的所有数据（幻兽列表 + 玩家资源）"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    # 获取玩家信息
    player = services.player_repo.get_by_id(user_id)
    if not player:
        return jsonify({"ok": False, "error": "玩家不存在"})
    
    # 获取所有幻兽
    all_beasts = services.player_beast_repo.get_all_by_user(user_id)
    
    beast_list = [
        {
            "id": b.id,
            "name": b.name,
            "realm": b.realm,
            "level": b.level,
        }
        for b in all_beasts
    ]

    enhancement_stone = services.inventory_service.get_item_count(user_id, 9001, include_temp=True)
    
    return jsonify({
        "ok": True,
        "beasts": beast_list,
        "gold": player.gold,
        "enhancementStone": enhancement_stone,
    })


@bone_bp.get("/unequipped")
def get_unequipped_bones():
    """获取背包中未装备的战骨（可按槽位筛选），同时包含背包中的战骨物品"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    slot_filter = request.args.get('slot')  # 可选：头骨、胸骨、臂骨、手骨、腿骨、尾骨、元魂
    
    # 获取玩家所有战骨
    all_bones = services.bone_service.get_bones(user_id)
    
    # 筛选未装备的
    unequipped = [b for b in all_bones if b.bone.beast_id is None]
    
    # 如果指定了槽位，进一步筛选
    if slot_filter:
        unequipped = [b for b in unequipped if b.bone.slot == slot_filter]
    
    # 战骨阶段名称
    stage_names = {
        1: "原始",
        2: "碎空",
        3: "猎魔",
        4: "龙炎",
        5: "奔雷",
        6: "凌霄",
        7: "麒麟",
        8: "武神",
        9: "弑天",
        10: "毁灭",
    }
    
    # 品质名称
    quality_names = {
        1: "青铜",
        2: "白银",
        3: "黄金",
        4: "铂金",
        5: "钻石",
        6: "星耀",
        7: "王者",
        8: "传说",
        9: "神话",
        10: "至尊",
    }
    
    bones_data = []
    for b in unequipped:
        stage_name = stage_names.get(b.bone.stage, "原始")
        quality_name = quality_names.get(b.bone.stage, "青铜")
        
        # 收集非零属性
        attrs = []
        if b.bone.hp_flat and b.bone.hp_flat > 0:
            attrs.append(f"气血+{b.bone.hp_flat}")
        if b.bone.attack_flat and b.bone.attack_flat > 0:
            attrs.append(f"攻击+{b.bone.attack_flat}")
        if b.bone.physical_defense_flat and b.bone.physical_defense_flat > 0:
            attrs.append(f"物防+{b.bone.physical_defense_flat}")
        if b.bone.magic_defense_flat and b.bone.magic_defense_flat > 0:
            attrs.append(f"法防+{b.bone.magic_defense_flat}")
        if b.bone.speed_flat and b.bone.speed_flat > 0:
            attrs.append(f"速度+{b.bone.speed_flat}")
        
        bones_data.append({
            "id": b.bone.id,
            "name": f"{stage_name}{b.bone.slot}",
            "slot": b.bone.slot,
            "level": b.bone.level,
            "stage": b.bone.stage,
            "stageName": stage_name,
            "qualityName": quality_name,
            "hp": b.bone.hp_flat or 0,
            "attack": b.bone.attack_flat or 0,
            "physicalDefense": b.bone.physical_defense_flat or 0,
            "magicDefense": b.bone.magic_defense_flat or 0,
            "speed": b.bone.speed_flat or 0,
            "attrText": "".join(attrs),
            "isInventoryItem": False,  # 标记为战骨实体
        })
    
    # 获取背包中的战骨物品
    bone_items = services.bone_service.get_bone_items_from_inventory(user_id)
    
    # 筛选槽位
    if slot_filter:
        bone_items = [item for item in bone_items if item["slot"] == slot_filter]
    
    # 将背包中的战骨物品添加到列表
    for item in bone_items:
        bones_data.append({
            "id": None,  # 背包物品没有bone id
            "itemId": item["item_id"],  # 物品ID，用于使用
            "inventoryId": item["inventory_id"],
            "name": f"原始{item['slot']}",
            "slot": item["slot"],
            "level": 1,
            "stage": 1,
            "stageName": "原始",
            "qualityName": "青铜",
            "hp": 0,
            "attack": 0,
            "physicalDefense": 0,
            "magicDefense": 0,
            "speed": 0,
            "attrText": "(背包物品)",
            "isInventoryItem": True,  # 标记为背包物品
            "quantity": item["quantity"],  # 物品数量
        })
    
    return jsonify({
        "ok": True,
        "bones": bones_data,
    })


@bone_bp.post("/use-item")
def use_bone_item_api():
    """使用背包中的战骨物品（消耗物品创建战骨实体，可选直接装备到幻兽）"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    data = request.get_json() or {}
    item_id = data.get('itemId')
    beast_id = data.get('beastId')  # 可选，如果传入则直接装备
    
    if not item_id:
        return jsonify({"ok": False, "error": "缺少物品ID"})
    
    try:
        bone_info = services.bone_service.use_bone_item(user_id, item_id, beast_id)
        return jsonify({
            "ok": True,
            "message": "使用成功" if not beast_id else "装备成功",
            "bone": bone_info.to_dict(),
        })
    except BoneError as e:
        return jsonify({"ok": False, "error": str(e)})


@bone_bp.post("/equip")
def equip_bone_api():
    """装备战骨到幻兽"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    data = request.get_json() or {}
    bone_id = data.get('boneId')
    beast_id = data.get('beastId')
    
    if not bone_id:
        return jsonify({"ok": False, "error": "缺少战骨ID"})
    if not beast_id:
        return jsonify({"ok": False, "error": "缺少幻兽ID"})
    
    try:
        bone_info = services.bone_service.equip_bone(user_id, beast_id, bone_id)
        return jsonify({
            "ok": True,
            "message": "装备成功",
            "bone": bone_info.to_dict(),
        })
    except BoneError as e:
        return jsonify({"ok": False, "error": str(e)})


@bone_bp.post("/unequip/<int:bone_id>")
def unequip_bone_api(bone_id: int):
    """卸下战骨"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    try:
        bone_info = services.bone_service.unequip_bone(user_id, bone_id)
        return jsonify({
            "ok": True,
            "message": "卸下成功",
            "bone": bone_info.to_dict(),
        })
    except BoneError as e:
        return jsonify({"ok": False, "error": str(e)})


@bone_bp.post("/unequip-all/<int:beast_id>")
def unequip_all_bones(beast_id: int):
    """一键卸下幻兽所有战骨"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    # 获取该幻兽装备的所有战骨
    bones = services.bone_repo.get_by_beast_id(beast_id)
    
    count = 0
    for bone in bones:
        if bone.user_id == user_id:
            bone.beast_id = None
            services.bone_repo.save(bone)
            count += 1
    
    return jsonify({
        "ok": True,
        "message": f"已卸下{count}件战骨",
        "count": count,
    })
