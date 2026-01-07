"""战骨升级服务单元测试（无需启动HTTP服务）

运行方式（项目根目录）：
    python -m pytest tests/bone/test_bone_service_unit.py -vv -s
"""

import pytest
import sys
sys.path.insert(0, '.')

from domain.entities.bone import BeastBone
from domain.entities.player import Player
from application.services.bone_service import BoneService, BoneError


class MockBoneRepo:
    """模拟战骨仓库"""
    def __init__(self):
        self.bones = {}
        self.next_id = 1
    
    def get_by_id(self, bone_id):
        return self.bones.get(bone_id)
    
    def get_by_user_id(self, user_id):
        return [b for b in self.bones.values() if b.user_id == user_id]
    
    def get_by_beast_id(self, beast_id):
        return [b for b in self.bones.values() if b.beast_id == beast_id]
    
    def save(self, bone):
        if bone.id is None:
            bone.id = self.next_id
            self.next_id += 1
        self.bones[bone.id] = bone


class MockBoneTemplateRepo:
    """模拟战骨模板仓库"""
    def get_by_id(self, template_id):
        from dataclasses import dataclass
        @dataclass
        class Template:
            id: int = template_id
            slot: str = "头骨"
        return Template()


class MockInventoryService:
    """模拟背包服务"""
    def __init__(self):
        self.items = {}  # {(user_id, item_id): quantity}
    
    def has_item(self, user_id, item_id, qty):
        return self.items.get((user_id, item_id), 0) >= qty
    
    def remove_item(self, user_id, item_id, qty):
        key = (user_id, item_id)
        self.items[key] = self.items.get(key, 0) - qty
    
    def add_item(self, user_id, item_id, qty):
        key = (user_id, item_id)
        self.items[key] = self.items.get(key, 0) + qty
    
    def _get_item_count(self, user_id, item_id):
        return self.items.get((user_id, item_id), 0)
    
    @property
    def item_repo(self):
        class ItemRepo:
            def get_by_id(self, item_id):
                return None
        return ItemRepo()


class MockPlayerRepo:
    """模拟玩家仓库"""
    def __init__(self):
        self.players = {}
    
    def get_by_id(self, user_id):
        return self.players.get(user_id)
    
    def save(self, player):
        self.players[player.user_id] = player


class TestBoneServiceUnit:
    """战骨服务单元测试"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """初始化服务和模拟对象"""
        self.bone_repo = MockBoneRepo()
        self.template_repo = MockBoneTemplateRepo()
        self.inventory_service = MockInventoryService()
        self.player_repo = MockPlayerRepo()
        
        self.service = BoneService(
            bone_repo=self.bone_repo,
            bone_template_repo=self.template_repo,
            inventory_service=self.inventory_service,
            player_repo=self.player_repo,
        )
        
        # 创建测试玩家（Player字段: user_id, nickname, level, exp, gold）
        self.player = Player(user_id=1, nickname="test", level=50, exp=0, gold=10000)
        self.player_repo.players[1] = self.player
        
        # 添加强化石
        self.inventory_service.add_item(1, 9001, 1000)

    def test_upgrade_success(self):
        """测试升级成功"""
        # 创建战骨
        bone_info = self.service.create_bone(user_id=1, template_id=910001, stage=1, level=1)
        bone_id = bone_info.bone.id
        
        # 升级
        result = self.service.upgrade_bone(user_id=1, bone_id=bone_id)
        
        assert result.bone.level == 2
        print(f"✅ 升级成功: 1级→2级")

    def test_upgrade_multiple_times(self):
        """测试连续升级"""
        bone_info = self.service.create_bone(user_id=1, template_id=910001, stage=1, level=1)
        bone_id = bone_info.bone.id
        
        for expected_level in range(2, 10):
            result = self.service.upgrade_bone(user_id=1, bone_id=bone_id)
            assert result.bone.level == expected_level
        
        print(f"✅ 连续升级成功: 1级→9级")

    def test_upgrade_insufficient_stone(self):
        """测试强化石不足"""
        # 清空强化石
        self.inventory_service.items[(1, 9001)] = 0
        
        bone_info = self.service.create_bone(user_id=1, template_id=910001, stage=1, level=1)
        bone_id = bone_info.bone.id
        
        with pytest.raises(BoneError) as exc_info:
            self.service.upgrade_bone(user_id=1, bone_id=bone_id)
        
        assert "强化石不足" in str(exc_info.value)
        print(f"✅ 强化石不足测试通过: {exc_info.value}")

    def test_upgrade_insufficient_gold(self):
        """测试铜钱不足"""
        self.player.gold = 0  # 清空铜钱
        
        bone_info = self.service.create_bone(user_id=1, template_id=910001, stage=1, level=1)
        bone_id = bone_info.bone.id
        
        with pytest.raises(BoneError) as exc_info:
            self.service.upgrade_bone(user_id=1, bone_id=bone_id)
        
        assert "铜钱不足" in str(exc_info.value)
        print(f"✅ 铜钱不足测试通过: {exc_info.value}")

    def test_upgrade_at_stage_max_level(self):
        """测试阶段满级无法升级"""
        bone_info = self.service.create_bone(user_id=1, template_id=910001, stage=1, level=10)
        bone_id = bone_info.bone.id
        
        with pytest.raises(BoneError) as exc_info:
            self.service.upgrade_bone(user_id=1, bone_id=bone_id)
        
        assert "进阶" in str(exc_info.value)
        print(f"✅ 阶段满级测试通过: {exc_info.value}")

    def test_upgrade_player_level_insufficient(self):
        """测试玩家等级不足"""
        # 规则：战骨升级后的等级不能超过玩家等级
        self.player.level = 2  # 允许 1->2

        bone_info = self.service.create_bone(user_id=1, template_id=910001, stage=1, level=1)
        bone_id = bone_info.bone.id

        # 先升到2级（需要玩家2级）
        self.service.upgrade_bone(user_id=1, bone_id=bone_id)

        # 玩家仍为2级，尝试升到3级应失败（需要玩家3级）
        with pytest.raises(BoneError) as exc_info:
            self.service.upgrade_bone(user_id=1, bone_id=bone_id)

        assert "玩家等级不足" in str(exc_info.value)
        print(f"✅ 玩家等级不足测试通过: {exc_info.value}")

    def test_upgrade_cost_query(self):
        """测试升级消耗查询"""
        bone_info = self.service.create_bone(user_id=1, template_id=910001, stage=1, level=5)
        bone_id = bone_info.bone.id
        
        cost = self.service.get_upgrade_cost(user_id=1, bone_id=bone_id)
        
        # 5级升6级，强化石 = 5 * 5 = 25
        stone_info = next(m for m in cost["materials"] if m["item_id"] == 9001)
        assert stone_info["required"] == 25
        assert cost["can_upgrade"] is True
        print(f"✅ 消耗查询测试通过: 需要{stone_info['required']}个强化石")


if __name__ == "__main__":
    pytest.main([__file__, "-vv", "-s"])