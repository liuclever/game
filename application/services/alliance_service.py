import json
from pathlib import Path
from datetime import datetime, timedelta
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
    WAR_START_WEEKDAYS = (2, 5)  # Wednesday=2, Saturday=5
    WAR_START_HOUR = 20
    WAR_START_MINUTE = 0

    ARMY_LEVEL_THRESHOLD = 40
    ARMY_DRAGON = 1
    ARMY_TIGER = 2
    DRAGON_ONLY_LANDS = {1, 2}
    TIGER_ONLY_LANDS = {3, 4}
    HONOR_EFFECT_DURATION_HOURS = 24
    WAR_LANDS = {
        1: {
            "land_name": "林中空地1号土地",
            "buffs": [
                "属性：林间祝福提升飞龙军参战成员攻击力5%，守望之力令守军生命提升3%",
            ],
        },
        2: {
            "land_name": "幻灵镇1号土地",
            "buffs": [
                "属性：联盟成员修行经验加成12%，联盟火修焚火晶加成40%",
            ],
        },
        3: {
            "land_name": "幻灵镇1号据点",
            "buffs": [
                "属性：幻灵守护令伏虎军参战成员防御提升4%",
            ],
        },
        4: {
            "land_name": "林中空地1号据点",
            "buffs": [
                "属性：联盟成员修行经验加成3%，联盟火修焚火晶加成20%",
            ],
        },
        5: {
            "land_name": "幻灵镇1号据点",
            "buffs": [
                "属性：联盟成员修行经验加成4%，联盟火修焚火晶加成20%",
            ],
        },
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
        leader_member = AllianceMember(
            alliance_id=alliance_id,
            user_id=user_id,
            role=1  # 盟主
        )
        self.alliance_repo.add_member(leader_member)
        for building_key in AllianceRules.BUILDING_KEYS:
            self.alliance_repo.set_alliance_building_level(alliance_id, building_key, 1)
        self._record_activity(
            alliance_id=alliance_id,
            event_type="join",
            actor_user_id=user_id,
            actor_name=self._player_display_name(player),
        )

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

        alliance = self.alliance_repo.get_alliance_by_id(alliance_id)
        if not alliance:
            return {"ok": False, "error": "联盟不存在"}

        member_count = self.alliance_repo.count_members(alliance_id)
        capacity = AllianceRules.member_capacity(alliance.level or 1)
        if member_count >= capacity:
            return {"ok": False, "error": "联盟成员已满"}

        member = AllianceMember(
            alliance_id=alliance_id,
            user_id=user_id,
            role=AllianceRules.ROLE_MEMBER,
        )
        self.alliance_repo.add_member(member)

        self._record_activity(
            alliance_id=alliance_id,
            event_type="join",
            actor_user_id=user_id,
            actor_name=self._player_display_name(player),
        )

        return {"ok": True, "message": "加入联盟成功"}

    def get_my_alliance(self, user_id: int) -> dict:
        """获取玩家当前联盟信息"""
        member = self.alliance_repo.get_member(user_id)
        if not member:
            return {"ok": False, "error": "未加入联盟"}
        
        alliance = self.alliance_repo.get_alliance_by_id(member.alliance_id)
        if not alliance:
            return {"ok": False, "error": "联盟数据异常"}
        
        members = self.alliance_repo.get_alliance_members(alliance.id)
        member_capacity = AllianceRules.member_capacity(alliance.level or 1)
        return {
            "ok": True,
            "alliance": alliance,
            "member_info": member,
            "member_count": len(members),
            "member_capacity": member_capacity,
        }

    def get_alliance_notice(self, user_id: int) -> dict:
        """获取联盟公告"""
        member = self.alliance_repo.get_member(user_id)
        if not member:
            return {"ok": False, "error": "未加入联盟"}

        alliance = self.alliance_repo.get_alliance_by_id(member.alliance_id)
        if not alliance:
            return {"ok": False, "error": "联盟数据异常"}

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
            return {"ok": False, "error": "联盟数据异常"}

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
            return {"ok": False, "error": "联盟数据异常"}

        members = self.alliance_repo.get_alliance_members(member.alliance_id)
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

        self.alliance_repo.remove_member(target_user_id)
        self._record_activity(
            alliance_id=actor.alliance_id,
            event_type="kick",
            actor_user_id=user_id,
            actor_name=self._member_display_name(actor),
            target_user_id=target.user_id,
            target_name=self._member_display_name(target),
        )
        return {"ok": True}

    def get_alliance_talent_info(self, user_id: int) -> dict:
        member = self.alliance_repo.get_member(user_id)
        if not member:
            return {"ok": False, "error": "未加入联盟"}

        alliance = self.alliance_repo.get_alliance_by_id(member.alliance_id)
        if not alliance:
            return {"ok": False, "error": "联盟数据异常"}

        building_level = alliance.level or 1
        research_map = self._get_talent_research_map(alliance.id)
        player_map = self._get_player_talent_map(user_id)

        talent_rows = []
        for key in AllianceRules.TALENT_KEYS:
            research_level = research_map.get(key, 1)
            max_level = AllianceRules.get_talent_max_level(building_level, research_level)
            player_level = player_map.get(key, 0)
            can_research_talent = (
                AllianceRules.can_research_talent(member.role)
                and research_level < building_level
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
            "building_level": building_level,
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
            return {"ok": False, "error": "联盟数据异常"}

        research_map = self._get_talent_research_map(member.alliance_id)
        player_map = self._get_player_talent_map(user_id)

        research_level = research_map.get(talent_key, 1)
        max_level = AllianceRules.get_talent_max_level(alliance.level or 1, research_level)
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
            return {"ok": False, "error": "联盟数据异常"}

        building_level = alliance.level or 1
        research_map = self._get_talent_research_map(alliance.id)
        current_level = research_map.get(talent_key, 1)

        if current_level >= building_level:
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

        new_level = min(building_level, next_level)
        self.alliance_repo.update_alliance_talent_research(alliance.id, talent_key, new_level)
        max_level = AllianceRules.get_talent_max_level(building_level, new_level)

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
            "building_level": building_level,
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
            return None, None, {"ok": False, "error": "联盟数据异常"}
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

        capacity = AllianceRules.item_storage_capacity(alliance.level or 1)
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

        capacity = AllianceRules.item_storage_capacity(alliance.level or 1)
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
        _, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error
        capacity = AllianceRules.beast_storage_capacity(alliance.level or 1)
        records = self.alliance_repo.get_beast_storage(alliance.id)
        storage_list = []
        for record in records:
            beast = self.beast_repo.get_by_id(record.beast_id)
            beast_name = ""
            beast_level = 0
            template_id = None
            if beast:
                beast_name = beast.nickname or f"幻兽{beast.id}"
                beast_level = beast.level
                template_id = beast.template_id
            stored_at = self._format_datetime(record.stored_at)
            storage_list.append({
                "storageId": record.id,
                "beastId": record.beast_id,
                "ownerUserId": record.owner_user_id,
                "ownerIsSelf": record.owner_user_id == user_id,
                "name": beast_name,
                "level": beast_level,
                "templateId": template_id,
                "storedAt": stored_at,
            })
        return {
            "ok": True,
            "allianceId": alliance.id,
            "allianceLevel": alliance.level or 1,
            "capacity": capacity,
            "count": len(storage_list),
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
            end_time = self._get_room_end_time(room)
            finished = self._is_room_finished(room, now)
            if finished and room.status != "completed":
                self.alliance_repo.update_training_room_status(room.id, "completed")
                room.status = "completed"

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
                and not finished
                and not is_full
                and self_participant is None
            )
            room_list.append({
                "roomId": room.id,
                "index": idx,
                "title": room.title,
                "status": "completed" if finished else "ongoing",
                "statusLabel": "已结束" if finished else "进行中",
                "createdAt": self._format_datetime(room.created_at),
                "endsAt": self._format_datetime(end_time),
                "maxParticipants": room.max_participants or 4,
                "participantCount": len(participants),
                "participants": participant_rows,
                "isFull": is_full,
                "canJoin": can_join,
                "selfParticipantId": self_participant.id if self_participant else None,
            })

        any_ongoing = any(room["status"] == "ongoing" for room in room_list)
        return {
            "ok": True,
            "allianceLevel": alliance.level or 1,
            "allianceCrystals": alliance.crystals,
            "hasJoinedToday": has_joined_today,
            "trainingDurationMinutes": AllianceRules.TRAINING_DURATION_MINUTES,
            "dailyLimit": AllianceRules.TRAINING_DAILY_LIMIT,
            "rooms": room_list,
            "practiceStatus": "进行中" if any_ongoing else "已结束",
        }

    def create_training_room(self, user_id: int, title: Optional[str] = None) -> dict:
        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error

        if self._has_joined_training_today(alliance.id, user_id):
            return {"ok": False, "error": "今日已参与修行，无法再次创建"}

        room_title = (title or "焚天炉").strip()[:20] or "焚天炉"
        room = AllianceTrainingRoom(
            id=None,
            alliance_id=alliance.id,
            creator_user_id=user_id,
            title=room_title,
            status="ongoing",
            max_participants=4,
        )
        room_id = self.alliance_repo.create_training_room(room)
        participant = AllianceTrainingParticipant(
            id=None,
            room_id=room_id,
            user_id=user_id,
        )
        self.alliance_repo.add_training_participant(participant)
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

        if self._is_room_finished(room):
            return {"ok": False, "error": "修行已结束，无法加入"}

        existing = self.alliance_repo.get_training_participant_by_room(room_id, user_id)
        if existing:
            return {"ok": False, "error": "已加入该修行房间"}

        participants = self.alliance_repo.get_training_participants(room_id)
        if len(participants) >= (room.max_participants or 4):
            return {"ok": False, "error": "修行房间已满"}

        participant = AllianceTrainingParticipant(
            id=None,
            room_id=room_id,
            user_id=user_id,
        )
        self.alliance_repo.add_training_participant(participant)
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

    # === 联盟兵营 / 盟战 ===
    def get_war_ranking(self, user_id: int, page: int = 1, size: int = 10) -> dict:
        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error

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

        rows = self.alliance_repo.list_alliance_war_leaderboard(season_start, size, offset)
        total = self.alliance_repo.count_alliance_war_leaderboard(season_start)
        ranking = [
            {
                "rank": offset + idx + 1,
                "allianceId": row["alliance_id"],
                "allianceName": row["alliance_name"],
                "score": row["score"],
            }
            for idx, row in enumerate(rows)
        ]

        my_rank = None
        if alliance:
            entry = self.alliance_repo.get_alliance_war_leaderboard_entry(alliance.id, season_start)
            if entry:
                my_rank = {
                    "rank": entry["rank"],
                    "allianceId": entry["alliance_id"],
                    "allianceName": entry["alliance_name"],
                    "score": entry["score"],
                }

        return {
            "ok": True,
            "data": {
                "ranking": ranking,
                "myRank": my_rank,
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
            return {"ok": False, "error": "只有盟主可以报名土地"}

        player = self.player_repo.get_by_id(user_id)
        if not player:
            return {"ok": False, "error": "玩家不存在"}

        normalized_army = self._normalize_army_choice(army, player.level or 1)
        allowed_land_ids = (
            self.DRAGON_ONLY_LANDS if normalized_army == AllianceRules.ARMY_DRAGON else self.TIGER_ONLY_LANDS
        )
        if land_id not in allowed_land_ids:
            msg = (
                "飞龙军仅能报名前两块土地"
                if normalized_army == AllianceRules.ARMY_DRAGON
                else "伏虎军仅能报名后两个据点"
            )
            return {"ok": False, "error": msg}

        existing_same_army = self.alliance_repo.get_active_land_registration_by_range(
            alliance.id, list(allowed_land_ids)
        )
        if existing_same_army and existing_same_army.land_id != land_id:
            msg = (
                "飞龙军只能选择土地1或2中的一个"
                if normalized_army == AllianceRules.ARMY_DRAGON
                else "伏虎军只能选择据点3或4中的一个"
            )
            return {"ok": False, "error": msg}

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
        land_meta = self.WAR_LANDS.get(land_id)
        if not land_meta:
            return {"ok": False, "error": "未找到该土地"}

        statuses = [STATUS_CONFIRMED, STATUS_IN_BATTLE]
        registrations = self.alliance_repo.list_land_registrations_by_land(
            land_id, statuses=statuses
        )

        alliances = []
        seen_ids = set()
        for reg in registrations:
            if reg.alliance_id in seen_ids:
                continue
            alliance = self.alliance_repo.get_alliance_by_id(reg.alliance_id)
            alliances.append(
                {
                    "alliance_id": reg.alliance_id,
                    "name": alliance.name if alliance else f"联盟{reg.alliance_id}",
                }
            )
            seen_ids.add(reg.alliance_id)

        data = {
            "land_id": land_id,
            "land_name": land_meta["land_name"],
            "buffs": land_meta["buffs"],
            "alliances": alliances,
        }
        return {"ok": True, "data": data}

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

    def get_war_info(self, user_id: int) -> dict:
        member, alliance, error = self._get_alliance_context(user_id)
        if error:
            return error

        player = self.player_repo.get_by_id(user_id)
        if not player:
            return {"ok": False, "error": "玩家不存在"}

       

        dragon, tiger = self._fetch_army_members(alliance.id)
        recommended_army = self._determine_army_type(player.level or 0)
        assigned_army = member.army_type or 0
        signed_up = assigned_army != 0

        schedule_payload = self._build_war_schedule_payload()

        return {
            "ok": True,
            "data": {
                "personal": {
                    "user_id": user_id,
                    "nickname": player.nickname,
                    "level": player.level or 1,
                    "signed_up": signed_up,
                    "current_army": assigned_army,
                    "current_army_label": self._army_label(assigned_army),
                    "recommended_army": recommended_army,
                    "recommended_army_label": self._army_label(recommended_army),
                },
                "statistics": {
                    "dragon_count": len(dragon),
                    "tiger_count": len(tiger),
                    "total_signed": len(dragon) + len(tiger),
                    "threshold_level": self.ARMY_LEVEL_THRESHOLD,
                },
                "armies": {
                    "dragon": [self._member_army_row(m) for m in dragon],
                    "tiger": [self._member_army_row(m) for m in tiger],
                },
                "schedule": schedule_payload,
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
                    "created_at": m.created_at.strftime("%H:%M:%S") if m.created_at else ""
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

    def _get_room_end_time(self, room: AllianceTrainingRoom) -> datetime:
        if not room.created_at:
            return datetime.utcnow()
        return room.created_at + timedelta(minutes=AllianceRules.TRAINING_DURATION_MINUTES)

    def _is_room_finished(self, room: AllianceTrainingRoom, now: Optional[datetime] = None) -> bool:
        if room.status == "completed":
            return True
        if not now:
            now = datetime.utcnow()
        end_time = self._get_room_end_time(room)
        return now >= end_time

    def _format_datetime(self, value: Optional[datetime]) -> str:
        if not value:
            return ""
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M")
        return str(value)

    def _next_war_start(self, now: Optional[datetime] = None) -> datetime:
        if not now:
            now = datetime.utcnow()
        base_today = datetime(
            now.year,
            now.month,
            now.day,
            self.WAR_START_HOUR,
            self.WAR_START_MINUTE,
        )
        for day_offset in range(0, 8):
            candidate = base_today + timedelta(days=day_offset)
            if candidate.weekday() not in self.WAR_START_WEEKDAYS:
                continue
            if candidate <= now:
                continue
            return candidate
        return base_today + timedelta(days=7)

    def _build_war_schedule_payload(self, now: Optional[datetime] = None) -> Dict[str, Any]:
        if not now:
            now = datetime.utcnow()
        next_start = self._next_war_start(now)
        countdown_seconds = max(0, int((next_start - now).total_seconds()))
        detail = [
            {
                "weekday": day,
                "label": self._weekday_label(day),
                "hour": self.WAR_START_HOUR,
                "minute": self.WAR_START_MINUTE,
            }
            for day in self.WAR_START_WEEKDAYS
        ]
        return {
            "nextWarTime": next_start.replace(microsecond=0).isoformat() + "Z",
            "countdownSeconds": countdown_seconds,
            "weekdays": list(self.WAR_START_WEEKDAYS),
            "weekdaysDetail": detail,
            "startHour": self.WAR_START_HOUR,
            "startMinute": self.WAR_START_MINUTE,
        }

    def _weekday_label(self, weekday: int) -> str:
        labels = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        return labels[weekday % 7]

    def _determine_army_type(self, level: int) -> int:
        if level > self.ARMY_LEVEL_THRESHOLD:
            return self.ARMY_DRAGON
        return self.ARMY_TIGER

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
        expected = self._determine_army_type(level)
        if member.army_type != expected:
            self.alliance_repo.update_member_army(member.user_id, expected)
            member.army_type = expected

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
            created_at=datetime.utcnow(),
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
