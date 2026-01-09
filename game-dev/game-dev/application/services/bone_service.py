"""战骨服务：升级、进阶、查询消耗"""
from typing import List, Optional, Dict
from dataclasses import dataclass

from domain.entities.bone import BeastBone
from domain.repositories.bone_repo import IBoneRepo, IBoneTemplateRepo
from infrastructure.config.bone_system_config import get_bone_system_config


class BoneError(Exception):
    """战骨相关错误"""
    pass


@dataclass
class BoneWithInfo:
    """战骨实例 + 计算后的属性信息"""
    bone: BeastBone
    stage_name: str = ""
    stars: int = 0

    def to_dict(self) -> dict:
        return {
            "id": self.bone.id,
            "user_id": self.bone.user_id,
            "beast_id": self.bone.beast_id,
            "template_id": self.bone.template_id,
            "slot": self.bone.slot,
            "level": self.bone.level,
            "stage": self.bone.stage,
            "stage_name": self.stage_name,
            "stars": self.stars,
            "hp_flat": self.bone.hp_flat,
            "attack_flat": self.bone.attack_flat,
            "physical_defense_flat": self.bone.physical_defense_flat,
            "magic_defense_flat": self.bone.magic_defense_flat,
            "speed_flat": self.bone.speed_flat,
        }


