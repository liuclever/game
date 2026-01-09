# interfaces/web_api/bootstrap.py
"""
服务依赖初始化（依赖注入容器）
所有服务实例在此创建，供路由模块使用
"""

from domain.entities.player import Player
from infrastructure.memory.player_repo_inmemory import InMemoryPlayerRepo
from infrastructure.config.monster_repo_from_config import ConfigMonsterRepo
from infrastructure.config.map_repo_from_config import ConfigMapRepo
from infrastructure.config.item_repo_from_config import ConfigItemRepo
from infrastructure.config.beast_template_repo_from_config import ConfigBeastTemplateRepo
from infrastructure.config.bone_template_repo_from_config import ConfigBoneTemplateRepo
from infrastructure.config.tower_config_repo import ConfigTowerRepo
from infrastructure.config.handbook_repo_from_config import ConfigHandbookRepo

from infrastructure.db.inventory_repo_mysql import MySQLInventoryRepo
from infrastructure.db.tower_state_repo_mysql import MySQLTowerStateRepo
from infrastructure.db.player_beast_repo_mysql import MySQLPlayerBeastRepo
from infrastructure.db.player_repo_mysql import MySQLPlayerRepo, MySQLZhenyaoRepo
from infrastructure.db.bone_repo_mysql import MySQLBoneRepo
from infrastructure.db.spirit_repo_mysql import MySQLSpiritRepo
from infrastructure.db.spirit_account_repo_mysql import MySQLSpiritAccountRepo
from infrastructure.db.mosoul_repo_mysql import MySQLMoSoulRepo, MySQLBeastMoSoulRepo
from infrastructure.db.alliance_repo_mysql import MySQLAllianceRepo
from infrastructure.db.task_reward_repo_mysql import MySQLTaskRewardRepo
from infrastructure.db.daily_activity_repo_mysql import MySQLDailyActivityRepo
from infrastructure.db.manor_repo_mysql import MySQLManorRepo
from infrastructure.db.refine_pot_log_repo_mysql import MySQLRefinePotLogRepo
from infrastructure.db.month_card_repo_mysql import MySQLMonthCardRepo
from infrastructure.db.immortalize_pool_repo_mysql import MySQLImmortalizePoolRepo
from infrastructure.db.player_effect_repo_mysql import MySQLPlayerEffectRepo
from infrastructure.db.player_gift_claim_repo_mysql import MySQLPlayerGiftClaimRepo
from infrastructure.memory.beast_repo_inmemory import InMemoryBeastRepo

from application.services.battle_service import BattleService
from application.services.signin_service import SigninService
from application.services.map_service import MapService
from application.services.inventory_service import InventoryService
from application.services.beast_service import BeastService
from application.services.bone_service import BoneService
from application.services.spirit_service import SpiritService
from application.services.drop_service import DropService
from application.services.capture_service import CaptureService
from application.services.tower_service import TowerBattleService
from application.services.zhenyao_service import ZhenyaoService
from application.services.auth_service import AuthService
from application.services.battlefield_service import BattlefieldService
from application.services.beast_pvp_service import BeastPvpService
from application.services.alliance_service import AllianceService
from application.services.alliance_battle_service import AllianceBattleService
from application.services.task_reward_service import TaskRewardService
from application.services.daily_activity_service import DailyActivityService
from application.services.activity_gift_service import ActivityGiftService
from application.services.cultivation_service import CultivationService
from application.services.handbook_service import HandbookService
from application.services.manor_service import ManorService
from application.services.refine_pot_service import RefinePotService
from application.services.month_card_service import MonthCardService
from application.services.immortalize_pool_service import ImmortalizePoolService
from application.services.home_gift_service import HomeGiftService
from infrastructure.config.immortalize_config import ImmortalizeConfig


