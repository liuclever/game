"""
登录注册服务
"""
import json
import os
from typing import Optional, Dict, List
from dataclasses import dataclass
from domain.entities.player import Player
from domain.entities.tower import TowerState
from domain.repositories.player_repo import IPlayerRepo
from domain.repositories.beast_repo import IBeastTemplateRepo
from domain.repositories.tower_repo import ITowerStateRepo
from domain.services.beast_factory import create_initial_beast
from domain.services.beast_stats import BeastStatCalculator
from infrastructure.db.player_beast_repo_mysql import MySQLPlayerBeastRepo, PlayerBeastData
from infrastructure.db.mosoul_repo_mysql import create_mosoul


def load_game_config() -> dict:
    """加载游戏配置"""
    config_path = os.path.join(os.path.dirname(__file__), "../../configs/game_config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"mode": "production"}  # 默认正式模式


def is_test_mode() -> bool:
    """判断是否为测试模式"""
    config = load_game_config()
    return config.get("mode") == "test"


# 测试模式下新用户默认获得的神兽模板ID列表
DEFAULT_BEAST_TEMPLATE_IDS: List[int] = [
    62,  # 神·朱雀
    63,  # 神·玄武
    64,  # 神·青龙
]

# 测试模式下的初始道具配置
TEST_MODE_ITEMS = {
    "gold": 50000000,  # 铜钱
    "zhenyaofu": {"item_id": 6001, "quantity": 100},  # 镇妖符
    "strengthen_stone": {"item_id": 9001, "quantity": 10000},  # 强化石
    # 结晶 (1001-1007) 各60个
    "crystals": [
        {"item_id": 1001, "quantity": 60},  # 金之结晶
        {"item_id": 1002, "quantity": 60},  # 木之结晶
        {"item_id": 1003, "quantity": 60},  # 水之结晶
        {"item_id": 1004, "quantity": 60},  # 火之结晶
        {"item_id": 1005, "quantity": 60},  # 土之结晶
        {"item_id": 1006, "quantity": 60},  # 风之结晶
        {"item_id": 1007, "quantity": 60},  # 电之结晶
    ],
    # 骨魂 (2001-2009) 各100个
    "bone_souls": [
        {"item_id": 2001, "quantity": 100},  # 碎空骨魂
        {"item_id": 2002, "quantity": 100},  # 猎魔骨魂
        {"item_id": 2003, "quantity": 100},  # 龙炎骨魂
        {"item_id": 2004, "quantity": 100},  # 奔雷骨魂
        {"item_id": 2005, "quantity": 100},  # 凌霄骨魂
        {"item_id": 2006, "quantity": 100},  # 麒麟骨魂
        {"item_id": 2007, "quantity": 100},  # 武神骨魂
        {"item_id": 2008, "quantity": 100},  # 弑天骨魂
        {"item_id": 2009, "quantity": 100},  # 毁灭骨魂
    ],
    # 龙魂 template_id: 101, 102, 103 各3个，等级10
    "dragon_souls": [101, 102, 103],
    # 天魂 template_id: 201-212 各3个，等级10
    "heaven_souls": [201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212],
}


class AuthError(Exception):
    """认证相关错误"""
    pass


@dataclass
class LoginResult:
    """登录结果"""
    success: bool
    user_id: Optional[int] = None
    nickname: str = ""
    level: int = 0
    rank_name: str = ""
    error: str = ""


class AuthService:
    """登录注册服务"""
    
    def __init__(
        self, 
        player_repo: IPlayerRepo,
        beast_template_repo: IBeastTemplateRepo = None,
        player_beast_repo: MySQLPlayerBeastRepo = None,
        inventory_service = None,
        tower_state_repo: ITowerStateRepo = None,
    ):
        self.player_repo = player_repo
        self.beast_template_repo = beast_template_repo
        self.player_beast_repo = player_beast_repo
        self.inventory_service = inventory_service
        self.tower_state_repo = tower_state_repo
    
    def register(self, username: str, password: str, nickname: str = "") -> LoginResult:
        """
        注册新用户
        
        Args:
            username: 账号
            password: 密码
            nickname: 昵称（可选，默认与账号相同）
        
        Returns:
            LoginResult
        """
        # 验证输入
        if not username or len(username) < 2:
            return LoginResult(success=False, error="账号至少2个字符")
        
        if not password or len(password) < 4:
            return LoginResult(success=False, error="密码至少4个字符")
        
        # 检查账号是否已存在
        existing = self.player_repo.get_by_username(username)
        if existing:
            return LoginResult(success=False, error="账号已存在")
        
        # 创建新用户
        if not nickname:
            nickname = username
        
        # 测试模式下给更多初始金币和更高等级
        if is_test_mode():
            initial_gold = TEST_MODE_ITEMS["gold"]
            initial_level = 100  # 测试模式100级
            initial_location = "落龙镇"
        else:
            initial_gold = 100
            initial_level = 1
            initial_location = "林中空地"
        
        player = Player(
            user_id=0,  # 自动生成
            nickname=nickname,
            level=initial_level,
            exp=0,
            gold=initial_gold,
            location=initial_location,
        )
        
        user_id = self.player_repo.create_with_auth(username, password, player)
        
        if user_id:
            # 仅在测试模式下为新用户创建默认幻兽和道具
            if is_test_mode():
                self._create_default_beasts(user_id)
                self._create_test_mode_items(user_id)
                self._create_test_mode_tower_progress(user_id)
                self._create_test_mode_bag(user_id)

            # 新用户默认获得三种召唤球
            # 血螳螂(20003) / 追风狼(20006) / 羽精灵(20009)
            if self.inventory_service:
                try:
                    self.inventory_service.add_item(user_id, 20003, 1)
                    self.inventory_service.add_item(user_id, 20006, 1)
                    self.inventory_service.add_item(user_id, 20009, 1)
                except Exception:
                    # 注册不应因为发放初始道具失败而整体失败
                    pass
            
            # 测试模式下等级名称为"10星0品召唤师"
            rank_name = "10星0品召唤师" if is_test_mode() else "黄阶"
            
            return LoginResult(
                success=True,
                user_id=user_id,
                nickname=nickname,
                level=initial_level,
                rank_name=rank_name,
            )
        else:
            return LoginResult(success=False, error="注册失败")
    
    def _create_default_beasts(self, user_id: int) -> None:
        """为测试模式新用户创建默认幻兽
        
        测试模式下：
        - 默认给三只幻兽：神朱雀、神玄武、神青龙
        - 满资质（地界最大值）
        - 阶段：地界
        - 技能：图鉴全部技能
        
        Args:
            user_id: 新用户ID
        """
        if not self.beast_template_repo or not self.player_beast_repo:
            return
        
        for idx, template_id in enumerate(DEFAULT_BEAST_TEMPLATE_IDS):
            template = self.beast_template_repo.get_by_id(template_id)
            if not template:
                continue
            
            # 测试模式：使用满资质（地界最大值）
            # 模板的资质上限已经是地界的值
            hp_aptitude_max = template.hp_aptitude_max
            speed_aptitude_max = template.speed_aptitude_max
            physical_atk_aptitude_max = template.physical_atk_aptitude_max
            physical_def_aptitude_max = template.physical_def_aptitude_max
            magic_def_aptitude_max = template.magic_def_aptitude_max
            
            # 测试模式：使用图鉴技能 (all_skill_names)
            skills = template.all_skill_names if template.all_skill_names else []
            
            # 创建幻兽实例（满资质，地界）
            from domain.entities.beast import Beast
            beast = Beast(
                user_id=user_id,
                template_id=template.id,
                nickname=template.name,
                level=1,
                exp=0,
                is_main=False,
                personality="勇敢",
                attack_type=template.attack_type,
                realm="地界",  # 固定地界
                hp_aptitude=hp_aptitude_max,
                speed_aptitude=speed_aptitude_max,
                physical_atk_aptitude=physical_atk_aptitude_max,
                physical_def_aptitude=physical_def_aptitude_max,
                magic_def_aptitude=magic_def_aptitude_max,
                skills=skills,
            )
            
            # 计算战斗属性（使用地界上限）
            stats = BeastStatCalculator.calc_base_stats(beast, template, max_realm="地界")
            
            # 将 Beast 转换为 PlayerBeastData
            beast_data = PlayerBeastData(
                user_id=user_id,
                name=template.name,
                realm="地界",
                race=template.race,
                level=beast.level,
                exp=beast.exp,
                nature="物系" if template.attack_type == "physical" else "法系",
                personality=beast.personality,
                hp=stats.hp,
                physical_attack=stats.physical_attack,
                magic_attack=stats.magic_attack,
                physical_defense=stats.physical_defense,
                magic_defense=stats.magic_defense,
                speed=stats.speed,
                combat_power=stats.hp + stats.physical_attack + stats.magic_attack + stats.physical_defense + stats.magic_defense + stats.speed * 100,
                growth_rate=template.growth_score,
                hp_aptitude=hp_aptitude_max,
                speed_aptitude=speed_aptitude_max,
                magic_attack_aptitude=physical_atk_aptitude_max,  # 物系幻兽用此字段存储物攻资质
                physical_defense_aptitude=physical_def_aptitude_max,
                magic_defense_aptitude=magic_def_aptitude_max,
                lifespan="10000/10000",
                skills=skills,
                counters="",
                countered_by="",
                is_in_team=1 if idx < 3 else 0,  # 前3只加入战斗队
                team_position=idx + 1 if idx < 3 else 0,  # 设置队伍位置
            )
            
            self.player_beast_repo.create_beast(beast_data)
    
    def _create_test_mode_items(self, user_id: int) -> None:
        """为测试模式新用户创建默认道具
        
        Args:
            user_id: 新用户ID
        """
        if not self.inventory_service:
            return
        
        # 添加镇妖符
        item = TEST_MODE_ITEMS["zhenyaofu"]
        self.inventory_service.add_item(user_id, item["item_id"], item["quantity"])
        
        # 添加强化石
        item = TEST_MODE_ITEMS["strengthen_stone"]
        self.inventory_service.add_item(user_id, item["item_id"], item["quantity"])
        
        # 添加结晶
        for item in TEST_MODE_ITEMS["crystals"]:
            self.inventory_service.add_item(user_id, item["item_id"], item["quantity"])
        
        # 添加骨魂
        for item in TEST_MODE_ITEMS["bone_souls"]:
            self.inventory_service.add_item(user_id, item["item_id"], item["quantity"])
        
        # 添加所有卷轴 (5001-5096) 各10个
        scroll_ids = (
            list(range(5001, 5008)) +   # 碎空卷轴 5001-5007
            list(range(5011, 5018)) +   # 猎魔卷轴 5011-5017
            list(range(5021, 5028)) +   # 龙炎卷轴 5021-5027
            list(range(5031, 5038)) +   # 奔雷卷轴 5031-5037
            list(range(5041, 5048)) +   # 凌霄卷轴 5041-5047
            list(range(5051, 5058)) +   # 麒麟卷轴 5051-5057
            list(range(5061, 5068)) +   # 武神卷轴 5061-5067
            list(range(5071, 5078)) +   # 弑天卷轴 5071-5077
            list(range(5081, 5088)) +   # 毁灭卷轴 5081-5087
            list(range(5091, 5097))     # 圣魂卷轴 5091-5096
        )
        for scroll_id in scroll_ids:
            self.inventory_service.add_item(user_id, scroll_id, 10)
        
        # 添加所有技能书各5个
        skill_book_ids = (
            list(range(10001, 10014)) +  # 普通主动技能书
            list(range(10101, 10114)) +  # 高级主动技能书
            list(range(10201, 10204)) +  # 普通被动技能书
            list(range(10301, 10304)) +  # 高级被动技能书
            list(range(10401, 10410)) +  # 普通Buff技能书
            list(range(10501, 10509)) +  # 高级Buff技能书
            list(range(10601, 10605))    # 负面技能书
        )
        for book_id in skill_book_ids:
            self.inventory_service.add_item(user_id, book_id, 5)
        
        # 添加龙魂 (各3个，等级10)
        for template_id in TEST_MODE_ITEMS["dragon_souls"]:
            for _ in range(3):
                create_mosoul(user_id, template_id, level=10, exp=0)
        
        # 添加天魂 (各3个，等级10)
        for template_id in TEST_MODE_ITEMS["heaven_souls"]:
            for _ in range(3):
                create_mosoul(user_id, template_id, level=10, exp=0)
    
    def _create_test_mode_tower_progress(self, user_id: int) -> None:
        """为测试模式新用户初始化通天塔进度
        
        测试模式下：
        - 通天塔已通关120层（max_floor_record=121, current_floor=121）
        
        Args:
            user_id: 新用户ID
        """
        if not self.tower_state_repo:
            return
        
        # 创建通天塔进度：已通关120层
        tower_state = TowerState(
            user_id=user_id,
            tower_type="tongtian",
            current_floor=121,
            max_floor_record=121,
            today_count=0,
            last_challenge_date=None,
        )
        self.tower_state_repo.save(tower_state)
    
    def _create_test_mode_bag(self, user_id: int) -> None:
        """为测试模式新用户初始化背包
        
        测试模式下：
        - 背包等级：999
        - 背包容量：99999
        
        Args:
            user_id: 新用户ID
        """
        if not self.inventory_service:
            return
        
        from domain.entities.item import PlayerBag
        
        # 创建超大背包
        bag = PlayerBag(
            user_id=user_id,
            bag_level=999,
            capacity=99999,
        )
        self.inventory_service.inventory_repo.save_bag_info(bag)
    
    def login(self, username: str, password: str) -> LoginResult:
        """
        登录
        
        Args:
            username: 账号
            password: 密码
        
        Returns:
            LoginResult
        """
        if not username or not password:
            return LoginResult(success=False, error="请输入账号和密码")
        
        # 验证账号密码
        player = self.player_repo.verify_login(username, password)
        
        if not player:
            return LoginResult(success=False, error="账号或密码错误")
        
        return LoginResult(
            success=True,
            user_id=player.user_id,
            nickname=player.nickname,
            level=player.level,
            rank_name=player.get_rank_name(),
        )
    
    def get_player(self, user_id: int) -> Optional[Player]:
        """获取玩家信息"""
        return self.player_repo.get_by_id(user_id)
