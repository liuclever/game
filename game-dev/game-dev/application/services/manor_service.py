from typing import List, Tuple, Dict
from datetime import datetime, timedelta
from domain.repositories.manor_repo import IManorRepo
from domain.repositories.player_repo import IPlayerRepo
from domain.rules.manor_rules import ManorRules, GROWTH_HOURS
from application.services.inventory_service import InventoryService, InventoryError

MANOR_MANUAL_ITEM_ID = 6029  # 庄园建造手册

class ManorService:
    def __init__(
        self, 
        manor_repo: IManorRepo, 
        player_repo: IPlayerRepo, 
        inventory_service: InventoryService
    ):
        self.manor_repo = manor_repo
        self.player_repo = player_repo
        self.inventory_service = inventory_service

    def expand_land(self, user_id: int, land_index: int) -> Tuple[bool, str]:
        """开启/扩建土地"""
        player = self.player_repo.get_by_id(user_id)
        if not player:
            return False, "玩家不存在"

        if land_index > 9 and ManorRules.get_special_land_requirement(land_index) is None:
            return False, "普通土地最多10块，无法继续扩建"

        # 获取现有土地状态，确保不是已开启
        land = self.manor_repo.get_land(user_id, land_index)
        if land and land.status != 0:
            return False, "该土地已开启"

        # 获取手册数量
        item_count = self.inventory_service.get_item_count(user_id, MANOR_MANUAL_ITEM_ID)
        
        # 规则校验
        can_open, msg = ManorRules.can_expand(
            land_index, 
            player.level, 
            player.vip_level, 
            item_count
        )
        if not can_open:
            return False, msg

        # 获取扣除数量
        req = ManorRules.get_expansion_requirement(land_index)
        if not req:
            req = ManorRules.get_special_land_requirement(land_index)
        
        if not req:
            return False, "非法的土地索引"
        
        req_manuals = req[1]

        # 扣除道具
        try:
            self.inventory_service.remove_item(user_id, MANOR_MANUAL_ITEM_ID, req_manuals)
        except InventoryError as e:
            return False, str(e)

        # 开启土地
        success = self.manor_repo.open_land(user_id, land_index)
        if success:
            return True, "开启成功"
        return False, "开启失败，数据库错误"

    def plant_tree(self, user_id: int, land_indices: List[int], tree_type: int) -> Tuple[bool, str]:
        """种植摇钱树（支持一键种植）"""
        player = self.player_repo.get_by_id(user_id)
        if not player:
            return False, "玩家不存在"

        cost_per_tree = ManorRules.get_tree_cost(tree_type)
        if cost_per_tree <= 0:
            return False, "无效的树种"

        # 获取选中的土地并校验状态/树种锁定规则
        lands_to_plant = []
        for idx in land_indices:
            land = self.manor_repo.get_land(user_id, idx)
            if not land or land.status != 1:
                continue
            if land.tree_type and land.tree_type != tree_type:
                continue
            lands_to_plant.append(idx)
        
        if not lands_to_plant:
            return False, "没有可种植的土地"

        total_cost = cost_per_tree * len(lands_to_plant)
        if player.yuanbao < total_cost:
            return False, f"元宝不足，需要{total_cost}元宝"

        # 扣除元宝
        player.yuanbao -= total_cost
        self.player_repo.save(player)

        now = datetime.now()

        # 执行种植
        success_count = 0
        for idx in lands_to_plant:
            land = self.manor_repo.get_land(user_id, idx)
            if not land or land.status != 1:
                continue

            # 规则：第一次种植后可立刻收获；第二次开始需等待 6 小时
            if land.tree_type == 0:
                plant_time = now - timedelta(hours=GROWTH_HOURS)
            else:
                plant_time = now

            if self.manor_repo.start_planting(user_id, idx, tree_type, plant_time):
                success_count += 1
        
        if success_count <= 0:
            player.yuanbao += total_cost
            self.player_repo.save(player)
            return False, "种植失败"

        refund = (len(lands_to_plant) - success_count) * cost_per_tree
        if refund > 0:
            player.yuanbao += refund
            self.player_repo.save(player)

        actual_cost = success_count * cost_per_tree
        return True, f"成功种植{success_count}块土地，消耗{actual_cost}元宝"

    def harvest_all(self, user_id: int) -> Tuple[bool, str, Dict]:
        """一键收获成熟土地"""
        player = self.player_repo.get_by_id(user_id)
        if not player:
            return False, "玩家不存在", {}

        lands = self.manor_repo.get_user_lands(user_id)
        now = datetime.now()
        
        mature_lands = [l for l in lands if l.is_mature(now, GROWTH_HOURS)]
        if not mature_lands:
            return False, "没有已成熟的土地", {}

        total_gold = 0
        harvest_count = len(mature_lands)
        
        for land in mature_lands:
            # 传入 land_index 以应用土地加成
            earnings = ManorRules.calculate_earnings(player.level, land.tree_type, land.land_index)
            total_gold += earnings
            # 重置土地
            self.manor_repo.reset_land(user_id, land.land_index)

        # 增加收益
        player.gold += total_gold
        self.player_repo.save(player)

        # 更新庄园统计信息
        self.manor_repo.create_player_manor_if_not_exists(user_id)
        stats = self.manor_repo.get_player_manor(user_id)
        if stats:
            stats.total_harvest_count += harvest_count
            stats.total_gold_earned += total_gold
            self.manor_repo.update_player_manor(stats)

        return True, f"收获成功，获得{total_gold}铜钱", {
            "gold_earned": total_gold,
            "harvest_count": harvest_count
        }

    def get_manor_info(self, user_id: int) -> Dict:
        """获取庄园完整信息用于展示"""
        lands = self.manor_repo.get_user_lands(user_id)
        stats = self.manor_repo.get_player_manor(user_id)
        
        now = datetime.now()
        land_data = []
        for l in lands:
            land_data.append({
                "land_index": l.land_index,
                "status": l.status,
                "tree_type": l.tree_type,
                "remaining_seconds": l.get_remaining_seconds(now, GROWTH_HOURS),
                "is_mature": l.is_mature(now, GROWTH_HOURS)
            })
            
        return {
            "lands": land_data,
            "stats": {
                "total_harvest_count": stats.total_harvest_count if stats else 0,
                "total_gold_earned": stats.total_gold_earned if stats else 0
            }
        }