class ServiceContainer:
    """服务容器，管理所有服务实例"""
    
    def __init__(self):
        # 仓储层
        self.player_repo_inmemory = InMemoryPlayerRepo({1: Player(user_id=1, username="hero", level=5, exp=0, gold=0, energy=100)})
        self.map_repo = ConfigMapRepo()
        self.monster_repo = ConfigMonsterRepo()
        self.item_repo = ConfigItemRepo()
        self.handbook_repo = ConfigHandbookRepo()
        self.inventory_repo = MySQLInventoryRepo()
        self.beast_template_repo = ConfigBeastTemplateRepo()
        # 暂时使用内存仓库保存玩家幻兽（重启进程后会清空）
        self.beast_repo = InMemoryBeastRepo()

        # 战骨模板 & 玩家战骨
        self.bone_template_repo = ConfigBoneTemplateRepo()
        self.bone_repo = MySQLBoneRepo()
        self.tower_state_repo = MySQLTowerStateRepo()
        self.tower_config_repo = ConfigTowerRepo()
        self.player_beast_repo = MySQLPlayerBeastRepo()
        self.player_repo = MySQLPlayerRepo()
        self.zhenyao_repo = MySQLZhenyaoRepo()
        self.task_reward_repo = MySQLTaskRewardRepo()
        self.daily_activity_repo = MySQLDailyActivityRepo()
        self.manor_repo = MySQLManorRepo()
        self.refine_pot_log_repo = MySQLRefinePotLogRepo()
        self.month_card_repo = MySQLMonthCardRepo()
        self.immortalize_pool_repo = MySQLImmortalizePoolRepo()
        self.immortalize_config = ImmortalizeConfig()
        self.player_effect_repo = MySQLPlayerEffectRepo()
        self.player_gift_claim_repo = MySQLPlayerGiftClaimRepo()

        # 战灵仓库
        self.spirit_repo = MySQLSpiritRepo()
        self.spirit_account_repo = MySQLSpiritAccountRepo()

        # 联盟仓库
        self.alliance_repo = MySQLAllianceRepo()

        # 魔魂仓库
        self.mosoul_repo = MySQLMoSoulRepo()
        self.beast_mosoul_repo = MySQLBeastMoSoulRepo(mosoul_repo=self.mosoul_repo)
        
        # 服务层
        self.beast_service = BeastService(
            template_repo=self.beast_template_repo, 
            beast_repo=self.player_beast_repo
        )
        self.inventory_service = InventoryService(
            item_repo=self.item_repo, 
            inventory_repo=self.inventory_repo,
            player_repo=self.player_repo,
            beast_service=self.beast_service,
            player_effect_repo=self.player_effect_repo,
        )
        self.bone_service = BoneService(
            bone_repo=self.bone_repo,
            bone_template_repo=self.bone_template_repo,
            inventory_service=self.inventory_service,
            player_repo=self.player_repo,
        )
        self.spirit_service = SpiritService(
            spirit_repo=self.spirit_repo,
            account_repo=self.spirit_account_repo,
            inventory_service=self.inventory_service,
            player_repo=self.player_repo,
            tower_state_repo=self.tower_state_repo,
            player_beast_repo=self.player_beast_repo,
        )
        self.drop_service = DropService(
            item_repo=self.item_repo, 
            inventory_service=self.inventory_service
        )
        self.capture_service = CaptureService(
            inventory_service=self.inventory_service, 
            beast_service=self.beast_service
        )
        self.beast_pvp_service = BeastPvpService(
            spirit_repo=self.spirit_repo,
            bone_repo=self.bone_repo,
            mosoul_repo=self.beast_mosoul_repo,
        )
        self.battle_service = BattleService(
            player_repo=self.player_repo_inmemory, 
            monster_repo=self.monster_repo, 
            drop_service=self.drop_service
        )
        # 同时依赖联盟仓库：用于从盟战榜前三联盟随机选取“颁发者”
        self.signin_service = SigninService(player_repo=self.player_repo, alliance_repo=self.alliance_repo)
        self.map_service = MapService(
            map_repo=self.map_repo, 
            monster_repo=self.monster_repo
        )
        self.tower_service = TowerBattleService(
            state_repo=self.tower_state_repo,
            config_repo=self.tower_config_repo,
            inventory_service=self.inventory_service,
            player_repo=self.player_repo,
        )
        self.zhenyao_service = ZhenyaoService(
            player_repo=self.player_repo,
            zhenyao_repo=self.zhenyao_repo,
            tower_state_repo=self.tower_state_repo,
            bone_repo=self.bone_repo,
            spirit_repo=self.spirit_repo,
            beast_pvp_service=self.beast_pvp_service,
            inventory_service=self.inventory_service,
        )
        self.auth_service = AuthService(
            player_repo=self.player_repo,
            beast_template_repo=self.beast_template_repo,
            player_beast_repo=self.player_beast_repo,
            inventory_service=self.inventory_service,
            tower_state_repo=self.tower_state_repo,
        )
        self.battlefield_service = BattlefieldService(
            player_repo=self.player_repo,
            player_beast_repo=self.player_beast_repo,
            beast_pvp_service=self.beast_pvp_service,
        )
        self.alliance_service = AllianceService(
            alliance_repo=self.alliance_repo,
            player_repo=self.player_repo,
            inventory_service=self.inventory_service,
            beast_repo=self.player_beast_repo,
        )
        self.alliance_battle_service = AllianceBattleService(
            alliance_repo=self.alliance_repo,
            player_repo=self.player_repo,
            player_beast_repo=self.player_beast_repo,
            beast_pvp_service=self.beast_pvp_service,
        )
        self.task_reward_service = TaskRewardService(
            reward_repo=self.task_reward_repo,
            player_repo=self.player_repo,
            inventory_service=self.inventory_service,
        )
        self.daily_activity_service = DailyActivityService(
            daily_activity_repo=self.daily_activity_repo,
        )
        self.activity_gift_service = ActivityGiftService(
            inventory_service=self.inventory_service,
            daily_activity_service=self.daily_activity_service,
            player_repo=self.player_repo,
        )
        self.inventory_service.set_activity_gift_service(self.activity_gift_service)
        self.cultivation_service = CultivationService(
            player_repo=self.player_repo,
            beast_repo=self.player_beast_repo,
            item_repo=self.item_repo,
            inventory_service=self.inventory_service,
            player_effect_repo=self.player_effect_repo,
        )
        self.home_gift_service = HomeGiftService(
            gift_claim_repo=self.player_gift_claim_repo,
            inventory_service=self.inventory_service,
            player_repo=self.player_repo,
            item_repo=self.item_repo,
        )
        self.immortalize_pool_service = ImmortalizePoolService(
            pool_repo=self.immortalize_pool_repo,
            player_repo=self.player_repo,
            inventory_service=self.inventory_service,
            config=self.immortalize_config,
        )
        self.inventory_service.set_immortalize_pool_service(self.immortalize_pool_service)
        self.manor_service = ManorService(
            manor_repo=self.manor_repo,
            player_repo=self.player_repo,
            inventory_service=self.inventory_service
        )
        self.refine_pot_service = RefinePotService(
            player_repo=self.player_repo,
            player_beast_repo=self.player_beast_repo,
            inventory_service=self.inventory_service,
            refine_log_repo=self.refine_pot_log_repo,
        )
        self.month_card_service = MonthCardService(
            player_repo=self.player_repo,
            inventory_service=self.inventory_service,
            month_card_repo=self.month_card_repo,
        )

        # 图鉴（独立模块）
        self.handbook_service = HandbookService(repo=self.handbook_repo)


# 全局服务容器实例
services = ServiceContainer()
