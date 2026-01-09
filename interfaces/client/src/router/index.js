import { createRouter, createWebHistory } from 'vue-router'
import http from '../services/http.js'

import MainPage from '@/features/main/MainPage.vue'
import RefinePotPage from '@/features/refine-pot/RefinePotPage.vue'
import RefinePotDetailPage from '@/features/refine-pot/RefinePotDetailPage.vue'
import RefinePotHpPage from '@/features/refine-pot/RefinePotHpPage.vue'
import RefinePotSpeedPage from '@/features/refine-pot/RefinePotSpeedPage.vue'
import RefinePotPhysicalPage from '@/features/refine-pot/RefinePotPhysicalPage.vue'
import RefinePotPhysicalDefensePage from '@/features/refine-pot/RefinePotPhysicalDefensePage.vue'
import RefinePotMagicPage from '@/features/refine-pot/RefinePotMagicPage.vue'
import RefinePotMagicDefensePage from '@/features/refine-pot/RefinePotMagicDefensePage.vue'
import ExchangePage from '@/features/exchange/ExchangePage.vue'
import ExchangeDetailPage from '@/features/exchange/ExchangeDetailPage.vue'
import ExchangeNilinPage from '@/features/exchange/ExchangeNilinPage.vue'
import ExchangeGodHerbPage from '@/features/exchange/ExchangeGodHerbPage.vue'
import ExchangeGodCrystalPage from '@/features/exchange/ExchangeGodCrystalPage.vue'
import ExchangeXuanwuPage from '@/features/exchange/ExchangeXuanwuPage.vue'
import ExchangeZhuquePage from '@/features/exchange/ExchangeZhuquePage.vue'
import ExchangeJueyingPage from '@/features/exchange/ExchangeJueyingPage.vue'
import ExchangeBaihuPage from '@/features/exchange/ExchangeBaihuPage.vue'
import ExchangeBusiniaoPage from '@/features/exchange/ExchangeBusiniaoPage.vue'
import ExchangeLuoshaPage from '@/features/exchange/ExchangeLuoshaPage.vue'
import InventoryPage from '@/features/inventory/InventoryPage.vue'
import BagUpgradePage from '@/features/inventory/BagUpgradePage.vue'
import TowerPage from '@/features/tower/TowerPage.vue'
import TowerChallengePage from '@/features/tower/TowerChallengePage.vue'
import BattleReportPage from '@/features/tower/BattleReportPage.vue'
import BeastPage from '@/features/beast/BeastPage.vue'
import BeastDetailPage from '@/features/beast/BeastDetailPage.vue'
import BeastEvolvePage from '@/features/beast/BeastEvolvePage.vue'
import SkillBookPage from '@/features/beast/SkillBookPage.vue'
import BeastBonePage from '@/features/beast/BeastBonePage.vue'
import BoneDetailPage from '@/features/beast/BoneDetailPage.vue'
import BoneRefinePage from '@/features/beast/BoneRefinePage.vue'
import BoneSelectPage from '@/features/beast/BoneSelectPage.vue'
import BeastSpiritPage from '@/features/beast/BeastSpiritPage.vue'
import SpiritEmbedPage from '@/features/beast/SpiritEmbedPage.vue'
import SpiritWarehousePage from '@/features/beast/SpiritWarehousePage.vue'
import SpiritDetailPage from '@/features/beast/SpiritDetailPage.vue'
import SpiritRefinePage from '@/features/beast/SpiritRefinePage.vue'
import SpiritKeyInsufficientPage from '@/features/beast/SpiritKeyInsufficientPage.vue'
import MoSoulPage from '@/features/beast/MoSoulPage.vue'
import MoSoulSelectPage from '@/features/beast/MoSoulSelectPage.vue'
import MoSoulDetailPage from '@/features/beast/MoSoulDetailPage.vue'
import MoSoulOverviewPage from '@/features/beast/MoSoulOverviewPage.vue'
import MoSoulWarehousePage from '@/features/beast/MoSoulWarehousePage.vue'
import MoSoulHuntingPage from '@/features/beast/MoSoulHuntingPage.vue'
import MoSoulAbsorbPage from '@/features/beast/MoSoulAbsorbPage.vue'
import DungeonChallengePage from '@/features/dungeon/DungeonChallengePage.vue'
import MizongPage from '@/features/dungeon/MizongPage.vue'
import DungeonBattleResultPage from '@/features/dungeon/DungeonBattleResultPage.vue'
import DungeonDetailReportPage from '@/features/dungeon/DungeonDetailReportPage.vue'
import DungeonCapturePage from '@/features/dungeon/DungeonCapturePage.vue'
import DiceSupplementPage from '@/features/dungeon/DiceSupplementPage.vue'
import TowerIntroPage from '@/features/tower/TowerIntroPage.vue'
import TowerBeastDetailPage from '@/features/tower/BeastDetailPage.vue'
import ZhenYaoPage from '@/features/tower/ZhenYaoPage.vue'
import ZhenYaoBattlePage from '@/features/tower/ZhenYaoBattlePage.vue'
import LoginPage from '@/features/auth/LoginPage.vue'
import PlayerProfilePage from '@/features/player/PlayerProfilePage.vue'
import PlayerDetailPage from '@/features/player/PlayerDetailPage.vue'
import MapPage from '@/features/map/MapPage.vue'
import TeleportPage from '@/features/map/TeleportPage.vue'
import TeleportSuccessPage from '@/features/map/TeleportSuccessPage.vue'
import MailPage from '@/features/mail/MailPage.vue'
import FriendPage from '@/features/friend/FriendPage.vue'
import FriendSearchPage from '@/features/friend/FriendSearchPage.vue'
import ArenaPage from '@/features/arena/ArenaPage.vue'
import ArenaBattlePage from '@/features/arena/ArenaBattlePage.vue'
import RankingPage from '@/features/ranking/RankingPage.vue'
import ArenaIntroPage from '@/features/arena/ArenaIntroPage.vue'
import SummonKingChallengePage from '@/features/king/SummonKingChallengePage.vue'
import KingIntroPage from '@/features/king/KingIntroPage.vue'
import KingRankingPage from '@/features/king/KingRankingPage.vue'
import ShopPage from '@/features/shop/ShopPage.vue'
import ShopItemDetailPage from '@/features/shop/ShopItemDetailPage.vue'
import ShopBuySuccessPage from '@/features/shop/ShopBuySuccessPage.vue'
import BattlefieldPage from '@/features/battlefield/BattlefieldPage.vue'
import BattlefieldIntroPage from '@/features/battlefield/BattlefieldIntroPage.vue'
import BattlefieldYesterdayPage from '@/features/battlefield/BattlefieldYesterdayPage.vue'
import BattlefieldBattlePage from '@/features/battlefield/BattlefieldBattlePage.vue'
import PvpArenaPage from '@/features/pvp/PvpArenaPage.vue'
import PvpIntroPage from '@/features/pvp/PvpIntroPage.vue'
import PvpBattleReportPage from '@/features/pvp/PvpBattleReportPage.vue'
import HuaXianPage from '@/features/huaxian/HuaXianPage.vue'
import HuaXianAllocatePage from '@/features/huaxian/HuaXianAllocatePage.vue'
import HuaXianAllocateDetailPage from '@/features/huaxian/HuaXianAllocateDetailPage.vue'
import HuaXianUpgradePage from '@/features/huaxian/HuaXianUpgradePage.vue'
import VipPrivilegePage from '@/features/main/VipPrivilegePage.vue'
import VipTestPage from '@/features/main/VipTestPage.vue'
import SponsorPage from '@/features/main/SponsorPage.vue'
import SponsorMonthCardPage from '@/features/main/SponsorMonthCardPage.vue'
import GiftsPage from '@/features/main/GiftsPage.vue'
import SparBattleReportPage from '@/features/player/SparBattleReportPage.vue'
import AlliancePage from '@/features/alliance/AlliancePage.vue'
import AllianceHallPage from '@/features/alliance/AllianceHallPage.vue'
import AllianceWarPage from '@/features/alliance/AllianceWarPage.vue'
import AllianceWarLivePage from '@/features/alliance/AllianceWarLivePage.vue'
import AllianceWarRulePage from '@/features/alliance/AllianceWarRulePage.vue'
import AllianceWarHonorPage from '@/features/alliance/AllianceWarHonorPage.vue'
import AllianceWarRankingPage from '@/features/alliance/AllianceWarRankingPage.vue'
import AllianceWarLandListPage from '@/features/alliance/AllianceWarTargetsPage.vue'
import AllianceWarLandDetailPage from '@/features/alliance/AllianceWarLandDetailPage.vue'
import AllianceWarDragonSignupPage from '@/features/alliance/AllianceWarDragonSignupPage.vue'
import AllianceBarracksPage from '@/features/alliance/AllianceBarracksPage.vue'
import AllianceChatPage from '@/features/alliance/AllianceChatPage.vue'
import AllianceCouncilPage from '@/features/alliance/AllianceCouncilPage.vue'
import AllianceNoticePage from '@/features/alliance/AllianceNoticePage.vue'
import AllianceMembersPage from '@/features/alliance/AllianceMembersPage.vue'
import AllianceTalentPage from '@/features/alliance/AllianceTalentPage.vue'
import AllianceTalentLearnPage from '@/features/alliance/AllianceTalentLearnPage.vue'
import AllianceTalentResearchPage from '@/features/alliance/AllianceTalentResearchPage.vue'
import AllianceBuildingUpgradePage from '@/features/alliance/AllianceBuildingUpgradePage.vue'
import AllianceCouncilUpgradePage from '@/features/alliance/AllianceCouncilUpgradePage.vue'
import AllianceFurnaceUpgradePage from '@/features/alliance/AllianceFurnaceUpgradePage.vue'
import AllianceTalentUpgradePage from '@/features/alliance/AllianceTalentUpgradePage.vue'
import AllianceBeastUpgradePage from '@/features/alliance/AllianceBeastUpgradePage.vue'
import AllianceItemUpgradePage from '@/features/alliance/AllianceItemUpgradePage.vue'
import AllianceWarehousePage from '@/features/alliance/AllianceWarehousePage.vue'
import AllianceTrainingGroundPage from '@/features/alliance/AllianceTrainingGroundPage.vue'
import AllianceDonatePage from '@/features/alliance/AllianceDonatePage.vue'
import AllianceItemStoragePage from '@/features/alliance/AllianceItemStoragePage.vue'
import AllianceTrainingIntroPage from '@/features/alliance/AllianceTrainingIntroPage.vue'
import AllianceRenamePage from '@/features/alliance/AllianceRenamePage.vue'
import TaskRewardsPage from '@/features/tasks/TaskRewardsPage.vue'
import DailyTasksPage from '@/features/tasks/DailyTasksPage.vue'
import CompletedTasksPage from '@/features/tasks/CompletedTasksPage.vue'
import ActivityGiftsPage from '@/features/tasks/ActivityGiftsPage.vue'
import CultivationPage from '@/features/cultivation/CultivationPage.vue'
import HandbookIndexPage from '@/features/handbook/HandbookIndexPage.vue'
import HandbookIntroPage from '@/features/handbook/HandbookIntroPage.vue'
import HandbookPetDetailPage from '@/features/handbook/HandbookPetDetailPage.vue'
import HandbookSkillDetailPage from '@/features/handbook/HandbookSkillDetailPage.vue'
import TreePage from '@/features/tree/TreePage.vue'
import TreeRulePage from '@/features/tree/TreeRulePage.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: MainPage,
  },
  {
    path: '/handbook',
    name: 'HandbookIndex',
    component: HandbookIndexPage,
  },
  {
    path: '/handbook/intro',
    name: 'HandbookIntro',
    component: HandbookIntroPage,
  },
  {
    path: '/handbook/pet/:id',
    name: 'HandbookPetDetail',
    component: HandbookPetDetailPage,
  },
  {
    path: '/handbook/skill/:key',
    name: 'HandbookSkillDetail',
    component: HandbookSkillDetailPage,
  },
  {
    path: '/tree',
    name: 'Tree',
    component: TreePage,
  },
  {
    path: '/tree/rule',
    name: 'TreeRule',
    component: TreeRulePage,
  },
  {
    path: '/gifts',
    name: 'Gifts',
    component: GiftsPage,
  },
  {
    path: '/refine-pot',
    name: 'RefinePot',
    component: RefinePotPage,
  },
  {
    path: '/refine-pot/refine',
    name: 'RefinePotDetail',
    component: RefinePotDetailPage,
  },
  {
    path: '/refine-pot/refine/hp',
    name: 'RefinePotHp',
    component: RefinePotHpPage,
  },
  {
    path: '/refine-pot/refine/speed',
    name: 'RefinePotSpeed',
    component: RefinePotSpeedPage,
  },
  {
    path: '/refine-pot/refine/physical',
    name: 'RefinePotPhysical',
    component: RefinePotPhysicalPage,
  },
  {
    path: '/refine-pot/refine/physical-defense',
    name: 'RefinePotPhysicalDefense',
    component: RefinePotPhysicalDefensePage,
  },
  {
    path: '/refine-pot/refine/magic',
    name: 'RefinePotMagic',
    component: RefinePotMagicPage,
  },
  {
    path: '/refine-pot/refine/magic-defense',
    name: 'RefinePotMagicDefense',
    component: RefinePotMagicDefensePage,
  },
  {
    path: '/exchange',
    name: 'Exchange',
    component: ExchangePage,
  },
  {
    path: '/exchange/beast/qinglong',
    name: 'ExchangeBeastQinglong',
    component: ExchangeDetailPage,
  },
  {
    path: '/exchange/item/nilin',
    name: 'ExchangeItemNilin',
    component: ExchangeNilinPage,
  },
  {
    path: '/exchange/item/god-herb',
    name: 'ExchangeItemGodHerb',
    component: ExchangeGodHerbPage,
  },
  {
    path: '/exchange/item/god-crystal',
    name: 'ExchangeItemGodCrystal',
    component: ExchangeGodCrystalPage,
  },
  {
    path: '/exchange/beast/xuanwu',
    name: 'ExchangeBeastXuanwu',
    component: ExchangeXuanwuPage,
  },
  {
    path: '/exchange/beast/zhuque',
    name: 'ExchangeBeastZhuque',
    component: ExchangeZhuquePage,
  },
  {
    path: '/exchange/beast/jueying',
    name: 'ExchangeBeastJueying',
    component: ExchangeJueyingPage,
  },
  {
    path: '/exchange/beast/baihu',
    name: 'ExchangeBeastBaihu',
    component: ExchangeBaihuPage,
  },
  {
    path: '/exchange/beast/businiao',
    name: 'ExchangeBeastBusiniao',
    component: ExchangeBusiniaoPage,
  },
  {
    path: '/exchange/beast/luosha',
    name: 'ExchangeBeastLuosha',
    component: ExchangeLuoshaPage,
  },
    {
      path: '/tasks/daily',
      name: 'DailyTasks',
      component: DailyTasksPage,
    },
    {
      path: '/tasks/completed',
      name: 'CompletedTasks',
      component: CompletedTasksPage,
    },
    {
      path: '/tasks/activity-gifts',
      name: 'ActivityGifts',
      component: ActivityGiftsPage,
    },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
  },
  {
    path: '/inventory',
    name: 'Inventory',
    component: InventoryPage,
  },
  {
    path: '/inventory/upgrade',
    name: 'BagUpgrade',
    component: BagUpgradePage,
  },
  {
    path: '/tower',
    name: 'Tower',
    component: TowerPage,
  },
  {
    path: '/tower/challenge',
    name: 'TowerChallenge',
    component: TowerChallengePage,
  },
  {
    path: '/tower/report',
    name: 'BattleReport',
    component: BattleReportPage,
  },
  {
    path: '/beast',
    name: 'Beast',
    component: BeastPage,
  },
    {
      path: '/beast/:id',
      name: 'BeastDetail',
      component: BeastDetailPage,
    },
    {
      path: '/beast/:id/evolve',
      name: 'BeastEvolve',
      component: BeastEvolvePage,
    },
  {
    path: '/beast/:id/skill-book',
    name: 'SkillBook',
    component: SkillBookPage,
  },
  {
    path: '/beast/:beastId/bone',
    name: 'BeastBone',
    component: BeastBonePage,
  },
  {
    path: '/beast/:beastId/bone/select',
    name: 'BoneSelect',
    component: BoneSelectPage,
  },
  {
    path: '/bone/:boneId',
    name: 'BoneDetail',
    component: BoneDetailPage,
  },
  {
    path: '/bone/:boneId/refine',
    name: 'BoneRefine',
    component: BoneRefinePage,
  },
  {
    path: '/beast/:beastId/spirit',
    name: 'BeastSpirit',
    component: BeastSpiritPage,
  },
  {
    path: '/beast/:beastId/spirit/embed/:element',
    name: 'SpiritEmbed',
    component: SpiritEmbedPage,
  },
  {
    path: '/spirit/warehouse',
    name: 'SpiritWarehouse',
    component: SpiritWarehousePage,
  },
  {
    path: '/spirit/:id',
    name: 'SpiritDetail',
    component: SpiritDetailPage,
  },
  {
    path: '/spirit/:id/refine',
    name: 'SpiritRefine',
    component: SpiritRefinePage,
  },
  {
    path: '/spirit/key-insufficient',
    name: 'SpiritKeyInsufficient',
    component: SpiritKeyInsufficientPage,
  },
  {
    path: '/mosoul',
    name: 'MoSoulOverview',
    component: MoSoulOverviewPage,
  },
  {
    path: '/mosoul/warehouse',
    name: 'MoSoulWarehouse',
    component: MoSoulWarehousePage,
  },
  {
    path: '/mosoul/hunting',
    name: 'MoSoulHunting',
    component: MoSoulHuntingPage,
  },
  {
    path: '/beast/:id/mosoul',
    name: 'MoSoul',
    component: MoSoulPage,
  },
    {
      path: '/beast/:id/mosoul/select',
      name: 'MoSoulSelect',
      component: MoSoulSelectPage,
    },
    {
      path: '/beast/:id/mosoul/:mosoulId/absorb',
      name: 'MoSoulAbsorb',
      component: MoSoulAbsorbPage,
    },
    {
      path: '/mosoul/:id',
      name: 'MoSoulDetail',
      component: MoSoulDetailPage,
    },
    {
      path: '/mosoul/:id/absorb',
      name: 'MoSoulAbsorbFromWarehouse',
      component: MoSoulAbsorbPage,
    },
        {
          path: '/dungeon/challenge/:name',
          name: 'DungeonChallenge',
          component: DungeonChallengePage,
        },
        {
          path: '/dungeon/dice-supplement',
          name: 'DiceSupplement',
          component: DiceSupplementPage,
        },
        {
          path: '/dungeon/:name/mizong',

        name: 'Mizong',
        component: MizongPage,
      },
{
          path: '/dungeon/:name/battle-result',
          name: 'DungeonBattleResult',
          component: DungeonBattleResultPage,
        },
        {
          path: '/dungeon/:name/capture',
          name: 'DungeonCapture',
          component: DungeonCapturePage,
        },
        {
          path: '/dungeon/:name/detail-report',
          name: 'DungeonDetailReport',
          component: DungeonDetailReportPage,
        },
    {
      path: '/tower/intro',
    name: 'TowerIntro',
    component: TowerIntroPage,
  },
  {
    path: '/tower/beast',
    name: 'TowerBeastDetail',
    component: TowerBeastDetailPage,
  },
  {
    path: '/tower/zhenyao',
    name: 'ZhenYao',
    component: ZhenYaoPage,
  },
  {
    path: '/tower/zhenyao/battle',
    name: 'ZhenYaoBattle',
    component: ZhenYaoBattlePage,
  },
  {
    path: '/player/profile',
    name: 'PlayerProfile',
    component: PlayerProfilePage,
  },
  {
    path: '/map',
    name: 'Map',
    component: MapPage,
  },
  {
    path: '/mail',
    name: 'Mail',
    component: MailPage,
  },
  {
    path: '/friend',
    name: 'Friend',
    component: FriendPage,
  },
  {
    path: '/friend/search',
    name: 'FriendSearch',
    component: FriendSearchPage,
  },
  {
    path: '/map/teleport',
    name: 'Teleport',
    component: TeleportPage,
  },
  {
    path: '/map/teleport-success',
    name: 'TeleportSuccess',
    component: TeleportSuccessPage,
  },
  {
    path: '/arena',
    name: 'Arena',
    component: ArenaPage,
  },
  {
    path: '/arena/battle',
    name: 'ArenaBattle',
    component: ArenaBattlePage,
  },
  {
    path: '/king',
    name: 'SummonKingChallenge',
    component: SummonKingChallengePage,
  },
  {
    path: '/king/intro',
    name: 'KingIntro',
    component: KingIntroPage,
  },
  {
    path: '/king/ranking',
    name: 'KingRanking',
    component: KingRankingPage,
  },
  {
    path: '/arena/intro',
    name: 'ArenaIntro',
    component: ArenaIntroPage,
  },
  {
    path: '/ranking',
    name: 'Ranking',
    component: RankingPage,
  },
  {
    path: '/shop',
    name: 'Shop',
    component: ShopPage,
  },
  {
    path: '/shop/item/:id',
    name: 'ShopItemDetail',
    component: ShopItemDetailPage,
  },
  {
    path: '/shop/success',
    name: 'ShopBuySuccess',
    component: ShopBuySuccessPage,
  },
  {
    path: '/battlefield',
    name: 'Battlefield',
    component: BattlefieldPage,
  },
  {
    path: '/battlefield/intro',
    name: 'BattlefieldIntro',
    component: BattlefieldIntroPage,
  },
  {
    path: '/battlefield/yesterday',
    name: 'BattlefieldYesterday',
    component: BattlefieldYesterdayPage,
  },
  {
    path: '/battlefield/battle',
    name: 'BattlefieldBattle',
    component: BattlefieldBattlePage,
  },
  {
    path: '/battlefield/kill-detail',
    name: 'BattlefieldKillDetail',
    component: () => import('@/features/battlefield/BattlefieldKillDetailPage.vue'),
  },
  {
    path: '/tasks/rewards',
    name: 'TaskRewards',
    component: TaskRewardsPage,
  },
  {
    path: '/pvp',
    name: 'PvpArena',
    component: PvpArenaPage,
  },
  {
    path: '/pvp/intro',
    name: 'PvpIntro',
    component: PvpIntroPage,
  },
  {
    path: '/pvp/report',
    name: 'PvpBattleReport',
    component: PvpBattleReportPage,
  },
  {
    path: '/player/detail',
    name: 'PlayerDetail',
    component: PlayerDetailPage,
  },
  {
    path: '/huaxian',
    name: 'HuaXian',
    component: HuaXianPage,
  },
  {
    path: '/huaxian/allocate',
    name: 'HuaXianAllocate',
    component: HuaXianAllocatePage,
  },
  {
    path: '/huaxian/allocate/:beastId',
    name: 'HuaXianAllocateDetail',
    component: HuaXianAllocateDetailPage,
  },
  {
    path: '/huaxian/upgrade',
    name: 'HuaXianUpgrade',
    component: HuaXianUpgradePage,
  },
  {
    path: '/vip',
    name: 'VipPrivilege',
    component: VipPrivilegePage,
  },
  {
    path: '/vip-test',
    name: 'VipTest',
    component: VipTestPage,
  },
  {
    path: '/sponsor',
    name: 'Sponsor',
    component: SponsorPage,
  },
  {
    path: '/sponsor/month-card',
    name: 'SponsorMonthCard',
    component: SponsorMonthCardPage,
  },
  {
    path: '/main',
    name: 'Main',
    component: MainPage,
  },
    {
      path: '/spar/report',
      name: 'SparBattleReport',
      component: SparBattleReportPage,
    },
      {
        path: '/alliance',
        name: 'Alliance',
        component: AlliancePage,
      },
      {
        path: '/alliance/hall',
        name: 'AllianceHall',
        component: AllianceHallPage,
      },
      {
        path: '/alliance/war',
        name: 'AllianceWar',
        component: AllianceWarPage,
      },
      {
        path: '/alliance/war/live',
        name: 'AllianceWarLive',
        component: AllianceWarLivePage,
      },
      {
        path: '/alliance/war/rules',
        name: 'AllianceWarRules',
        component: AllianceWarRulePage,
      },
      {
        path: '/alliance/war/honor',
        name: 'AllianceWarHonor',
        component: AllianceWarHonorPage,
      },
      {
        path: '/alliance/war/ranking',
        name: 'AllianceWarRanking',
        component: AllianceWarRankingPage,
      },
      {
        path: '/alliance/war/targets',
        name: 'AllianceWarLandList',
        component: AllianceWarLandListPage,
      },
      {
        path: '/alliance/war/land/:landId',
        name: 'AllianceWarLandDetail',
        component: AllianceWarLandDetailPage,
        props: true,
      },
      {
        path: '/alliance/war/dragon-signup',
        name: 'AllianceWarDragonSignup',
        component: AllianceWarDragonSignupPage,
      },
      {
        path: '/alliance/barracks',
        name: 'AllianceBarracks',
        component: AllianceBarracksPage,
      },
      {
        path: '/alliance/chat',
        name: 'AllianceChat',
        component: AllianceChatPage,
      },
        {
          path: '/alliance/council',
          name: 'AllianceCouncil',
          component: AllianceCouncilPage,
        },
        {
          path: '/alliance/notice',
          name: 'AllianceNotice',
          component: AllianceNoticePage,
        },
        {
          path: '/alliance/members',
          name: 'AllianceMembers',
          component: AllianceMembersPage,
        },
        {
          path: '/alliance/talent',
          name: 'AllianceTalent',
          component: AllianceTalentPage,
        },
        {
          path: '/alliance/buildings',
          name: 'AllianceBuildingUpgrade',
          component: AllianceBuildingUpgradePage,
        },
        {
          path: '/alliance/council/upgrade',
          name: 'AllianceCouncilUpgrade',
          component: AllianceCouncilUpgradePage,
        },
        {
          path: '/alliance/furnace/upgrade',
          name: 'AllianceFurnaceUpgrade',
          component: AllianceFurnaceUpgradePage,
        },
        {
          path: '/alliance/talent/upgrade',
          name: 'AllianceTalentUpgrade',
          component: AllianceTalentUpgradePage,
        },
        {
          path: '/alliance/beast/upgrade',
          name: 'AllianceBeastUpgrade',
          component: AllianceBeastUpgradePage,
        },
        {
          path: '/alliance/item/upgrade',
          name: 'AllianceItemUpgrade',
          component: AllianceItemUpgradePage,
        },
        {
          path: '/alliance/talent/research/:key',
          name: 'AllianceTalentResearch',
          component: AllianceTalentResearchPage,
        },
        {
          path: '/alliance/training-ground',
          name: 'AllianceTrainingGround',
          component: AllianceTrainingGroundPage,
        },
        {
          path: '/alliance/training-intro',
          name: 'AllianceTrainingIntro',
          component: AllianceTrainingIntroPage,
        },
        {
          path: '/alliance/rename',
          name: 'AllianceRename',
          component: AllianceRenamePage,
        },
        {
          path: '/alliance/talent/learn/:key',
          name: 'AllianceTalentLearn',
          component: AllianceTalentLearnPage,
          props: true,
        },
        {
          path: '/alliance/warehouse',
          name: 'AllianceWarehouse',
          component: AllianceWarehousePage,
        },
        {
          path: '/alliance/item-storage',
          name: 'AllianceItemStorage',
          component: AllianceItemStoragePage,
        },
        {
          path: '/alliance/donate',
          name: 'AllianceDonate',
          component: AllianceDonatePage,
        },
      {
        path: '/manor',
        name: 'manor',
        component: () => import('@/features/manor/ManorPage.vue')
      },
        {
          path: '/manor/expand',
          name: 'manorExpand',
          component: () => import('@/features/manor/ManorExpandPage.vue')
        },
        {
          path: '/manor/plant',
          name: 'manorPlant',
          component: () => import('@/features/manor/ManorPlantPage.vue')
        },
        {
          path: '/cultivation',
          name: 'Cultivation',
          component: CultivationPage
        }

]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫：测试模式下禁止访问某些页面
router.beforeEach(async (to, from, next) => {
  // 测试模式下禁止访问的路由
  const blockedPaths = ['/arena', '/king', '/pvp']
  const isBlocked = blockedPaths.some(p => to.path.startsWith(p))
  
  if (isBlocked) {
    try {
      const res = await http.get('/auth/game-config')
      if (res.data.is_test_mode) {
        alert('测试模式下该功能未开放')
        return next(false)
      }
    } catch (e) {
      console.error('获取游戏配置失败', e)
    }
  }
  next()
})

export default router
