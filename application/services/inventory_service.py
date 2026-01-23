import json
import os
import random
from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple, Optional, TYPE_CHECKING

from domain.entities.item import Item, InventoryItem, PlayerBag
from domain.repositories.inventory_repo import IInventoryRepo
from domain.repositories.item_repo import IItemRepo
from domain.rules.dragonpalace_rules import pick_dragonpalace_reward_item_id
from infrastructure.db.connection import execute_query, execute_update
from infrastructure.db.player_effect_repo_mysql import MySQLPlayerEffectRepo

if TYPE_CHECKING:
    from application.services.immortalize_pool_service import ImmortalizePoolService


def load_bag_upgrade_config():
    """加载背包升级配置"""
    config_path = os.path.join(
        os.path.dirname(__file__),
        '..', '..', 'configs', 'bag_upgrade.json'
    )
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


class InventoryError(Exception):
    """背包相关错误"""
    pass


@dataclass
class InventoryItemWithInfo:
    """背包物品 + 模板信息（用于返回给前端）"""
    inv_item: InventoryItem
    item_info: Item


PRESTIGE_STONE_ITEM_ID = 12001
PRESTIGE_STONE_CONSUME_AMOUNT = 5
PRESTIGE_STONE_TARGET_LEVEL = 19

# 神兽召唤球（兑换获得）等级门槛 + 同一神兽仅一只
DIVINE_BEAST_BALL_CONFIG = {
    # ball_item_id: (template_id, beast_name, min_player_level)
    26060: (58, "神·罗刹", 30),
    26059: (59, "神·不死鸟", 40),
    26058: (60, "神·白虎", 40),
    26061: (61, "神·绝影", 50),
    26062: (62, "神·朱雀", 60),
    26063: (63, "神·玄武", 70),
    26064: (64, "神·青龙", 70),
}

LUCKY_CHEST_ITEM_ID = 6008
NINGSHEN_INCENSE_ITEM_ID = 6009
ANCIENT_SILVER_CHEST_ITEM_ID = 6003
ANCIENT_TITANIUM_CHEST_ITEM_ID = 6014
SKILL_BOOK_POUCH_ITEM_ID = 6007
ANCIENT_EVOLVE_CHEST_ITEM_ID = 6030
FORTUNE_TALISMAN_ITEM_ID = 6004
VITALITY_GRASS_ITEM_IDS = {4001, 6013}
NINGSHEN_INCENSE_EFFECT_KEY = "cultivation_prestige_20"
NINGSHEN_INCENSE_DURATION_SECONDS = 24 * 3600

ZHENYAO_TRIAL_CHEST_ITEM_ID = 92001
ZHENYAO_HELL_CHEST_ITEM_ID = 92002
DRAGONPALACE_EXPLORE_GIFT_ITEM_ID = 93001
DRAGONPALACE_EXPLORE_GIFT_COPPER = 20000


