import json
from pathlib import Path
from datetime import datetime, timedelta, date, timezone
from typing import Optional, List, Dict, Tuple, Any
from collections import defaultdict
from domain.entities.alliance import (
    Alliance,
    AllianceMember,
    AllianceArmyAssignment,
    AllianceChatMessage,
    AllianceBeastStorage,
    AllianceItemStorage,
    AllianceTrainingRoom,
    AllianceTrainingParticipant,
    AllianceActivity,
)
from domain.entities.alliance_registration import (
    AllianceRegistration,
    STATUS_REGISTERED,
    STATUS_PENDING,
    STATUS_CONFIRMED,
    STATUS_IN_BATTLE,
    STATUS_VICTOR,
    STATUS_ELIMINATED,
)
from domain.entities.item import PlayerBag
from domain.repositories.alliance_repo import IAllianceRepo
from domain.repositories.player_repo import IPlayerRepo
from domain.repositories.beast_repo import IBeastRepo
from application.services.inventory_service import InventoryService, InventoryError
from domain.rules.alliance_rules import AllianceRules

class AllianceService:
    # 盟战时间规则
    # 第一次：周一0:00-周三24:00（报名签到：周一0:00-周三20:00，对战：周三20:00-22:00，结果展示：周三22:00-24:00）
    # 第二次：周四0:00-周六24:00（报名签到：周四0:00-周六20:00，对战：周六20:00-22:00，结果展示：周六22:00-24:00）
    # 周日休战
    WAR_FIRST_START_WEEKDAY = 0  # 周一
    WAR_FIRST_END_WEEKDAY = 2    # 周三
    WAR_SECOND_START_WEEKDAY = 3  # 周四
    WAR_SECOND_END_WEEKDAY = 5    # 周六
    WAR_BATTLE_START_HOUR = 20
    WAR_BATTLE_END_HOUR = 22
    WAR_RESULT_END_HOUR = 24

    ARMY_LEVEL_THRESHOLD = 40  # 40级以上飞龙军，40级及以下伏虎军
    ARMY_DRAGON = 1
    ARMY_TIGER = 2
    # 飞龙军只能选择土地，伏虎军只能选择据点
    DRAGON_ONLY_LANDS = {1, 2}  # 土地：迷雾城1号土地、飞龙港1号土地
    TIGER_ONLY_LANDS = {3, 4}   # 据点：幻灵镇1号据点、定老城1号据点
    HONOR_EFFECT_DURATION_HOURS = 24
    WAR_LANDS = {
        1: {
            "land_name": "迷雾城1号土地",
            "land_type": "land",  # 土地
            "daily_reward_copper": 10000,  # 联盟占领后，盟员每天可获得10000铜钱
            "buffs": [
                "联盟占领后的奖励：联盟内的盟员每天可获得10000铜钱"
            ],
        },
        2: {
            "land_name": "飞龙港1号土地",
            "land_type": "land",  # 土地
            "daily_reward_copper": 10000,  # 联盟占领后，盟员每天可获得10000铜钱
            "buffs": [
                "联盟占领后的奖励：联盟内的盟员每天可获得10000铜钱"
            ],
        },
        3: {
            "land_name": "幻灵镇1号据点",
            "land_type": "stronghold",  # 据点
            "daily_reward_copper": 5000,  # 联盟占领后的奖励：联盟内的盟员每天可获得5000铜钱
            "buffs": [
                "联盟占领后的奖励：联盟内的盟员每天可获得5000铜钱"
            ],
        },
        4: {
            "land_name": "定老城1号据点",
            "land_type": "stronghold",  # 据点
            "daily_reward_copper": 5000,  # 联盟占领后的奖励：联盟内的盟员每天可获得5000铜钱
            "buffs": [
                "联盟占领后的奖励：联盟内的盟员每天可获得5000铜钱"
            ],
        },
    }
    # 盟战签到奖励
    WAR_CHECKIN_REWARD_COPPER = 30000  # 签到获得30000铜钱
    # 战功兑换规则
    WAR_HONOR_EXCHANGE_RULES = {
        "fire_crystal": {"honor": 2, "item_id": 6102, "item_name": "焚火晶", "quantity": 1, "type": "item"},  # 2战功=1焚火晶
        "gold_bag": {"honor": 4, "item_id": 6005, "item_name": "金袋", "quantity": 1, "type": "item"},  # 4战功=1金袋
        "prosperity": {"honor": 6, "prosperity": 1000, "item_name": "繁荣度", "quantity": 1000, "type": "prosperity"},  # 6战功=1000繁荣度
    }
    # 赛季奖励
    SEASON_REWARD_RULES = {
        1: {"copper": 1_000_000, "items": [{"item_id": 6019, "item_name": "追魂法宝", "quantity": 1}]},  # 第一名：100w铜钱，1追魂法宝
        2: {"copper": 700_000, "items": []},  # 第二名：70w铜钱
        3: {"copper": 400_000, "items": []},  # 第三名：40w铜钱
    }
    def __init__(
        self,
        alliance_repo: IAllianceRepo,
        player_repo: IPlayerRepo,
        inventory_service: InventoryService,
        beast_repo: IBeastRepo,
    ):
        self.alliance_repo = alliance_repo
        self.player_repo = player_repo
        self.inventory_service = inventory_service
        self.beast_repo = beast_repo
        self._honor_effects_cache: List[Dict] | None = None
        self._honor_effects_map: Dict[str, Dict] | None = None

    def create_alliance(self, user_id: int, alliance_name: str) -> dict:
        """创建联盟逻辑"""
        # 1. 获取玩家
        player = self.player_repo.get_by_id(user_id)
        if not player:
            return {"ok": False, "error": "玩家不存在"}

        # 2. 检查是否已经有联盟
        if self.alliance_repo.get_member(user_id):
            return {"ok": False, "error": "你已经在一个联盟中了"}

        # 3. 检查名字是否占用
        if self.alliance_repo.get_alliance_by_name(alliance_name):
            return {"ok": False, "error": "联盟名字已被占用"}

        # 4. 获取创建证明数量
        token_count = self.inventory_service.get_item_count(
            user_id, 
            AllianceRules.LEAGUE_LEADER_TOKEN_ID
        )

        # 5. 校验规则
        can_create, error = AllianceRules.can_create_alliance(player, token_count > 0)
        if not can_create:
            return {"ok": False, "error": error}

        # 6. 扣除物品
        try:
            self.inventory_service.remove_item(
                user_id, 
                AllianceRules.LEAGUE_LEADER_TOKEN_ID, 
                1
            )
        except Exception as e:
            return {"ok": False, "error": f"消耗盟主证明失败: {str(e)}"}

        # 7. 创建联盟
        new_alliance = Alliance(
            name=alliance_name,
            leader_id=user_id
        )
        alliance_id = self.alliance_repo.create_alliance(new_alliance)
        
        # 8. 添加成员关系（盟主）
        # 根据等级自动分配军队：40级以上飞龙军，40级及以下伏虎军
        army_type = self._determine_army_type(player.level or 0)
        leader_member = AllianceMember(
            alliance_id=alliance_id,
            user_id=user_id,
            role=1  # 盟主
        )
        leader_member.army_type = army_type
        self.alliance_repo.add_member(leader_member)
        # 更新军队类型
        self.alliance_repo.update_member_army(user_id, army_type)
        for building_key in AllianceRules.BUILDING_KEYS:
            self.alliance_repo.set_alliance_building_level(alliance_id, building_key, 1)
        # 创建联盟时不记录"加入联盟"动态，因为创建者不是"加入"，而是"创建"
        # 如果需要记录创建动态，可以使用 event_type="create"

        return {
            "ok": True, 
            "message": "联盟创建成功！", 
            "alliance_id": alliance_id
        }

    def list_alliances(self, user_id: int, keyword: Optional[str] = None, page: int = 1, size: int = 10) -> dict:
        if not user_id:
            return {"ok": False, "error": "请先登录"}

        try:
            page_i = int(page or 1)
        except (TypeError, ValueError):
            page_i = 1
        try:
            size_i = int(size or 10)
        except (TypeError, ValueError):
            size_i = 10

        page_i = max(1, page_i)
        size_i = max(1, min(50, size_i))
        offset = (page_i - 1) * size_i

        total = self.alliance_repo.count_alliances(keyword)
        rows = self.alliance_repo.list_alliances(keyword, limit=size_i, offset=offset)

        self_member = self.alliance_repo.get_member(user_id)
        already_in_alliance = self_member is not None

        alliances = []
        for r in rows:
            alliance_id = int(r.get("id", 0) or 0)
            level = int(r.get("level", 1) or 1)
            member_count = int(r.get("member_count", 0) or 0)
            capacity = AllianceRules.member_capacity(level)
            can_join = (not already_in_alliance) and (member_count < capacity)
            alliances.append({
                "id": alliance_id,
                "name": r.get("name") or "",
                "level": level,
                "leader_id": int(r.get("leader_id", 0) or 0),
                "notice": r.get("notice") or "",
                "member_count": member_count,
                "member_capacity": capacity,
                "can_join": can_join,
            })

        total_pages = max(1, (int(total) + size_i - 1) // size_i)
        return {
            "ok": True,
            "alliances": alliances,
            "page": page_i,
            "size": size_i,
            "total": int(total),
            "total_pages": total_pages,
            "already_in_alliance": already_in_alliance,
        }

    def join_alliance(self, user_id: int, alliance_id: int) -> dict:
        if not user_id:
            return {"ok": False, "error": "请先登录"}
        try:
            alliance_id = int(alliance_id)
        except (TypeError, ValueError):
            alliance_id = 0
        if not alliance_id:
            return {"ok": False, "error": "缺少联盟ID"}

        player = self.player_repo.get_by_id(user_id)
        if not player:
            return {"ok": False, "error": "玩家不存在"}

        if self.alliance_repo.get_member(user_id):
            return {"ok": False, "error": "你已经在一个联盟中了"}

        # 检查48小时加入限制
        quit_time = self.alliance_repo.get_quit_time(user_id)
        if quit_time:
            # pymysql通常返回datetime对象，但为了兼容性也处理字符串格式
            if isinstance(quit_time, str):
                try:
                    # 尝试解析ISO格式的datetime字符串
                    quit_time = datetime.fromisoformat(quit_time.replace('Z', '+00:00').replace('+00:00', ''))
                except (ValueError, AttributeError):
                    # 如果解析失败，假设已经过了48小时，允许加入
                    quit_time = None
            
            if quit_time and isinstance(quit_time, datetime):
                # 计算时间差
                now = datetime.utcnow()
                # 如果quit_time有时区信息，转换为naive UTC时间
                if quit_time.tzinfo is not None:
                    quit_time = quit_time.replace(tzinfo=None)
                
                time_since_quit = now - quit_time
                hours_since_quit = time_since_quit.total_seconds() / 3600
                
                if hours_since_quit < 48:
                    remaining_hours = int(48 - hours_since_quit)
                    remaining_minutes = int((48 - hours_since_quit) * 60 % 60)
                    return {
                        "ok": False,
                        "error": f"退出联盟后需要等待48小时才能再次加入，还需等待{remaining_hours}小时{remaining_minutes}分钟"
                    }

        alliance = self.alliance_repo.get_alliance_by_id(alliance_id)
        if not alliance:
            return {"ok": False, "error": "联盟不存在"}

        member_count = self.alliance_repo.count_members(alliance_id)
        capacity = AllianceRules.member_capacity(alliance.level or 1)
        if member_count >= capacity:
            return {"ok": False, "error": "联盟成员已满"}

        # 根据等级自动分配军队：40级以上飞龙军，40级及以下伏虎军
        army_type = self._determine_army_type(player.level or 0)
        
        member = AllianceMember(
            alliance_id=alliance_id,
            user_id=user_id,
            role=AllianceRules.ROLE_MEMBER,
        )
        member.army_type = army_type
        self.alliance_repo.add_member(member)
        # 更新军队类型
        self.alliance_repo.update_member_army(user_id, army_type)

        self._record_activity(
            alliance_id=alliance_id,
            event_type="join",
            actor_user_id=user_id,
            actor_name=self._player_display_name(player),
        )

        return {"ok": True, "message": "加入联盟成功"}

    def get_my_alliance(self, user_id: int) -> dict:
        """获取玩家当前联盟信息"""
        try:
            member = self.alliance_repo.get_member(user_id)
            if not member:
                return {"ok": False, "error": "未加入联盟"}
            
            alliance = self.alliance_repo.get_alliance_by_id(member.alliance_id)
            if not alliance:
                # 联盟不存在，但成员记录还在，说明联盟已被解散但成员记录未清理
                # 清理孤儿成员记录，并返回"未加入联盟"
                try:
                    self.alliance_repo.remove_member(user_id)
                except Exception:
                    pass  # 清理失败不影响返回结果
                return {"ok": False, "error": "未加入联盟"}
            
            # 同步当前成员的军队类型（如果等级变化导致军队类型变化）
            try:
                player = self.player_repo.get_by_id(user_id)
                if player:
                    self._sync_member_army(member, player.level or 0)
            except Exception as e:
                # 同步军队类型失败不影响主要功能
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"同步成员 {user_id} 军队类型时出错: {e}")
            
            try:
                members = self.alliance_repo.get_alliance_members(alliance.id)
                member_capacity = AllianceRules.member_capacity(alliance.level or 1)
            except Exception as e:
                # 获取成员列表失败，使用默认值
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"获取联盟 {alliance.id} 成员列表时出错: {e}")
                members = []
                member_capacity = AllianceRules.member_capacity(alliance.level or 1)
            
            # 检查火能原石领取状态
            try:
                fire_ore_claimed_today = self.alliance_repo.has_claimed_fire_ore_today(user_id)
                # 确保返回布尔值
                fire_ore_claimed_today = bool(fire_ore_claimed_today)
            except Exception as e:
                # 检查火能原石状态失败，默认为未领取
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"检查用户 {user_id} 火能原石领取状态时出错: {e}")
                fire_ore_claimed_today = False
            
            return {
                "ok": True,
                "alliance": alliance,
                "member_info": member,
                "member_count": len(members),
                "member_capacity": member_capacity,
                "fire_ore_claimed_today": fire_ore_claimed_today,
            }
        except Exception as e:
            # 捕获所有未预期的异常，返回友好的错误信息
            import logging
            logger = logging.getLogger(__name__)
            logger.exception(f"获取用户 {user_id} 联盟信息时出错: {e}")
            return {"ok": False, "error": f"获取联盟信息失败: {str(e)}"}

    def get_alliance_notice(self, user_id: int) -> dict:
        """获取联盟公告"""
        member = self.alliance_repo.get_member(user_id)
        if not member:
            return {"ok": False, "error": "未加入联盟"}

        alliance = self.alliance_repo.get_alliance_by_id(member.alliance_id)
        if not alliance:
            # 联盟不存在，但成员记录还在，说明联盟已被解散但成员记录未清理
            try:
                self.alliance_repo.remove_member(user_id)
            except Exception:
                pass
            return {"ok": False, "error": "未加入联盟"}

        return {
            "ok": True,
            "alliance_id": alliance.id,
            "alliance_name": alliance.name,
            "notice": alliance.notice or "",
            "can_edit": AllianceRules.can_edit_notice(member.role)
        }

    def update_alliance_notice(self, user_id: int, notice: str) -> dict:
        """更新联盟公告"""
        member = self.alliance_repo.get_member(user_id)
        if not member:
            return {"ok": False, "error": "未加入联盟"}

        if not AllianceRules.can_edit_notice(member.role):
            return {"ok": False, "error": "只有管理职位可以修改公告"}

        content = (notice or "").strip()
        if not content:
            return {"ok": False, "error": "公告不能为空"}

        if len(content) > 35:
            return {"ok": False, "error": "公告限制为35个字以内"}

        self.alliance_repo.update_notice(member.alliance_id, content)

        return {"ok": True, "notice": content}

    def rename_alliance(self, user_id: int, new_name: str) -> dict:
        member = self.alliance_repo.get_member(user_id)
        if not member:
            return {"ok": False, "error": "未加入联盟"}
        if member.role != AllianceRules.ROLE_LEADER:
            return {"ok": False, "error": "只有盟主可以修改联盟名称"}

        alliance = self.alliance_repo.get_alliance_by_id(member.alliance_id)
        if not alliance:
            # 联盟不存在，但成员记录还在，说明联盟已被解散但成员记录未清理
            try:
                self.alliance_repo.remove_member(user_id)
            except Exception:
                pass
            return {"ok": False, "error": "未加入联盟"}

        validation_error = AllianceRules.validate_alliance_name(new_name)
        if validation_error:
            return {"ok": False, "error": validation_error}

        cleaned_name = new_name.strip()
        if cleaned_name == alliance.name:
            return {"ok": False, "error": "新名称与当前名称相同"}
        if self.alliance_repo.get_alliance_by_name(cleaned_name):
            return {"ok": False, "error": "该名称已被其他联盟占用"}

        leader = self.player_repo.get_by_id(user_id)
        if not leader:
            return {"ok": False, "error": "玩家不存在"}

        cost = AllianceRules.RENAME_COST_YUANBAO
        if leader.yuanbao < cost:
            return {"ok": False, "error": f"元宝不足，修改名称需要{cost}元宝"}

        leader.yuanbao -= cost
        self.player_repo.save(leader)

        self.alliance_repo.update_alliance_name(alliance.id, cleaned_name)
        alliance.name = cleaned_name

        self._record_activity(
            alliance_id=alliance.id,
            event_type="rename",
            actor_user_id=user_id,
            actor_name=self._member_display_name(member),
            target_name=cleaned_name,
            item_name="元宝",
            item_quantity=cost,
        )

        return {
            "ok": True,
            "message": "联盟名称修改成功",
            "alliance": {
                "id": alliance.id,
                "name": cleaned_name,
            },
            "yuanbao": leader.yuanbao,
            "cost": cost,
        }

    def get_alliance_members_info(self, user_id: int, sort: str = "role") -> dict:
        member = self.alliance_repo.get_member(user_id)
        if not member:
            return {"ok": False, "error": "未加入联盟"}

        alliance = self.alliance_repo.get_alliance_by_id(member.alliance_id)
        if not alliance:
            # 联盟不存在，但成员记录还在，说明联盟已被解散但成员记录未清理
            try:
                self.alliance_repo.remove_member(user_id)
            except Exception:
                pass
            return {"ok": False, "error": "未加入联盟"}

        members = self.alliance_repo.get_alliance_members(member.alliance_id)
        
        # 同步成员军队类型（如果等级变化导致军队类型变化）
        for m in members:
            player = self.player_repo.get_by_id(m.user_id)
            if player:
                self._sync_member_army(m, player.level or 0)
        
        sort_key = self._get_sort_key(sort)
        sorted_members = sorted(members, key=sort_key)

        def display_name(m: AllianceMember) -> str:
            return m.nickname or f"玩家{m.user_id}"

        leader_names = [display_name(m) for m in members if m.role == AllianceRules.ROLE_LEADER]
        vice_names = [display_name(m) for m in members if m.role == AllianceRules.ROLE_VICE_LEADER]
        elder_names = [display_name(m) for m in members if m.role == AllianceRules.ROLE_ELDER]

        member_rows = []
        for idx, m in enumerate(sorted_members, start=1):
            member_rows.append({
                "index": idx,
                "user_id": m.user_id,
                "nickname": display_name(m),
                "level": m.level or 1,
                "role": m.role,
                "role_label": AllianceRules.role_label(m.role),
                "contribution": m.contribution,
                "army_type": m.army_type or 0,
                "team_type": getattr(m, 'team_type', 0) or 0,
                "is_self": m.user_id == user_id,
                "can_kick": self._can_kick(member, m),
                "can_assign_role": self._can_assign_role(member, m)
            })

        return {
            "ok": True,
            "sort": sort if sort in {"role", "contribution", "level"} else "role",
            "leader_name": leader_names[0] if leader_names else "",
            "vice_leaders": vice_names,
            "elders": elder_names,
            "current_role": member.role,
            "can_manage_roles": AllianceRules.can_manage_roles(member.role),
            "members": member_rows,
            "role_options": [
                {"value": AllianceRules.ROLE_MEMBER, "label": AllianceRules.role_label(AllianceRules.ROLE_MEMBER)},
                {"value": AllianceRules.ROLE_VICE_LEADER, "label": AllianceRules.role_label(AllianceRules.ROLE_VICE_LEADER)},
                {"value": AllianceRules.ROLE_ELDER, "label": AllianceRules.role_label(AllianceRules.ROLE_ELDER)},
            ]
        }

    def update_member_role(self, user_id: int, target_user_id: int, role: int) -> dict:
        actor = self.alliance_repo.get_member(user_id)
        if not actor:
            return {"ok": False, "error": "未加入联盟"}

        target = self.alliance_repo.get_member(target_user_id)
        if not target or target.alliance_id != actor.alliance_id:
            return {"ok": False, "error": "未找到该成员"}

        if actor.user_id == target.user_id:
            return {"ok": False, "error": "无法修改自己的职位"}

        if not AllianceRules.can_manage_roles(actor.role):
            return {"ok": False, "error": "只有盟主可以调整职位"}

        if role not in {AllianceRules.ROLE_MEMBER, AllianceRules.ROLE_VICE_LEADER, AllianceRules.ROLE_ELDER}:
            return {"ok": False, "error": "无效的职位"}

        if target.role == AllianceRules.ROLE_LEADER:
            return {"ok": False, "error": "无法修改盟主职位"}

        self.alliance_repo.update_member_role(target_user_id, role)
        return {"ok": True, "role": role, "role_label": AllianceRules.role_label(role)}

    def kick_member(self, user_id: int, target_user_id: int) -> dict:
        actor = self.alliance_repo.get_member(user_id)
        if not actor:
            return {"ok": False, "error": "未加入联盟"}

        target = self.alliance_repo.get_member(target_user_id)
        if not target or target.alliance_id != actor.alliance_id:
            return {"ok": False, "error": "未找到该成员"}

        if actor.user_id == target.user_id:
            return {"ok": False, "error": "无法踢出自己"}

        if not self._can_kick(actor, target):
            return {"ok": False, "error": "无权踢出该成员"}

        alliance_id = actor.alliance_id
        target_name = self._member_display_name(target)
        self.alliance_repo.remove_member(target_user_id)
        
        # 记录被踢出成员的退出时间，用于48小时加入限制
        from datetime import datetime
        self.alliance_repo.record_quit_time(target_user_id, datetime.utcnow())
        
        self._record_activity(
            alliance_id=alliance_id,
            event_type="kick",
            actor_user_id=user_id,
            actor_name=self._member_display_name(actor),
            target_user_id=target.user_id,
            target_name=target_name,
        )
        return {"ok": True}

    def quit_alliance(self, user_id: int) -> dict:
        """退出联盟"""
        member = self.alliance_repo.get_member(user_id)
        if not member:
            return {"ok": False, "error": "未加入联盟"}

        # 如果是盟主，不能直接退出，需要先转让或解散
        if member.role == AllianceRules.ROLE_LEADER:
            return {"ok": False, "error": "盟主不能直接退出联盟，请先转让盟主职位或解散联盟"}

        alliance_id = member.alliance_id
        member_name = self._member_display_name(member)
        self.alliance_repo.remove_member(user_id)
        
        # 记录退出时间，用于48小时加入限制
        from datetime import datetime
        self.alliance_repo.record_quit_time(user_id, datetime.utcnow())
        
        self._record_activity(
            alliance_id=alliance_id,
            event_type="leave",
            actor_user_id=user_id,
            actor_name=member_name,
        )
        return {"ok": True, "message": "已退出联盟"}

    def transfer_alliance(self, user_id: int, target_user_id: int) -> dict:
        """转让联盟"""
        actor = self.alliance_repo.get_member(user_id)
        if not actor:
            return {"ok": False, "error": "未加入联盟"}

        if actor.role != AllianceRules.ROLE_LEADER:
            return {"ok": False, "error": "只有盟主可以转让联盟"}

        target = self.alliance_repo.get_member(target_user_id)
        if not target or target.alliance_id != actor.alliance_id:
            return {"ok": False, "error": "未找到该成员"}

        if target.role == AllianceRules.ROLE_LEADER:
            return {"ok": False, "error": "该成员已经是盟主"}

        # 检查被转让者条件：等级30级及以上，拥有1个盟主证明
        player = self.player_repo.get_by_id(target_user_id)
        if not player:
            return {"ok": False, "error": "未找到该玩家"}

        if player.level < 30:
            return {"ok": False, "error": "被转让者需要等级30级及以上"}

        # 检查是否有盟主证明
        proof_count = self.inventory_service.get_item_count(target_user_id, AllianceRules.LEAGUE_LEADER_TOKEN_ID)
        if proof_count < 1:
            return {"ok": False, "error": "被转让者需要拥有1个盟主证明"}

        # 扣除盟主证明
        self.inventory_service.remove_item(target_user_id, AllianceRules.LEAGUE_LEADER_TOKEN_ID, 1)

        # 更新联盟盟主
        alliance_id = actor.alliance_id
        self.alliance_repo.update_leader_id(alliance_id, target_user_id)

        # 更新成员角色：原盟主变为普通成员，新盟主角色设为盟主
        self.alliance_repo.update_member_role(user_id, AllianceRules.ROLE_MEMBER)
        self.alliance_repo.update_member_role(target_user_id, AllianceRules.ROLE_LEADER)

        # 记录活动
        actor_name = self._member_display_name(actor)
        target_name = self._member_display_name(target)
        self._record_activity(
            alliance_id=alliance_id,
            event_type="transfer",
            actor_user_id=user_id,
            actor_name=actor_name,
            target_user_id=target_user_id,
            target_name=target_name,
        )

        return {"ok": True, "message": f"联盟已成功转让给{target_name}"}

    def disband_alliance(self, user_id: int) -> dict:
        """解散联盟"""
        member = self.alliance_repo.get_member(user_id)
        if not member:
            return {"ok": False, "error": "未加入联盟"}

        if member.role != AllianceRules.ROLE_LEADER:
            return {"ok": False, "error": "只有盟主可以解散联盟"}

        alliance_id = member.alliance_id
        alliance = self.alliance_repo.get_alliance_by_id(alliance_id)
        if not alliance:
            return {"ok": False, "error": "联盟不存在"}

        # 获取所有成员，记录退出时间
        members = self.alliance_repo.get_alliance_members(alliance_id)
        from datetime import datetime
        quit_time = datetime.utcnow()
        for m in members:
            self.alliance_repo.record_quit_time(m.user_id, quit_time)

        # 记录活动（在删除前）
        member_name = self._member_display_name(member)
        try:
            self._record_activity(
                alliance_id=alliance_id,
                event_type="disband",
                actor_user_id=user_id,
                actor_name=member_name,
            )
        except Exception:
            # 如果记录活动失败，不影响解散流程
            pass

        # 删除联盟（级联删除成员记录）
        self.alliance_repo.delete_alliance(alliance_id)

        return {"ok": True, "message": "联盟已解散"}

    def get_alliance_talent_info(self, user_id: int) -> dict:
        member = self.alliance_repo.get_member(user_id)
        if not member:
            return {"ok": False, "error": "未加入联盟"}

        alliance = self.alliance_repo.get_alliance_by_id(member.alliance_id)
        if not alliance:
            # 联盟不存在，但成员记录还在，说明联盟已被解散但成员记录未清理
            try:
                self.alliance_repo.remove_member(user_id)
            except Exception:
                pass
            return {"ok": False, "error": "未加入联盟"}

        building_map = self._get_building_level_map(alliance.id)
        talent_pool_level = building_map.get("talent", 1)
        research_map = self._get_talent_research_map(alliance.id)
        player_map = self._get_player_talent_map(user_id)

        talent_rows = []
        for key in AllianceRules.TALENT_KEYS:
            research_level = research_map.get(key, 1)
            max_level = AllianceRules.get_talent_max_level(talent_pool_level, research_level)
            player_level = player_map.get(key, 0)
            can_research_talent = (
                AllianceRules.can_research_talent(member.role)
                and research_level < talent_pool_level
            )
            next_research_level = research_level + 1
            research_cost = None
            if can_research_talent:
                research_cost = AllianceRules.get_talent_research_cost(next_research_level, key)
            can_learn_talent = player_level < max_level
            next_learn_level = player_level + 1
            learn_cost = None
            if can_learn_talent:
                learn_cost = AllianceRules.get_talent_learn_contribution_cost(next_learn_level)
            talent_rows.append({
                "key": key,
                "label": AllianceRules.talent_label(key),
                "player_level": player_level,
                "max_level": max_level,
                "research_level": research_level,
                "effect_percent": AllianceRules.get_talent_effect_percent(player_level),
                "can_learn": can_learn_talent,
                "next_level": next_learn_level if can_learn_talent else None,
                "learn_cost": learn_cost,
                "can_research": can_research_talent,
                "research_cost": research_cost,
                "next_research_level": next_research_level if can_research_talent else None,
            })

        return {
            "ok": True,
            "building_level": talent_pool_level,
            "can_research": AllianceRules.can_research_talent(member.role),
            "member": {
                "contribution": member.contribution or 0,
            },
            "talents": talent_rows,
        }

    def learn_alliance_talent(self, user_id: int, talent_key: str) -> dict:
        if not AllianceRules.is_valid_talent_key(talent_key):
            return {"ok": False, "error": "无效的天赋"}

        member = self.alliance_repo.get_member(user_id)
        if not member:
            return {"ok": False, "error": "未加入联盟"}

        alliance = self.alliance_repo.get_alliance_by_id(member.alliance_id)
        if not alliance:
            # 联盟不存在，但成员记录还在，说明联盟已被解散但成员记录未清理
            try:
                self.alliance_repo.remove_member(user_id)
            except Exception:
                pass
            return {"ok": False, "error": "未加入联盟"}

        building_map = self._get_building_level_map(alliance.id)
        talent_pool_level = building_map.get("talent", 1)
        research_map = self._get_talent_research_map(member.alliance_id)
        player_map = self._get_player_talent_map(user_id)

        research_level = research_map.get(talent_key, 1)
        max_level = AllianceRules.get_talent_max_level(talent_pool_level, research_level)
        current_level = player_map.get(talent_key, 0)

        if current_level >= max_level:
            return {"ok": False, "error": "天赋等级已达到上限"}

        new_level = current_level + 1
        learn_cost = AllianceRules.get_talent_learn_contribution_cost(new_level)
        required_contribution = learn_cost["per_talent"]
        current_contribution = member.contribution or 0
        if current_contribution < required_contribution:
            return {"ok": False, "error": "贡献不足"}

        self.alliance_repo.update_member_contribution(user_id, -required_contribution)
        remaining_contribution = max(0, current_contribution - required_contribution)
        member.contribution = remaining_contribution
        self.alliance_repo.update_player_talent_level(user_id, talent_key, new_level)
        return {
            "ok": True,
            "level": new_level,
            "max_level": max_level,
            "effect_percent": AllianceRules.get_talent_effect_percent(new_level),
            "learn_cost": learn_cost,
            "member_contribution": remaining_contribution,
        }

    def research_alliance_talent(self, user_id: int, talent_key: str) -> dict:
        if not AllianceRules.is_valid_talent_key(talent_key):
            return {"ok": False, "error": "无效的天赋"}

        member = self.alliance_repo.get_member(user_id)
        if not member:
            return {"ok": False, "error": "未加入联盟"}

        if not AllianceRules.can_research_talent(member.role):
            return {"ok": False, "error": "只有盟主可以研究天赋"}

        alliance = self.alliance_repo.get_alliance_by_id(member.alliance_id)
        if not alliance:
            # 联盟不存在，但成员记录还在，说明联盟已被解散但成员记录未清理
            try:
                self.alliance_repo.remove_member(user_id)
            except Exception:
                pass
            return {"ok": False, "error": "未加入联盟"}

        building_map = self._get_building_level_map(alliance.id)
        talent_pool_level = building_map.get("talent", 1)
        research_map = self._get_talent_research_map(alliance.id)
        current_level = research_map.get(talent_key, 1)

        if current_level >= talent_pool_level:
            return {"ok": False, "error": "研究等级已达到建筑上限"}

        next_level = current_level + 1
        cost = AllianceRules.get_talent_research_cost(next_level, talent_key)
        if not cost:
            return {"ok": False, "error": "研究等级已达到最高上限"}

        if alliance.funds < cost["funds"]:
            return {"ok": False, "error": "联盟资金不足"}
        if alliance.crystals < cost["crystals"]:
            return {"ok": False, "error": "焚火晶不足"}

        if cost["funds"]:
            self.alliance_repo.update_alliance_resources(alliance.id, -cost["funds"], 0)
            alliance.funds = (alliance.funds or 0) - cost["funds"]
        if cost["crystals"]:
            self.alliance_repo.update_alliance_crystals(alliance.id, -cost["crystals"])
            alliance.crystals = (alliance.crystals or 0) - cost["crystals"]

        new_level = min(talent_pool_level, next_level)
        self.alliance_repo.update_alliance_talent_research(alliance.id, talent_key, new_level)
        max_level = AllianceRules.get_talent_max_level(talent_pool_level, new_level)

        self._record_activity(
            alliance_id=alliance.id,
            event_type="research_talent",
            actor_user_id=member.user_id,
            actor_name=self._member_display_name(member),
            item_name=AllianceRules.talent_label(talent_key),
            item_quantity=new_level,
        )

        return {
            "ok": True,
            "research_level": new_level,
            "building_level": talent_pool_level,
            "max_level": max_level,
            "cost": cost,
            "alliance": {
                "funds": alliance.funds,
                "crystals": alliance.crystals,
            },
        }

    def _get_sort_key(self, sort: str):
        if sort == "contribution":
            return lambda m: (-(m.contribution or 0), AllianceRules.role_priority(m.role), -(m.level or 0), m.user_id)
        if sort == "level":
            return lambda m: (-(m.level or 0), AllianceRules.role_priority(m.role), -(m.contribution or 0), m.user_id)
        return lambda m: (AllianceRules.role_priority(m.role), -(m.contribution or 0), -(m.level or 0), m.user_id)

    def _can_kick(self, actor: AllianceMember, target: AllianceMember) -> bool:
        return AllianceRules.can_kick_member(actor.role, target.role) and actor.user_id != target.user_id

    def _can_assign_role(self, actor: AllianceMember, target: AllianceMember) -> bool:
        if actor.user_id == target.user_id:
            return False
        if target.role == AllianceRules.ROLE_LEADER:
            return False
        return AllianceRules.can_manage_roles(actor.role)

    def _get_talent_research_map(self, alliance_id: int) -> Dict[str, int]:
        researches = self.alliance_repo.get_alliance_talent_research(alliance_id)
        data = {r.talent_key: r.research_level for r in researches}
        for key in AllianceRules.TALENT_KEYS:
            data.setdefault(key, 1)
        return data

    def _get_player_talent_map(self, user_id: int) -> Dict[str, int]:
        levels = self.alliance_repo.get_player_talent_levels(user_id)
        data = {lvl.talent_key: lvl.level for lvl in levels}
        for key in AllianceRules.TALENT_KEYS:
            data.setdefault(key, 0)
        return data

    def _get_alliance_context(self, user_id: int):
        member = self.alliance_repo.get_member(user_id)
        if not member:
            return None, None, {"ok": False, "error": "未加入联盟"}
        alliance = self.alliance_repo.get_alliance_by_id(member.alliance_id)
        if not alliance:
            # 联盟不存在，但成员记录还在，说明联盟已被解散但成员记录未清理
            # 清理孤儿成员记录，并返回"未加入联盟"
            try:
                self.alliance_repo.remove_member(user_id)
            except Exception:
                pass  # 清理失败不影响返回结果
            return None, None, {"ok": False, "error": "未加入联盟"}
        return member, alliance, None

    def get_donation_info(self, user_id: int) -> dict:
        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error

        items = []
        for key in AllianceRules.donation_keys():
            rule = AllianceRules.get_donation_rule(key)
            if not rule:
                continue
            available = self.inventory_service.get_item_count(user_id, rule["item_id"])
            items.append({
                "key": key,
                "itemId": rule["item_id"],
                "name": rule["item_name"],
                "available": available,
                "effects": {
                    "funds": rule.get("funds", 0),
                    "prosperity": rule.get("prosperity", 0),
                    "crystals": rule.get("crystals", 0),
                    "contribution": rule.get("contribution", 0),
                },
            })

        return {
            "ok": True,
            "items": items,
            "alliance": {
                "id": alliance.id,
                "name": alliance.name,
                "funds": alliance.funds or 0,
                "prosperity": alliance.prosperity or 0,
                "crystals": alliance.crystals or 0,
            },
            "member": {
                "userId": member.user_id,
                "contribution": member.contribution or 0,
            },
            
        }

    def donate_resources(self, user_id: int, donations: Dict[str, int]) -> dict:
        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error

        if not isinstance(donations, dict) or not donations:
            return {"ok": False, "error": "请至少选择一种物资"}

        consumption_plan = []
        total_funds = 0
        total_prosperity = 0
        total_contribution = 0
        total_crystals = 0

        for key, raw_quantity in donations.items():
            rule = AllianceRules.get_donation_rule(key)
            if not rule:
                return {"ok": False, "error": f"未知的捐赠物资：{key}"}
            try:
                quantity = int(raw_quantity)
            except (TypeError, ValueError):
                return {"ok": False, "error": "捐赠数量必须为整数"}
            if quantity <= 0:
                return {"ok": False, "error": "捐赠数量必须大于 0"}

            available = self.inventory_service.get_item_count(user_id, rule["item_id"])
            if available < quantity:
                return {"ok": False, "error": f"{rule['item_name']}数量不足"}

            consumption_plan.append((rule, quantity))
            total_funds += rule.get("funds", 0) * quantity
            total_prosperity += rule.get("prosperity", 0) * quantity
            total_contribution += rule.get("contribution", 0) * quantity
            total_crystals += rule.get("crystals", 0) * quantity

        if not consumption_plan:
            return {"ok": False, "error": "请输入有效的捐赠数量"}

        for rule, quantity in consumption_plan:
            try:
                self.inventory_service.remove_item(user_id, rule["item_id"], quantity)
            except InventoryError as exc:
                return {"ok": False, "error": f"扣除{rule['item_name']}失败：{str(exc)}"}

        if total_funds or total_prosperity:
            self.alliance_repo.update_alliance_resources(
                alliance.id,
                funds_delta=total_funds,
                prosperity_delta=total_prosperity,
            )
        if total_contribution:
            self.alliance_repo.update_member_contribution(user_id, total_contribution)
        if total_crystals:
            self.alliance_repo.update_alliance_crystals(alliance.id, total_crystals)
        actor_name = self._member_display_name(member)
        for rule, quantity in consumption_plan:
            self._record_activity(
                alliance_id=alliance.id,
                event_type="donate",
                actor_user_id=user_id,
                actor_name=actor_name,
                item_name=rule.get("item_name"),
                item_quantity=quantity,
            )

        new_funds = (alliance.funds or 0) + total_funds
        new_prosperity = (alliance.prosperity or 0) + total_prosperity
        new_crystals = (alliance.crystals or 0) + total_crystals
        new_contribution = (member.contribution or 0) + total_contribution

        return {
            "ok": True,
            "message": "捐赠成功，感谢你的支持！",
            "delta": {
                "funds": total_funds,
                "prosperity": total_prosperity,
                "crystals": total_crystals,
                "contribution": total_contribution,
            },
            "alliance": {
                "funds": new_funds,
                "prosperity": new_prosperity,
                "crystals": new_crystals,
            },
            "member": {
                "contribution": new_contribution,
            },
        }

    def upgrade_item_storage(self, user_id: int) -> dict:
        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error

        if member.role != AllianceRules.ROLE_LEADER:
            return {"ok": False, "error": "只有盟主可以升级寄存仓库"}

        building_map = self._get_building_level_map(alliance.id)
        storage_level = building_map.get("warehouse", 1)
        council_level = building_map.get("council", alliance.level or 1)

        rule = AllianceRules.get_item_storage_upgrade_rule(storage_level)
        if not rule:
            return {"ok": False, "error": "寄存仓库已达到最高等级"}

        if council_level < rule["council_level"]:
            return {"ok": False, "error": f"议事厅需达到{rule['council_level']}级"}
        if alliance.funds < rule["funds"]:
            return {"ok": False, "error": "联盟资金不足"}
        if alliance.crystals < rule["crystals"]:
            return {"ok": False, "error": "焚火晶不足"}
        if alliance.prosperity < rule["prosperity"]:
            return {"ok": False, "error": "繁荣度不足"}

        if rule["funds"]:
            self.alliance_repo.update_alliance_resources(alliance.id, -rule["funds"], 0)
            alliance.funds = (alliance.funds or 0) - rule["funds"]
        if rule["crystals"]:
            self.alliance_repo.update_alliance_crystals(alliance.id, -rule["crystals"])
            alliance.crystals = (alliance.crystals or 0) - rule["crystals"]

        new_level = rule["next_level"]
        self.alliance_repo.set_alliance_building_level(alliance.id, "warehouse", new_level)

        self._record_activity(
            alliance_id=alliance.id,
            event_type="upgrade_building",
            actor_user_id=member.user_id,
            actor_name=self._member_display_name(member),
            item_name="寄存仓库",
            item_quantity=new_level,
        )

        return {
            "ok": True,
            "message": f"寄存仓库成功升级至 {new_level} 级！",
            "itemStorage": {
                "level": new_level,
                "capacity": AllianceRules.item_storage_capacity_from_level(new_level),
            },
            "alliance": {
                "funds": alliance.funds,
                "crystals": alliance.crystals,
                "prosperity": alliance.prosperity,
            },
        }

    def upgrade_furnace(self, user_id: int) -> dict:
        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error

        if member.role != AllianceRules.ROLE_LEADER:
            return {"ok": False, "error": "只有盟主可以升级焚天炉"}

        building_map = self._get_building_level_map(alliance.id)
        furnace_level = building_map.get("furnace", 1)
        council_level = building_map.get("council", alliance.level or 1)

        rule = AllianceRules.get_furnace_upgrade_rule(furnace_level)
        if not rule:
            return {"ok": False, "error": "焚天炉已达到最高等级"}

        if council_level < rule["council_level"]:
            return {"ok": False, "error": f"议事厅需达到{rule['council_level']}级"}
        if alliance.funds < rule["funds"]:
            return {"ok": False, "error": "联盟资金不足"}
        if alliance.crystals < rule["crystals"]:
            return {"ok": False, "error": "焚火晶不足"}
        if alliance.prosperity < rule["prosperity"]:
            return {"ok": False, "error": "繁荣度不足"}

        if rule["funds"]:
            self.alliance_repo.update_alliance_resources(alliance.id, -rule["funds"], 0)
            alliance.funds = (alliance.funds or 0) - rule["funds"]
        if rule["crystals"]:
            self.alliance_repo.update_alliance_crystals(alliance.id, -rule["crystals"])
            alliance.crystals = (alliance.crystals or 0) - rule["crystals"]

        new_level = rule["next_level"]
        self.alliance_repo.set_alliance_building_level(alliance.id, "furnace", new_level)

        self._record_activity(
            alliance_id=alliance.id,
            event_type="upgrade_building",
            actor_user_id=member.user_id,
            actor_name=self._member_display_name(member),
            item_name="焚天炉",
            item_quantity=new_level,
        )

        return {
            "ok": True,
            "message": f"焚天炉成功升级至 {new_level} 级！",
            "furnace": {
                "level": new_level,
                "trainingRooms": AllianceRules.furnace_training_room_count(new_level),
                "crystalBonus": AllianceRules.furnace_crystal_bonus(new_level),
            },
            "alliance": {
                "funds": alliance.funds,
                "crystals": alliance.crystals,
                "prosperity": alliance.prosperity,
            },
        }

    def upgrade_beast_room(self, user_id: int) -> dict:
        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error

        if member.role != AllianceRules.ROLE_LEADER:
            return {"ok": False, "error": "只有盟主可以升级幻兽室"}

        building_map = self._get_building_level_map(alliance.id)
        beast_level = building_map.get("beast", 1)
        council_level = building_map.get("council", alliance.level or 1)

        rule = AllianceRules.get_beast_room_upgrade_rule(beast_level)
        if not rule:
            return {"ok": False, "error": "幻兽室已达到最高等级"}

        if council_level < rule["council_level"]:
            return {"ok": False, "error": f"议事厅需达到{rule['council_level']}级"}
        if alliance.funds < rule["funds"]:
            return {"ok": False, "error": "联盟资金不足"}
        if alliance.crystals < rule["crystals"]:
            return {"ok": False, "error": "焚火晶不足"}
        if alliance.prosperity < rule["prosperity"]:
            return {"ok": False, "error": "繁荣度不足"}

        if rule["funds"]:
            self.alliance_repo.update_alliance_resources(alliance.id, -rule["funds"], 0)
            alliance.funds = (alliance.funds or 0) - rule["funds"]
        if rule["crystals"]:
            self.alliance_repo.update_alliance_crystals(alliance.id, -rule["crystals"])
            alliance.crystals = (alliance.crystals or 0) - rule["crystals"]

        new_level = rule["next_level"]
        self.alliance_repo.set_alliance_building_level(alliance.id, "beast", new_level)

        self._record_activity(
            alliance_id=alliance.id,
            event_type="upgrade_building",
            actor_user_id=member.user_id,
            actor_name=self._member_display_name(member),
            item_name="幻兽室",
            item_quantity=new_level,
        )

        return {
            "ok": True,
            "message": f"幻兽室成功升级至 {new_level} 级！",
            "beastRoom": {
                "level": new_level,
                "capacity": AllianceRules.beast_room_capacity_from_level(new_level),
            },
            "alliance": {
                "funds": alliance.funds,
                "crystals": alliance.crystals,
                "prosperity": alliance.prosperity,
            },
        }

    def upgrade_talent_pool(self, user_id: int) -> dict:
        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error

        if member.role != AllianceRules.ROLE_LEADER:
            return {"ok": False, "error": "只有盟主可以升级天赋池"}

        building_map = self._get_building_level_map(alliance.id)
        talent_level = building_map.get("talent", 1)
        council_level = building_map.get("council", alliance.level or 1)

        rule = AllianceRules.get_talent_pool_upgrade_rule(talent_level)
        if not rule:
            return {"ok": False, "error": "天赋池已达到最高等级"}

        if council_level < rule["council_level"]:
            return {"ok": False, "error": f"议事厅需达到{rule['council_level']}级"}
        if alliance.funds < rule["funds"]:
            return {"ok": False, "error": "联盟资金不足"}
        if alliance.crystals < rule["crystals"]:
            return {"ok": False, "error": "焚火晶不足"}
        if alliance.prosperity < rule["prosperity"]:
            return {"ok": False, "error": "繁荣度不足"}

        if rule["funds"]:
            self.alliance_repo.update_alliance_resources(alliance.id, -rule["funds"], 0)
            alliance.funds = (alliance.funds or 0) - rule["funds"]
        if rule["crystals"]:
            self.alliance_repo.update_alliance_crystals(alliance.id, -rule["crystals"])
            alliance.crystals = (alliance.crystals or 0) - rule["crystals"]

        new_level = rule["next_level"]
        self.alliance_repo.set_alliance_building_level(alliance.id, "talent", new_level)

        self._record_activity(
            alliance_id=alliance.id,
            event_type="upgrade_building",
            actor_user_id=member.user_id,
            actor_name=self._member_display_name(member),
            item_name="天赋池",
            item_quantity=new_level,
        )

        return {
            "ok": True,
            "message": f"天赋池成功升级至 {new_level} 级！",
            "talentPool": {
                "level": new_level,
                "researchCap": AllianceRules.talent_pool_research_cap(new_level),
                "maxTalentLevel": AllianceRules.talent_pool_max_talent_level(new_level),
            },
            "alliance": {
                "funds": alliance.funds,
                "crystals": alliance.crystals,
                "prosperity": alliance.prosperity,
            },
        }

    def get_alliance_activities(self, user_id: int, limit: Optional[int] = None) -> dict:
        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error

        try:
            parsed_limit = int(limit) if limit is not None else 20
        except (TypeError, ValueError):
            parsed_limit = 20
        parsed_limit = max(1, min(parsed_limit, 50))

        activities = self.alliance_repo.list_activities(alliance.id, parsed_limit)
        rows = []
        for activity in activities:
            timestamp = ""
            if isinstance(activity.created_at, datetime):
                timestamp = self._format_datetime(activity.created_at)
            else:
                timestamp = self._format_datetime(activity.created_at)
            rows.append({
                "id": activity.id,
                "type": activity.event_type,
                "actorUserId": activity.actor_user_id,
                "actorName": activity.actor_name or (activity.actor_user_id and f"玩家{activity.actor_user_id}") or "",
                "targetUserId": activity.target_user_id,
                "targetName": activity.target_name or (activity.target_user_id and f"玩家{activity.target_user_id}") or "",
                "itemName": activity.item_name or "",
                "itemQuantity": activity.item_quantity or 0,
                "timeText": timestamp,
            })

        return {
            "ok": True,
            "activities": rows,
            "limit": parsed_limit,
        }

    def get_alliance_buildings_info(self, user_id: int) -> dict:
        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error

        building_map = self._get_building_level_map(alliance.id)
        buildings = []
        for key in AllianceRules.BUILDING_KEYS:
            buildings.append({
                "key": key,
                "name": AllianceRules.building_label(key),
                "level": building_map.get(key, 1),
            })

        rule = AllianceRules.get_council_upgrade_rule(alliance.level or 1)
        upgrade_info = {
            "currentLevel": alliance.level or 1,
            "memberCapacity": AllianceRules.member_capacity(alliance.level or 1),
            "isMaxLevel": rule is None,
        }
        if rule:
            requirements = []
            blocked_reasons = []
            for dep_key, dep_level in rule["requires"].items():
                current = building_map.get(dep_key, 1)
                met = current >= dep_level
                requirements.append({
                    "key": dep_key,
                    "name": AllianceRules.building_label(dep_key),
                    "requiredLevel": dep_level,
                    "currentLevel": current,
                    "met": met,
                })
                if not met:
                    blocked_reasons.append(f"{AllianceRules.building_label(dep_key)}需达到{dep_level}级")

            is_leader = member.role == AllianceRules.ROLE_LEADER
            if not is_leader:
                blocked_reasons.append("只有盟主可以升级议事厅")
            if alliance.funds < rule["funds"]:
                blocked_reasons.append("联盟资金不足")
            if alliance.crystals < rule["crystals"]:
                blocked_reasons.append("焚火晶不足")
            if alliance.prosperity < rule["prosperity"]:
                blocked_reasons.append("繁荣度不足")

            upgrade_info.update({
                "nextLevel": rule["next_level"],
                "costs": {
                    "funds": rule["funds"],
                    "crystals": rule["crystals"],
                },
                "prosperityRequirement": rule["prosperity"],
                "requirements": requirements,
                "blockedReasons": blocked_reasons,
                "canUpgrade": not blocked_reasons,
                "isLeader": is_leader,
            })

        return {
            "ok": True,
            "alliance": {
                "id": alliance.id,
                "name": alliance.name,
                "level": alliance.level or 1,
                "funds": alliance.funds or 0,
                "crystals": alliance.crystals or 0,
                "prosperity": alliance.prosperity or 0,
                "memberCapacity": AllianceRules.member_capacity(alliance.level or 1),
            },
            "member": {
                "role": member.role,
                "canUpgrade": member.role == AllianceRules.ROLE_LEADER,
            },
            "buildings": buildings,
            "councilUpgrade": upgrade_info,
        }

    def get_furnace_upgrade_info(self, user_id: int) -> dict:
        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error

        building_map = self._get_building_level_map(alliance.id)
        furnace_level = building_map.get("furnace", 1)
        council_level = building_map.get("council", alliance.level or 1)
        info = {
            "currentLevel": furnace_level,
            "trainingRooms": AllianceRules.furnace_training_room_count(furnace_level),
            "crystalBonus": AllianceRules.furnace_crystal_bonus(furnace_level),
        }

        rule = AllianceRules.get_furnace_upgrade_rule(furnace_level)
        blocked_reasons = []
        if rule:
            if member.role != AllianceRules.ROLE_LEADER:
                blocked_reasons.append("只有盟主可以升级焚天炉")
            if council_level < rule["council_level"]:
                blocked_reasons.append(f"议事厅等级需达到{rule['council_level']}级")
            if alliance.funds < rule["funds"]:
                blocked_reasons.append("联盟资金不足")
            if alliance.crystals < rule["crystals"]:
                blocked_reasons.append("焚火晶不足")
            if alliance.prosperity < rule["prosperity"]:
                blocked_reasons.append("繁荣度不足")

            info.update({
                "nextLevel": rule["next_level"],
                "requiredCouncilLevel": rule["council_level"],
                "costs": {
                    "funds": rule["funds"],
                    "crystals": rule["crystals"],
                },
                "prosperityRequirement": rule["prosperity"],
                "blockedReasons": blocked_reasons,
                "canUpgrade": not blocked_reasons,
            })
        else:
            info["isMaxLevel"] = True

        return {
            "ok": True,
            "alliance": {
                "id": alliance.id,
                "name": alliance.name,
                "funds": alliance.funds or 0,
                "crystals": alliance.crystals or 0,
                "prosperity": alliance.prosperity or 0,
            },
            "member": {
                "role": member.role,
            },
            "furnace": info,
        }

    def get_talent_pool_upgrade_info(self, user_id: int) -> dict:
        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error

        building_map = self._get_building_level_map(alliance.id)
        talent_level = building_map.get("talent", 1)
        council_level = building_map.get("council", alliance.level or 1)
        info = {
            "currentLevel": talent_level,
            "researchCap": AllianceRules.talent_pool_research_cap(talent_level),
            "maxTalentLevel": AllianceRules.talent_pool_max_talent_level(talent_level),
        }

        rule = AllianceRules.get_talent_pool_upgrade_rule(talent_level)
        blocked_reasons = []
        if rule:
            if member.role != AllianceRules.ROLE_LEADER:
                blocked_reasons.append("只有盟主可以升级天赋池")
            if council_level < rule["council_level"]:
                blocked_reasons.append(f"议事厅等级需达到{rule['council_level']}级")
            if alliance.funds < rule["funds"]:
                blocked_reasons.append("联盟资金不足")
            if alliance.crystals < rule["crystals"]:
                blocked_reasons.append("焚火晶不足")
            if alliance.prosperity < rule["prosperity"]:
                blocked_reasons.append("繁荣度不足")

            info.update({
                "nextLevel": rule["next_level"],
                "requiredCouncilLevel": rule["council_level"],
                "costs": {
                    "funds": rule["funds"],
                    "crystals": rule["crystals"],
                },
                "prosperityRequirement": rule["prosperity"],
                "blockedReasons": blocked_reasons,
                "canUpgrade": not blocked_reasons,
            })
        else:
            info["isMaxLevel"] = True

        return {
            "ok": True,
            "alliance": {
                "id": alliance.id,
                "name": alliance.name,
                "funds": alliance.funds or 0,
                "crystals": alliance.crystals or 0,
                "prosperity": alliance.prosperity or 0,
            },
            "member": {
                "role": member.role,
            },
            "talentPool": info,
        }

    def get_beast_room_upgrade_info(self, user_id: int) -> dict:
        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error

        building_map = self._get_building_level_map(alliance.id)
        beast_level = building_map.get("beast", 1)
        council_level = building_map.get("council", alliance.level or 1)
        info = {
            "currentLevel": beast_level,
            "capacity": AllianceRules.beast_room_capacity_from_level(beast_level),
        }

        rule = AllianceRules.get_beast_room_upgrade_rule(beast_level)
        blocked_reasons = []
        if rule:
            if member.role != AllianceRules.ROLE_LEADER:
                blocked_reasons.append("只有盟主可以升级幻兽室")
            if council_level < rule["council_level"]:
                blocked_reasons.append(f"议事厅等级需达到{rule['council_level']}级")
            if alliance.funds < rule["funds"]:
                blocked_reasons.append("联盟资金不足")
            if alliance.crystals < rule["crystals"]:
                blocked_reasons.append("焚火晶不足")
            if alliance.prosperity < rule["prosperity"]:
                blocked_reasons.append("繁荣度不足")

            info.update({
                "nextLevel": rule["next_level"],
                "requiredCouncilLevel": rule["council_level"],
                "costs": {
                    "funds": rule["funds"],
                    "crystals": rule["crystals"],
                },
                "prosperityRequirement": rule["prosperity"],
                "blockedReasons": blocked_reasons,
                "canUpgrade": not blocked_reasons,
            })
        else:
            info["isMaxLevel"] = True

        return {
            "ok": True,
            "alliance": {
                "id": alliance.id,
                "name": alliance.name,
                "funds": alliance.funds or 0,
                "crystals": alliance.crystals or 0,
                "prosperity": alliance.prosperity or 0,
            },
            "member": {"role": member.role},
            "beastRoom": info,
        }

    def get_item_storage_upgrade_info(self, user_id: int) -> dict:
        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error

        building_map = self._get_building_level_map(alliance.id)
        storage_level = building_map.get("warehouse", 1)
        council_level = building_map.get("council", alliance.level or 1)
        info = {
            "currentLevel": storage_level,
            "capacity": AllianceRules.item_storage_capacity_from_level(storage_level),
        }

        rule = AllianceRules.get_item_storage_upgrade_rule(storage_level)
        blocked_reasons = []
        if rule:
            if member.role != AllianceRules.ROLE_LEADER:
                blocked_reasons.append("只有盟主可以升级寄存仓库")
            if council_level < rule["council_level"]:
                blocked_reasons.append(f"议事厅等级需达到{rule['council_level']}级")
            if alliance.funds < rule["funds"]:
                blocked_reasons.append("联盟资金不足")
            if alliance.crystals < rule["crystals"]:
                blocked_reasons.append("焚火晶不足")
            if alliance.prosperity < rule["prosperity"]:
                blocked_reasons.append("繁荣度不足")

            info.update({
                "nextLevel": rule["next_level"],
                "requiredCouncilLevel": rule["council_level"],
                "costs": {
                    "funds": rule["funds"],
                    "crystals": rule["crystals"],
                },
                "prosperityRequirement": rule["prosperity"],
                "blockedReasons": blocked_reasons,
                "canUpgrade": not blocked_reasons,
            })
        else:
            info["isMaxLevel"] = True

        return {
            "ok": True,
            "alliance": {
                "id": alliance.id,
                "name": alliance.name,
                "funds": alliance.funds or 0,
                "crystals": alliance.crystals or 0,
                "prosperity": alliance.prosperity or 0,
            },
            "member": {"role": member.role},
            "itemStorage": info,
        }

    def upgrade_council_hall(self, user_id: int) -> dict:
        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error

        if member.role != AllianceRules.ROLE_LEADER:
            return {"ok": False, "error": "只有盟主可以升级议事厅"}

        current_level = alliance.level or 1
        rule = AllianceRules.get_council_upgrade_rule(current_level)
        if not rule:
            return {"ok": False, "error": "议事厅已达到最高等级"}

        building_map = self._get_building_level_map(alliance.id)
        for dep_key, dep_level in rule["requires"].items():
            if building_map.get(dep_key, 1) < dep_level:
                return {
                    "ok": False,
                    "error": f"{AllianceRules.building_label(dep_key)}需要达到{dep_level}级",
                }

        if alliance.funds < rule["funds"]:
            return {"ok": False, "error": "联盟资金不足"}
        if alliance.crystals < rule["crystals"]:
            return {"ok": False, "error": "焚火晶不足"}
        if alliance.prosperity < rule["prosperity"]:
            return {"ok": False, "error": "繁荣度不足"}

        funds_cost = rule["funds"]
        crystals_cost = rule["crystals"]
        if funds_cost:
            self.alliance_repo.update_alliance_resources(alliance.id, -funds_cost, 0)
            alliance.funds = (alliance.funds or 0) - funds_cost
        if crystals_cost:
            self.alliance_repo.update_alliance_crystals(alliance.id, -crystals_cost)
            alliance.crystals = (alliance.crystals or 0) - crystals_cost

        new_level = rule["next_level"]
        self.alliance_repo.update_alliance_level(alliance.id, new_level)
        self.alliance_repo.set_alliance_building_level(alliance.id, "council", new_level)
        alliance.level = new_level

        self._record_activity(
            alliance_id=alliance.id,
            event_type="upgrade_building",
            actor_user_id=member.user_id,
            actor_name=self._member_display_name(member),
            item_name="议事厅",
            item_quantity=new_level,
        )

        return {
            "ok": True,
            "message": f"议事厅成功升级至 {new_level} 级！",
            "alliance": {
                "id": alliance.id,
                "level": new_level,
                "funds": alliance.funds,
                "crystals": alliance.crystals,
                "prosperity": alliance.prosperity,
                "memberCapacity": AllianceRules.member_capacity(new_level),
            },
        }

    def get_item_storage_info(self, user_id: int) -> dict:
        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error

        bag_info = self.inventory_service.get_bag_info(user_id)
        bag_items = self._build_inventory_items_for_storage(user_id)

        records = self.alliance_repo.get_item_storage(alliance.id)
        storage_items, own_storage_items = self._build_storage_payload(records, user_id)

        building_map = self._get_building_level_map(alliance.id)
        storage_level = building_map.get("warehouse", 1)
        capacity = AllianceRules.item_storage_capacity_from_level(storage_level)
        used = self.alliance_repo.count_item_storage(alliance.id)

        return {
            "ok": True,
            "alliance": {
                "id": alliance.id,
                "name": alliance.name,
                "level": alliance.level or 1,
            },
            "bag": bag_info,
            "inventory": bag_items,
            "storage": {
                "level": storage_level,
                "capacity": capacity,
                "used": used,
                "items": storage_items,
                "ownItems": own_storage_items,
            },
        }

    def deposit_item_to_storage(self, user_id: int, item_id: int, quantity: int) -> dict:
        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error

        try:
            item_id = int(item_id)
            quantity = int(quantity)
        except (TypeError, ValueError):
            return {"ok": False, "error": "参数错误"}

        if quantity <= 0:
            return {"ok": False, "error": "寄存数量必须大于0"}

        available = self.inventory_service.get_item_count(user_id, item_id)
        if available < quantity:
            return {"ok": False, "error": "背包中该物品数量不足"}

        building_map = self._get_building_level_map(alliance.id)
        storage_level = building_map.get("warehouse", 1)
        capacity = AllianceRules.item_storage_capacity_from_level(storage_level)
        used_slots = self.alliance_repo.count_item_storage(alliance.id)
        owner_slots = self.alliance_repo.get_item_storage_slots(alliance.id, user_id, item_id)

        plan_updates = []
        remaining = quantity
        for slot in owner_slots:
            if remaining <= 0:
                break
            free_space = PlayerBag.MAX_STACK_SIZE - slot.quantity
            if free_space <= 0:
                continue
            add_amount = min(free_space, remaining)
            plan_updates.append(("update", slot.id, slot.quantity + add_amount))
            remaining -= add_amount

        plan_inserts = []
        temp_remaining = remaining
        while temp_remaining > 0:
            if used_slots + len(plan_inserts) >= capacity:
                return {"ok": False, "error": "寄存仓库容量不足"}
            add_amount = min(PlayerBag.MAX_STACK_SIZE, temp_remaining)
            plan_inserts.append(add_amount)
            temp_remaining -= add_amount

        # 扣除背包物品
        try:
            self.inventory_service.remove_item(user_id, item_id, quantity)
        except InventoryError as exc:
            return {"ok": False, "error": f"扣除背包物品失败：{str(exc)}"}

        try:
            for _, slot_id, new_quantity in plan_updates:
                self.alliance_repo.update_item_storage_quantity(slot_id, new_quantity)

            for add_amount in plan_inserts:
                storage = AllianceItemStorage(
                    id=None,
                    alliance_id=alliance.id,
                    item_id=item_id,
                    quantity=add_amount,
                    owner_user_id=user_id,
                )
                self.alliance_repo.add_item_storage(storage)
        except Exception as exc:
            # 回滚物品
            self.inventory_service.add_item(user_id, item_id, quantity)
            return {"ok": False, "error": f"寄存失败，请稍后再试：{str(exc)}"}

        snapshot = self.get_item_storage_info(user_id)
        return {
            "ok": True,
            "message": "寄存成功",
            "snapshot": snapshot,
        }

    def withdraw_item_from_storage(self, user_id: int, storage_id: int, quantity: int) -> dict:
        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error

        try:
            storage_id = int(storage_id)
            quantity = int(quantity)
        except (TypeError, ValueError):
            return {"ok": False, "error": "参数错误"}

        if quantity <= 0:
            return {"ok": False, "error": "取回数量必须大于0"}

        record = self.alliance_repo.get_item_storage_by_id(storage_id)
        if not record or record.alliance_id != alliance.id:
            return {"ok": False, "error": "寄存记录不存在"}
        if record.owner_user_id != user_id:
            return {"ok": False, "error": "只能取回自己寄存的物品"}
        if quantity > record.quantity:
            return {"ok": False, "error": "取回数量超出寄存数量"}

        try:
            added_item, is_temp = self.inventory_service.add_item(user_id, record.item_id, quantity)
        except InventoryError as exc:
            return {"ok": False, "error": f"放入背包失败：{str(exc)}"}

        remaining = record.quantity - quantity
        if remaining > 0:
            self.alliance_repo.update_item_storage_quantity(record.id, remaining)
        else:
            self.alliance_repo.remove_item_storage(record.id)

        snapshot = self.get_item_storage_info(user_id)
        message = "取回成功"
        if snapshot.get("ok") and is_temp:
            message += "（背包空间不足，物品已进入临时背包）"

        return {
            "ok": True,
            "message": message,
            "snapshot": snapshot,
        }

    def get_beast_storage_summary(self, user_id: int) -> dict:
        member = self.alliance_repo.get_member(user_id)
        if not member:
            return {"hasAlliance": False, "count": 0, "capacity": 0}
        alliance = self.alliance_repo.get_alliance_by_id(member.alliance_id)
        if not alliance:
            return {"hasAlliance": False, "count": 0, "capacity": 0}
        capacity = AllianceRules.beast_storage_capacity(alliance.level or 1)
        count = self.alliance_repo.count_beast_storage(alliance.id)
        return {
            "hasAlliance": True,
            "allianceId": alliance.id,
            "allianceLevel": alliance.level or 1,
            "count": count,
            "capacity": capacity,
        }

    def get_my_stored_beast_ids(self, user_id: int) -> List[int]:
        records = self.alliance_repo.get_beast_storage_by_owner(user_id)
        return [record.beast_id for record in records]

    def get_beast_storage_info(self, user_id: int) -> dict:
        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error
        
        building_map = self._get_building_level_map(alliance.id)
        beast_room_level = building_map.get("beast", 1)
        capacity = AllianceRules.beast_room_capacity_from_level(beast_room_level)
        records = self.alliance_repo.get_beast_storage(alliance.id)
        
        # 获取玩家幻兽栏信息
        player = self.player_repo.get_by_id(user_id)
        player_beasts = self.beast_repo.get_by_user_id(user_id)
        from application.services.vip_service import get_beast_slot_limit
        beast_slot_capacity = get_beast_slot_limit(player.vip_level if player else 0)
        beast_slot_used = len(player_beasts)
        
        storage_list = []
        for record in records:
            beast = self.beast_repo.get_by_id(record.beast_id)
            beast_name = ""
            beast_level = 0
            beast_realm = ""
            template_id = None
            if beast:
                beast_name = beast.nickname or getattr(beast, 'name', '') or f"幻兽{beast.id}"
                beast_level = beast.level
                beast_realm = getattr(beast, 'realm', '') or ''
                template_id = getattr(beast, 'template_id', None)
            stored_at = self._format_datetime(record.stored_at)
            storage_list.append({
                "storageId": record.id,
                "beastId": record.beast_id,
                "ownerUserId": record.owner_user_id,
                "ownerIsSelf": record.owner_user_id == user_id,
                "name": beast_name,
                "level": beast_level,
                "realm": beast_realm,
                "templateId": template_id,
                "storedAt": stored_at,
            })
        return {
            "ok": True,
            "allianceId": alliance.id,
            "allianceLevel": alliance.level or 1,
            "beastRoomLevel": beast_room_level,
            "storage": {
                "level": beast_room_level,
                "capacity": capacity,
                "used": len(storage_list),
            },
            "beastPen": {
                "used": beast_slot_used,
                "capacity": beast_slot_capacity,
            },
            "storageList": storage_list,
        }

    def store_beast_in_alliance_storage(self, user_id: int, beast_id: int) -> dict:
        if not beast_id:
            return {"ok": False, "error": "缺少幻兽ID"}
        _, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error
        capacity = AllianceRules.beast_storage_capacity(alliance.level or 1)
        used = self.alliance_repo.count_beast_storage(alliance.id)
        if used >= capacity:
            return {"ok": False, "error": "幻兽室已满"}
        beast = self.beast_repo.get_by_id(beast_id)
        if not beast or beast.user_id != user_id:
            return {"ok": False, "error": "幻兽不存在"}
        if getattr(beast, "is_main", False):
            return {"ok": False, "error": "出战中的幻兽无法寄存"}
        if getattr(beast, "is_in_team", 0):
            return {"ok": False, "error": "战斗队中的幻兽无法寄存"}
        existing = self.alliance_repo.get_beast_storage_by_beast(beast_id)
        if existing:
            return {"ok": False, "error": "该幻兽已在寄存室中"}
        storage = AllianceBeastStorage(
            id=None,
            alliance_id=alliance.id,
            beast_id=beast.id,
            owner_user_id=user_id,
        )
        storage_id = self.alliance_repo.add_beast_storage(storage)
        return {
            "ok": True,
            "storageId": storage_id,
            "used": used + 1,
            "capacity": capacity,
        }

    def retrieve_beast_from_alliance_storage(self, user_id: int, storage_id: int) -> dict:
        if not storage_id:
            return {"ok": False, "error": "缺少寄存记录ID"}
        _, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error
        record = self.alliance_repo.get_beast_storage_by_id(storage_id)
        if not record or record.alliance_id != alliance.id:
            return {"ok": False, "error": "寄存记录不存在"}
        if record.owner_user_id != user_id:
            return {"ok": False, "error": "只能取回自己寄存的幻兽"}
        self.alliance_repo.remove_beast_storage(storage_id)
        remaining = self.alliance_repo.count_beast_storage(alliance.id)
        capacity = AllianceRules.beast_storage_capacity(alliance.level or 1)
        return {
            "ok": True,
            "beastId": record.beast_id,
            "remaining": remaining,
            "capacity": capacity,
        }

    # === 修行广场 ===
    def get_training_ground_info(self, user_id: int) -> dict:
        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error

        rooms = self.alliance_repo.get_training_rooms(alliance.id)
        has_joined_today = self._has_joined_training_today(alliance.id, user_id)
        room_list = []
        now = datetime.utcnow()

        for idx, room in enumerate(rooms, start=1):
            participants = self.alliance_repo.get_training_participants(room.id)
            
            # 确保 status 字段存在，默认为 "ongoing"
            room_status = getattr(room, 'status', None) or "ongoing"
            
            # 如果房间是等待状态且满足2人，自动开始
            if room_status == "waiting" and len(participants) >= AllianceRules.MIN_TRAINING_PARTICIPANTS:
                self.alliance_repo.update_training_room_status(room.id, "ongoing")
                room_status = "ongoing"
                room.status = "ongoing"
            
            end_time = self._get_room_end_time(room)
            finished = self._is_room_finished(room, now) if room_status == "ongoing" else False
            
            # 不自动标记为完成，需要手动结束
            # if finished and room.status != "completed":
            #     self.alliance_repo.update_training_room_status(room.id, "completed")
            #     room.status = "completed"

            participant_rows = []
            self_participant = None
            for p in participants:
                display_name = p.nickname or f"玩家{p.user_id}"
                claimed = p.claimed_at is not None
                can_claim = (p.user_id == user_id) and not claimed and finished
                if p.user_id == user_id:
                    self_participant = p
                participant_rows.append({
                    "participantId": p.id,
                    "userId": p.user_id,
                    "nickname": display_name,
                    "joinedAt": self._format_datetime(p.joined_at),
                    "claimed": claimed,
                    "rewardAmount": p.reward_amount or 0,
                    "canClaim": can_claim,
                    "isSelf": p.user_id == user_id,
                })

            is_full = len(participants) >= (room.max_participants or 4)
            can_join = (
                not has_joined_today
                and room_status == "waiting"  # 只能加入等待中的房间
                and not is_full
                and self_participant is None
            )
            can_end = (
                room_status == "ongoing"
                and finished
                and self_participant is not None
            )
            
            # 状态标签
            if room_status == "completed":
                status_label = "已结束"
            elif room_status == "ongoing":
                status_label = "修行中" if not finished else "可结束"
            else:
                status_label = "等待中"
            
            # 获取房间的修行时长（固定2小时）
            duration_hours = 2
            
            room_list.append({
                "roomId": room.id,
                "index": idx,
                "title": room.title,
                "status": room_status,
                "statusLabel": status_label,
                "createdAt": self._format_datetime(room.created_at),
                "endsAt": self._format_datetime(end_time) if end_time else None,
                "maxParticipants": room.max_participants or 4,
                "participantCount": len(participants),
                "participants": participant_rows,
                "isFull": is_full,
                "canJoin": can_join,
                "canEnd": can_end,
                "isFinished": finished,
                "selfParticipantId": self_participant.id if self_participant else None,
                "durationHours": duration_hours,  # 修行时长（小时），固定2小时
            })

        # 检查是否有火能原石
        fire_ore_count = self.inventory_service.get_item_count(user_id, AllianceRules.FIRE_ORE_ITEM_ID)
        has_fire_ore = fire_ore_count > 0
        
        # 检查今日是否已领取火能原石
        has_claimed_fire_ore_today = self.alliance_repo.has_claimed_fire_ore_today(user_id)
        
        # 获取焚火炉等级
        furnace_building = self.alliance_repo.get_alliance_building(alliance.id, "furnace")
        furnace_level = furnace_building.level if furnace_building else 1
        expected_reward = AllianceRules.training_crystal_reward(furnace_level)
        
        any_ongoing = any(room.get("status") == "ongoing" for room in room_list)
        any_waiting = any(room.get("status") == "waiting" for room in room_list)
        
        return {
            "ok": True,
            "allianceLevel": alliance.level or 1,
            "allianceCrystals": alliance.crystals,
            "hasJoinedToday": has_joined_today,
            "trainingDurationMinutes": 120,  # 固定2小时=120分钟
            "dailyLimit": AllianceRules.TRAINING_DAILY_LIMIT,
            "rooms": room_list,
            "practiceStatus": "进行中" if any_ongoing else ("等待中" if any_waiting else "已结束"),
            "hasFireOre": has_fire_ore,
            "fireOreCount": fire_ore_count,
            "hasClaimedFireOreToday": has_claimed_fire_ore_today,
            "furnaceLevel": furnace_level,
            "expectedReward": expected_reward,
            "minParticipants": AllianceRules.MIN_TRAINING_PARTICIPANTS,
            "contributionCost": AllianceRules.FIRE_ORE_CONTRIBUTION_COST,
        }

    def create_training_room(self, user_id: int, title: Optional[str] = None, duration_hours: int = 2) -> dict:
        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error

        if self._has_joined_training_today(alliance.id, user_id):
            return {"ok": False, "error": "今日已参与修行，无法再次创建"}

        # 固定修行时长为2小时
        duration_hours = 2

        # 检查是否有火能原石
        fire_ore_count = self.inventory_service.get_item_count(user_id, AllianceRules.FIRE_ORE_ITEM_ID)
        if fire_ore_count < 1:
            return {"ok": False, "error": "需要火能原石才能进行修行，请先领取火能原石"}

        # 消耗火能原石
        try:
            self.inventory_service.remove_item(user_id, AllianceRules.FIRE_ORE_ITEM_ID, 1)
        except InventoryError as exc:
            return {"ok": False, "error": f"消耗火能原石失败：{str(exc)}"}

        room_title = (title or "焚天炉").strip()[:20] or "焚天炉"
        room = AllianceTrainingRoom(
            id=None,
            alliance_id=alliance.id,
            creator_user_id=user_id,
            title=room_title,
            status="waiting",  # 初始状态为等待中，满足2人后自动开始
            max_participants=4,
            duration_hours=duration_hours,  # 固定为2小时
        )
        room_id = self.alliance_repo.create_training_room(room)
        participant = AllianceTrainingParticipant(
            id=None,
            room_id=room_id,
            user_id=user_id,
        )
        self.alliance_repo.add_training_participant(participant)
        
        # 检查是否满足开始条件（至少2人）
        participants = self.alliance_repo.get_training_participants(room_id)
        if len(participants) >= AllianceRules.MIN_TRAINING_PARTICIPANTS:
            # 自动开始修行
            self.alliance_repo.update_training_room_status(room_id, "ongoing")
        
        return {"ok": True, "roomId": room_id}

    def join_training_room(self, user_id: int, room_id: int) -> dict:
        if not room_id:
            return {"ok": False, "error": "缺少修行房间ID"}

        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error

        room = self.alliance_repo.get_training_room_by_id(room_id)
        if not room or room.alliance_id != alliance.id:
            return {"ok": False, "error": "修行房间不存在"}

        if self._has_joined_training_today(alliance.id, user_id):
            return {"ok": False, "error": "今日已参与修行，无法加入其他房间"}

        # 如果房间已经开始或已结束，不能加入
        if room.status == "ongoing" or room.status == "completed":
            return {"ok": False, "error": "修行已开始或已结束，无法加入"}

        existing = self.alliance_repo.get_training_participant_by_room(room_id, user_id)
        if existing:
            return {"ok": False, "error": "已加入该修行房间"}

        participants = self.alliance_repo.get_training_participants(room_id)
        if len(participants) >= (room.max_participants or 4):
            return {"ok": False, "error": "修行房间已满"}

        # 检查是否有火能原石
        fire_ore_count = self.inventory_service.get_item_count(user_id, AllianceRules.FIRE_ORE_ITEM_ID)
        if fire_ore_count < 1:
            return {"ok": False, "error": "需要火能原石才能进行修行，请先领取火能原石"}

        # 消耗火能原石
        try:
            self.inventory_service.remove_item(user_id, AllianceRules.FIRE_ORE_ITEM_ID, 1)
        except InventoryError as exc:
            return {"ok": False, "error": f"消耗火能原石失败：{str(exc)}"}

        participant = AllianceTrainingParticipant(
            id=None,
            room_id=room_id,
            user_id=user_id,
        )
        self.alliance_repo.add_training_participant(participant)
        
        # 检查是否满足开始条件（至少2人）
        participants = self.alliance_repo.get_training_participants(room_id)
        if len(participants) >= AllianceRules.MIN_TRAINING_PARTICIPANTS and room.status == "waiting":
            # 自动开始修行
            self.alliance_repo.update_training_room_status(room_id, "ongoing")
        
        return {"ok": True}

    def claim_training_reward(self, user_id: int, participant_id: int) -> dict:
        if not participant_id:
            return {"ok": False, "error": "缺少参与记录"}

        participant = self.alliance_repo.get_training_participant(participant_id)
        if not participant or participant.user_id != user_id:
            return {"ok": False, "error": "未找到修行记录"}

        if participant.claimed_at:
            return {"ok": False, "error": "奖励已领取"}

        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error

        room = self.alliance_repo.get_training_room_by_id(participant.room_id)
        if not room or room.alliance_id != alliance.id:
            return {"ok": False, "error": "修行房间不存在"}

        if not self._is_room_finished(room):
            return {"ok": False, "error": "修行尚未结束，暂不可领取奖励"}

        if room.status != "completed":
            self.alliance_repo.update_training_room_status(room.id, "completed")

        participants = self.alliance_repo.get_training_participants(room.id)
        reward = AllianceRules.training_crystal_reward(
            alliance.level or 1,
            len(participants),
        )

        self.alliance_repo.mark_training_claimed(participant.id, reward)
        self.alliance_repo.update_alliance_crystals(alliance.id, reward)

        total_crystals = (alliance.crystals or 0) + reward
        return {
            "ok": True,
            "reward": reward,
            "totalCrystals": total_crystals,
        }

    def claim_fire_ore(self, user_id: int) -> dict:
        """领取火能原石（需要消耗5贡献值，一人一天只能领取一次）"""
        # 检查联盟成员身份
        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error

        # 检查今日是否已领取（使用数据库日期确保时区一致）
        if self.alliance_repo.has_claimed_fire_ore_today(user_id):
            return {"ok": False, "error": "今日已领取过火能原石，每人每天只能领取一次"}

        # 检查贡献值是否足够
        if member.contribution < AllianceRules.FIRE_ORE_CONTRIBUTION_COST:
            return {"ok": False, "error": f"贡献值不足，需要{AllianceRules.FIRE_ORE_CONTRIBUTION_COST}点贡献值"}

        # 扣除贡献值
        self.alliance_repo.update_member_contribution(user_id, -AllianceRules.FIRE_ORE_CONTRIBUTION_COST)
        member.contribution = member.contribution - AllianceRules.FIRE_ORE_CONTRIBUTION_COST

        # 发放火能原石
        try:
            self.inventory_service.add_item(user_id, AllianceRules.FIRE_ORE_ITEM_ID, 1)
        except InventoryError as exc:
            # 如果发放失败，回滚贡献值
            self.alliance_repo.update_member_contribution(user_id, AllianceRules.FIRE_ORE_CONTRIBUTION_COST)
            return {"ok": False, "error": f"发放火能原石失败：{str(exc)}"}

        # 发放成功后，记录领取日期（使用条件更新，确保原子性，防止并发重复领取）
        record_success = self.alliance_repo.record_fire_ore_claim(user_id)
        
        # 如果记录失败（返回False），说明今日已领取过（可能是并发请求）
        if not record_success:
            # 回滚：扣除物品，恢复贡献值
            try:
                self.inventory_service.remove_item(user_id, AllianceRules.FIRE_ORE_ITEM_ID, 1)
                self.alliance_repo.update_member_contribution(user_id, AllianceRules.FIRE_ORE_CONTRIBUTION_COST)
                member.contribution = member.contribution + AllianceRules.FIRE_ORE_CONTRIBUTION_COST
            except Exception as rollback_error:
                # 如果回滚失败，记录错误
                import logging
                logging.error(f"回滚火能原石领取失败 user_id={user_id}, error={rollback_error}")
            return {"ok": False, "error": "今日已领取过火能原石，每人每天只能领取一次"}

        # 记录动态
        self._record_activity(
            alliance_id=alliance.id,
            event_type="claim_fire_ore",
            actor_user_id=user_id,
            actor_name=self._member_display_name(member),
        )

        # 直接使用"火能原石"作为物品名称（在联盟系统中统一使用此名称）
        item_name = "火能原石"

        return {
            "ok": True,
            "message": f"领取成功！消耗{AllianceRules.FIRE_ORE_CONTRIBUTION_COST}贡献值，获得{item_name}×1",
            "item_id": AllianceRules.FIRE_ORE_ITEM_ID,
            "item_name": item_name,
            "contribution_cost": AllianceRules.FIRE_ORE_CONTRIBUTION_COST,
            "remaining_contribution": member.contribution,
        }

    # === 联盟兵营 / 盟战 ===
    def get_top3_alliances(self) -> dict:
        """获取盟战排行榜前三名联盟信息（用于首页显示）
        基于alliances表的war_honor字段，与联盟内战功显示保持一致
        """
        season_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        try:
            rows = self.alliance_repo.list_alliance_war_leaderboard(season_start, limit=3, offset=0)
        except Exception as e:
            import traceback
            traceback.print_exc()
            rows = []
        
        top3 = []
        for idx, row in enumerate(rows):
            alliance_id = row["alliance_id"]
            alliance = self.alliance_repo.get_alliance_by_id(alliance_id)
            top3.append({
                "rank": idx + 1,
                "allianceId": alliance_id,
                "allianceName": row["alliance_name"],
                "allianceLevel": alliance.level if alliance else 1,
                "score": row["score"],
            })
        
        return {
            "ok": True,
            "data": {
                "top3": top3,
            },
        }
    
    def get_war_ranking(self, user_id: int, page: int = 1, size: int = 10) -> dict:
        # 排行榜对所有用户可见，不要求必须加入联盟
        try:
            page = int(page)
        except (TypeError, ValueError):
            page = 1
        page = max(1, page)

        try:
            size = int(size)
        except (TypeError, ValueError):
            size = 10
        size = max(1, min(50, size))
        offset = (page - 1) * size

        season_key = datetime.utcnow().strftime("%Y-%m")
        season_start = datetime.strptime(season_key, "%Y-%m")

        try:
            rows = self.alliance_repo.list_alliance_war_leaderboard(season_start, size, offset)
            total = self.alliance_repo.count_alliance_war_leaderboard(season_start)
        except Exception as e:
            # 如果查询失败，返回空列表而不是错误
            import traceback
            traceback.print_exc()
            rows = []
            total = 0

        ranking = [
            {
                "rank": offset + idx + 1,
                "allianceId": row["alliance_id"],
                "allianceName": row["alliance_name"],
                "score": row["score"],
            }
            for idx, row in enumerate(rows)
        ]

        # 获取用户所在联盟的排名（如果用户有联盟）
        my_rank = None
        my_alliance_id = None
        try:
            member = self.alliance_repo.get_member(user_id)
            if member:
                alliance = self.alliance_repo.get_alliance_by_id(member.alliance_id)
                if alliance:
                    my_alliance_id = alliance.id
                    entry = self.alliance_repo.get_alliance_war_leaderboard_entry(alliance.id, season_start)
                    if entry:
                        my_rank = {
                            "rank": entry["rank"],
                            "allianceId": entry["alliance_id"],
                            "allianceName": entry["alliance_name"],
                            "score": entry["score"],
                        }
                    else:
                        # 即使 entry 为 None，也尝试从当前页的 ranking 中查找
                        # 这样可以处理分页的情况
                        for rank_item in ranking:
                            if rank_item["allianceId"] == alliance.id:
                                my_rank = rank_item
                                break
        except Exception:
            # 获取用户排名失败不影响整体返回
            pass

        return {
            "ok": True,
            "data": {
                "ranking": ranking,
                "myRank": my_rank,
                "myAllianceId": my_alliance_id,  # 返回用户的联盟ID，方便前端判断
                "page": page,
                "size": size,
                "total": total,
                "season": season_key,
            },
        }

    def signup_for_war(self, user_id: int) -> dict:
        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error

        if member.army_type:
            return {"ok": False, "error": "你已经报名过了"}

        player = self.player_repo.get_by_id(user_id)
        if not player:
            return {"ok": False, "error": "玩家不存在"}

        army_type = self._determine_army_type(player.level or 0)
        self.alliance_repo.update_member_army(user_id, army_type)
        member.army_type = army_type

        self._record_activity(
            alliance_id=alliance.id,
            event_type="war_signup",
            actor_user_id=user_id,
            actor_name=self._member_display_name(member),
            target_name=self._army_label(army_type),
        )

        return {
            "ok": True,
            "data": {
                "user_id": user_id,
                "army_type": army_type,
                "army_label": self._army_label(army_type),
                "level": player.level or 1,
            },
        }
    def signup_target(self, user_id: int, land_id: int, army: Optional[str] = None) -> dict:
        if not land_id:
            return {"ok": False, "error": "缺少土地ID"}

        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error

        if member.role != AllianceRules.ROLE_LEADER:
            return {"ok": False, "error": "只有盟主可以报名"}

        # 检查是否在报名时间内
        now = datetime.utcnow()
        is_war, phase, status = self._is_war_time(now)
        if not is_war or status != "signup":
            return {"ok": False, "error": "当前不在盟战报名时间内"}

        player = self.player_repo.get_by_id(user_id)
        if not player:
            return {"ok": False, "error": "玩家不存在"}

        normalized_army = self._normalize_army_choice(army, player.level or 1)
        
        # 检查该军队是否有成员（基于成员的等级自动分配的army_type）
        # 将字符串army转换为整数army_type：dragon -> 1, tiger -> 2
        army_type_int = self.ARMY_DRAGON if normalized_army == AllianceRules.ARMY_DRAGON else self.ARMY_TIGER
        army_members = self.alliance_repo.get_members_by_army(alliance.id, army_type_int)
        if len(army_members) == 0:
            army_label = "飞龙军" if normalized_army == AllianceRules.ARMY_DRAGON else "伏虎军"
            return {"ok": False, "error": f"{army_label}没有成员，无法报名攻打"}
        
        # 检查该军队的所有成员是否有出战幻兽（战灵）
        # 通过全局services访问player_beast_repo
        from interfaces.web_api.bootstrap import services as global_services
        members_without_beasts = []
        for member in army_members:
            team_beasts = global_services.player_beast_repo.get_team_beasts(member.user_id)
            if len(team_beasts) == 0:
                members_without_beasts.append(member)
        
        if len(members_without_beasts) > 0:
            army_label = "飞龙军" if normalized_army == AllianceRules.ARMY_DRAGON else "伏虎军"
            member_names = [m.nickname or f"玩家{m.user_id}" for m in members_without_beasts[:3]]  # 最多显示3个
            if len(members_without_beasts) > 3:
                member_names.append(f"等{len(members_without_beasts)}人")
            return {"ok": False, "error": f"{army_label}中以下成员没有出战幻兽：{', '.join(member_names)}，无法报名攻打"}
        
        # 自动为所有符合条件的成员创建 army_assignments 记录
        # 确保配对时能够找到这些成员
        army_str = "dragon" if normalized_army == AllianceRules.ARMY_DRAGON else "tiger"
        for member in army_members:
            self.alliance_repo.upsert_army_assignment(alliance.id, member.user_id, army_str)
        
        allowed_land_ids = (
            self.DRAGON_ONLY_LANDS if normalized_army == AllianceRules.ARMY_DRAGON else self.TIGER_ONLY_LANDS
        )
        if land_id not in allowed_land_ids:
            msg = (
                "飞龙军只能选择土地报名（迷雾城1号土地或飞龙港1号土地）"
                if normalized_army == AllianceRules.ARMY_DRAGON
                else "伏虎军只能选择据点报名（幻灵镇1号据点或定老城1号据点）"
            )
            return {"ok": False, "error": msg}

        # 检查同一军队类型是否已经报名了其他土地/据点
        existing_same_army = self.alliance_repo.get_active_land_registration_by_range(
            alliance.id, list(allowed_land_ids)
        )
        if existing_same_army and existing_same_army.land_id != land_id:
            land_names = {
                1: "迷雾城1号土地",
                2: "飞龙港1号土地",
                3: "幻灵镇1号据点",
                4: "定老城1号据点"
            }
            if normalized_army == AllianceRules.ARMY_DRAGON:
                msg = f"飞龙军只能选择一个土地报名（{land_names[1]}或{land_names[2]}）"
            else:
                msg = f"伏虎军只能选择一个据点报名（{land_names[3]}或{land_names[4]}）"
            return {"ok": False, "error": msg}
        
        # 检查联盟是否已经报名了2个目标（飞龙军1个 + 伏虎军1个）
        # 使用更严格的方法：直接查询所有活跃状态的报名记录
        dragon_registered = False
        tiger_registered = False
        
        # 检查飞龙军是否已报名土地
        dragon_reg = self.alliance_repo.get_active_land_registration_by_range(
            alliance.id, list(self.DRAGON_ONLY_LANDS)
        )
        if dragon_reg and dragon_reg.land_id != land_id:
            dragon_registered = True
        
        # 检查伏虎军是否已报名据点
        tiger_reg = self.alliance_repo.get_active_land_registration_by_range(
            alliance.id, list(self.TIGER_ONLY_LANDS)
        )
        if tiger_reg and tiger_reg.land_id != land_id:
            tiger_registered = True
        
        # 如果当前要报名的是飞龙军土地，检查是否已有飞龙军报名
        if normalized_army == AllianceRules.ARMY_DRAGON:
            if dragon_registered:
                return {"ok": False, "error": "飞龙军已经报名了一个土地，不能再报名其他土地"}
        # 如果当前要报名的是伏虎军据点，检查是否已有伏虎军报名
        elif normalized_army == AllianceRules.ARMY_TIGER:
            if tiger_registered:
                return {"ok": False, "error": "伏虎军已经报名了一个据点，不能再报名其他据点"}

        registration = self.alliance_repo.get_land_registration(alliance.id, land_id)
        if registration and registration.is_active():
            return {"ok": False, "error": "该土地已报名"}

        now = datetime.utcnow()
        status_active = 1
        if registration:
            registration.army = normalized_army
            registration.registration_time = now
            registration.status = status_active
            registration.cost = 0
        else:
            registration = AllianceRegistration(
                id=None,
                alliance_id=alliance.id,
                land_id=land_id,
                army=normalized_army,
                status=status_active,
                cost=0,
                registration_time=now,
                created_at=now,
            )

        self.alliance_repo.save_land_registration(registration)

        self._record_activity(
            alliance_id=alliance.id,
            event_type="land_signup",
            actor_user_id=user_id,
            actor_name=self._member_display_name(member),
            target_name=f"土地{land_id}",
        )

        return {
            "ok": True,
            "data": {
                "land_id": land_id,
                "status": registration.status,
                "army": normalized_army,
                "army_label": self._army_label_from_string(normalized_army),
            },
        }

    def get_land_detail(self, land_id: int) -> dict:
        """土地详情查询：用于前端详情页展示土地属性与报名联盟名单。"""
        try:
            land_meta = self.WAR_LANDS.get(land_id)
            if not land_meta:
                return {"ok": False, "error": "未找到该土地"}

            # 显示所有活跃状态的报名记录（包括已报名、待审核、已确认、战斗中）
            statuses = [STATUS_REGISTERED, STATUS_PENDING, STATUS_CONFIRMED, STATUS_IN_BATTLE]
            registrations = self.alliance_repo.list_land_registrations_by_land(
                land_id, statuses=statuses
            )

            alliances = []
            seen_ids = set()
            for reg in registrations:
                if reg.alliance_id in seen_ids:
                    continue
                try:
                    alliance = self.alliance_repo.get_alliance_by_id(reg.alliance_id)
                    # 只添加存在的联盟
                    if alliance:
                        alliances.append(
                            {
                                "alliance_id": reg.alliance_id,
                                "name": alliance.name,
                            }
                        )
                    seen_ids.add(reg.alliance_id)
                except Exception as e:
                    # 如果查询联盟信息出错，跳过该联盟，不影响其他联盟的显示
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"查询联盟 {reg.alliance_id} 信息时出错: {e}")
                    continue

            data = {
                "land_id": land_id,
                "land_name": land_meta["land_name"],
                "buffs": land_meta.get("buffs", []),  # 安全获取buffs字段，如果不存在则返回空列表
                "alliances": alliances,
            }
            return {"ok": True, "data": data}
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception(f"获取土地 {land_id} 详情时出错: {e}")
            return {"ok": False, "error": f"获取土地详情失败: {str(e)}"}

    def list_war_lands(self, user_id: Optional[int] = None, army_type: Optional[str] = None) -> dict:
        """获取盟战土地/据点列表及其占领联盟信息
        
        根据用户的军队类型返回对应的目标：
        - 飞龙军：只返回土地（迷雾城1号土地、飞龙港1号土地）
        - 伏虎军：只返回据点（幻灵镇1号据点、定老城1号据点）
        
        如果未提供user_id和army_type，返回所有目标（用于管理界面）
        """
        # 确定要返回的土地/据点ID
        # 优先级：army_type 参数 > user_id 的实际军队类型
        # 这样可以确保飞龙军报名页面和伏虎军报名页面能够正确显示对应的目标
        if army_type:
            # 优先使用明确指定的军队类型参数（用于特定军队的报名页面）
            if army_type.lower() in ("dragon", "飞龙军", "1"):
                allowed_land_ids = self.DRAGON_ONLY_LANDS
            elif army_type.lower() in ("tiger", "伏虎军", "2"):
                allowed_land_ids = self.TIGER_ONLY_LANDS
            else:
                allowed_land_ids = set(self.WAR_LANDS.keys())  # 未知类型，返回所有
        elif user_id:
            # 如果没有指定army_type，则根据用户的实际军队类型确定
            member = self.alliance_repo.get_member(user_id)
            if member:
                # 根据成员的army_type确定
                if member.army_type == self.ARMY_DRAGON:
                    allowed_land_ids = self.DRAGON_ONLY_LANDS
                elif member.army_type == self.ARMY_TIGER:
                    allowed_land_ids = self.TIGER_ONLY_LANDS
                else:
                    # 未分配军队，根据等级自动判断
                    player = self.player_repo.get_by_id(user_id)
                    if player:
                        army_type_int = self._determine_army_type(player.level or 0)
                        allowed_land_ids = self.DRAGON_ONLY_LANDS if army_type_int == self.ARMY_DRAGON else self.TIGER_ONLY_LANDS
                    else:
                        allowed_land_ids = set()  # 玩家不存在，返回空列表
            else:
                # 未加入联盟，根据等级自动判断
                player = self.player_repo.get_by_id(user_id)
                if player:
                    army_type_int = self._determine_army_type(player.level or 0)
                    allowed_land_ids = self.DRAGON_ONLY_LANDS if army_type_int == self.ARMY_DRAGON else self.TIGER_ONLY_LANDS
                else:
                    allowed_land_ids = set()  # 玩家不存在，返回空列表
        else:
            # 未提供用户ID和军队类型，返回所有目标（用于管理界面）
            allowed_land_ids = set(self.WAR_LANDS.keys())
        
        lands = []
        for land_id, land_meta in self.WAR_LANDS.items():
            # 只返回允许的土地/据点
            if land_id not in allowed_land_ids:
                continue
            
            # 获取占领信息（只返回通过对战获胜的联盟，使用INNER JOIN确保联盟存在）
            occupation = self.alliance_repo.get_land_occupation(land_id)
            owner_name = occupation.get("alliance_name") if occupation else None
            
            # 获取报名联盟数量
            all_registrations = self.alliance_repo.list_land_registrations_by_land(land_id)
            # 只统计活跃状态的报名（已报名、待审核、已确认、战斗中）
            from domain.entities.alliance_registration import STATUS_REGISTERED, STATUS_PENDING, STATUS_CONFIRMED, STATUS_IN_BATTLE
            active_statuses = [STATUS_REGISTERED, STATUS_PENDING, STATUS_CONFIRMED, STATUS_IN_BATTLE]
            signup_count = len([r for r in all_registrations if r.status in active_statuses])
            
            lands.append({
                "id": land_id,
                "label": land_meta["land_name"],
                "owner": owner_name if owner_name else "无",
                "signup_count": signup_count,
                "land_type": land_meta.get("land_type", "land"),  # land 或 stronghold
            })
        
        return {"ok": True, "data": {"lands": lands}}

    def get_alliance_barracks(self, user_id: int) -> dict:
        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error

        dragon, tiger = self._fetch_army_members(alliance.id)
        return {
            "ok": True,
            "data": {
                "alliance_id": alliance.id,
                "dragon": [self._member_army_row(m) for m in dragon],
                "tiger": [self._member_army_row(m) for m in tiger],
            },
        }
    
    def manage_member_army(self, user_id: int, target_user_id: int, action: str, army_type: Optional[int] = None) -> dict:
        """
        管理成员的军队分配
        action: 'kick' (踢出到未分配) 或 'assign' (分配到军队)
        army_type: 当action='assign'时，1=飞龙军，2=伏虎军；当action='kick'时忽略，设为0
        """
        # 检查操作者权限
        actor = self.alliance_repo.get_member(user_id)
        if not actor:
            return {"ok": False, "error": "未加入联盟"}
        
        # 检查是否是盟主
        if actor.role != AllianceRules.ROLE_LEADER:
            return {"ok": False, "error": "只有盟主可以管理军队成员"}
        
        # 检查目标成员
        target = self.alliance_repo.get_member(target_user_id)
        if not target or target.alliance_id != actor.alliance_id:
            return {"ok": False, "error": "未找到该成员"}
        
        if actor.user_id == target_user_id:
            return {"ok": False, "error": "无法修改自己的军队分配"}
        
        # 执行操作
        if action == "kick":
            # 踢出：将army_type设为0（未分配）
            new_army_type = 0
            army_label = "未分配"
            action_label = "踢出"
        elif action == "assign":
            # 分配：根据成员等级自动决定军队类型
            # 如果指定了army_type，则使用指定的；否则根据等级自动决定
            player = self.player_repo.get_by_id(target_user_id)
            if not player:
                return {"ok": False, "error": "玩家不存在"}
            
            if army_type is not None:
                if army_type not in (self.ARMY_DRAGON, self.ARMY_TIGER):
                    return {"ok": False, "error": "无效的军队类型"}
                new_army_type = army_type
                # 检查等级限制：40级及以下只能加入伏虎军
                level = player.level or 0
                if new_army_type == self.ARMY_DRAGON and level <= self.ARMY_LEVEL_THRESHOLD:
                    return {"ok": False, "error": "40级及以下的成员只能加入伏虎军"}
            else:
                # 根据成员等级自动决定：40级及以下伏虎军，40级以上飞龙军
                level = player.level or 0
                new_army_type = self._determine_army_type(level)
            
            army_label = "飞龙军" if new_army_type == self.ARMY_DRAGON else "伏虎军"
            action_label = "分配到"
        else:
            return {"ok": False, "error": "无效的操作类型"}
        
        # 更新成员的军队类型
        self.alliance_repo.update_member_army(target_user_id, new_army_type)
        
        # 同步alliance_army_assignments表
        if new_army_type == 0:
            # 踢出时，从alliance_army_assignments表删除记录
            from infrastructure.db.connection import execute_update
            execute_update(
                "DELETE FROM alliance_army_assignments WHERE alliance_id = %s AND user_id = %s",
                (actor.alliance_id, target_user_id)
            )
        else:
            # 分配时，更新或插入alliance_army_assignments表
            army_str = "dragon" if new_army_type == self.ARMY_DRAGON else "tiger"
            self.alliance_repo.upsert_army_assignment(actor.alliance_id, target_user_id, army_str)
        
        # 记录动态
        target_name = target.nickname or f"玩家{target_user_id}"
        self._record_activity(
            alliance_id=actor.alliance_id,
            event_type="army_manage",
            actor_user_id=user_id,
            actor_name=self._member_display_name(actor),
            target_name=target_name,
            item_name=f"{action_label}{army_label}",
        )
        
        return {
            "ok": True,
            "message": f"已将{target_name}{action_label}{army_label}",
        }

    def get_war_info(self, user_id: int) -> dict:
        """获取盟战信息（允许未加入联盟的用户查看）"""
        player = self.player_repo.get_by_id(user_id)
        if not player:
            return {"ok": False, "error": "玩家不存在"}

        # 尝试获取联盟信息，但不强制要求
        member = self.alliance_repo.get_member(user_id)
        alliance = None
        if member:
            alliance = self.alliance_repo.get_alliance_by_id(member.alliance_id)

        # 构建基础数据
        recommended_army = self._determine_army_type(player.level or 0)
        assigned_army = 0
        signed_up = False
        dragon_count = 0
        tiger_count = 0
        total_signed = 0
        dragon_members = []
        tiger_members = []

        checked_in = False
        dragon_reg = None
        tiger_reg = None
        
        if alliance and member:
            dragon, tiger = self._fetch_army_members(alliance.id)
            assigned_army = member.army_type or 0
            signed_up = assigned_army != 0
            dragon_count = len(dragon)
            tiger_count = len(tiger)
            total_signed = len(dragon) + len(tiger)
            dragon_members = [self._member_army_row(m) for m in dragon]
            tiger_members = [self._member_army_row(m) for m in tiger]
            
            # 获取攻城目标信息并检查是否已签到
            active_registration = None
            for land_id in self.DRAGON_ONLY_LANDS:
                reg = self.alliance_repo.get_land_registration(alliance.id, land_id)
                if reg and reg.is_active():
                    dragon_reg = {"land_id": land_id, "land_name": self.WAR_LANDS.get(land_id, {}).get("land_name", f"土地{land_id}")}
                    if not active_registration:
                        active_registration = reg
                    break
            for land_id in self.TIGER_ONLY_LANDS:
                reg = self.alliance_repo.get_land_registration(alliance.id, land_id)
                if reg and reg.is_active():
                    tiger_reg = {"land_id": land_id, "land_name": self.WAR_LANDS.get(land_id, {}).get("land_name", f"据点{land_id}")}
                    if not active_registration:
                        active_registration = reg
                    break
            
            # 检查是否已签到（基于当前活跃的报名记录）
            if signed_up and active_registration and active_registration.id:
                checked_in = self.alliance_repo.has_war_checkin(active_registration.id, user_id)

        schedule_payload = self._build_war_schedule_payload()
        
        # 计算盟战届次（按照实际开战次数）
        war_session_number = self._get_war_session_number()

        # 获取用户角色（用于前端权限控制）
        user_role = None
        if member:
            user_role = member.role
        
        return {
            "ok": True,
            "data": {
                "personal": {
                    "user_id": user_id,
                    "nickname": player.nickname or f"玩家{user_id}",
                    "level": player.level or 1,
                    "signed_up": signed_up,
                    "checked_in": checked_in,
                    "current_army": assigned_army,
                    "current_army_label": self._army_label(assigned_army) if assigned_army else "未报名",
                    "recommended_army": recommended_army,
                    "recommended_army_label": self._army_label(recommended_army),
                    "role": user_role,  # 添加角色信息，用于前端权限控制
                },
                "statistics": {
                    "dragon_count": dragon_count,
                    "tiger_count": tiger_count,
                    "total_signed": total_signed,
                    "threshold_level": self.ARMY_LEVEL_THRESHOLD,
                },
                "armies": {
                    "dragon": dragon_members,
                    "tiger": tiger_members,
                },
                "schedule": schedule_payload,
                "targets": {
                    "dragon_registration": dragon_reg,
                    "tiger_registration": tiger_reg,
                },
                "war_session_number": war_session_number,
            },
        }

    def get_war_honor_status(self, user_id: int) -> dict:
        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error

        effects_config, _ = self._ensure_honor_effects()
        current_honor, historical_honor = self.alliance_repo.get_alliance_war_points(alliance.id)
        active_records = self.alliance_repo.get_active_honor_effects(alliance.id)
        active_by_key = {record.get("effect_key"): record for record in active_records}
        xp_effect_active = any(record.get("effect_type") == "xp" for record in active_records)
        can_manage = member.role in (
            AllianceRules.ROLE_LEADER,
            AllianceRules.ROLE_VICE_LEADER,
        )

        effects_payload: List[Dict[str, Any]] = []
        for cfg in effects_config:
            key = cfg.get("key")
            if not key:
                continue
            record = active_by_key.get(key)
            is_active = record is not None
            reason = ""
            can_exchange = True
            if not can_manage:
                can_exchange = False
                reason = "仅盟主和副盟主可兑换"
            elif is_active:
                can_exchange = False
                reason = "效果正在生效"
            elif cfg.get("type") == "xp" and xp_effect_active:
                can_exchange = False
                reason = "已有经验加成生效"
            elif cfg.get("cost", 0) > current_honor:
                can_exchange = False
                reason = "战功不足"

            effects_payload.append(
                {
                    "key": key,
                    "name": cfg.get("name"),
                    "type": cfg.get("type"),
                    "description": cfg.get("description"),
                    "bonus": cfg.get("bonus"),
                    "cost": cfg.get("cost", 0),
                    "active": is_active,
                    "expiresAt": self._datetime_to_iso(record.get("expires_at")) if record else None,
                    "startedAt": self._datetime_to_iso(record.get("started_at")) if record else None,
                    "canExchange": can_exchange,
                    "reason": reason if not can_exchange else "",
                }
            )

        return {
            "ok": True,
            "data": {
                "currentHonor": current_honor,
                "historicalHonor": historical_honor,
                "effects": effects_payload,
            },
        }

    def exchange_war_honor(self, user_id: int, effect_key: str) -> dict:
        effect_key = (effect_key or "").strip()
        if not effect_key:
            return {"ok": False, "error": "请选择要兑换的战功效果"}

        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error

        if member.role not in (AllianceRules.ROLE_LEADER, AllianceRules.ROLE_VICE_LEADER):
            return {"ok": False, "error": "只有盟主和副盟主可以兑换"}

        _, effects_map = self._ensure_honor_effects()
        config = effects_map.get(effect_key)
        if not config:
            return {"ok": False, "error": "未知的战功效果"}

        current_honor, _ = self.alliance_repo.get_alliance_war_points(alliance.id)
        cost = int(config.get("cost", 0) or 0)
        if cost <= 0:
            return {"ok": False, "error": "该战功效果配置有误"}
        if current_honor < cost:
            return {"ok": False, "error": "战功不足"}

        active_effects = self.alliance_repo.get_active_honor_effects(alliance.id)
        same_effect = next((record for record in active_effects if record.get("effect_key") == effect_key), None)
        if same_effect:
            return {"ok": False, "error": "该效果正在生效，请等待结束后再兑换"}
        if config.get("type") == "xp":
            xp_active = any(record.get("effect_type") == "xp" for record in active_effects)
            if xp_active:
                return {"ok": False, "error": "已有经验加成生效，无法同时兑换其他经验效果"}

        now = datetime.utcnow()
        expires_at = now + timedelta(hours=self.HONOR_EFFECT_DURATION_HOURS)

        deducted = False
        try:
            self.alliance_repo.update_alliance_war_points(alliance.id, -cost)
            deducted = True
            self.alliance_repo.insert_honor_effect(
                alliance_id=alliance.id,
                effect_key=effect_key,
                effect_type=config.get("type", "unknown"),
                cost=cost,
                started_at=now,
                expires_at=expires_at,
                created_by=user_id,
            )
        except Exception as exc:
            if deducted:
                # 尝试回滚战功扣减，确保前端显示正确
                self.alliance_repo.update_alliance_war_points(alliance.id, cost)
            return {"ok": False, "error": f"兑换失败：{str(exc)}"}

        remaining_honor = current_honor - cost
        return {
            "ok": True,
            "data": {
                "effect": {
                    "key": config.get("key"),
                    "name": config.get("name"),
                    "type": config.get("type"),
                    "description": config.get("description"),
                    "bonus": config.get("bonus"),
                    "cost": cost,
                },
                "expiresAt": self._datetime_to_iso(expires_at),
                "startedAt": self._datetime_to_iso(now),
                "remainingHonor": remaining_honor,
            },
        }

    def get_war_live_feed(self, user_id: int) -> dict:
        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error

        battles = self.alliance_repo.list_alliance_battles(alliance.id)
        if not battles:
            return {"ok": True, "data": {"battles": []}}

        registrations_cache: Dict[int, AllianceRegistration] = {}
        alliance_cache: Dict[int, Alliance] = {}
        results = []

        for battle in battles:
            land_meta = self.WAR_LANDS.get(battle.land_id, {})
            land_name = land_meta.get("land_name", f"未知土地{battle.land_id}")

            left_reg = self._get_cached_registration(battle.left_registration_id, registrations_cache)
            right_reg = self._get_cached_registration(battle.right_registration_id, registrations_cache)
            if not left_reg or not right_reg:
                continue

            is_left = left_reg.alliance_id == alliance.id
            own_reg = left_reg if is_left else right_reg
            opponent_reg = right_reg if is_left else left_reg

            opponent = self._get_cached_alliance(opponent_reg.alliance_id, alliance_cache)
            opponent_name = opponent.name if opponent else f"联盟{opponent_reg.alliance_id}"

            result_label = self._derive_battle_result(own_reg.status)

            results.append(
                {
                    "battle_id": battle.id,
                    "land_id": battle.land_id,
                    "land_name": land_name,
                    "opponent_alliance_name": opponent_name,
                    "phase": battle.phase,
                    "current_round": battle.current_round,
                    "result": result_label,
                }
            )

        return {"ok": True, "data": {"battles": results}}

    def get_chat_messages(self, user_id: int) -> dict:
        """获取联盟聊天消息"""
        member = self.alliance_repo.get_member(user_id)
        if not member:
            return {"ok": False, "error": "未加入联盟"}
        
        messages = self.alliance_repo.get_chat_messages(member.alliance_id)
        return {
            "ok": True,
            "messages": [
                {
                    "id": m.id,
                    "user_id": m.user_id,
                    "nickname": m.nickname or f"玩家{m.user_id}",
                    "content": m.content,
                    "created_at": m.created_at.isoformat() if m.created_at else ""
                }
                for m in messages
            ]
        }

    def send_chat_message(self, user_id: int, content: str) -> dict:
        """发送联盟聊天消息"""
        if not content.strip():
            return {"ok": False, "error": "内容不能为空"}
            
        member = self.alliance_repo.get_member(user_id)
        if not member:
            return {"ok": False, "error": "未加入联盟"}
            
        message = AllianceChatMessage(
            alliance_id=member.alliance_id,
            user_id=user_id,
            content=content.strip()
        )
        self.alliance_repo.add_chat_message(message)
        
        return {"ok": True}

    def _build_inventory_items_for_storage(self, user_id: int) -> List[dict]:
        inventory_items = self.inventory_service.get_inventory(user_id, include_temp=False)
        aggregated: Dict[int, dict] = {}
        for entry in inventory_items:
            inv_item = entry.inv_item
            item_info = entry.item_info
            bucket = aggregated.get(inv_item.item_id)
            if not bucket:
                bucket = {
                    "itemId": inv_item.item_id,
                    "name": item_info.name if item_info else f"物品{inv_item.item_id}",
                    "description": item_info.description if item_info else "",
                    "type": item_info.type if item_info else "material",
                    "stackable": item_info.stackable if item_info else True,
                    "maxStack": PlayerBag.MAX_STACK_SIZE,
                    "quantity": 0,
                }
                aggregated[inv_item.item_id] = bucket
            bucket["quantity"] += inv_item.quantity
        return sorted(aggregated.values(), key=lambda item: (-item["quantity"], item["itemId"]))

    def _build_storage_payload(
        self,
        records: List[AllianceItemStorage],
        user_id: int,
    ) -> Tuple[List[dict], List[dict]]:
        items: List[dict] = []
        own_items: List[dict] = []
        template_cache: Dict[int, object] = {}
        for record in records:
            template = template_cache.get(record.item_id)
            if template is None:
                template = self.inventory_service.item_repo.get_by_id(record.item_id)
                template_cache[record.item_id] = template
            name = getattr(template, "name", None) or f"物品{record.item_id}"
            description = getattr(template, "description", None) or ""
            item_type = getattr(template, "type", None) or "material"
            row = {
                "storageId": record.id,
                "itemId": record.item_id,
                "quantity": record.quantity,
                "ownerUserId": record.owner_user_id,
                "ownerIsSelf": record.owner_user_id == user_id,
                "storedAt": self._format_datetime(record.stored_at),
                "name": name,
                "description": description,
                "type": item_type,
            }
            items.append(row)
            if record.owner_user_id == user_id:
                own_items.append(row)
        items.sort(key=lambda entry: (entry["ownerUserId"], entry["itemId"]))
        own_items.sort(key=lambda entry: entry["itemId"])
        return items, own_items

    def _has_joined_training_today(self, alliance_id: int, user_id: int) -> bool:
        record = self.alliance_repo.get_training_participation_today(alliance_id, user_id)
        return record is not None

    def _get_building_level_map(self, alliance_id: int) -> Dict[str, int]:
        records = self.alliance_repo.get_alliance_buildings(alliance_id)
        data = {record.building_key: record.level for record in records}
        for key in AllianceRules.BUILDING_KEYS:
            data.setdefault(key, 1)
        return data

    def _get_room_end_time(self, room: AllianceTrainingRoom) -> Optional[datetime]:
        # 如果房间是等待状态，返回None（还未开始）
        room_status = getattr(room, 'status', None) or "ongoing"
        if room_status == "waiting":
            return None
        # 如果房间已开始，从创建时间计算（如果房间状态是ongoing，使用创建时间）
        if not room.created_at:
            return datetime.utcnow()
        # 如果房间状态是ongoing，从创建时间计算（因为创建时如果满足2人会自动开始）
        # 根据房间的修行时长计算结束时间
        duration_hours = getattr(room, "duration_hours", 2) or 2  # 兼容旧数据，默认2小时
        duration_minutes = AllianceRules.get_training_duration_minutes(duration_hours)
        if room.created_at:
            return room.created_at + timedelta(minutes=duration_minutes)
        return None

    def _is_room_finished(self, room: AllianceTrainingRoom, now: Optional[datetime] = None) -> bool:
        room_status = getattr(room, 'status', None) or "ongoing"
        if room_status == "completed":
            return True
        if room_status == "waiting":
            return False
        if not now:
            now = datetime.utcnow()
        end_time = self._get_room_end_time(room)
        if end_time is None:
            return False
        return now >= end_time

    def _format_datetime(self, value: Optional[datetime]) -> str:
        if not value:
            return ""
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M")
        return str(value)

    def _next_war_start(self, now: Optional[datetime] = None) -> datetime:
        if not now:
            # 使用中国时区（UTC+8）的当前时间
            china_tz = timezone(timedelta(hours=8))
            now = datetime.now(china_tz)
        else:
            # 如果传入的now没有时区信息，假设它是UTC时间，转换为中国时区
            if now.tzinfo is None:
                utc_tz = timezone.utc
                china_tz = timezone(timedelta(hours=8))
                now = now.replace(tzinfo=utc_tz).astimezone(china_tz)
        
        # 盟战开始时间：周三20:00和周六20:00（中国时区）
        war_weekdays = {self.WAR_FIRST_END_WEEKDAY, self.WAR_SECOND_END_WEEKDAY}  # 周三和周六 (2, 5)
        
        # 计算今天的20:00时间（中国时区）
        today_at_20 = now.replace(hour=self.WAR_BATTLE_START_HOUR, minute=0, second=0, microsecond=0)
        
        # 如果今天是开战日且还没到20:00，返回今天的20:00
        if today_at_20.weekday() in war_weekdays and today_at_20 > now:
            return today_at_20
        
        # 如果今天是开战日但已经过了20:00，或者今天不是开战日，从明天开始查找
        # 从明天开始查找下一个开战日
        for day_offset in range(1, 8):
            candidate_date = (now + timedelta(days=day_offset)).date()
            candidate = datetime(
                candidate_date.year,
                candidate_date.month,
                candidate_date.day,
                self.WAR_BATTLE_START_HOUR,
                0,
                0,
                tzinfo=now.tzinfo,
            )
            if candidate.weekday() in war_weekdays:
                return candidate
        
        # 如果8天内没找到（理论上不应该发生），返回下周三
        days_until_wednesday = (self.WAR_FIRST_END_WEEKDAY - now.weekday() + 7) % 7
        if days_until_wednesday == 0:
            days_until_wednesday = 7  # 如果今天是周三，返回下周三
        next_wednesday_date = (now + timedelta(days=days_until_wednesday)).date()
        return datetime(
            next_wednesday_date.year,
            next_wednesday_date.month,
            next_wednesday_date.day,
            self.WAR_BATTLE_START_HOUR,
            0,
            0,
            tzinfo=now.tzinfo,
        )

    def _build_war_schedule_payload(self, now: Optional[datetime] = None) -> Dict[str, Any]:
        if not now:
            # 使用中国时区（UTC+8）的当前时间
            china_tz = timezone(timedelta(hours=8))
            now = datetime.now(china_tz)
        else:
            # 如果传入的now没有时区信息，假设它是UTC时间，转换为中国时区
            if now.tzinfo is None:
                utc_tz = timezone.utc
                china_tz = timezone(timedelta(hours=8))
                now = now.replace(tzinfo=utc_tz).astimezone(china_tz)
        
        next_start = self._next_war_start(now)
        countdown_seconds = max(0, int((next_start - now).total_seconds()))
        # 盟战开始时间：周三20:00和周六20:00
        war_weekdays = [self.WAR_FIRST_END_WEEKDAY, self.WAR_SECOND_END_WEEKDAY]  # 周三和周六
        detail = [
            {
                "weekday": day,
                "label": self._weekday_label(day),
                "hour": self.WAR_BATTLE_START_HOUR,
                "minute": 0,
            }
            for day in war_weekdays
        ]
        # 将时区时间转换为UTC时间返回（前端会转换为本地时间显示）
        next_start_utc = next_start.astimezone(timezone.utc) if next_start.tzinfo else next_start
        # 确保返回正确的ISO格式（UTC时间，以Z结尾）
        if next_start_utc.tzinfo:
            # 如果有时区信息，转换为UTC并格式化为标准ISO格式
            next_start_utc = next_start_utc.replace(microsecond=0)
            iso_str = next_start_utc.isoformat()
            # 如果isoformat()返回的是+00:00格式，替换为Z
            if iso_str.endswith('+00:00'):
                iso_str = iso_str[:-6] + 'Z'
            elif not iso_str.endswith('Z'):
                # 如果没有Z，添加Z（假设已经是UTC时间）
                iso_str = iso_str + 'Z'
        else:
            # 如果没有时区信息，假设是UTC并添加Z
            iso_str = next_start_utc.replace(microsecond=0).isoformat() + 'Z'
        
        return {
            "nextWarTime": iso_str,
            "countdownSeconds": countdown_seconds,
            "weekdays": war_weekdays,
            "weekdaysDetail": detail,
            "startHour": self.WAR_BATTLE_START_HOUR,
            "startMinute": 0,
        }

    def _weekday_label(self, weekday: int) -> str:
        labels = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        return labels[weekday % 7]
    
    def _get_war_session_number(self) -> int:
        """获取盟战届次（从配置表读取，初始为1）"""
        from infrastructure.db.connection import execute_query, execute_update
        # 尝试从配置表读取当前届次
        sql = """
            SELECT session_number FROM alliance_war_session_config 
            WHERE config_key = 'current_session' 
            LIMIT 1
        """
        rows = execute_query(sql)
        if rows and rows[0].get('session_number'):
            return rows[0]['session_number']
        # 如果配置不存在，创建并初始化为1
        create_sql = """
            INSERT INTO alliance_war_session_config (config_key, session_number, updated_at)
            VALUES ('current_session', 1, NOW())
            ON DUPLICATE KEY UPDATE session_number = 1
        """
        execute_update(create_sql)
        return 1
    
    def _increment_war_session_number(self) -> int:
        """递增盟战届次（在开战结束后调用）"""
        from infrastructure.db.connection import execute_update, execute_query
        # 递增届次
        update_sql = """
            INSERT INTO alliance_war_session_config (config_key, session_number, updated_at)
            VALUES ('current_session', 1, NOW())
            ON DUPLICATE KEY UPDATE 
                session_number = session_number + 1,
                updated_at = NOW()
        """
        execute_update(update_sql)
        # 返回新的届次
        sql = """
            SELECT session_number FROM alliance_war_session_config 
            WHERE config_key = 'current_session' 
            LIMIT 1
        """
        rows = execute_query(sql)
        if rows and rows[0].get('session_number'):
            return rows[0]['session_number']
        return 1

    def _determine_army_type(self, level: int) -> int:
        """根据等级确定军队类型：40级以上飞龙军，40级及以下伏虎军"""
        if level > self.ARMY_LEVEL_THRESHOLD:
            return self.ARMY_DRAGON
        return self.ARMY_TIGER

    def _is_war_time(self, now: Optional[datetime] = None) -> tuple:
        """检查当前是否在盟战时间范围内
        返回: (is_war_period, phase, status)
        phase: 'first' 或 'second' 或 None
        status: 'signup' (报名签到), 'battle' (对战), 'result' (结果展示), 'rest' (休战)
        """
        if now is None:
            now = datetime.utcnow()
        weekday = now.weekday()  # 0=周一, 6=周日
        hour = now.hour

        # 周日休战
        if weekday == 6:
            return (False, None, "rest")

        # 第一次盟战：周一0:00-周三24:00
        if weekday == self.WAR_FIRST_START_WEEKDAY:  # 周一
            if hour < self.WAR_BATTLE_START_HOUR:
                return (True, "first", "signup")
            elif hour < self.WAR_BATTLE_END_HOUR:
                return (True, "first", "battle")
            elif hour < self.WAR_RESULT_END_HOUR:
                return (True, "first", "result")
            else:
                return (True, "first", "signup")  # 跨天
        elif weekday == self.WAR_FIRST_START_WEEKDAY + 1:  # 周二
            if hour < self.WAR_BATTLE_START_HOUR:
                return (True, "first", "signup")
            elif hour < self.WAR_BATTLE_END_HOUR:
                return (True, "first", "battle")
            elif hour < self.WAR_RESULT_END_HOUR:
                return (True, "first", "result")
            else:
                return (True, "first", "signup")
        elif weekday == self.WAR_FIRST_END_WEEKDAY:  # 周三
            if hour < self.WAR_BATTLE_START_HOUR:
                return (True, "first", "signup")
            elif hour < self.WAR_BATTLE_END_HOUR:
                return (True, "first", "battle")
            elif hour < self.WAR_RESULT_END_HOUR:
                return (True, "first", "result")
            else:
                return (False, None, "rest")  # 周三24:00后进入休战

        # 第二次盟战：周四0:00-周六24:00
        elif weekday == self.WAR_SECOND_START_WEEKDAY:  # 周四
            if hour < self.WAR_BATTLE_START_HOUR:
                return (True, "second", "signup")
            elif hour < self.WAR_BATTLE_END_HOUR:
                return (True, "second", "battle")
            elif hour < self.WAR_RESULT_END_HOUR:
                return (True, "second", "result")
            else:
                return (True, "second", "signup")
        elif weekday == self.WAR_SECOND_START_WEEKDAY + 1:  # 周五
            if hour < self.WAR_BATTLE_START_HOUR:
                return (True, "second", "signup")
            elif hour < self.WAR_BATTLE_END_HOUR:
                return (True, "second", "battle")
            elif hour < self.WAR_RESULT_END_HOUR:
                return (True, "second", "result")
            else:
                return (True, "second", "signup")
        elif weekday == self.WAR_SECOND_END_WEEKDAY:  # 周六
            if hour < self.WAR_BATTLE_START_HOUR:
                return (True, "second", "signup")
            elif hour < self.WAR_BATTLE_END_HOUR:
                return (True, "second", "battle")
            elif hour < self.WAR_RESULT_END_HOUR:
                return (True, "second", "result")
            else:
                return (False, None, "rest")  # 周六24:00后进入休战

        return (False, None, "rest")

    def war_checkin(self, user_id: int) -> dict:
        """盟战签到：在签到时间内签到，获得30000铜钱"""
        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error

        now = datetime.utcnow()
        is_war, phase, status = self._is_war_time(now)
        if not is_war or status != "signup":
            return {"ok": False, "error": "当前不在盟战签到时间内"}

        # 检查联盟是否已报名土地或据点，并获取报名记录
        all_land_ids = list(self.DRAGON_ONLY_LANDS) + list(self.TIGER_ONLY_LANDS)
        active_registration = None
        for land_id in all_land_ids:
            reg = self.alliance_repo.get_land_registration(alliance.id, land_id)
            if reg and reg.is_active():
                active_registration = reg
                break
        
        if not active_registration:
            return {"ok": False, "error": "联盟尚未报名土地或据点，请先由盟主或副盟主报名"}

        # 检查玩家是否已报名军队
        if not member.army_type:
            return {"ok": False, "error": "请先报名加入军队"}

        # 检查是否已为该报名记录签到（每次报名只能签到一次）
        if not active_registration.id:
            return {"ok": False, "error": "报名记录异常，无法签到"}
        
        if self.alliance_repo.has_war_checkin(active_registration.id, user_id):
            return {"ok": False, "error": "本次报名已签到，请等待盟战结束后再次报名才能签到"}

        # 发放奖励
        player = self.player_repo.get_by_id(user_id)
        if not player:
            return {"ok": False, "error": "玩家不存在"}

        # 增加铜钱（兼容新旧字段）
        current_copper = getattr(player, "copper", 0) or 0
        current_gold = getattr(player, "gold", 0) or 0
        new_copper = current_copper + self.WAR_CHECKIN_REWARD_COPPER
        player.copper = new_copper
        player.gold = current_gold + self.WAR_CHECKIN_REWARD_COPPER  # 兼容旧字段
        self.player_repo.save(player)

        # 记录签到（关联到报名记录）
        weekday = now.weekday()
        checkin_date = now.date()
        self.alliance_repo.add_war_checkin(
            alliance.id, user_id, active_registration.id, phase, weekday, checkin_date, self.WAR_CHECKIN_REWARD_COPPER
        )

        self._record_activity(
            alliance_id=alliance.id,
            event_type="war_checkin",
            actor_user_id=user_id,
            actor_name=self._member_display_name(member),
            item_name="铜钱",
            item_quantity=self.WAR_CHECKIN_REWARD_COPPER,
        )

        return {
            "ok": True,
            "message": f"签到成功，获得{self.WAR_CHECKIN_REWARD_COPPER}铜钱",
            "copper_gained": self.WAR_CHECKIN_REWARD_COPPER,
            "total_copper": new_copper,
        }

    def _normalize_army_choice(self, army: Optional[str], player_level: int) -> str:
        if isinstance(army, str):
            army_lower = army.lower()
            if army_lower in (AllianceRules.ARMY_DRAGON, AllianceRules.ARMY_TIGER):
                return army_lower
        return (
            AllianceRules.ARMY_DRAGON
            if self._determine_army_type(player_level) == self.ARMY_DRAGON
            else AllianceRules.ARMY_TIGER
        )

    def _army_label(self, army_type: int) -> str:
        if army_type == self.ARMY_DRAGON:
            return "飞龙军"
        if army_type == self.ARMY_TIGER:
            return "伏虎军"
        return "未报名"

    def _army_label_from_string(self, army: Optional[str]) -> str:
        return AllianceRules.army_label_for_key(army)

    def _member_army_row(self, member: AllianceMember) -> dict:
        return {
            "user_id": member.user_id,
            "nickname": member.nickname or f"玩家{member.user_id}",
            "level": member.level or 1,
            "battle_power": member.battle_power or 0,
            "army_type": member.army_type or 0,
            "army_label": self._army_label(member.army_type or 0),
        }

    def _fetch_army_members(self, alliance_id: int) -> Tuple[List[AllianceMember], List[AllianceMember]]:
        dragon = self.alliance_repo.get_members_by_army(alliance_id, self.ARMY_DRAGON)
        tiger = self.alliance_repo.get_members_by_army(alliance_id, self.ARMY_TIGER)
        return dragon, tiger

    def _sync_member_army(self, member: AllianceMember, level: int) -> None:
        """同步成员军队类型：根据等级自动分配（40级及以下伏虎军，40级以上飞龙军）
        
        规则：
        - 如果成员未分配（army_type=0），自动根据等级分配
        - 如果成员已分配，但等级变化导致需要重新分配，则自动重新分配
        - 特例：如果玩家加入时为40级（分到伏虎军），后面升级为43级，系统会将其重新分到飞龙军
        """
        expected = self._determine_army_type(level)
        
        # 如果未分配或需要重新分配，则更新
        if member.army_type == 0 or member.army_type != expected:
            self.alliance_repo.update_member_army(member.user_id, expected)
            member.army_type = expected
    
    def sync_member_army_by_user_id(self, user_id: int) -> None:
        """根据用户ID同步军队类型（用于玩家升级后自动同步）"""
        member = self.alliance_repo.get_member(user_id)
        if not member:
            return  # 未加入联盟，无需同步
        
        player = self.player_repo.get_by_id(user_id)
        if not player:
            return  # 玩家不存在
        
        self._sync_member_army(member, player.level or 0)

    def _get_cached_registration(
        self, registration_id: Optional[int], cache: Dict[int, AllianceRegistration]
    ) -> Optional[AllianceRegistration]:
        if not registration_id:
            return None
        if registration_id not in cache:
            cache[registration_id] = self.alliance_repo.get_land_registration_by_id(registration_id)
        return cache[registration_id]

    def _get_cached_alliance(self, alliance_id: int, cache: Dict[int, Alliance]) -> Optional[Alliance]:
        if alliance_id not in cache:
            cache[alliance_id] = self.alliance_repo.get_alliance_by_id(alliance_id)
        return cache[alliance_id]

    def _ensure_honor_effects(self) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
        if self._honor_effects_cache is not None and self._honor_effects_map is not None:
            return self._honor_effects_cache, self._honor_effects_map

        config_path = Path(__file__).resolve().parents[2] / "configs" / "alliance_honor_effects.json"
        try:
            with config_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    data = []
        except FileNotFoundError:
            data = []
        except json.JSONDecodeError:
            data = []

        effect_map: Dict[str, Dict[str, Any]] = {}
        for entry in data:
            key = entry.get("key")
            if key:
                effect_map[key] = entry
        self._honor_effects_cache = data
        self._honor_effects_map = effect_map
        return data, effect_map

    def _datetime_to_iso(self, value: Optional[Any]) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, str):
            return value
        if isinstance(value, datetime):
            return value.replace(microsecond=0).isoformat() + "Z"
        return str(value)

    def _derive_battle_result(self, status: Optional[int]) -> str:
        if status == STATUS_VICTOR:
            return "胜利"
        if status == STATUS_ELIMINATED:
            return "战败"
        return "进行中"

    def _record_activity(
        self,
        alliance_id: int,
        event_type: str,
        actor_user_id: Optional[int] = None,
        actor_name: Optional[str] = None,
        target_user_id: Optional[int] = None,
        target_name: Optional[str] = None,
        item_name: Optional[str] = None,
        item_quantity: Optional[int] = None,
    ) -> None:
        activity = AllianceActivity(
            id=None,
            alliance_id=alliance_id,
            event_type=event_type,
            actor_user_id=actor_user_id,
            actor_name=actor_name,
            target_user_id=target_user_id,
            target_name=target_name,
            item_name=item_name,
            item_quantity=item_quantity,
            created_at=None,  # 不设置时间，让数据库使用NOW()（本地时间），保持一致性
        )
        try:
            self.alliance_repo.add_activity(activity)
        except Exception:
            # 写入动态失败不影响主流程
            pass

    def _member_display_name(self, member: Optional[AllianceMember]) -> str:
        if not member:
            return ""
        return member.nickname or f"玩家{member.user_id}"

    def _player_display_name(self, player) -> str:
        if not player:
            return ""
        nickname = getattr(player, "nickname", None)
        user_id = getattr(player, "user_id", None) or getattr(player, "id", None)
        return nickname or (user_id and f"玩家{user_id}") or ""

    def exchange_war_honor_item(self, user_id: int, exchange_type: str) -> dict:
        """战功兑换物品：盟主或副盟主可以将盟战战功兑换为相应的奖品（2战功=1焚火晶，4战功=1金袋，6战功=1000繁荣度）"""
        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error

        if member.role not in (AllianceRules.ROLE_LEADER, AllianceRules.ROLE_VICE_LEADER):
            return {"ok": False, "error": "只有盟主或副盟主可以兑换战功"}

        # 获取兑换规则
        rule = self.WAR_HONOR_EXCHANGE_RULES.get(exchange_type)
        if not rule:
            return {"ok": False, "error": "无效的兑换类型"}

        # 获取当前战功
        current_honor, _ = self.alliance_repo.get_alliance_war_points(alliance.id)
        
        # 检查战功是否足够
        if current_honor < rule["honor"]:
            return {"ok": False, "error": f"战功不足，需要{rule['honor']}战功"}

        # 扣除战功
        new_honor = current_honor - rule["honor"]
        from infrastructure.db.connection import execute_update
        update_sql = "UPDATE alliances SET war_honor = %s WHERE id = %s"
        
        exchange_type_internal = rule.get("type", "item")
        
        # 根据兑换类型处理
        if exchange_type_internal == "prosperity":
            # 兑换繁荣度
            prosperity_delta = rule.get("prosperity", 0)
            self.alliance_repo.update_alliance_resources(alliance.id, funds_delta=0, prosperity_delta=prosperity_delta)
            execute_update(update_sql, (new_honor, alliance.id))
            
            # 记录兑换（繁荣度使用item_id=0表示）
            self.alliance_repo.add_war_honor_exchange(
                alliance.id, user_id, exchange_type, rule["honor"],
                0, rule["item_name"], rule["quantity"]
            )
            
            self._record_activity(
                alliance_id=alliance.id,
                event_type="war_honor_exchange",
                actor_user_id=user_id,
                actor_name=self._member_display_name(member),
                item_name=rule["item_name"],
                item_quantity=rule["quantity"],
            )
            
            return {
                "ok": True,
                "message": f"兑换成功，联盟获得{rule['quantity']}{rule['item_name']}",
                "honor_cost": rule["honor"],
                "remaining_honor": new_honor,
                "prosperity": prosperity_delta,
            }
        else:
            # 兑换物品
            self.alliance_repo.update_alliance_resources(alliance.id, funds_delta=0, prosperity_delta=0)
            execute_update(update_sql, (new_honor, alliance.id))

            # 发放物品
            try:
                self.inventory_service.add_item(user_id, rule["item_id"], rule["quantity"])
            except Exception as e:
                # 如果发放失败，回滚战功
                execute_update(update_sql, (current_honor, alliance.id))
                return {"ok": False, "error": f"发放物品失败：{str(e)}"}

            # 记录兑换
            self.alliance_repo.add_war_honor_exchange(
                alliance.id, user_id, exchange_type, rule["honor"],
                rule["item_id"], rule["item_name"], rule["quantity"]
            )

            self._record_activity(
                alliance_id=alliance.id,
                event_type="war_honor_exchange",
                actor_user_id=user_id,
                actor_name=self._member_display_name(member),
                item_name=rule["item_name"],
                item_quantity=rule["quantity"],
            )

            return {
                "ok": True,
                "message": f"兑换成功，获得{rule['quantity']}x{rule['item_name']}",
                "honor_cost": rule["honor"],
                "remaining_honor": new_honor,
                "item": {
                    "id": rule["item_id"],
                    "name": rule["item_name"],
                    "quantity": rule["quantity"],
                },
            }

    def get_war_battle_records(self, user_id: int, limit: int = 50) -> dict:
        """获取联盟战绩：查看每次盟战联盟与其他联盟的对战情况"""
        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error

        try:
            limit = int(limit)
            limit = max(1, min(limit, 100))
        except (TypeError, ValueError):
            limit = 50

        records = self.alliance_repo.list_war_battle_records(alliance.id, limit)
        
        return {
            "ok": True,
            "records": records,
            "total": len(records),
        }

    def get_war_status(self, user_id: int) -> dict:
        """获取盟战状态信息"""
        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error

        now = datetime.utcnow()
        is_war, phase, status = self._is_war_time(now)
        weekday = now.weekday()
        checkin_date = now.date()

        # 获取报名情况
        dragon_reg = None
        tiger_reg = None
        active_registration = None
        for land_id in self.DRAGON_ONLY_LANDS:
            reg = self.alliance_repo.get_land_registration(alliance.id, land_id)
            if reg and reg.is_active():
                dragon_reg = {"land_id": land_id, "land_name": self.WAR_LANDS.get(land_id, {}).get("land_name", f"土地{land_id}")}
                if not active_registration:
                    active_registration = reg
                break
        for land_id in self.TIGER_ONLY_LANDS:
            reg = self.alliance_repo.get_land_registration(alliance.id, land_id)
            if reg and reg.is_active():
                tiger_reg = {"land_id": land_id, "land_name": self.WAR_LANDS.get(land_id, {}).get("land_name", f"据点{land_id}")}
                if not active_registration:
                    active_registration = reg
                break

        # 检查是否已签到（基于当前活跃的报名记录）
        has_checkin = False
        if is_war and phase and active_registration and active_registration.id:
            has_checkin = self.alliance_repo.has_war_checkin(active_registration.id, user_id)

        # 获取联盟战功
        current_honor, historical_honor = self.alliance_repo.get_alliance_war_points(alliance.id)
        
        return {
            "ok": True,
            "is_war_time": is_war,
            "phase": phase,
            "status": status,
            "has_checkin": has_checkin,
            "can_checkin": is_war and status == "signup" and not has_checkin and member.army_type,
            "dragon_registration": dragon_reg,
            "tiger_registration": tiger_reg,
            "current_honor": current_honor,
            "war_honor_history": historical_honor,
        }

    def distribute_season_rewards(self, season_key: Optional[str] = None) -> dict:
        """发放赛季奖励（管理员功能）"""
        if season_key is None:
            now = datetime.utcnow()
            # 获取上个月的赛季
            if now.month == 1:
                season_key = f"{now.year - 1}-12"
            else:
                season_key = f"{now.year}-{now.month - 1:02d}"

        # 获取前三名并记录奖励
        distributed_records = self.alliance_repo.distribute_season_rewards(season_key)
        
        # 实际发放奖励给联盟成员
        distributed = []
        for record in distributed_records:
            alliance_id = record["alliance_id"]
            rank = record["rank"]
            copper_reward = record["copper_reward"]
            items = record["items"]
            
            # 获取联盟所有成员
            members = self.alliance_repo.get_alliance_members(alliance_id)
            if not members:
                continue
            
            # 给每个成员发放奖励
            member_count = 0
            success_count = 0
            for member in members:
                member_count += 1
                try:
                    player = self.player_repo.get_by_id(member.user_id)
                    if not player:
                        continue
                    
                    # 发放铜钱
                    current_copper = getattr(player, "copper", 0) or 0
                    current_gold = getattr(player, "gold", 0) or 0
                    player.copper = current_copper + copper_reward
                    player.gold = current_gold + copper_reward  # 兼容旧字段
                    self.player_repo.save(player)
                    
                    # 发放物品
                    for item in items:
                        item_id = item.get("item_id")
                        quantity = item.get("quantity", 1)
                        if item_id:
                            try:
                                self.inventory_service.add_item(member.user_id, item_id, quantity)
                            except Exception as e:
                                # 记录错误但不中断流程
                                import traceback
                                traceback.print_exc()
                    
                    success_count += 1
                except Exception as e:
                    # 记录错误但不中断流程
                    import traceback
                    traceback.print_exc()
            
            distributed.append({
                "alliance_id": alliance_id,
                "alliance_name": record["alliance_name"],
                "rank": rank,
                "copper_reward": copper_reward,
                "items": items,
                "member_count": member_count,
                "success_count": success_count,
            })
        
        return {
            "ok": True,
            "season_key": season_key,
            "distributed": distributed,
            "count": len(distributed),
        }
