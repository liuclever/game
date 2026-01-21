from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import Optional, List, Dict, Tuple
from domain.entities.alliance import (
    Alliance,
    AllianceMember,
    AllianceArmyAssignment,
    AllianceChatMessage,
    AllianceTalentResearch,
    PlayerTalentLevel,
    AllianceBeastStorage,
    AllianceItemStorage,
    AllianceTrainingRoom,
    AllianceTrainingParticipant,
    AllianceActivity,
    AllianceBuilding,
)
from domain.entities.alliance_registration import AllianceRegistration
from domain.entities.alliance_battle import (
    AllianceArmySignup,
    AllianceLandBattle,
    AllianceLandBattleRound,
    AllianceLandBattleDuel,
)

class IAllianceRepo(ABC):
    @abstractmethod
    def create_alliance(self, alliance: Alliance) -> int:
        """创建联盟"""
        pass

    @abstractmethod
    def get_alliance_by_id(self, alliance_id: int) -> Optional[Alliance]:
        """通过ID获取联盟"""
        pass

    @abstractmethod
    def get_alliance_by_name(self, name: str) -> Optional[Alliance]:
        """通过名字获取联盟"""
        pass

    @abstractmethod
    def list_alliances(self, keyword: Optional[str], limit: int, offset: int) -> List[Dict]:
        """联盟大厅：分页获取联盟列表（包含成员数等）"""
        pass

    @abstractmethod
    def count_alliances(self, keyword: Optional[str]) -> int:
        """联盟大厅：统计联盟总数（支持关键字筛选）"""
        pass

    @abstractmethod
    def count_members(self, alliance_id: int) -> int:
        """统计联盟成员数量"""
        pass

    @abstractmethod
    def add_member(self, member: AllianceMember) -> None:
        """添加成员"""
        pass

    @abstractmethod
    def get_member(self, user_id: int) -> Optional[AllianceMember]:
        """获取玩家所在的联盟成员信息"""
        pass

    @abstractmethod
    def get_alliance_members(self, alliance_id: int) -> List[AllianceMember]:
        """获取联盟所有成员"""
        pass

    @abstractmethod
    def get_members_by_army(self, alliance_id: int, army_type: int) -> List[AllianceMember]:
        """根据阵营获取成员"""
        pass

    @abstractmethod
    def update_member_role(self, user_id: int, role: int) -> None:
        """调整成员职位"""
        pass

    @abstractmethod
    def update_member_army(self, user_id: int, army_type: int) -> None:
        """更新成员阵营"""
        pass

    @abstractmethod
    def remove_member(self, user_id: int) -> None:
        """将成员移出联盟"""
        pass

    @abstractmethod
    def record_quit_time(self, user_id: int, quit_at: datetime) -> None:
        """记录玩家退出联盟的时间"""
        pass

    @abstractmethod
    def get_quit_time(self, user_id: int) -> Optional[datetime]:
        """获取玩家最后一次退出联盟的时间，如果从未退出过则返回None"""
        pass

    # 兵营相关
    @abstractmethod
    def get_army_assignments(self, alliance_id: int) -> List[AllianceArmyAssignment]:
        pass

    @abstractmethod
    def upsert_army_assignment(self, alliance_id: int, user_id: int, army: str) -> None:
        pass

    @abstractmethod
    def update_notice(self, alliance_id: int, notice: str) -> None:
        """更新联盟公告"""
        pass

    @abstractmethod
    def update_alliance_name(self, alliance_id: int, name: str) -> None:
        """更新联盟名字"""
        pass

    @abstractmethod
    def update_alliance_level(self, alliance_id: int, level: int) -> None:
        """更新联盟等级"""
        pass

    @abstractmethod
    def add_chat_message(self, message: AllianceChatMessage) -> int:
        """添加聊天消息"""
        pass

    @abstractmethod
    def get_chat_messages(self, alliance_id: int, limit: int = 50) -> List[AllianceChatMessage]:
        """获取联盟聊天消息"""
        pass

    # === 联盟动态 ===
    @abstractmethod
    def add_activity(self, activity: AllianceActivity) -> int:
        """新增联盟动态事件"""
        pass

    @abstractmethod
    def list_activities(self, alliance_id: int, limit: int = 20) -> List[AllianceActivity]:
        """获取最近的联盟动态"""
        pass

    @abstractmethod
    def get_alliance_talent_research(self, alliance_id: int) -> List[AllianceTalentResearch]:
        """获取联盟各天赋的研究等级"""
        pass

    @abstractmethod
    def update_alliance_talent_research(self, alliance_id: int, talent_key: str, level: int) -> None:
        """更新联盟某个天赋的研究等级"""
        pass

    @abstractmethod
    def get_player_talent_levels(self, user_id: int) -> List[PlayerTalentLevel]:
        """获取玩家在联盟内的天赋等级"""
        pass

    @abstractmethod
    def update_player_talent_level(self, user_id: int, talent_key: str, level: int) -> None:
        """更新玩家某项天赋等级"""
        pass

    @abstractmethod
    def get_beast_storage(self, alliance_id: int) -> List[AllianceBeastStorage]:
        """获取联盟幻兽室记录"""
        pass

    @abstractmethod
    def add_beast_storage(self, storage: AllianceBeastStorage) -> int:
        """新增幻兽寄存记录"""
        pass

    @abstractmethod
    def remove_beast_storage(self, storage_id: int) -> None:
        """移除幻兽寄存记录"""
        pass

    @abstractmethod
    def get_beast_storage_by_id(self, storage_id: int) -> Optional[AllianceBeastStorage]:
        """根据寄存记录ID获取"""
        pass

    @abstractmethod
    def get_beast_storage_by_beast(self, beast_id: int) -> Optional[AllianceBeastStorage]:
        """根据幻兽ID获取寄存记录"""
        pass

    @abstractmethod
    def count_beast_storage(self, alliance_id: int) -> int:
        """统计联盟幻兽室占用数量"""
        pass

    @abstractmethod
    def get_beast_storage_by_owner(self, owner_user_id: int) -> List[AllianceBeastStorage]:
        """根据玩家获取其寄存记录"""
        pass

    # === 道具寄存仓库 ===
    @abstractmethod
    def get_item_storage(self, alliance_id: int) -> List[AllianceItemStorage]:
        """获取联盟寄存仓库记录"""
        pass

    @abstractmethod
    def get_item_storage_slots(self, alliance_id: int, owner_user_id: int, item_id: int) -> List[AllianceItemStorage]:
        """获取指定玩家某物品的寄存槽位"""
        pass

    @abstractmethod
    def add_item_storage(self, storage: AllianceItemStorage) -> int:
        """新增寄存槽位"""
        pass

    @abstractmethod
    def update_item_storage_quantity(self, storage_id: int, quantity: int) -> None:
        """更新寄存槽位数量"""
        pass

    @abstractmethod
    def remove_item_storage(self, storage_id: int) -> None:
        """删除寄存槽位"""
        pass

    @abstractmethod
    def count_item_storage(self, alliance_id: int) -> int:
        """统计寄存槽位数量"""
        pass

    @abstractmethod
    def get_item_storage_by_owner(self, alliance_id: int, owner_user_id: int) -> List[AllianceItemStorage]:
        """获取玩家自己寄存的道具"""
        pass

    @abstractmethod
    def get_item_storage_by_id(self, storage_id: int) -> Optional[AllianceItemStorage]:
        """根据寄存记录ID获取道具"""
        pass

    @abstractmethod
    def update_alliance_crystals(self, alliance_id: int, delta: int) -> None:
        """调整联盟焚火晶数量"""
        pass

    @abstractmethod
    def update_alliance_resources(self, alliance_id: int, funds_delta: int = 0, prosperity_delta: int = 0) -> None:
        """调整联盟资金与繁荣度"""
        pass

    @abstractmethod
    def update_member_contribution(self, user_id: int, delta: int) -> None:
        """调整成员贡献"""
        pass

    # === 战功 / 荣誉 ===
    @abstractmethod
    def get_alliance_war_points(self, alliance_id: int) -> Tuple[int, int]:
        """返回联盟当前战功与历史累计战功"""
        pass

    @abstractmethod
    def update_alliance_war_points(self, alliance_id: int, delta: int) -> None:
        """调节联盟战功，delta 可为负；历史战功仅在 delta>0 时累加"""
        pass

    @abstractmethod
    def list_top_alliance_names_by_war_honor_history(self, limit: int) -> List[str]:
        """按盟战榜（历史累计战功 war_honor_history）倒序取前 N 个联盟名字。"""
        pass

    @abstractmethod
    def get_active_honor_effects(self, alliance_id: int) -> List[Dict]:
        """列出联盟当前未过期的战功兑换效果"""
        pass

    @abstractmethod
    def insert_honor_effect(
        self,
        alliance_id: int,
        effect_key: str,
        effect_type: str,
        cost: int,
        started_at: datetime,
        expires_at: datetime,
        created_by: int,
    ) -> int:
        """写入战功兑换记录，返回新记录ID"""
        pass

    @abstractmethod
    def increment_alliance_war_score(self, alliance_id: int, season_key: str, delta: int = 1) -> None:
        """为指定联盟的自然月战功累加"""
        pass

    @abstractmethod
    def list_alliance_war_leaderboard(self, since: datetime, limit: int, offset: int) -> List[Dict]:
        """按时间窗口分页列出联盟战功排行"""
        pass

    @abstractmethod
    def count_alliance_war_leaderboard(self, since: datetime) -> int:
        """统计参与排行的联盟数量"""
        pass

    @abstractmethod
    def get_alliance_war_leaderboard_entry(self, alliance_id: int, since: datetime) -> Optional[Dict]:
        """获取指定联盟在战功榜中的数据及排名"""
        pass

    # === 盟战签到 ===
    @abstractmethod
    def has_war_checkin(self, alliance_id: int, user_id: int, war_phase: str, war_weekday: int, checkin_date: date) -> bool:
        """检查是否已签到"""
        pass

    @abstractmethod
    def add_war_checkin(self, alliance_id: int, user_id: int, war_phase: str, war_weekday: int, checkin_date: date, copper_reward: int) -> int:
        """添加盟战签到记录"""
        pass

    # === 盟战战绩 ===
    @abstractmethod
    def add_war_battle_record(self, alliance_id: int, opponent_alliance_id: int, land_id: int, army_type: str, war_phase: str, war_date: date, battle_result: str, honor_gained: int, battle_id: Optional[int] = None) -> int:
        """添加盟战战绩记录"""
        pass

    @abstractmethod
    def list_war_battle_records(self, alliance_id: int, limit: int = 50) -> List[Dict]:
        """获取联盟战绩列表"""
        pass

    # === 战功兑换 ===
    @abstractmethod
    def add_war_honor_exchange(self, alliance_id: int, user_id: int, exchange_type: str, honor_cost: int, item_id: int, item_name: str, item_quantity: int) -> int:
        """添加战功兑换记录"""
        pass

    @abstractmethod
    def list_war_honor_exchanges(self, alliance_id: int, limit: int = 50) -> List[Dict]:
        """获取战功兑换记录列表"""
        pass

    # === 赛季奖励 ===
    @abstractmethod
    def get_season_reward(self, alliance_id: int, season_key: str) -> Optional[Dict]:
        """获取赛季奖励记录"""
        pass

    @abstractmethod
    def add_season_reward(self, alliance_id: int, season_key: str, rank: int, copper_reward: int, items_json: str) -> int:
        """添加赛季奖励记录"""
        pass

    @abstractmethod
    def distribute_season_rewards(self, season_key: str) -> List[Dict]:
        """发放赛季奖励（返回发放记录）"""
        pass

    # === 土地占领 ===
    @abstractmethod
    def get_land_occupation(self, land_id: int) -> Optional[Dict]:
        """获取土地占领情况"""
        pass

    @abstractmethod
    def set_land_occupation(self, land_id: int, alliance_id: int, war_phase: str, war_date: date) -> int:
        """设置土地占领"""
        pass

    # === 土地报名 ===
    @abstractmethod
    def get_land_registration(self, alliance_id: int, land_id: int) -> Optional[AllianceRegistration]:
        """获取联盟针对某块土地的报名记录"""
        pass

    @abstractmethod
    def save_land_registration(self, registration: AllianceRegistration) -> int:
        """创建或更新联盟土地报名记录"""
        pass

    @abstractmethod
    def get_active_land_registration_by_range(
        self, alliance_id: int, land_ids: List[int]
    ) -> Optional[AllianceRegistration]:
        """获取联盟在指定土地集合中的任意活动报名"""
        pass

    @abstractmethod
    def list_land_registrations_by_land(
        self, land_id: int, statuses: Optional[List[int]] = None
    ) -> List[AllianceRegistration]:
        """获取指定土地的所有报名记录，可按状态过滤"""
        pass

    @abstractmethod
    def get_land_registration_by_id(self, registration_id: int) -> Optional[AllianceRegistration]:
        """根据报名ID获取记录"""
        pass

    # === 军团报名玩家 ===
    @abstractmethod
    def add_army_signups(self, signups: List[AllianceArmySignup]) -> None:
        """批量插入军团报名玩家"""
        pass

    @abstractmethod
    def list_army_signups(self, registration_id: int) -> List[AllianceArmySignup]:
        """按报名记录获取所有军团玩家（按报名顺序排序）"""
        pass

    @abstractmethod
    def update_army_signup_state(
        self, signup_id: int, status: int, hp_state: Optional[dict]
    ) -> None:
        """更新军团玩家的状态和血量快照"""
        pass

    # === 土地战斗 ===
    @abstractmethod
    def create_land_battle(self, battle: AllianceLandBattle) -> int:
        """创建一场土地战斗"""
        pass

    @abstractmethod
    def update_land_battle(self, battle: AllianceLandBattle) -> None:
        """更新土地战斗状态"""
        pass

    @abstractmethod
    def get_land_battle_by_id(self, battle_id: int) -> Optional[AllianceLandBattle]:
        """根据ID获取土地战斗"""
        pass

    @abstractmethod
    def get_active_battle_by_land(self, land_id: int) -> Optional[AllianceLandBattle]:
        """获取土地上进行中的战斗"""
        pass

    @abstractmethod
    def list_alliance_battles(self, alliance_id: int) -> List[AllianceLandBattle]:
        """返回该联盟参与的所有战斗（包含左右两侧）"""
        pass

    # === 战斗轮次 ===
    @abstractmethod
    def create_battle_round(self, battle_round: AllianceLandBattleRound) -> int:
        """创建战斗轮次"""
        pass

    @abstractmethod
    def update_battle_round(self, battle_round: AllianceLandBattleRound) -> None:
        """更新战斗轮次信息"""
        pass

    @abstractmethod
    def list_battle_rounds(self, battle_id: int) -> List[AllianceLandBattleRound]:
        """列出战斗的全部轮次"""
        pass

    @abstractmethod
    def get_battle_round_by_id(self, round_id: int) -> Optional[AllianceLandBattleRound]:
        """根据ID获取战斗轮次"""
        pass

    # === 战斗对战日志 ===
    @abstractmethod
    def add_battle_duels(self, duels: List[AllianceLandBattleDuel]) -> None:
        """批量写入 1v1 对战日志"""
        pass

    @abstractmethod
    def list_duels_by_round(self, round_id: int) -> List[AllianceLandBattleDuel]:
        """获取某轮的全部对战日志"""
        pass

    # === 建筑等级 ===
    @abstractmethod
    def get_alliance_buildings(self, alliance_id: int) -> List[AllianceBuilding]:
        """获取联盟所有建筑等级"""
        pass

    @abstractmethod
    def get_alliance_building(self, alliance_id: int, building_key: str) -> Optional[AllianceBuilding]:
        """获取联盟单个建筑等级"""
        pass

    @abstractmethod
    def set_alliance_building_level(self, alliance_id: int, building_key: str, level: int) -> None:
        """更新或创建建筑等级"""
        pass

    # === 修行广场 ===
    @abstractmethod
    def create_training_room(self, room: AllianceTrainingRoom) -> int:
        """创建修行房间"""
        pass

    @abstractmethod
    def get_training_rooms(self, alliance_id: int) -> List[AllianceTrainingRoom]:
        """获取联盟当前所有修行房间"""
        pass

    @abstractmethod
    def get_training_room_by_id(self, room_id: int) -> Optional[AllianceTrainingRoom]:
        """根据房间ID获取修行房间"""
        pass

    @abstractmethod
    def add_training_participant(self, participant: AllianceTrainingParticipant) -> int:
        """添加修行参与者"""
        pass

    @abstractmethod
    def get_training_participant(self, participant_id: int) -> Optional[AllianceTrainingParticipant]:
        """根据参与记录ID获取"""
        pass

    @abstractmethod
    def get_training_participant_by_room(self, room_id: int, user_id: int) -> Optional[AllianceTrainingParticipant]:
        """根据房间与玩家获取参与记录"""
        pass

    @abstractmethod
    def get_training_participants(self, room_id: int) -> List[AllianceTrainingParticipant]:
        """获取房间参与者"""
        pass

    @abstractmethod
    def get_training_participation_today(self, alliance_id: int, user_id: int) -> Optional[AllianceTrainingParticipant]:
        """获取玩家当日的修行记录"""
        pass

    @abstractmethod
    def mark_training_claimed(self, participant_id: int, reward_amount: int) -> None:
        """标记修行奖励已领取"""
        pass

    @abstractmethod
    def update_training_room_status(self, room_id: int, status: str) -> None:
        """更新修行房间状态"""
        pass

    @abstractmethod
    def has_claimed_fire_ore_today(self, user_id: int) -> bool:
        """检查玩家今日是否已领取火能原石"""
        pass

    @abstractmethod
    def record_fire_ore_claim(self, user_id: int) -> bool:
        """记录火能原石领取，返回是否更新成功（如果今日已领取则返回False）"""
        pass