class InventoryService:
    def __init__(
            self,
            item_repo: IItemRepo,
            inventory_repo: IInventoryRepo,
            player_repo=None,
            beast_service=None,
            player_effect_repo: Optional[MySQLPlayerEffectRepo] = None,
    ):
        self.item_repo = item_repo
        self.inventory_repo = inventory_repo
        self.player_repo = player_repo
        self.beast_service = beast_service
        self.player_effect_repo = player_effect_repo
        self.activity_gift_service = None
        self.immortalize_pool_service: Optional["ImmortalizePoolService"] = None
        self.spirit_service = None

    def set_activity_gift_service(self, activity_gift_service):
        self.activity_gift_service = activity_gift_service

    def set_immortalize_pool_service(self, service: "ImmortalizePoolService"):
        self.immortalize_pool_service = service

    def set_spirit_service(self, spirit_service):
        """依赖注入：战灵服务（用于背包内直接开启灵石）。"""
        self.spirit_service = spirit_service

    def get_inventory(self, user_id: int, include_temp: bool = True) -> List[InventoryItemWithInfo]:
        """获取玩家背包（带物品详情）"""
        inv_items = self.inventory_repo.get_by_user_id(user_id, include_temp)
        result = []
        for inv in inv_items:
            # 过滤掉数量为0的物品
            if inv.quantity <= 0:
                # 如果发现数量为0的物品，尝试删除它
                try:
                    self.inventory_repo.delete(inv.id)
                except:
                    pass  # 忽略删除失败的情况
                continue
            item_info = self.item_repo.get_by_id(inv.item_id)
            if item_info:
                result.append(InventoryItemWithInfo(inv_item=inv, item_info=item_info))
        return result
    
    def can_use_or_open_item(self, item_template) -> tuple[bool, str]:
        """
        判断道具是否可以打开或使用
        返回: (是否可用, 动作名称: "打开" 或 "使用" 或 "")
        """
        if not item_template:
            return (False, "")
        
        # special类型不可使用
        if item_template.type == "special":
            return (False, "")
        
        # 检查是否有usable字段且为false
        if hasattr(item_template, 'usable') and item_template.usable is False:
            return (False, "")
        
        # consumable类型可以打开或使用
        if item_template.type == "consumable":
            # 明确不在背包实现的道具：不显示“使用/打开”
            if item_template.id in (6031, 6032):  # 洗髓丹/坐骑口粮
                return (False, "")
            # 判断是"打开"还是"使用"
            name = item_template.name or ""
            # 包含"召唤球"、"礼包"、"宝箱"、"箱"的显示"打开"
            if any(keyword in name for keyword in ["召唤球", "礼包", "宝箱", "箱", "盒"]):
                return (True, "打开")
            else:
                return (True, "使用")
        
        # material类型：部分道具允许在背包中“使用/打开”
        if item_template.type == "material":
            if item_template.id == 12001:  # 声望石
                return (True, "使用")
            # 神·逆鳞：用于兑换神兽召唤球，背包内提供“使用”按钮引导跳转
            if int(item_template.id) == 3010:
                return (True, "使用")
            # 神·逆鳞碎片：背包内允许“使用”用于直接合成（集齐100 -> 1神·逆鳞）
            if int(item_template.id) == 3011:
                return (True, "使用")
            # 战灵钥匙：跳转战灵功能页核销（前端会提示并跳转）
            if int(item_template.id) == 6006:
                return (True, "使用")
            # 灵力水晶：跳转战灵功能页兑换灵力（前端会提示并跳转）
            if int(item_template.id) == 6101:
                return (True, "使用")
            # 六系灵石（未开）：背包内直接“打开”
            if int(item_template.id) in (7101, 7102, 7103, 7104, 7105, 7106):
                return (True, "打开")
        
        return (False, "")

    def get_bag_info(self, user_id: int) -> dict:
        """获取背包信息"""
        config = load_bag_upgrade_config()
        bag_names = config.get('bag_names', {})

        bag = self.inventory_repo.get_bag_info(user_id)
        slot_count = self.inventory_repo.get_slot_count(user_id, is_temporary=False)
        temp_count = self.inventory_repo.get_slot_count(user_id, is_temporary=True)
        bag_name = bag_names.get(str(bag.bag_level), f"{bag.bag_level}级背包")

        return {
            "bag_level": bag.bag_level,
            "bag_name": bag_name,
            "capacity": bag.capacity,
            "used_slots": slot_count,
            "temp_slots": temp_count,
            "is_full": slot_count >= bag.capacity,
        }

    def _is_bag_full(self, user_id: int) -> bool:
        """检查背包是否已满"""
        bag = self.inventory_repo.get_bag_info(user_id)
        slot_count = self.inventory_repo.get_slot_count(user_id, is_temporary=False)
        return slot_count >= bag.capacity

    def add_item(self, user_id: int, item_id: int, quantity: int = 1) -> Tuple[InventoryItem, bool]:
        """
        给玩家添加物品（单格上限99）
        返回: (物品实例, 是否放入临时背包)
        """
        MAX_STACK = PlayerBag.MAX_STACK_SIZE  # 99

        item_template = self.item_repo.get_by_id(item_id)
        if item_template is None:
            raise InventoryError(f"物品不存在: {item_id}")

        remaining = quantity
        last_item = None
        is_temp = False

        # 先尝试填充正式背包中已有的格子（未满99的）
        if item_template.stackable:
            existing_items = self.inventory_repo.find_all_items(user_id, item_id, is_temporary=False)
            for existing in existing_items:
                if remaining <= 0:
                    break
                if existing.quantity < MAX_STACK:
                    space = MAX_STACK - existing.quantity
                    add_amount = min(space, remaining)
                    existing.quantity += add_amount
                    remaining -= add_amount
                    self.inventory_repo.save(existing)
                    last_item = existing

        # 如果还有剩余，需要创建新格子
        while remaining > 0:
            # 检查背包是否已满
            is_temp = self._is_bag_full(user_id)

            if is_temp:
                # 背包已满，尝试填充临时背包
                if item_template.stackable:
                    temp_items = self.inventory_repo.find_all_items(user_id, item_id, is_temporary=True)
                    for temp_item in temp_items:
                        if remaining <= 0:
                            break
                        if temp_item.quantity < MAX_STACK:
                            space = MAX_STACK - temp_item.quantity
                            add_amount = min(space, remaining)
                            temp_item.quantity += add_amount
                            remaining -= add_amount
                            self.inventory_repo.save(temp_item)
                            last_item = temp_item

                # 如果还有剩余，创建新的临时格子
                if remaining > 0:
                    add_amount = min(MAX_STACK, remaining)
                    new_item = InventoryItem(
                        user_id=user_id,
                        item_id=item_id,
                        quantity=add_amount,
                        is_temporary=True,
                        created_at=datetime.now(),
                    )
                    self.inventory_repo.save(new_item)
                    remaining -= add_amount
                    last_item = new_item
            else:
                # 背包有空间，创建新格子（最多99个）
                add_amount = min(MAX_STACK, remaining)
                new_item = InventoryItem(
                    user_id=user_id,
                    item_id=item_id,
                    quantity=add_amount,
                    is_temporary=False,
                    created_at=None,
                )
                self.inventory_repo.save(new_item)
                remaining -= add_amount
                last_item = new_item

        return last_item, is_temp

    def add_item_to_temp(self, user_id: int, item_id: int, quantity: int = 1) -> InventoryItem:
        """
        强制将物品放入临时背包（不尝试放入正式背包）。

        用途：
        - 某些活动“领取后在背包-临时栏展示”的交互（例如：龙宫之谜探索礼包）。
        """
        MAX_STACK = PlayerBag.MAX_STACK_SIZE  # 99

        item_template = self.item_repo.get_by_id(item_id)
        if item_template is None:
            raise InventoryError(f"物品不存在: {item_id}")

        remaining = int(quantity or 0)
        if remaining <= 0:
            raise InventoryError("quantity 必须为正整数")

        last_item: Optional[InventoryItem] = None

        # 先尝试填充临时背包中已有的格子（未满 99 的）
        if item_template.stackable:
            temp_items = self.inventory_repo.find_all_items(user_id, item_id, is_temporary=True)
            for temp_item in temp_items:
                if remaining <= 0:
                    break
                if temp_item.quantity < MAX_STACK:
                    space = MAX_STACK - temp_item.quantity
                    add_amount = min(space, remaining)
                    temp_item.quantity += add_amount
                    remaining -= add_amount
                    self.inventory_repo.save(temp_item)
                    last_item = temp_item

        # 仍有剩余则创建新临时格子
        while remaining > 0:
            add_amount = min(MAX_STACK, remaining)
            new_item = InventoryItem(
                user_id=user_id,
                item_id=item_id,
                quantity=add_amount,
                is_temporary=True,
                created_at=datetime.now(),
            )
            self.inventory_repo.save(new_item)
            remaining -= add_amount
            last_item = new_item

        if last_item is None:
            raise InventoryError("添加物品失败")
        return last_item

    def remove_item(self, user_id: int, item_id: int, quantity: int = 1) -> bool:
        """移除玩家物品（只从正式背包移除，支持跨多格）"""
        total = self._get_item_count(user_id, item_id)
        if total < quantity:
            raise InventoryError("物品数量不足")

        self._remove_item_quantity(user_id, item_id, quantity)
        return True

    def has_item(self, user_id: int, item_id: int, quantity: int = 1) -> bool:
        """检查是否拥有足够物品（只检查正式背包，支持跨多格）"""
        total = self._get_item_count(user_id, item_id)
        return total >= quantity

    def get_item_count(self, user_id: int, item_id: int, include_temp: bool = False) -> int:
        """
        获取玩家拥有的某物品数量。
        
        :param user_id: 玩家ID
        :param item_id: 物品ID
        :param include_temp: 是否包含临时背包中的数量，默认仅统计正式背包
        """
        if not include_temp:
            return self._get_item_count(user_id, item_id)

        # 同时统计正式背包和临时背包
        normal_items = self.inventory_repo.find_all_items(user_id, item_id, is_temporary=False)
        temp_items = self.inventory_repo.find_all_items(user_id, item_id, is_temporary=True)
        return sum(item.quantity for item in normal_items) + sum(item.quantity for item in temp_items)

    def find_item_by_item_id(self, user_id: int, item_id: int):
        """根据物品模板ID查找背包中的物品记录（返回第一个匹配的）"""
        items = self.inventory_repo.find_all_items(user_id, item_id, is_temporary=False)
        if items:
            return items[0]
        return None

    def get_upgrade_cost(self, user_id: int) -> dict:
        """获取背包升级所需材料"""
        config = load_bag_upgrade_config()
        bag = self.inventory_repo.get_bag_info(user_id)
        bag_names = config.get('bag_names', {})

        # 获取玩家等级
        player_level = 1
        if self.player_repo:
            player = self.player_repo.get_by_id(user_id)
            if player:
                player_level = player.level

        current_bag_name = bag_names.get(str(bag.bag_level), f"{bag.bag_level}级背包")

        if bag.bag_level >= config.get('max_level', 10):
            return {
                "can_upgrade": False,
                "reason": "已达最高等级",
                "materials": [],
                "current_bag_name": current_bag_name,
                "current_capacity": bag.capacity,
                "player_level": player_level,
            }

        next_level = bag.bag_level + 1
        next_bag_name = bag_names.get(str(next_level), f"{next_level}级背包")
        upgrade_costs = config.get('upgrade_costs', [])

        cost_info = None
        for cost in upgrade_costs:
            if cost['level'] == next_level:
                cost_info = cost
                break

        if not cost_info:
            return {"can_upgrade": False, "reason": "配置错误", "materials": []}

        # 检查人物等级要求
        required_player_level = cost_info.get('required_player_level', 0)
        level_ok = player_level >= required_player_level

        # 检查玩家是否有足够材料
        materials_status = []
        materials_ok = True
        for mat in cost_info['materials']:
            owned = self._get_item_count(user_id, mat['item_id'])
            has_enough = owned >= mat['quantity']
            if not has_enough:
                materials_ok = False
            materials_status.append({
                "item_id": mat['item_id'],
                "name": mat['name'],
                "required": mat['quantity'],
                "owned": owned,
                "has_enough": has_enough,
            })

        can_upgrade = level_ok and materials_ok

        return {
            "can_upgrade": can_upgrade,
            "current_level": bag.bag_level,
            "next_level": next_level,
            "current_bag_name": current_bag_name,
            "next_bag_name": next_bag_name,
            "current_capacity": bag.capacity,
            "next_capacity": PlayerBag.calc_capacity(next_level),
            "materials": materials_status,
            "required_player_level": required_player_level,
            "player_level": player_level,
            "level_ok": level_ok,
            "materials_ok": materials_ok,
        }

    def _get_item_count(self, user_id: int, item_id: int) -> int:
        """获取玩家拥有的某物品总数"""
        items = self.inventory_repo.find_all_items(user_id, item_id, is_temporary=False)
        return sum(item.quantity for item in items)

    def upgrade_bag(self, user_id: int) -> PlayerBag:
        """升级背包"""
        config = load_bag_upgrade_config()
        bag = self.inventory_repo.get_bag_info(user_id)

        if bag.bag_level >= config.get('max_level', 10):
            raise InventoryError("背包已达最高等级")

        next_level = bag.bag_level + 1
        upgrade_costs = config.get('upgrade_costs', [])

        cost_info = None
        for cost in upgrade_costs:
            if cost['level'] == next_level:
                cost_info = cost
                break

        if not cost_info:
            raise InventoryError("升级配置错误")

        # 检查人物等级
        required_player_level = cost_info.get('required_player_level', 0)
        if self.player_repo:
            player = self.player_repo.get_by_id(user_id)
            if player and player.level < required_player_level:
                raise InventoryError(f"人物等级不足，需要{required_player_level}级")

        # 检查并扣除材料
        for mat in cost_info['materials']:
            owned = self._get_item_count(user_id, mat['item_id'])
            if owned < mat['quantity']:
                raise InventoryError(f"{mat['name']}不足，需要{mat['quantity']}个，当前{owned}个")

        # 扣除材料
        for mat in cost_info['materials']:
            self._remove_item_quantity(user_id, mat['item_id'], mat['quantity'])

        # 升级背包
        bag.bag_level = next_level
        bag.capacity = PlayerBag.calc_capacity(next_level)
        self.inventory_repo.save_bag_info(bag)
        return bag

    def _remove_item_quantity(self, user_id: int, item_id: int, quantity: int):
        """从背包移除指定数量的物品（可能跨多个格子）"""
        remaining = quantity
        items = self.inventory_repo.find_all_items(user_id, item_id, is_temporary=False)

        for item in items:
            if remaining <= 0:
                break
            if item.quantity <= remaining:
                remaining -= item.quantity
                self.inventory_repo.delete(item.id)
            else:
                item.quantity -= remaining
                self.inventory_repo.save(item)
                remaining = 0

    def clean_expired_temp_items(self) -> int:
        """清理过期的临时物品（每天24点调用）"""
        # 删除昨天24点之前的临时物品
        today_midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return self.inventory_repo.delete_temp_items_before(today_midnight)

    def transfer_temp_to_bag(self, user_id: int) -> List[dict]:
        """
        将临时背包中的物品转移到正式背包（按时间先后顺序）
        每次转移一件，直到背包满为止
        返回: 转移的物品列表 [{"item_id": x, "name": "xx", "quantity": n}, ...]
        """
        transferred = []

        while True:
            # 检查背包是否还有空间
            bag = self.inventory_repo.get_bag_info(user_id)
            slot_count = self.inventory_repo.get_slot_count(user_id, is_temporary=False)

            if slot_count >= bag.capacity:
                # 背包已满，停止转移
                break

            # 获取临时背包中最早的物品
            oldest_temp = self.inventory_repo.get_oldest_temp_item(user_id)
            if not oldest_temp:
                # 临时背包为空
                break

            # 尝试转移到正式背包
            item_template = self.item_repo.get_by_id(oldest_temp.item_id)

            # 检查正式背包是否有同类物品可堆叠
            existing = self.inventory_repo.find_item(user_id, oldest_temp.item_id, is_temporary=False)

            if existing and item_template and item_template.stackable:
                # 堆叠到现有格子
                existing.quantity += oldest_temp.quantity
                self.inventory_repo.save(existing)
                self.inventory_repo.delete(oldest_temp.id)
                transferred.append({
                    "item_id": oldest_temp.item_id,
                    "name": item_template.name if item_template else f"物品{oldest_temp.item_id}",
                    "quantity": oldest_temp.quantity,
                })
            else:
                # 需要占用新格子
                if slot_count < bag.capacity:
                    # 有空间，直接将临时物品改为正式
                    oldest_temp.is_temporary = False
                    self.inventory_repo.save(oldest_temp)
                    transferred.append({
                        "item_id": oldest_temp.item_id,
                        "name": item_template.name if item_template else f"物品{oldest_temp.item_id}",
                        "quantity": oldest_temp.quantity,
                    })
                else:
                    # 无空间，停止
                    break

        return transferred

    def consume_prestige_stones_for_level_jump(self, user_id: int) -> dict:
        """
        消耗声望石将玩家从1级直接提升到19级。
        要求：仅限等级1的玩家使用，且背包中需要有足够的声望石。
        """
        if not self.player_repo:
            raise InventoryError("系统错误：PlayerRepo 未配置")

        player = self.player_repo.get_by_id(user_id)
        if not player:
            raise InventoryError("玩家不存在")

        if player.level != 1:
            raise InventoryError("仅等级1玩家可使用声望石晋升")

        if player.level >= PRESTIGE_STONE_TARGET_LEVEL:
            raise InventoryError("当前等级已不可使用声望石晋升")

        self.remove_item(user_id, PRESTIGE_STONE_ITEM_ID, PRESTIGE_STONE_CONSUME_AMOUNT)

        player.level = PRESTIGE_STONE_TARGET_LEVEL
        player.exp = 0
        self.player_repo.save(player)

        return {
            "ok": True,
            "level": player.level,
            "message": "成功使用声望石晋升至19级",
        }

    def get_temp_items(self, user_id: int) -> List[InventoryItemWithInfo]:
        """获取临时背包物品（按时间排序）"""
        inv_items = self.inventory_repo.get_temp_items_sorted(user_id)
        result = []
        for inv in inv_items:
            item_info = self.item_repo.get_by_id(inv.item_id)
            if item_info:
                result.append(InventoryItemWithInfo(inv_item=inv, item_info=item_info))
        return result

    def use_item(self, user_id: int, inv_item_id: int, quantity: int = 1) -> dict:
        """
        使用背包中的物品
        :param user_id: 玩家ID
        :param inv_item_id: 背包格子ID
        :param quantity: 使用数量
        :return: 使用结果字典，包含message和rewards
        """
        # 1. 获取背包项
        inv_item = self.inventory_repo.get_by_id(inv_item_id)
        if not inv_item or inv_item.user_id != user_id:
            raise InventoryError("物品不存在")

        if inv_item.quantity < quantity:
            raise InventoryError("物品数量不足")

        # 2. 获取物品模板
        item_template = self.item_repo.get_by_id(inv_item.item_id)
        if not item_template:
            raise InventoryError("物品模板不存在")

        # 检查物品是否可使用
        if item_template.type == "special":
            raise InventoryError("该物品不可直接使用")
        
        if item_template.type not in ("consumable", "material"):
            raise InventoryError("该物品不可使用")

        # ========== 批量使用规则（严格按文档要求优化）==========
        # - 可批量使用/打开的道具：一次最多 10 个
        # - 不可批量的道具：禁止批量（quantity 必须为 1）
        batch_allowed_item_ids = {
            6003,  # 远古秘银宝箱
            6014,  # 远古钛金宝箱
            6030,  # 远古进化宝箱
            6007,  # 技能书口袋
            6008,  # 幸运宝箱
            6009,  # 凝神香
            6010,  # 骰子包
            6004,  # 招财神符
            4001, 6013,  # 活力草
            3011,  # 神·逆鳞碎片（背包内合成）
            7101, 7102, 7103, 7104, 7105, 7106,  # 六系灵石（未开）-> 背包内直接开启
        }
        if int(item_template.id) in batch_allowed_item_ids:
            if int(quantity) > 10:
                raise InventoryError("一次最多只能使用/打开10个")
        else:
            if int(quantity) != 1:
                raise InventoryError("该物品不支持批量使用")

        # ========== 直接在背包内合成：神·逆鳞碎片(3011) -> 神·逆鳞(3010) ==========
        # 规则：100碎片兑换1个神·逆鳞（跨格统计与扣除；背包页表现为“合成”而非“批量使用”）
        if int(item_template.id) == 3011:
            total_available = int(self._get_item_count(user_id, 3011) or 0)
            if total_available < 100:
                # 按需求：不展示“现有多少”，避免碎片分格/临时背包等造成误导
                raise InventoryError("神·逆鳞碎片不足，需要集齐100块可合成1块神·逆鳞")

            # 每次点击合成 1 个（消耗 100 碎片），避免与“批量使用<=10”的概念混淆
            exchange_count = 1
            consume_count = 100

            # 跨多格扣除碎片（仅正式背包）
            self._remove_item_quantity(user_id, 3011, consume_count)
            # 发放神·逆鳞
            self.add_item(user_id, 3010, exchange_count)

            return {
                "message": f"合成成功，消耗神·逆鳞碎片×{consume_count}，获得神·逆鳞×{exchange_count}",
                "rewards": {"神·逆鳞": exchange_count},
            }

        # ========== 背包内开启灵石：六系灵石(未开)(7101-7106) ==========
        # 规则：开启消耗灵石，获得对应元素随机种族战灵（由 SpiritService 严格按配置执行）
        if int(item_template.id) in (7101, 7102, 7103, 7104, 7105, 7106):
            # 检查等级要求（35级）
            if self.player_repo:
                player = self.player_repo.get_by_id(user_id)
                player_level = int(getattr(player, "level", 0) or 0) if player else 0
                if player_level < 35:
                    raise InventoryError("战灵系统需要35级才能解锁，无法开启灵石")
            
            if not self.spirit_service:
                raise InventoryError("系统错误：SpiritService 未配置")
            id_to_element = {
                7101: "earth",
                7102: "fire",
                7103: "water",
                7104: "wood",
                7105: "metal",
                7106: "god",
            }
            element_key = id_to_element.get(int(item_template.id))
            if not element_key:
                raise InventoryError("灵石配置错误")

            created = self.spirit_service.open_stone(user_id=user_id, element_key=element_key, quantity=int(quantity))
            got = len(created or [])
            return {
                "message": f"开启成功，消耗{item_template.name}×{quantity}，获得战灵×{got}",
                "rewards": {"战灵": got},
            }

        # ========== 不允许在背包直接“使用”的物品：给出明确指引（不扣除物品） ==========
        # 严格遵循《商城购买 + 背包核销机制》：不能在背包用的道具应提示去对应功能界面核销
        non_bag_use_hints = {
            6001: "镇妖符请在【镇妖】界面镇妖时自动消耗",
            6002: "迷踪符请在【地图副本】界面点击【迷踪】使用",
            4002: "捕捉球请在【地图副本】捕捉幻兽时选择使用",
            4003: "强力捕捉球请在【地图副本】捕捉幻兽时选择使用",
            6018: "传送符请在【地图】界面的传送处使用",
            6019: "追魂法宝请在【魔魂-猎魂高级场】使用",
            6024: "双倍卡请在【地图副本】打开战利品/宝箱时选择使用",
            6022: "魔纹布用于【背包升级】材料，升级背包时会自动消耗",
            6023: "丝线用于【背包升级】材料，升级背包时会自动消耗",
            6005: "金袋请在【联盟-捐赠物资】界面捐献使用",
            11001: "盟主证明用于【创建联盟】时自动消耗",
            6028: "炼魂丹请在【炼妖壶】功能中开始炼妖时自动消耗",
            6029: "庄园建造手册请在【庄园】扩建土地时自动消耗",
            6006: "战灵钥匙请前往【战灵】界面用于激活第2/第3条属性条",
            6016: "神奇重生丹请在【幻兽-重生】界面使用",
            6017: "重生丹请在【幻兽-重生】界面使用",
            6031: "洗髓丹暂未开放（背包中不可使用）",
            6032: "坐骑口粮暂未开放（背包中不可使用）",
        }
        hint = non_bag_use_hints.get(int(item_template.id))
        if hint:
            raise InventoryError(hint)

        # 3. 处理不同物品的使用效果
        message = ""
        rewards = {}  # 奖励字典，格式：{物品名: 数量}
        if item_template.id == 6010:  # 骰子包
            dice_to_add = 10 * quantity
            if self.player_repo:
                player = self.player_repo.get_by_id(user_id)
                if player:
                    player.dice += dice_to_add
                    self.player_repo.save(player)
                    message = f"成功使用{item_template.name}×{quantity}，获得{dice_to_add}个骰子"
                    rewards["骰子"] = dice_to_add
                else:
                    raise InventoryError("玩家不存在")
            else:
                raise InventoryError("系统错误：PlayerRepo 未配置")
        elif 20001 <= item_template.id < 30000:  # 幻兽召唤球
            if not self.beast_service:
                raise InventoryError("系统错误：BeastService 未配置")

            # 神兽召唤球：等级门槛 & 唯一持有（同一神兽仅一只）
            if int(item_template.id) in DIVINE_BEAST_BALL_CONFIG:
                if quantity != 1:
                    raise InventoryError("神兽召唤球一次只能打开1个")
                if not self.player_repo:
                    raise InventoryError("系统错误：PlayerRepo 未配置")
                player = self.player_repo.get_by_id(user_id)
                if not player:
                    raise InventoryError("玩家不存在")

                template_id, beast_name, min_lv = DIVINE_BEAST_BALL_CONFIG[int(item_template.id)]
                player_level = int(getattr(player, "level", 0) or 0)
                if player_level < int(min_lv):
                    raise InventoryError(f"人物等级不足，需要{int(min_lv)}级才能打开{item_template.name}")

                existing = self.beast_service.beast_repo.get_by_user_id(user_id)
                if any(int(getattr(b, "template_id", 0) or 0) == int(template_id) for b in (existing or [])):
                    raise InventoryError(f"你已拥有{beast_name}，无法再次获得")

                beast_template = self.beast_service.template_repo.get_by_id(int(template_id))
                if not beast_template:
                    raise InventoryError(f"幻兽模板不存在: {beast_name}")
                beast_template_id = int(template_id)
            else:
                # 改进：通过名称查找模板
                beast_name = item_template.name.replace("召唤球", "")
                beast_template = self.beast_service.template_repo.get_by_name(beast_name)

                if not beast_template:
                    # 兼容逻辑：通过ID偏移查找
                    beast_template_id = item_template.id - 20000
                    beast_template = self.beast_service.template_repo.get_by_id(beast_template_id)

                if not beast_template:
                    raise InventoryError(f"幻兽模板不存在: {beast_name}")

                beast_template_id = beast_template.id

            # 使用 beast_routes 里的 obtain_beast_for_user 方法 (即 obtain_beast 的核心逻辑)
            # 采用局部导入以避免循环依赖
            from interfaces.routes.beast_routes import obtain_beast_for_user

            # 一个一个处理，防止超过幻兽栏上限
            for _ in range(quantity):
                payload, status_code = obtain_beast_for_user(
                    user_id=user_id,
                    template_id=beast_template_id,
                    realm="地界",
                    level=1
                )
                if not payload.get("ok"):
                    if _ == 0:
                        raise InventoryError(payload.get("error", "获取幻兽失败"))
                    else:
                        quantity = _
                        break

            message = f"成功使用{item_template.name}×{quantity}，获得了幻兽【{beast_template.name}】"
            rewards[f"幻兽【{beast_template.name}】"] = quantity
        elif item_template.id == PRESTIGE_STONE_ITEM_ID:
            if not self.player_repo:
                raise InventoryError("系统错误：PlayerRepo 未配置")
            player = self.player_repo.get_by_id(user_id)
            if not player:
                raise InventoryError("玩家不存在")
            prestige_gain = 2000 * quantity
            player.prestige += prestige_gain
            self.player_repo.save(player)
            message = f"成功使用{item_template.name}×{quantity}，获得{prestige_gain}声望"
            rewards["声望"] = prestige_gain
        elif item_template.id in VITALITY_GRASS_ITEM_IDS:  # 活力草
            if not self.player_repo:
                raise InventoryError("系统错误：PlayerRepo 未配置")
            player = self.player_repo.get_by_id(user_id)
            if not player:
                raise InventoryError("玩家不存在")
            per = 50
            before = int(getattr(player, "energy", 0) or 0)
            max_energy = int(getattr(player, "max_energy", 0) or 0) or 100

            # 活力已满则禁止使用（避免出现“活力+0但道具被消耗”的糟糕体验）
            if before >= max_energy:
                raise InventoryError("活力已满，无需使用活力草")

            remaining = max_energy - before
            need_count = (remaining + per - 1) // per  # 达到上限所需活力草数量
            use_count = min(int(quantity), int(need_count))
            gained = min(remaining, per * use_count)

            player.energy = before + gained
            self.player_repo.save(player)
            # 实际只消耗必要数量
            quantity = int(use_count)
            message = f"成功使用{item_template.name}×{quantity}，活力+{gained}"
            rewards["活力"] = gained
        elif item_template.id == FORTUNE_TALISMAN_ITEM_ID:  # 招财神符
            if not self.player_repo:
                raise InventoryError("系统错误：PlayerRepo 未配置")
            player = self.player_repo.get_by_id(user_id)
            if not player:
                raise InventoryError("玩家不存在")

            # ===== 每日使用次数限制（按 VIP 特权）=====
            # 说明：
            # - 招财神符(6004) 的“每日限购”由商城 daily_limit 控制（configs/shop.json）
            # - 这里实现的是“每日使用次数限制”，需跟 VIP 特权 fortune_talisman_uses 对齐（configs/vip_privileges.json）
            def _ensure_fortune_talisman_daily_table():
                execute_update(
                    """
                    CREATE TABLE IF NOT EXISTS fortune_talisman_daily (
                        user_id INT NOT NULL,
                        use_date DATE NOT NULL,
                        use_count INT NOT NULL DEFAULT 0,
                        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        PRIMARY KEY (user_id, use_date)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """
                )

            def _get_used_today() -> int:
                _ensure_fortune_talisman_daily_table()
                rows = execute_query(
                    "SELECT use_count FROM fortune_talisman_daily WHERE user_id = %s AND use_date = CURDATE()",
                    (user_id,),
                )
                if not rows:
                    return 0
                return int(rows[0].get("use_count", 0) or 0)

            def _set_used_today(cnt: int) -> None:
                _ensure_fortune_talisman_daily_table()
                execute_update(
                    """
                    INSERT INTO fortune_talisman_daily (user_id, use_date, use_count)
                    VALUES (%s, CURDATE(), %s)
                    ON DUPLICATE KEY UPDATE use_count = VALUES(use_count)
                    """,
                    (user_id, int(cnt)),
                )

            vip_level = int(getattr(player, "vip_level", 0) or 0)
            from application.services.vip_service import get_fortune_talisman_limit

            daily_limit = int(get_fortune_talisman_limit(vip_level) or 0)
            used_today = _get_used_today()
            remaining = max(0, daily_limit - used_today)
            if remaining <= 0:
                raise InventoryError(f"今日招财神符使用次数已达上限（VIP{vip_level}：{daily_limit}次）")

            # 本次只允许使用 remaining 个（并同步调整扣除数量，避免“效果=0但道具被消耗”）
            use_count = min(int(quantity), int(remaining))
            if use_count <= 0:
                raise InventoryError(f"今日招财神符使用次数已达上限（VIP{vip_level}：{daily_limit}次）")

            lv = int(getattr(player, "level", 1) or 1)
            if 1 <= lv <= 9:
                base = 49300
            elif 10 <= lv <= 19:
                base = 66300
            elif 20 <= lv <= 29:
                base = 83300
            elif 30 <= lv <= 39:
                base = 100300
            elif 40 <= lv <= 49:
                base = 117300
            elif 50 <= lv <= 59:
                base = 134300
            elif 60 <= lv <= 69:
                base = 151300
            elif 70 <= lv <= 79:
                base = 168300
            elif 80 <= lv <= 89:
                base = 185300
            else:
                base = 202300

            total_gold = int(base) * int(use_count)
            player.gold = int(getattr(player, "gold", 0) or 0) + total_gold
            self.player_repo.save(player)

            _set_used_today(used_today + int(use_count))
            quantity = int(use_count)
            message = f"成功使用{item_template.name}×{quantity}，获得铜钱×{total_gold}"
            rewards["铜钱"] = total_gold
        elif item_template.id == 6015:  # 化仙丹
            raise InventoryError("化仙丹请在化仙池界面使用")
        elif item_template.id == LUCKY_CHEST_ITEM_ID:
            if not self.player_repo:
                raise InventoryError("系统错误：PlayerRepo 未配置")
            player = self.player_repo.get_by_id(user_id)
            if not player:
                raise InventoryError("玩家不存在")

            total_gold = 0
            for _ in range(quantity):
                total_gold += random.randint(10000, 100000)
            player.gold += total_gold
            self.player_repo.save(player)
            message = f"成功开启{item_template.name}×{quantity}，获得铜钱×{total_gold}"
            rewards["铜钱"] = total_gold
        elif item_template.id in (
        ANCIENT_SILVER_CHEST_ITEM_ID, ANCIENT_TITANIUM_CHEST_ITEM_ID, ANCIENT_EVOLVE_CHEST_ITEM_ID,
        SKILL_BOOK_POUCH_ITEM_ID):
            if not self.player_repo:
                raise InventoryError("系统错误：PlayerRepo 未配置")
            player = self.player_repo.get_by_id(user_id)
            if not player:
                raise InventoryError("玩家不存在")

            def _ensure_chest_counter_table():
                execute_update(
                    """
                    CREATE TABLE IF NOT EXISTS player_chest_counter (
                        user_id INT NOT NULL,
                        chest_item_id INT NOT NULL,
                        open_count INT NOT NULL DEFAULT 0,
                        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        PRIMARY KEY (user_id, chest_item_id)
                    )
                    """
                )

            def _get_open_count(chest_id: int) -> int:
                _ensure_chest_counter_table()
                rows = execute_query(
                    "SELECT open_count FROM player_chest_counter WHERE user_id = %s AND chest_item_id = %s",
                    (user_id, chest_id),
                )
                if not rows:
                    return 0
                return int(rows[0].get("open_count", 0) or 0)

            def _set_open_count(chest_id: int, count: int) -> None:
                _ensure_chest_counter_table()
                execute_update(
                    """
                    INSERT INTO player_chest_counter (user_id, chest_item_id, open_count)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE open_count = VALUES(open_count)
                    """,
                    (user_id, chest_id, int(count)),
                )

            def _inc_open_count(chest_id: int) -> int:
                cnt = _get_open_count(chest_id) + 1
                _set_open_count(chest_id, cnt)
                return cnt

            rewards_summary: dict[str, int] = {}
            gold_total = 0

            # 常用道具ID
            SHEN_NI_LIN_ID = 3010
            SHEN_NI_LIN_FRAGMENT_ID = 3011
            MO_WEN_BU_ID = 6022
            SI_XIAN_ID = 6023
            DOUBLE_CARD_ID = 6024
            DICE_BAG_ID = 6010
            HUA_XIAN_DAN_ID = 6015
            SOUL_CHARM_ID = 6019
            GOLD_BAG_ID = 6005
            REBIRTH_PILL_ID = 6017
            CRYSTAL_POOL = [1001, 1002, 1003, 1004, 1005, 1006, 1007]
            VITALITY_GRASS_ID = 4001
            STRONG_CAPTURE_BALL_ID = 4003
            EVOLVE_HERB_ID = 3012
            EVOLVE_FRAGMENT_ID = 3013
            EVOLVE_CRYSTAL_ID = 3014

            def _add_item_reward(item_id: int, count: int = 1):
                nonlocal rewards_summary
                self.add_item(user_id, int(item_id), int(count))
                it = self.item_repo.get_by_id(int(item_id))
                name = it.name if it else f"物品{item_id}"
                rewards_summary[name] = rewards_summary.get(name, 0) + int(count)

            def _add_gold(amount: int):
                nonlocal gold_total
                gold_total += int(amount)

            for _ in range(int(quantity)):
                if item_template.id == SKILL_BOOK_POUCH_ITEM_ID:
                    # 技能书口袋：随机一本技能书（配置里的每本等概率）
                    cfg_path = os.path.join(os.path.dirname(__file__), '..', '..', 'configs', 'skill_books.json')
                    try:
                        with open(cfg_path, 'r', encoding='utf-8') as f:
                            cfg = json.load(f)
                    except Exception:
                        cfg = {}
                    all_books = []
                    for _, books in (cfg.get('skill_books', {}) or {}).items():
                        for b in books or []:
                            if b and b.get('item_id'):
                                all_books.append(int(b['item_id']))
                    if not all_books:
                        raise InventoryError('技能书配置缺失，无法开启技能书口袋')
                    _add_item_reward(random.choice(all_books), 1)
                    continue

                if item_template.id == ANCIENT_EVOLVE_CHEST_ITEM_ID:
                    # 远古进化宝箱：
                    # - 进化神草 20%
                    # - 进化圣水晶：每开第10个必出1个（之后重置）
                    # - 进化碎片（其余概率）
                    cnt = _inc_open_count(ANCIENT_EVOLVE_CHEST_ITEM_ID)
                    if cnt >= 10:
                        _add_item_reward(EVOLVE_CRYSTAL_ID, 1)
                        _set_open_count(ANCIENT_EVOLVE_CHEST_ITEM_ID, 0)
                        continue
                    roll = random.random()
                    if roll < 0.20:
                        _add_item_reward(EVOLVE_HERB_ID, 1)
                    else:
                        _add_item_reward(EVOLVE_FRAGMENT_ID, 1)
                    continue

                if item_template.id == ANCIENT_SILVER_CHEST_ITEM_ID:
                    # 远古秘银宝箱：
                    # - 技能书口袋 0.5%
                    # - 神·逆鳞碎片 0.5%
                    # - 神·逆鳞：每开第800个必出1个（之后重置）
                    # - 其余道具：当前按已明确列出的道具等概率
                    cnt = _inc_open_count(ANCIENT_SILVER_CHEST_ITEM_ID)
                    if cnt >= 800:
                        _add_item_reward(SHEN_NI_LIN_ID, 1)
                        _set_open_count(ANCIENT_SILVER_CHEST_ITEM_ID, 0)
                        continue
                    roll = random.random()
                    if roll < 0.005:
                        _add_item_reward(SKILL_BOOK_POUCH_ITEM_ID, 1)
                    elif roll < 0.01:
                        _add_item_reward(SHEN_NI_LIN_FRAGMENT_ID, 1)
                    else:
                        # 文档要求：其余 99% 爆率由剩余 15 种道具平分（其中“七类结晶随机”按 7 类分别计入）
                        pool15 = [
                            NINGSHEN_INCENSE_ITEM_ID,
                            STRONG_CAPTURE_BALL_ID,
                            DICE_BAG_ID,
                            MO_WEN_BU_ID,
                            # 七类结晶（7种分别计入池子）
                            *CRYSTAL_POOL,
                            HUA_XIAN_DAN_ID,
                            DOUBLE_CARD_ID,
                            SI_XIAN_ID,
                            VITALITY_GRASS_ID,
                        ]
                        _add_item_reward(random.choice(pool15), 1)
                    continue

                if item_template.id == ANCIENT_TITANIUM_CHEST_ITEM_ID:
                    # 远古钛金宝箱：
                    # - 技能书口袋 2%
                    # - 神·逆鳞碎片 2%
                    # - 追魂法宝 2%
                    # - 神·逆鳞：每开第100个必出1个（之后重置）
                    # - 其余11种道具：剩余概率均分
                    cnt = _inc_open_count(ANCIENT_TITANIUM_CHEST_ITEM_ID)
                    if cnt >= 100:
                        _add_item_reward(SHEN_NI_LIN_ID, 1)
                        _set_open_count(ANCIENT_TITANIUM_CHEST_ITEM_ID, 0)
                        continue
                    roll = random.random()
                    if roll < 0.02:
                        _add_item_reward(SKILL_BOOK_POUCH_ITEM_ID, 1)
                    elif roll < 0.04:
                        _add_item_reward(SHEN_NI_LIN_FRAGMENT_ID, 1)
                    elif roll < 0.06:
                        _add_item_reward(SOUL_CHARM_ID, 1)
                    else:
                        pool11 = [
                            GOLD_BAG_ID,
                            REBIRTH_PILL_ID,
                            FORTUNE_TALISMAN_ITEM_ID,
                            HUA_XIAN_DAN_ID,
                            DICE_BAG_ID,
                            MO_WEN_BU_ID,
                            STRONG_CAPTURE_BALL_ID,
                            DOUBLE_CARD_ID,
                            SI_XIAN_ID,
                            VITALITY_GRASS_ID,
                            NINGSHEN_INCENSE_ITEM_ID,
                        ]
                        _add_item_reward(random.choice(pool11), 1)
                    continue

            if gold_total > 0:
                player.gold = int(getattr(player, 'gold', 0) or 0) + gold_total
                self.player_repo.save(player)

            parts = []
            if rewards_summary:
                parts.append("、".join([f"{name}×{qty}" for name, qty in rewards_summary.items()]))
            if gold_total > 0:
                parts.append(f"铜钱×{gold_total}")
            rewards_text = "、".join(parts) if parts else "无"
            message = f"成功开启{item_template.name}×{quantity}，获得：{rewards_text}"
            # 合并奖励到rewards字典
            rewards.update(rewards_summary)
            if gold_total > 0:
                rewards["铜钱"] = rewards.get("铜钱", 0) + gold_total
        elif item_template.id in (ZHENYAO_TRIAL_CHEST_ITEM_ID, ZHENYAO_HELL_CHEST_ITEM_ID):
            if not self.player_repo:
                raise InventoryError("系统错误：PlayerRepo 未配置")

            player = self.player_repo.get_by_id(user_id)
            if not player:
                raise InventoryError("玩家不存在")

            chest_type = "trial" if item_template.id == ZHENYAO_TRIAL_CHEST_ITEM_ID else "hell"
            reward_cfg = self._get_zhenyao_reward_config_by_level(player.level)
            rewards_def = reward_cfg.get(chest_type, {})

            total_gold = 0
            item_summary: dict[str, int] = {}
            for _ in range(quantity):
                total_gold += int(rewards_def.get("gold", 0) or 0)
                for item_cfg in rewards_def.get("items", []) or []:
                    # 检查是否是从池中随机选择
                    if "pool" in item_cfg:
                        pool = item_cfg.get("pool") or []
                        count = int(item_cfg.get("count", 1) or 1)
                        if pool and count > 0:
                            # 从池中随机选择count个不同的物品，每个给1个
                            selected_items = random.sample(pool, min(count, len(pool)))
                            for item_id in selected_items:
                                self.add_item(user_id, int(item_id), 1)
                                # 使用实际物品的名称，而不是配置中的"七类结晶"
                                actual_item = self.item_repo.get_by_id(int(item_id))
                                item_name = actual_item.name if actual_item else f"物品{item_id}"
                                item_summary[item_name] = item_summary.get(item_name, 0) + 1
                    else:
                        # 普通物品，直接发放
                        item_id = item_cfg.get("id")
                        if item_id:
                            count = int(item_cfg.get("count", 1) or 1)
                            self.add_item(user_id, int(item_id), count)
                            item_name = item_cfg.get("name") or (
                                self.item_repo.get_by_id(int(item_id)).name if self.item_repo.get_by_id(
                                    int(item_id)) else f"物品{item_id}")
                            item_summary[item_name] = item_summary.get(item_name, 0) + count

            if total_gold > 0:
                player.gold += total_gold
                self.player_repo.save(player)

            parts = []
            if item_summary:
                parts.append("、".join([f"{name}×{qty}" for name, qty in item_summary.items()]))
            if total_gold > 0:
                parts.append(f"铜钱×{total_gold}")
            rewards_text = "、".join(parts) if parts else "无"
            message = f"成功开启{item_template.name}×{quantity}，获得：{rewards_text}"
            # 合并奖励到rewards字典
            rewards.update(item_summary)
            if total_gold > 0:
                rewards["铜钱"] = rewards.get("铜钱", 0) + total_gold
        elif getattr(item_template, "use_effect", None) and item_template.use_effect.startswith("activity_gift_"):
            if not self.activity_gift_service:
                raise InventoryError("系统错误：礼包逻辑未初始化")
            gift_key = item_template.use_effect
            all_rewards = []
            for _ in range(quantity):
                reward_payload = self.activity_gift_service.open_gift(user_id, gift_key)
                all_rewards.append(reward_payload)
            message = self._format_activity_gift_message(item_template.name, quantity, all_rewards)
            # 提取奖励信息
            item_summary = {}
            gold_total = 0
            for payload in all_rewards:
                for reward in payload.get("rewards", []):
                    r_type = reward.get("type")
                    if r_type == "gold":
                        gold_total += reward.get("amount", 0)
                    elif r_type == "item":
                        name = reward.get("name") or f"物品{reward.get('item_id')}"
                        item_summary[name] = item_summary.get(name, 0) + reward.get("quantity", 0)
            rewards.update(item_summary)
            if gold_total > 0:
                rewards["铜钱"] = rewards.get("铜钱", 0) + gold_total
        elif item_template.id == DRAGONPALACE_EXPLORE_GIFT_ITEM_ID:
            # 龙宫之谜探索礼包：打开后获得（随机进化材料×N）+ 铜钱20000*N
            # 这里不要在 helper 里重复扣除物品，最终统一由 use_item() 的第4步扣除。
            payload = self.open_dragonpalace_explore_gift(
                user_id=user_id,
                inv_item_id=inv_item_id,
                open_count=int(quantity or 1),
                open_all=False,
                consume=False,
            )
            message = payload.get("message", "") or f"成功开启{item_template.name}×{quantity}"
            # 提取奖励信息
            if "rewards" in payload:
                rewards.update(payload["rewards"])
            if "gold" in payload and payload["gold"] > 0:
                rewards["铜钱"] = rewards.get("铜钱", 0) + payload["gold"]
        elif item_template.id == NINGSHEN_INCENSE_ITEM_ID:
            if not self.player_effect_repo:
                raise InventoryError("系统错误：PlayerEffectRepo 未配置")

            now = datetime.now()
            new_end = self.player_effect_repo.add_duration_seconds(
                user_id=user_id,
                effect_key=NINGSHEN_INCENSE_EFFECT_KEY,
                duration_seconds=NINGSHEN_INCENSE_DURATION_SECONDS * quantity,
                now=now,
            )

            remaining_seconds = int((new_end - now).total_seconds())
            remaining_hours = max(0, int(remaining_seconds / 3600))
            message = f"成功使用{item_template.name}×{quantity}，24小时内修行声望+20%。剩余有效时间约 {remaining_hours} 小时"
            rewards["修行声望加成"] = f"{remaining_hours}小时"
        else:
            raise InventoryError(f"物品 {item_template.name} 的使用尚未上线，尽情期待！")

        # 4. 扣除物品
        self._remove_item_from_slot(inv_item_id, quantity)

        return {
            "message": message,
            "rewards": rewards
        }

    def open_dragonpalace_explore_gift(
            self,
            user_id: int,
            inv_item_id: int,
            open_count: int = 1,
            open_all: bool = False,
            consume: bool = True,
    ) -> dict:
        """
        打开“龙宫之谜探索礼包”（通常来自临时背包）。

        返回结构用于前端展示：
        - message: 叙述文案（严格模仿外站风格）
        - reward_item_id / reward_item_name / reward_item_quantity
        - copper_gain
        - remaining_quantity: 当前格子剩余数量（本交互里通常为 0）
        """
        inv_item = self.inventory_repo.get_by_id(inv_item_id)
        if not inv_item or inv_item.user_id != user_id:
            raise InventoryError("物品不存在")
        if int(inv_item.item_id or 0) != DRAGONPALACE_EXPLORE_GIFT_ITEM_ID:
            raise InventoryError("该物品不是龙宫之谜探索礼包")
        available = int(inv_item.quantity or 0)
        if available < 1:
            raise InventoryError("物品数量不足")

        if not self.player_repo:
            raise InventoryError("系统错误：PlayerRepo 未配置")

        # 1) 计算本次打开数量
        if open_all:
            open_n = available
        else:
            try:
                open_n = int(open_count or 1)
            except Exception:
                open_n = 1
            open_n = max(1, open_n)
            open_n = min(open_n, available)

        # 2) 逐个开奖并汇总
        reward_summary: dict[str, int] = {}
        for _ in range(open_n):
            reward_item_id = int(pick_dragonpalace_reward_item_id())
            self.add_item(user_id, reward_item_id, 1)
            reward_item = self.item_repo.get_by_id(reward_item_id)
            reward_item_name = getattr(reward_item, "name",
                                       f"物品{reward_item_id}") if reward_item else f"物品{reward_item_id}"
            reward_summary[reward_item_name] = reward_summary.get(reward_item_name, 0) + 1

        # 3) 铜钱奖励：+20000 * open_n（兼容新旧字段：同时写 gold/copper）
        player = self.player_repo.get_by_id(user_id)
        if not player:
            raise InventoryError("玩家不存在")
        copper_gain = int(DRAGONPALACE_EXPLORE_GIFT_COPPER) * int(open_n)
        player.copper = int(getattr(player, "copper", 0) or 0) + copper_gain
        player.gold = int(getattr(player, "gold", 0) or 0) + copper_gain
        self.player_repo.save(player)

        # 4) 扣除礼包本体（默认 consume=True；若由 use_item 调用则 consume=False）
        if consume:
            self._remove_item_from_slot(inv_item_id, open_n)

        # 5) 计算剩余数量
        if consume:
            inv_after = self.inventory_repo.get_by_id(inv_item_id)
            remaining_quantity = int(inv_after.quantity or 0) if inv_after and inv_after.user_id == user_id else 0
        else:
            remaining_quantity = available - open_n

        reward_text = "、".join([f"{name}×{qty}" for name, qty in reward_summary.items()]) if reward_summary else "无"
        msg = f"悄悄的打开{open_n}个龙宫之谜探索礼包,惊喜的获得:{reward_text}，铜钱+{copper_gain}"
        return {
            "ok": True,
            "message": msg,
            "reward_items": [{"name": k, "quantity": v} for k, v in reward_summary.items()],
            "copper_gain": copper_gain,
            "remaining_quantity": remaining_quantity,
        }

    def _load_zhenyao_rewards_config(self) -> dict:
        config_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "configs",
            "zhenyao_rewards.json",
        )
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"reward_configs": []}

    def _get_zhenyao_reward_config_by_level(self, player_level: int) -> dict:
        data = self._load_zhenyao_rewards_config()
        for cfg in data.get("reward_configs", []) or []:
            if cfg.get("min_level", 0) <= player_level <= cfg.get("max_level", 0):
                return cfg
        raise InventoryError("镇妖奖励配置不存在")

    def _format_activity_gift_message(self, gift_name: str, quantity: int, rewards_payload: list) -> str:
        item_summary = {}
        gold_total = 0
        for payload in rewards_payload:
            for reward in payload.get("rewards", []):
                r_type = reward.get("type")
                if r_type == "gold":
                    gold_total += reward.get("amount", 0)
                elif r_type == "item":
                    name = reward.get("name") or f"物品{reward.get('item_id')}"
                    item_summary[name] = item_summary.get(name, 0) + reward.get("quantity", 0)
        parts = []
        if item_summary:
            parts.append("、".join([f"{name}×{qty}" for name, qty in item_summary.items()]))
        if gold_total:
            parts.append(f"铜钱×{gold_total}")
        rewards_text = "、".join(parts) if parts else "无额外奖励"
        return f"成功开启{gift_name}×{quantity}，获得：{rewards_text}"

    def _remove_item_from_slot(self, inv_item_id: int, quantity: int):
        """从特定格子扣除物品"""
        inv_item = self.inventory_repo.get_by_id(inv_item_id)
        if not inv_item:
            return

        if inv_item.quantity <= quantity:
            self.inventory_repo.delete(inv_item_id)
        else:
            inv_item.quantity -= quantity
            self.inventory_repo.save(inv_item)
