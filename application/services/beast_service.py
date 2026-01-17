from typing import List, Optional
from dataclasses import dataclass
import random

from domain.entities.beast import Beast, BeastTemplate
from domain.repositories.beast_repo import IBeastTemplateRepo, IBeastRepo
from domain.services.beast_factory import create_initial_beast
from domain.services.beast_stats import calc_aptitude_stars


class BeastError(Exception):
    """幻兽相关错误"""
    pass


@dataclass
class BeastWithInfo:
    """幻兽实例 + 模板信息（用于返回给前端）"""
    beast: Beast
    template: BeastTemplate

    def to_dict(self) -> dict:
        """将幻兽实例和模板信息组合成前端需要的完整数据结构。"""
        # 基础四维属性（暂时仍使用旧的 calc_* 计算公式）
        hp = self.beast.calc_hp(self.template)
        attack = self.beast.calc_attack(self.template)
        defense = self.beast.calc_defense(self.template)
        speed = self.beast.calc_speed(self.template)

        # 资质对应的星级信息
        stars = calc_aptitude_stars(self.beast, self.template)

        return {
            "id": self.beast.id,
            "template_id": self.beast.template_id,
            # 基本信息
            "name": self.template.name,
            "nickname": self.beast.nickname or self.template.name,
            "description": self.template.description,
            # 等级与经验
            "level": self.beast.level,
            "exp": self.beast.exp,
            "exp_to_next": self.beast.exp_to_next_level(),
            # 出战状态
            "is_main": self.beast.is_main,
            # 当前属性数值（基础版）
            "hp": hp,
            "attack": attack,
            "defense": defense,
            "speed": speed,
            # 模板相关标签（便于前端展示）
            "race": self.template.race,
            "realm": self.beast.realm or self.template.realm,
            "trait": self.template.trait,
            "rarity": self.template.rarity,
            "habitat": self.template.habitat,
            "attack_type": self.beast.attack_type or self.template.attack_type,
            # 性格（实例性格：勇敢 / 精明 / 胆小 / 谨慎 / 傻瓜）
            "personality": self.beast.personality,
            # 成长率（直接从模板读取的成长评分）
            "growth_score": self.template.growth_score,
            # 资质（实例真实资质）
            "hp_aptitude": self.beast.hp_aptitude,
            "speed_aptitude": self.beast.speed_aptitude,
            "physical_atk_aptitude": self.beast.physical_atk_aptitude,
            "physical_def_aptitude": self.beast.physical_def_aptitude,
            "magic_def_aptitude": self.beast.magic_def_aptitude,
            # 资质星级（实心 / 空心）
            "hp_solid_stars": stars["hp_solid_stars"],
            "hp_hollow_stars": stars["hp_hollow_stars"],
            "speed_solid_stars": stars["speed_solid_stars"],
            "speed_hollow_stars": stars["speed_hollow_stars"],
            "physical_atk_solid_stars": stars["physical_atk_solid_stars"],
            "physical_atk_hollow_stars": stars["physical_atk_hollow_stars"],
            "physical_def_solid_stars": stars["physical_def_solid_stars"],
            "physical_def_hollow_stars": stars["physical_def_hollow_stars"],
            "magic_def_solid_stars": stars["magic_def_solid_stars"],
            "magic_def_hollow_stars": stars["magic_def_hollow_stars"],
            # 成长率星级
            "growth_solid_stars": stars["growth_solid_stars"],
            "growth_hollow_stars": stars["growth_hollow_stars"],
            # 技能列表（名称）
            "skills": self.beast.skills,
        }


class BeastService:
    def __init__(self, template_repo: IBeastTemplateRepo, beast_repo: IBeastRepo):
        self.template_repo = template_repo
        self.beast_repo = beast_repo

    def get_beasts(self, user_id: int) -> List[BeastWithInfo]:
        """获取玩家所有幻兽（带详情）"""
        beasts = self.beast_repo.get_by_user_id(user_id)
        result = []
        for b in beasts:
            template = self.template_repo.get_by_id(b.template_id)
            if template:
                result.append(BeastWithInfo(beast=b, template=template))
        return result

    def get_main_beast(self, user_id: int) -> Optional[BeastWithInfo]:
        """获取玩家出战幻兽"""
        beast = self.beast_repo.get_main_beast(user_id)
        if beast is None:
            return None
        template = self.template_repo.get_by_id(beast.template_id)
        if template is None:
            return None
        return BeastWithInfo(beast=beast, template=template)

    def add_beast(self, user_id: int, template_id: int, nickname: str = "") -> Beast:
        """给玩家添加幻兽"""
        template = self.template_repo.get_by_id(template_id)
        if template is None:
            raise BeastError(f"幻兽模板不存在: {template_id}")

        # 用我们新写的初始化规则创建 Beast 实例
        beast = create_initial_beast(user_id=user_id, template=template)

        # 如有昵称参数，覆盖默认昵称
        if nickname:
            beast.nickname = nickname

        # 如果是玩家第一只幻兽，自动设为出战
        existing = self.beast_repo.get_by_user_id(user_id)
        if len(existing) == 0:
            beast.is_main = True

        self.beast_repo.save(beast)
        return beast

    def set_main_beast(self, user_id: int, beast_id: int) -> Beast:
        """设置出战幻兽"""
        beast = self.beast_repo.get_by_id(beast_id)
        if beast is None or beast.user_id != user_id:
            raise BeastError("幻兽不存在")

        # 取消当前出战
        current_main = self.beast_repo.get_main_beast(user_id)
        if current_main and current_main.id != beast_id:
            current_main.is_main = False
            self.beast_repo.save(current_main)

        # 设置新出战
        beast.is_main = True
        self.beast_repo.save(beast)
        return beast

    def add_exp_to_beast(self, user_id: int, beast_id: int, exp: int) -> BeastWithInfo:
        """给幻兽增加经验（带玩家校验）。"""
        if exp <= 0:
            raise BeastError("exp 必须是正整数")

        beast = self.beast_repo.get_by_id(beast_id)
        if beast is None or beast.user_id != user_id:
            raise BeastError("幻兽不存在")

        beast.add_exp(exp)
        self.beast_repo.save(beast)

        template = self.template_repo.get_by_id(beast.template_id)
        return BeastWithInfo(beast=beast, template=template)

    def obtain_beast_randomly(self, user_id: int, template_id: int, realm: str = None, level: int = 1) -> Beast:
        """为玩家随机生成并获得一只幻兽（供召唤球、捕捉等系统使用）"""
        template = self.template_repo.get_by_id(template_id)
        if template is None:
            raise BeastError(f"幻兽模板不存在: {template_id}")

        # 使用 factory 创建实例
        from domain.services.beast_factory import create_initial_beast
        beast = create_initial_beast(user_id=user_id, template=template)

        # 兜底：确保种族写入（历史版本 Beast 可能没有 race 字段）
        try:
            if not getattr(beast, "race", ""):
                beast.race = template.race
        except Exception:
            pass
        
        # 覆盖等级和境界（如果提供）
        if level > 1:
            beast.level = level
        if realm:
            beast.realm = realm
            
        # 如果是玩家第一只幻兽，自动设为出战
        existing = self.beast_repo.get_by_user_id(user_id)
        if len(existing) == 0:
            beast.is_main = True

        self.beast_repo.save(beast)
        return beast