class BoneService:
    def __init__(
        self,
        bone_repo: IBoneRepo,
        bone_template_repo: IBoneTemplateRepo,
        inventory_service,
        player_repo,
    ):
        self.bone_repo = bone_repo
        self.bone_template_repo = bone_template_repo
        self.inventory_service = inventory_service
        self.player_repo = player_repo
        self.config = get_bone_system_config()

    # ===================== 查询 =====================
    def get_bones(self, user_id: int) -> List[BoneWithInfo]:
        """获取玩家所有战骨"""
        bones = self.bone_repo.get_by_user_id(user_id)
        result = []
        for bone in bones:
            stage_cfg = self.config.get_stage_config(bone.stage)
            stage_name = stage_cfg["name"] if stage_cfg else ""
            stars = stage_cfg["stars"] if stage_cfg else 0
            result.append(BoneWithInfo(bone=bone, stage_name=stage_name, stars=stars))
        return result

    def get_bone(self, user_id: int, bone_id: int) -> Optional[BoneWithInfo]:
        """获取单个战骨"""
        bone = self.bone_repo.get_by_id(bone_id)
        if bone is None or bone.user_id != user_id:
            return None
        stage_cfg = self.config.get_stage_config(bone.stage)
        stage_name = stage_cfg["name"] if stage_cfg else ""
        stars = stage_cfg["stars"] if stage_cfg else 0
        return BoneWithInfo(bone=bone, stage_name=stage_name, stars=stars)

    # ===================== 创建 / 穿戴（临时接口使用） =====================
    def create_bone(self, user_id: int, template_id: int, stage: int = 1, level: int = 1) -> BoneWithInfo:
        """创建一枚战骨（用于开发测试接口 /api/bones/add）。"""
        if template_id <= 0:
            raise BoneError("template_id required")
        if stage <= 0:
            raise BoneError("stage 必须是正整数")
        if level <= 0:
            raise BoneError("level 必须是正整数")

        template = self.bone_template_repo.get_by_id(template_id)
        if template is None:
            raise BoneError(f"战骨模板不存在: {template_id}")

        stage_cfg = self.config.get_stage_config(stage)
        if stage_cfg is None:
            raise BoneError(f"阶段配置不存在: {stage}")

        # 校验等级是否落在该阶段允许的范围
        min_level = int(stage_cfg.get("min_level", 1) or 1)
        max_level = int(stage_cfg.get("max_level", self.config.get_max_level()) or self.config.get_max_level())
        if level < min_level or level > max_level:
            raise BoneError(f"level 必须在阶段{stage}的范围内: {min_level}~{max_level}")

        # 校验槽位是否合法
        slot = template.slot
        if slot not in self.config.get_slots():
            raise BoneError(f"战骨槽位无效: {slot}")

        bone = BeastBone(
            user_id=user_id,
            template_id=template_id,
            slot=slot,
            stage=stage,
            level=level,
            beast_id=None,
        )

        # 计算属性并保存
        self._recalc_bone_stats(bone)
        self.bone_repo.save(bone)

        return BoneWithInfo(bone=bone, stage_name=stage_cfg.get("name", ""), stars=int(stage_cfg.get("stars", 0) or 0))

    def equip_bone(self, user_id: int, beast_id: int, bone_id: int) -> BoneWithInfo:
        """将战骨装备到幻兽身上（临时接口使用）。"""
        bone = self.bone_repo.get_by_id(bone_id)
        if bone is None or bone.user_id != user_id:
            raise BoneError("战骨不存在")
        if beast_id <= 0:
            raise BoneError("beast_id 必须是正整数")

        # 同一只幻兽同一槽位只能装备一枚：先卸下旧的
        for b in self.bone_repo.get_by_beast_id(beast_id):
            if b.id != bone_id and b.slot == bone.slot:
                b.beast_id = None
                self.bone_repo.save(b)

        bone.beast_id = beast_id
        self.bone_repo.save(bone)

        stage_cfg = self.config.get_stage_config(bone.stage)
        stage_name = stage_cfg["name"] if stage_cfg else ""
        stars = stage_cfg["stars"] if stage_cfg else 0
        return BoneWithInfo(bone=bone, stage_name=stage_name, stars=stars)

    def unequip_bone(self, user_id: int, bone_id: int) -> BoneWithInfo:
        """卸下战骨（临时接口使用）。"""
        bone = self.bone_repo.get_by_id(bone_id)
        if bone is None or bone.user_id != user_id:
            raise BoneError("战骨不存在")

        bone.beast_id = None
        self.bone_repo.save(bone)

        stage_cfg = self.config.get_stage_config(bone.stage)
        stage_name = stage_cfg["name"] if stage_cfg else ""
        stars = stage_cfg["stars"] if stage_cfg else 0
        return BoneWithInfo(bone=bone, stage_name=stage_name, stars=stars)

    # ===================== 升级消耗查询 =====================
    def get_upgrade_cost(self, user_id: int, bone_id: int) -> Dict:
        """
        查询升级消耗及是否满足条件
        """
        bone = self.bone_repo.get_by_id(bone_id)
        if bone is None or bone.user_id != user_id:
            raise BoneError("战骨不存在")

        player = self.player_repo.get_by_id(user_id)
        if player is None:
            raise BoneError("玩家不存在")

        stage_cfg = self.config.get_stage_config(bone.stage)
        if stage_cfg is None:
            raise BoneError("阶段配置错误")

        max_level = stage_cfg["max_level"]
        max_total_level = self.config.get_max_level()

        # 检查是否已达上限
        if bone.level >= max_level:
            return {
                "can_upgrade": False,
                "reason": "已达当前阶段最大等级，请先进阶",
                "current_level": bone.level,
                "max_level": max_level,
                "materials": [],
            }

        if bone.level >= max_total_level:
            return {
                "can_upgrade": False,
                "reason": "已达战骨最大等级",
                "current_level": bone.level,
                "max_level": max_total_level,
                "materials": [],
            }

        target_level = bone.level + 1

        # 检查玩家等级
        if player.level < target_level:
            return {
                "can_upgrade": False,
                "reason": f"玩家等级不足，需要{target_level}级",
                "current_level": bone.level,
                "target_level": target_level,
                "player_level": player.level,
                "materials": [],
            }

        # 计算消耗
        cost = self.config.get_upgrade_cost(bone.level)
        stone_item_id = cost["strengthen_stone_item_id"]
        stone_qty = cost["strengthen_stone_qty"]
        gold_cost = cost["gold"]

        # 检查材料
        stone_owned = self._get_item_count(user_id, stone_item_id)
        stone_enough = stone_owned >= stone_qty
        gold_enough = player.gold >= gold_cost

        can_upgrade = stone_enough and gold_enough

        return {
            "can_upgrade": can_upgrade,
            "current_level": bone.level,
            "target_level": target_level,
            "player_level": player.level,
            "materials": [
                {
                    "item_id": stone_item_id,
                    "name": "强化石",
                    "required": stone_qty,
                    "owned": stone_owned,
                    "has_enough": stone_enough,
                },
                {
                    "item_id": 0,
                    "name": "铜钱",
                    "required": gold_cost,
                    "owned": player.gold,
                    "has_enough": gold_enough,
                },
            ],
        }

    # ===================== 升级 =====================
    def upgrade_bone(self, user_id: int, bone_id: int) -> BoneWithInfo:
        """
        升级战骨
        """
        bone = self.bone_repo.get_by_id(bone_id)
        if bone is None or bone.user_id != user_id:
            raise BoneError("战骨不存在")

        player = self.player_repo.get_by_id(user_id)
        if player is None:
            raise BoneError("玩家不存在")

        stage_cfg = self.config.get_stage_config(bone.stage)
        if stage_cfg is None:
            raise BoneError("阶段配置错误")

        max_level = stage_cfg["max_level"]
        max_total_level = self.config.get_max_level()

        # 检查等级上限
        if bone.level >= max_level:
            raise BoneError("已达当前阶段最大等级，请先进阶")

        if bone.level >= max_total_level:
            raise BoneError("已达战骨最大等级")

        target_level = bone.level + 1

        # 检查玩家等级
        if player.level < target_level:
            raise BoneError(f"玩家等级不足，需要{target_level}级")

        # 计算消耗
        cost = self.config.get_upgrade_cost(bone.level)
        stone_item_id = cost["strengthen_stone_item_id"]
        stone_qty = cost["strengthen_stone_qty"]
        gold_cost = cost["gold"]

        # 检查材料
        if not self.inventory_service.has_item(user_id, stone_item_id, stone_qty):
            raise BoneError(f"强化石不足，需要{stone_qty}个")

        if player.gold < gold_cost:
            raise BoneError(f"铜钱不足，需要{gold_cost}")

        # 扣除材料
        self.inventory_service.remove_item(user_id, stone_item_id, stone_qty)

        # 扣除铜钱
        player.gold -= gold_cost
        self.player_repo.save(player)

        # 升级
        bone.level = target_level

        # 重新计算属性
        self._recalc_bone_stats(bone)

        # 保存
        self.bone_repo.save(bone)

        stage_name = stage_cfg["name"]
        stars = stage_cfg["stars"]
        return BoneWithInfo(bone=bone, stage_name=stage_name, stars=stars)

    # ===================== 进阶消耗查询 =====================
    def get_refine_cost(self, user_id: int, bone_id: int) -> Dict:
        """
        查询进阶消耗及是否满足条件
        """
        bone = self.bone_repo.get_by_id(bone_id)
        if bone is None or bone.user_id != user_id:
            raise BoneError("战骨不存在")

        player = self.player_repo.get_by_id(user_id)
        if player is None:
            raise BoneError("玩家不存在")

        stage_cfg = self.config.get_stage_config(bone.stage)
        if stage_cfg is None:
            raise BoneError("阶段配置错误")

        max_level = stage_cfg["max_level"]
        to_stage = bone.stage + 1

        # 检查是否已达最高阶段
        next_stage_cfg = self.config.get_stage_config(to_stage)
        if next_stage_cfg is None:
            return {
                "can_refine": False,
                "reason": "已达最高阶段",
                "current_stage": bone.stage,
                "current_level": bone.level,
                "materials": [],
            }

        # 检查是否满级
        if bone.level < max_level:
            return {
                "can_refine": False,
                "reason": f"需要先升到{max_level}级才能进阶",
                "current_stage": bone.stage,
                "current_level": bone.level,
                "required_level": max_level,
                "materials": [],
            }

        # 检查玩家等级
        required_player_level = next_stage_cfg["min_player_level"]
        if player.level < required_player_level:
            return {
                "can_refine": False,
                "reason": f"玩家等级不足，需要{required_player_level}级",
                "current_stage": bone.stage,
                "to_stage": to_stage,
                "player_level": player.level,
                "required_player_level": required_player_level,
                "materials": [],
            }

        # 计算消耗
        cost = self.config.get_refine_cost(to_stage, bone.slot)
        if cost is None:
            raise BoneError("进阶配置错误")

        # 检查材料
        materials = []

        # 卷轴
        scroll_owned = self._get_item_count(user_id, cost["scroll_item_id"])
        scroll_enough = scroll_owned >= cost["scroll_qty"]
        materials.append({
            "item_id": cost["scroll_item_id"],
            "name": self._get_item_name(cost["scroll_item_id"]),
            "required": cost["scroll_qty"],
            "owned": scroll_owned,
            "has_enough": scroll_enough,
        })

        # 骨魂
        soul_owned = self._get_item_count(user_id, cost["bone_soul_item_id"])
        soul_enough = soul_owned >= cost["bone_soul_qty"]
        materials.append({
            "item_id": cost["bone_soul_item_id"],
            "name": self._get_item_name(cost["bone_soul_item_id"]),
            "required": cost["bone_soul_qty"],
            "owned": soul_owned,
            "has_enough": soul_enough,
        })

        # 主结晶
        primary_owned = self._get_item_count(user_id, cost["primary_crystal_item_id"])
        primary_enough = primary_owned >= cost["primary_crystal_qty"]
        materials.append({
            "item_id": cost["primary_crystal_item_id"],
            "name": self._get_item_name(cost["primary_crystal_item_id"]),
            "required": cost["primary_crystal_qty"],
            "owned": primary_owned,
            "has_enough": primary_enough,
        })

        # 副结晶
        secondary_owned = self._get_item_count(user_id, cost["secondary_crystal_item_id"])
        secondary_enough = secondary_owned >= cost["secondary_crystal_qty"]
        materials.append({
            "item_id": cost["secondary_crystal_item_id"],
            "name": self._get_item_name(cost["secondary_crystal_item_id"]),
            "required": cost["secondary_crystal_qty"],
            "owned": secondary_owned,
            "has_enough": secondary_enough,
        })

        can_refine = all(m["has_enough"] for m in materials)

        return {
            "can_refine": can_refine,
            "current_stage": bone.stage,
            "to_stage": to_stage,
            "current_stage_name": stage_cfg["name"],
            "to_stage_name": next_stage_cfg["name"],
            "player_level": player.level,
            "required_player_level": required_player_level,
            "materials": materials,
        }

    # ===================== 进阶 =====================
    def refine_bone(self, user_id: int, bone_id: int) -> BoneWithInfo:
        """
        进阶/炼制战骨
        """
        bone = self.bone_repo.get_by_id(bone_id)
        if bone is None or bone.user_id != user_id:
            raise BoneError("战骨不存在")

        player = self.player_repo.get_by_id(user_id)
        if player is None:
            raise BoneError("玩家不存在")

        stage_cfg = self.config.get_stage_config(bone.stage)
        if stage_cfg is None:
            raise BoneError("阶段配置错误")

        max_level = stage_cfg["max_level"]
        to_stage = bone.stage + 1

        # 检查是否已达最高阶段
        next_stage_cfg = self.config.get_stage_config(to_stage)
        if next_stage_cfg is None:
            raise BoneError("已达最高阶段")

        # 检查是否满级
        if bone.level < max_level:
            raise BoneError(f"需要先升到{max_level}级才能进阶")

        # 检查玩家等级
        required_player_level = next_stage_cfg["min_player_level"]
        if player.level < required_player_level:
            raise BoneError(f"玩家等级不足，需要{required_player_level}级")

        # 计算消耗
        cost = self.config.get_refine_cost(to_stage, bone.slot)
        if cost is None:
            raise BoneError("进阶配置错误")

        # 检查并扣除材料
        materials_to_remove = [
            (cost["scroll_item_id"], cost["scroll_qty"], "卷轴"),
            (cost["bone_soul_item_id"], cost["bone_soul_qty"], "骨魂"),
            (cost["primary_crystal_item_id"], cost["primary_crystal_qty"], "主结晶"),
            (cost["secondary_crystal_item_id"], cost["secondary_crystal_qty"], "副结晶"),
        ]

        for item_id, qty, name in materials_to_remove:
            if not self.inventory_service.has_item(user_id, item_id, qty):
                item_name = self._get_item_name(item_id) or name
                raise BoneError(f"{item_name}不足，需要{qty}个")

        # 扣除材料
        for item_id, qty, _ in materials_to_remove:
            self.inventory_service.remove_item(user_id, item_id, qty)

        # 进阶
        bone.stage = to_stage

        # 重新计算属性
        self._recalc_bone_stats(bone)

        # 保存
        self.bone_repo.save(bone)

        stage_name = next_stage_cfg["name"]
        stars = next_stage_cfg["stars"]
        return BoneWithInfo(bone=bone, stage_name=stage_name, stars=stars)

    # ===================== 辅助方法 =====================
    def _recalc_bone_stats(self, bone: BeastBone) -> None:
        """重新计算战骨属性"""
        stats = self.config.calc_bone_stats(bone.stage, bone.slot, bone.level)
        bone.hp_flat = stats["hp"]
        bone.attack_flat = max(int(stats.get("physical_attack", 0) or 0), int(stats.get("magic_attack", 0) or 0))
        bone.physical_defense_flat = stats["physical_defense"]
        bone.magic_defense_flat = stats["magic_defense"]
        bone.speed_flat = stats["speed"]

    def _get_item_count(self, user_id: int, item_id: int) -> int:
        """获取玩家拥有的物品数量"""
        return self.inventory_service._get_item_count(user_id, item_id)

    def _get_item_name(self, item_id: int) -> str:
        """获取物品名称"""
        item = self.inventory_service.item_repo.get_by_id(item_id)
        return item.name if item else f"物品{item_id}"

    # ===================== 背包战骨物品 =====================
    # 物品ID到槽位和模板ID的映射
    BONE_ITEM_MAPPING = {
        9101: {"slot": "头骨", "template_id": 910001},
        9102: {"slot": "胸骨", "template_id": 910002},
        9103: {"slot": "臂骨", "template_id": 910003},
        9104: {"slot": "手骨", "template_id": 910004},
        9105: {"slot": "腿骨", "template_id": 910005},
        9106: {"slot": "尾骨", "template_id": 910006},
        9107: {"slot": "元魂", "template_id": 910007},
    }

    def get_bone_items_from_inventory(self, user_id: int) -> List[dict]:
        """获取背包中的战骨物品"""
        result = []
        inv_items = self.inventory_service.get_inventory(user_id)
        for inv_with_info in inv_items:
            item_id = inv_with_info.inv_item.item_id
            if item_id in self.BONE_ITEM_MAPPING:
                mapping = self.BONE_ITEM_MAPPING[item_id]
                result.append({
                    "inventory_id": inv_with_info.inv_item.id,
                    "item_id": item_id,
                    "name": inv_with_info.item_info.name,
                    "slot": mapping["slot"],
                    "quantity": inv_with_info.inv_item.quantity,
                    "is_inventory_item": True,  # 标记为背包物品
                })
        return result

    def calc_bone_bonus(self, equipped_bones: List[BeastBone]) -> Dict[str, int]:
        """计算战骨属性加成"""
        result = {
            "hp": 0,
            "physical_attack": 0,
            "magic_attack": 0,
            "physical_defense": 0,
            "magic_defense": 0,
            "speed": 0,
        }
        if equipped_bones:
            for bone in equipped_bones:
                result["hp"] += bone.hp_flat or 0
                result["physical_attack"] += bone.attack_flat or 0
                result["magic_attack"] += bone.attack_flat or 0
                result["physical_defense"] += bone.physical_defense_flat or 0
                result["magic_defense"] += bone.magic_defense_flat or 0
                result["speed"] += bone.speed_flat or 0
        return result

    def use_bone_item(self, user_id: int, item_id: int, beast_id: int = None) -> BoneWithInfo:
        """
        使用背包中的战骨物品：消耗1个物品，创建战骨实体，可选直接装备到幻兽
        """
        if item_id not in self.BONE_ITEM_MAPPING:
            raise BoneError("这不是一个战骨物品")

        # 检查背包中是否有该物品
        if not self.inventory_service.has_item(user_id, item_id, 1):
            raise BoneError("背包中没有该战骨物品")

        mapping = self.BONE_ITEM_MAPPING[item_id]
        template_id = mapping["template_id"]
        slot = mapping["slot"]

        # 消耗物品
        self.inventory_service.remove_item(user_id, item_id, 1)

        # 创建战骨实体（原始战骨，stage=1, level=1）
        bone = BeastBone(
            user_id=user_id,
            template_id=template_id,
            slot=slot,
            stage=1,
            level=1,
            beast_id=beast_id,  # 如果传入了beast_id，直接装备
        )

        # 计算属性并保存
        self._recalc_bone_stats(bone)
        self.bone_repo.save(bone)

        stage_cfg = self.config.get_stage_config(1)
        stage_name = stage_cfg["name"] if stage_cfg else "原始"
        stars = stage_cfg["stars"] if stage_cfg else 0

        return BoneWithInfo(bone=bone, stage_name=stage_name, stars=stars)
