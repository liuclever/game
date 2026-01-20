"""
镇妖服务
"""
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import random

from domain.entities.player import Player, ZhenyaoFloor
from domain.repositories.player_repo import IPlayerRepo, IZhenyaoRepo
from domain.services.pvp_battle_engine import (
    PvpPlayer,
    PvpBeast,
    run_pvp_battle,
)
from domain.services.skill_system import apply_buff_debuff_skills
from infrastructure.db.tower_state_repo_mysql import MySQLTowerStateRepo
from infrastructure.db.player_beast_repo_mysql import MySQLPlayerBeastRepo
from infrastructure.db.zhenyao_battle_repo_mysql import (
    MySQLZhenyaoBattleRepo, 
    MySQLZhenyaoDailyCountRepo,
    ZhenyaoBattleLog
)
from domain.repositories.bone_repo import IBoneRepo
from domain.repositories.spirit_repo import ISpiritRepo
from application.services.beast_pvp_service import BeastPvpService
from application.services.inventory_service import InventoryService
from infrastructure.db.bone_repo_mysql import MySQLBoneRepo
from infrastructure.db.spirit_repo_mysql import MySQLSpiritRepo
from infrastructure.config.bone_system_config import get_bone_system_config
from domain.entities.player import RANK_CONFIG


# 配置常量
OCCUPY_DURATION_MINUTES = 30  # 占领时长（分钟）
TRIAL_DAILY_LIMIT = 1        # 试炼层每日次数
HELL_DAILY_LIMIT = 10         # 炼狱层每日次数
ZHENYAO_FU_ITEM_ID = 6001
ZHENYAO_TRIAL_CHEST_ITEM_ID = 92001
ZHENYAO_HELL_CHEST_ITEM_ID = 92002


class ZhenyaoError(Exception):
    """镇妖相关错误"""
    pass


@dataclass
class ZhenyaoInfo:
    """镇妖信息"""
    can_zhenyao: bool           # 是否可以镇妖
    player_level: int           # 玩家等级
    rank_name: str              # 阶位名称
    zhenyao_range: Optional[Tuple[int, int]]  # 可镇妖层数范围
    tower_max_floor: int        # 通天塔最高层
    trial_floors: List[int]     # 试炼层列表
    hell_floors: List[int]      # 炼狱层列表
    error_msg: str = ""         # 错误信息


class ZhenyaoService:
    """镇妖服务"""
    
    def __init__(
        self, 
        player_repo: IPlayerRepo,
        zhenyao_repo: IZhenyaoRepo,
        tower_state_repo: MySQLTowerStateRepo,
        beast_repo: MySQLPlayerBeastRepo = None,
        battle_repo: MySQLZhenyaoBattleRepo = None,
        daily_count_repo: MySQLZhenyaoDailyCountRepo = None,
        bone_repo: IBoneRepo | None = None,
        spirit_repo: ISpiritRepo | None = None,
        beast_pvp_service: BeastPvpService | None = None,
        inventory_service: InventoryService | None = None,
    ):
        self.player_repo = player_repo
        self.zhenyao_repo = zhenyao_repo
        self.tower_state_repo = tower_state_repo
        self.beast_repo = beast_repo or MySQLPlayerBeastRepo()
        self.battle_repo = battle_repo or MySQLZhenyaoBattleRepo()
        self.daily_count_repo = daily_count_repo or MySQLZhenyaoDailyCountRepo()
        self.inventory_service = inventory_service

        # 装备系统转换服务
        self.beast_pvp_service = beast_pvp_service

        # 加载奖励配置
        self.reward_config = self._load_reward_config()

    def _load_reward_config(self) -> Dict:
        """加载奖励配置"""
        import os
        import json
        config_path = os.path.join(os.path.dirname(__file__), "..", "..", "configs", "zhenyao_rewards.json")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"reward_configs": []}

    def _grant_zhenyao_reward(self, user_id: int, floor: int, player_level: int) -> Optional[Dict]:
        """发放镇妖奖励"""
        if not self.inventory_service:
            return None

        # 确定是试炼层还是炼狱层：按 floor 所在等级段区间判定
        floor_range = None
        for _min_lv, _max_lv, _rank_name, fr in RANK_CONFIG:
            if not fr:
                continue
            if fr[0] <= floor <= fr[1]:
                floor_range = fr
                break
        if not floor_range:
            return None

        start_floor, _end_floor = floor_range
        mid_floor = start_floor + 9
        is_trial = floor <= mid_floor

        # 根据玩家等级确定宝箱星级
        star_level = self._get_chest_star_level(player_level)
        star_prefix = f"{star_level}星" if star_level > 0 else ""
        
        chest_item_id = ZHENYAO_TRIAL_CHEST_ITEM_ID if is_trial else ZHENYAO_HELL_CHEST_ITEM_ID
        chest_base_name = "试炼宝箱" if is_trial else "炼狱宝箱"
        chest_name = f"{star_prefix}{chest_base_name}"
        
        self.inventory_service.add_item(user_id, chest_item_id, 1)
        
        # 标记为已发放
        self.zhenyao_repo.mark_floor_rewarded(floor)
        
        return {
            "chest_item_id": chest_item_id,
            "chest_name": chest_name,
            "is_trial": is_trial,
            "floor": floor,
            "star_level": star_level
        }
    
    def _get_chest_star_level(self, player_level: int) -> int:
        """根据玩家等级获取宝箱星级
        
        30-39级: 3星
        40-49级: 4星
        50-59级: 5星
        60-69级: 6星
        70-79级: 7星
        80级及以上: 8星
        """
        if player_level < 30:
            return 0
        elif player_level < 40:
            return 3
        elif player_level < 50:
            return 4
        elif player_level < 60:
            return 5
        elif player_level < 70:
            return 6
        elif player_level < 80:
            return 7
        else:
            return 8

    def check_and_grant_rewards(self, user_id: int) -> List[Dict]:
        """检查并为玩家发放已到期的占领奖励"""
        # 获取玩家当前占领的所有层（包括已过期的）
        # 我们需要一个能获取所有曾占领但未奖励的层的方法
        # 但目前 get_floors_by_occupant 只返回未过期的。
        # 我在 MySQLZhenyaoRepo 增加一个方法或修改它。
        
        # 其实我们可以直接查询数据库
        from infrastructure.db.connection import execute_query
        from datetime import datetime
        
        sql = """
            SELECT floor, occupant_id, expire_time, rewarded 
            FROM zhenyao_floor 
            WHERE occupant_id = %s AND rewarded = 0 AND expire_time <= NOW()
        """
        rows = execute_query(sql, (user_id,))
        
        player = self.player_repo.get_by_id(user_id)
        if not player: return []
        
        all_granted = []
        for row in rows:
            res = self._grant_zhenyao_reward(user_id, row['floor'], player.level)
            if res:
                all_granted.append(res)
        
        return all_granted

    def get_zhenyao_info(self, user_id: int) -> ZhenyaoInfo:
        """获取镇妖信息"""
        # 获取玩家信息
        player = self.player_repo.get_by_id(user_id)
        if not player:
            return ZhenyaoInfo(
                can_zhenyao=False,
                player_level=0,
                rank_name="",
                zhenyao_range=None,
                tower_max_floor=0,
                trial_floors=[],
                hell_floors=[],
                error_msg="玩家不存在"
            )
        
        # 检查并延迟发放奖励
        self.check_and_grant_rewards(user_id)
        
        # 检查等级
        if not player.can_zhenyao():
            return ZhenyaoInfo(
                can_zhenyao=False,
                player_level=player.level,
                rank_name=player.get_rank_name(),
                zhenyao_range=None,
                tower_max_floor=0,
                trial_floors=[],
                hell_floors=[],
                error_msg="等级不足30级，无法镇妖"
            )
        
        # 获取通天塔进度
        tower_state = self.tower_state_repo.get_by_user_id(user_id, "tongtian")
        tower_max_floor = tower_state.max_floor_record if tower_state else 0
        
        # 计算试炼层和炼狱层
        trial_floors, hell_floors = player.get_trial_and_hell_floors(tower_max_floor)
        
        zhenyao_range = player.get_zhenyao_range()
        
        # 检查是否有可用层
        if not trial_floors and not hell_floors:
            return ZhenyaoInfo(
                can_zhenyao=False,
                player_level=player.level,
                rank_name=player.get_rank_name(),
                zhenyao_range=zhenyao_range,
                tower_max_floor=tower_max_floor,
                trial_floors=[],
                hell_floors=[],
                error_msg=f"请先通关通天塔第{zhenyao_range[0]}层"
            )
        
        return ZhenyaoInfo(
            can_zhenyao=True,
            player_level=player.level,
            rank_name=player.get_rank_name(),
            zhenyao_range=zhenyao_range,
            tower_max_floor=tower_max_floor,
            trial_floors=trial_floors,
            hell_floors=hell_floors,
        )
    
    def get_floor_list(self, user_id: int, floor_type: str = "trial") -> Dict:
        """
        获取层数列表
        
        Args:
            user_id: 玩家ID
            floor_type: "trial" = 试炼层, "hell" = 炼狱层
        
        Returns:
            包含层信息的字典
        """
        info = self.get_zhenyao_info(user_id)
        
        if not info.can_zhenyao:
            return {
                "ok": False,
                "error": info.error_msg,
                "floors": []
            }
        
        # 选择可操作层列表（仅当前等级段）
        action_floors = info.trial_floors if floor_type == "trial" else info.hell_floors
        action_floor_set = set(action_floors)

        player = self.player_repo.get_by_id(user_id)
        if not player:
            return {
                "ok": False,
                "error": "玩家不存在",
                "floors": []
            }

        tower_max_floor = info.tower_max_floor

        visible_floors = []
        for min_lv, _max_lv, _rank_name, floor_range in RANK_CONFIG:
            if not floor_range:
                continue
            if player.level < min_lv:
                break

            start_floor, end_floor = floor_range
            actual_end = min(end_floor, tower_max_floor)
            if actual_end < start_floor:
                continue

            mid_floor = start_floor + 9
            if floor_type == "trial":
                trial_end = min(mid_floor, actual_end)
                visible_floors.extend(list(range(start_floor, trial_end + 1)))
            else:
                if actual_end > mid_floor:
                    visible_floors.extend(list(range(mid_floor + 1, actual_end + 1)))

        floor_nums = sorted(set(visible_floors))
        
        if not floor_nums:
            return {
                "ok": True,
                "floors": [],
                "floor_type": floor_type,
                "trial_count": len(info.trial_floors),
                "hell_count": len(info.hell_floors),
            }
        
        # 获取层详情
        start_floor = min(floor_nums)
        end_floor = max(floor_nums)
        floor_data = self.zhenyao_repo.get_floors_in_range(start_floor, end_floor)
        
        # 转换为返回格式
        floors = []
        for f in floor_data:
            if f.floor in floor_nums:
                floors.append({
                    "floor": f.floor,
                    "is_occupied": f.is_occupied(),
                    "occupant_id": f.occupant_id if f.is_occupied() else None,
                    "occupant_name": f.occupant_name if f.is_occupied() else "",
                    "remaining_seconds": f.get_remaining_seconds() if f.is_occupied() else 0,
                    "can_action": f.floor in action_floor_set,
                })
        
        # 按层数降序排列
        floors.sort(key=lambda x: x["floor"], reverse=True)
        
        return {
            "ok": True,
            "floors": floors,
            "floor_type": floor_type,
            "trial_count": len(info.trial_floors),
            "hell_count": len(info.hell_floors),
            "zhenyao_range": info.zhenyao_range,
            "rank_name": info.rank_name,
        }
    
    def occupy_floor(self, user_id: int, floor: int, duration_minutes: int = 30) -> Dict:
        """
        占领某层
        
        Args:
            user_id: 玩家ID
            floor: 层数
            duration_minutes: 占领时长（分钟）
        
        Returns:
            操作结果
        """
        # 获取玩家信息
        player = self.player_repo.get_by_id(user_id)
        if not player:
            return {"ok": False, "error": "玩家不存在"}
        
        # 检查镇妖资格
        info = self.get_zhenyao_info(user_id)
        if not info.can_zhenyao:
            return {"ok": False, "error": info.error_msg}
        
        # 检查层是否在可用范围内
        all_floors = info.trial_floors + info.hell_floors
        if floor not in all_floors:
            return {"ok": False, "error": "该层不在可镇妖范围内"}

        is_trial = floor in info.trial_floors
        is_hell = floor in info.hell_floors

        trial_count, hell_count = self.daily_count_repo.get_today_count(user_id)
        if is_trial and trial_count >= TRIAL_DAILY_LIMIT:
            return {"ok": False, "error": f"试炼层今日镇妖次数已用完（{TRIAL_DAILY_LIMIT}次）"}
        if is_hell and hell_count >= HELL_DAILY_LIMIT:
            return {"ok": False, "error": f"炼狱层今日镇妖次数已用完（{HELL_DAILY_LIMIT}次）"}

        # 检查该玩家是否已经占领了其他层（且未过期）
        occupied_floors = self.zhenyao_repo.get_floors_by_occupant(user_id)
        if occupied_floors:
            floors_str = "、".join(str(f.floor) for f in occupied_floors)
            return {
                "ok": False,
                "error": f"你当前已占领第{floors_str}层，未到期前不能再次占领其他层",
            }
        
        # 检查目标层是否已被占领
        floor_info = self.zhenyao_repo.get_floor(floor)
        if floor_info:
            if floor_info.is_occupied():
                return {"ok": False, "error": f"该层已被 {floor_info.occupant_name} 占领"}
            else:
                # 检查上一个占领者是否应该获得奖励
                if floor_info.occupant_id and not floor_info.rewarded:
                    prev_player = self.player_repo.get_by_id(floor_info.occupant_id)
                    if prev_player:
                        self._grant_zhenyao_reward(floor_info.occupant_id, floor, prev_player.level)

        if is_hell:
            if not self.inventory_service:
                return {"ok": False, "error": "系统错误：InventoryService 未配置"}
            if not self.inventory_service.has_item(user_id, ZHENYAO_FU_ITEM_ID, 1):
                return {"ok": False, "error": "镇妖符不足"}
            try:
                self.inventory_service.remove_item(user_id, ZHENYAO_FU_ITEM_ID, 1)
            except Exception as e:
                return {"ok": False, "error": str(e)}
        
        # 占领
        success = self.zhenyao_repo.occupy_floor(
            floor=floor,
            user_id=user_id,
            nickname=player.nickname,
            duration_minutes=duration_minutes
        )

        if success:
            if is_trial:
                self.daily_count_repo.increment_trial(user_id)
            elif is_hell:
                self.daily_count_repo.increment_hell(user_id)
        
        if success:
            return {"ok": True, "message": f"成功占领第{floor}层"}
        else:
            return {"ok": False, "error": "占领失败"}
    
    def challenge_floor(self, user_id: int, floor: int) -> Dict:
        """挑战某层（抢夺），并使用统一的 PVP 幻兽战斗规则计算结果。"""
        # 1. 获取挑战者信息
        attacker = self.player_repo.get_by_id(user_id)
        if not attacker:
            return {"ok": False, "error": "玩家不存在"}
        
        # 2. 检查镇妖资格
        info = self.get_zhenyao_info(user_id)
        if not info.can_zhenyao:
            return {"ok": False, "error": info.error_msg}
        
        # 2.5. 检查该玩家是否已经占领了其他层（且未过期），如果已占领则不允许挑战
        occupied_floors = self.zhenyao_repo.get_floors_by_occupant(user_id)
        if occupied_floors:
            floors_str = "、".join(str(f.floor) for f in occupied_floors)
            return {
                "ok": False,
                "error": f"你当前已占领第{floors_str}层，已占领层的玩家不能挑战其他玩家",
            }
        
        # 3. 检查层是否在可用范围内
        is_trial = floor in info.trial_floors
        is_hell = floor in info.hell_floors
        if not is_trial and not is_hell:
            return {"ok": False, "error": "该层不在可镇妖范围内"}
        
        # 4. 检查每日次数
        trial_count, hell_count = self.daily_count_repo.get_today_count(user_id)
        if is_trial and trial_count >= TRIAL_DAILY_LIMIT:
            return {"ok": False, "error": f"试炼层今日挑战次数已用完（{TRIAL_DAILY_LIMIT}次）"}
        if is_hell and hell_count >= HELL_DAILY_LIMIT:
            return {"ok": False, "error": f"炼狱层今日挑战次数已用完（{HELL_DAILY_LIMIT}次）"}

        # 5. 检查层是否被占领
        floor_info = self.zhenyao_repo.get_floor(floor)
        if not floor_info or not floor_info.is_occupied():
            return {"ok": False, "error": "该层无人占领，请直接占领"}
        
        # 不能挑战自己
        if floor_info.occupant_id == user_id:
            return {"ok": False, "error": "不能挑战自己占领的层"}
        
        # 获取被挑战者信息
        defender = self.player_repo.get_by_id(floor_info.occupant_id)
        if not defender:
            return {"ok": False, "error": "被挑战玩家不存在"}

        if is_hell:
            if not self.inventory_service:
                return {"ok": False, "error": "系统错误：InventoryService 未配置"}
            if not self.inventory_service.has_item(user_id, ZHENYAO_FU_ITEM_ID, 1):
                return {"ok": False, "error": "镇妖符不足"}
            try:
                self.inventory_service.remove_item(user_id, ZHENYAO_FU_ITEM_ID, 1)
            except Exception as e:
                return {"ok": False, "error": str(e)}
        
        # 6. 获取双方幻兽
        attacker_beasts = self.beast_repo.get_team_beasts(user_id)
        defender_beasts = self.beast_repo.get_team_beasts(floor_info.occupant_id)
        
        if not attacker_beasts:
            return {"ok": False, "error": "你没有出战幻兽"}
        if not defender_beasts:
            return {"ok": False, "error": "对方没有出战幻兽"}
        
        # 7. 进行战斗（使用统一 PVP 引擎）
        remaining_seconds = floor_info.get_remaining_seconds()
        battle_result = self._do_battle(
            attacker_beasts,
            defender_beasts,
            attacker_name=attacker.nickname,
            defender_name=floor_info.occupant_name,
            attacker_level=attacker.level,
            defender_level=defender.level,
        )
        
        # 8. 增加次数
        if is_trial:
            self.daily_count_repo.increment_trial(user_id)
        else:
            self.daily_count_repo.increment_hell(user_id)
        
        # 9. 保存战斗记录
        battle_id = self.battle_repo.save_battle(
            floor=floor,
            attacker_id=user_id,
            attacker_name=attacker.nickname,
            defender_id=floor_info.occupant_id,
            defender_name=floor_info.occupant_name,
            is_success=battle_result["is_victory"],
            remaining_seconds=remaining_seconds,
            battle_data=battle_result,
        )
        
        # 10. 如果胜利，更新占领信息
        if battle_result["is_victory"]:
            self.zhenyao_repo.occupy_floor(
                floor=floor,
                user_id=user_id,
                nickname=attacker.nickname,
                duration_minutes=OCCUPY_DURATION_MINUTES,
            )
        
        return {
            "ok": True,
            "is_victory": battle_result["is_victory"],
            "battle_id": battle_id,
            "floor": floor,
            "attacker_name": attacker.nickname,
            "defender_name": floor_info.occupant_name,
            "remaining_seconds": remaining_seconds,
            "message": f"{'挑战成功，成功占领第{floor}层！' if battle_result['is_victory'] else '挑战失败！'}",
            "battles": battle_result["battles"],
        }
    
    def _do_battle(
        self,
        attacker_beasts: List,
        defender_beasts: List,
        attacker_name: str,
        defender_name: str,
        attacker_level: int,
        defender_level: int,
    ) -> Dict:
        """使用统一 PVP 引擎执行完整战斗，并转换为镇妖前端需要的数据结构。

        返回结构示例：
        {
            "is_victory": bool,          # 挑战者是否胜利
            "attacker_wins": int,       # 兼容字段，这里胜利=1, 失败=0
            "defender_wins": int,
            "battles": [
                {
                    "battle_num": 1,
                    "winner": "attacker" / "defender",
                    "rounds": [
                        {"round": 1, "action": "...", "a_hp": 123, "d_hp": 456},
                        ...
                    ],
                    "result": "战斗结果描述",
                }
            ],
        }
        """

        pvp_result = run_pvp_battle(
            PvpPlayer(
                player_id=1,
                level=attacker_level,
                beasts=self.beast_pvp_service.to_pvp_beasts(attacker_beasts),
                name=attacker_name,
            ),
            PvpPlayer(
                player_id=2,
                level=defender_level,
                beasts=self.beast_pvp_service.to_pvp_beasts(defender_beasts),
                name=defender_name,
            ),
            max_log_turns=50
        )

        attacker_player_id = 1
        is_victory = pvp_result.winner_player_id == attacker_player_id

        # ===== 将整场 PVP 日志按 "每只幻兽对战" 分成多场战斗 =====
        def get_player_name(pid: int) -> str:
            return attacker_name if pid == attacker_player_id else defender_name

        def get_side_flag(pid: int) -> str:
            return "attacker" if pid == attacker_player_id else "defender"

        def build_battle_segment(battle_index: int, seg_logs):
            """根据一段连续日志（同一对幻兽对战）构建一场战斗的数据结构。

            seg_logs 中既包含普通攻击/技能攻击日志，也可能包含中毒等持续伤害日志。
            """
            if not seg_logs:
                return {
                    "battle_num": battle_index,
                    "attacker_beast": "",
                    "defender_beast": "",
                    "winner": "defender",
                    "rounds": [],
                    "result": "",
                }

            # 每一小战内部回合重新从 1 计数
            rounds = []
            for idx, log in enumerate(seg_logs, start=1):
                rounds.append({
                    "round": idx,
                    "action": log.description,
                    "a_hp": log.attacker_hp_after,
                    "d_hp": log.defender_hp_after,
                })

            # 统计本场对战中每只幻兽的最终气血
            # key = (player_id, beast_id) -> (beast_name, hp_after)
            beast_state: dict[tuple[int, int], tuple[str, int]] = {}
            for log in seg_logs:
                if log.attacker_beast_id != 0:
                    beast_state[(log.attacker_player_id, log.attacker_beast_id)] = (
                        log.attacker_name,
                        log.attacker_hp_after,
                    )
                if log.defender_beast_id != 0:
                    beast_state[(log.defender_player_id, log.defender_beast_id)] = (
                        log.defender_name,
                        log.defender_hp_after,
                    )

            # 默认使用整场战斗的胜负兜底
            winner_player_id = pvp_result.winner_player_id
            loser_player_id = pvp_result.loser_player_id
            winner_beast_name = ""
            loser_beast_name = ""
            winner_hp = 0

            keys = list(beast_state.keys())
            if keys:
                # 正常情况下这里有两只幻兽；如果只有一只，就简单复制一份避免下标错误
                if len(keys) == 1:
                    keys = keys * 2
                (p1, b1), (p2, b2) = keys[0], keys[1]
                name1, hp1 = beast_state[(p1, b1)]
                name2, hp2 = beast_state[(p2, b2)]

                if hp1 > 0 and hp2 <= 0:
                    winner_player_id, loser_player_id = p1, p2
                    winner_beast_name, winner_hp = name1, hp1
                    loser_beast_name = name2
                elif hp2 > 0 and hp1 <= 0:
                    winner_player_id, loser_player_id = p2, p1
                    winner_beast_name, winner_hp = name2, hp2
                    loser_beast_name = name1
                elif hp1 != hp2:
                    # 双方都活着，谁血多谁赢（主要用于日志截断等极端情况）
                    if hp1 > hp2:
                        winner_player_id, loser_player_id = p1, p2
                        winner_beast_name, winner_hp = name1, hp1
                        loser_beast_name = name2
                    else:
                        winner_player_id, loser_player_id = p2, p1
                        winner_beast_name, winner_hp = name2, hp2
                        loser_beast_name = name1

            winner_player_name = get_player_name(winner_player_id)
            loser_player_name = get_player_name(loser_player_id)
            winner_flag = get_side_flag(winner_player_id)

            # 结果文案，贴近老版本："某某的X阵亡，某某的Y剩余气血N"
            if winner_beast_name and loser_beast_name:
                result_text = (
                    f"『{loser_player_name}』的{loser_beast_name}阵亡，"
                    f"『{winner_player_name}』的{winner_beast_name}剩余气血{winner_hp}"
                )
            else:
                # 兜底：只写玩家胜负
                result_text = f"『{winner_player_name}』获胜"

            return {
                "battle_num": battle_index,
                "attacker_beast": "",
                "defender_beast": "",
                "winner": winner_flag,
                "rounds": rounds,
                "result": result_text,
            }

        battles = []
        current_pair = None  # 当前这场小战参与的两只幻兽（ID 集合）
        current_logs = []

        for log in pvp_result.logs:
            # 中毒等持续伤害（attacker_beast_id == 0）归入当前小战，不单独拆分
            if log.attacker_beast_id == 0 and current_pair is not None:
                current_logs.append(log)
                continue

            pair = frozenset({log.attacker_beast_id, log.defender_beast_id})

            if current_pair is None:
                current_pair = pair
                current_logs.append(log)
            elif pair == current_pair:
                current_logs.append(log)
            else:
                # 一方幻兽阵亡，开始新的小战
                battles.append(build_battle_segment(len(battles) + 1, current_logs))
                current_pair = pair
                current_logs = [log]

        # 收尾最后一场小战
        if current_logs:
            battles.append(build_battle_segment(len(battles) + 1, current_logs))

        attacker_wins = 1 if is_victory else 0
        defender_wins = 1 - attacker_wins

        return {
            "is_victory": is_victory,
            "attacker_wins": attacker_wins,
            "defender_wins": defender_wins,
            "battles": battles,
        }
    
    def _battle_one(self, attacker, defender, attacker_name: str, defender_name: str, battle_num: int) -> Dict:
        """
        单场战斗
        
        简化版战斗：根据战力+随机因素决定胜负
        """
        a_hp = attacker.hp
        d_hp = defender.hp
        
        rounds = []
        round_num = 0
        max_rounds = 20  # 最多20回合
        
        # 确定先手（速度快的先手）
        a_speed = attacker.speed
        d_speed = defender.speed
        
        while a_hp > 0 and d_hp > 0 and round_num < max_rounds:
            round_num += 1
            
            # 根据速度决定攻击顺序
            if a_speed >= d_speed:
                # 攻击方先手
                damage_to_d = self._calc_damage(attacker, defender)
                d_hp -= damage_to_d
                rounds.append({
                    "round": round_num,
                    "action": f"『{attacker_name}』的{attacker.name}-{attacker.realm}对『{defender_name}』的{defender.name}-{defender.realm}进行攻击,气血-{damage_to_d}",
                    "a_hp": a_hp,
                    "d_hp": max(0, d_hp),
                })
                
                if d_hp <= 0:
                    break
                
                # 防守方反击
                damage_to_a = self._calc_damage(defender, attacker)
                a_hp -= damage_to_a
                rounds.append({
                    "round": round_num,
                    "action": f"『{defender_name}』的{defender.name}-{defender.realm}对『{attacker_name}』的{attacker.name}-{attacker.realm}进行反击,气血-{damage_to_a}",
                    "a_hp": max(0, a_hp),
                    "d_hp": d_hp,
                })
            else:
                # 防守方先手
                damage_to_a = self._calc_damage(defender, attacker)
                a_hp -= damage_to_a
                rounds.append({
                    "round": round_num,
                    "action": f"『{defender_name}』的{defender.name}-{defender.realm}先手攻击『{attacker_name}』的{attacker.name}-{attacker.realm},气血-{damage_to_a}",
                    "a_hp": max(0, a_hp),
                    "d_hp": d_hp,
                })
                
                if a_hp <= 0:
                    break
                
                # 攻击方反击
                damage_to_d = self._calc_damage(attacker, defender)
                d_hp -= damage_to_d
                rounds.append({
                    "round": round_num,
                    "action": f"『{attacker_name}』的{attacker.name}-{attacker.realm}反击『{defender_name}』的{defender.name}-{defender.realm},气血-{damage_to_d}",
                    "a_hp": a_hp,
                    "d_hp": max(0, d_hp),
                })
        
        # 判断胜负
        if a_hp > 0 and d_hp <= 0:
            winner = "attacker"
            result_text = f"『{attacker_name}』的{attacker.name}获胜，剩余气血{a_hp}"
        elif d_hp > 0 and a_hp <= 0:
            winner = "defender"
            result_text = f"『{defender_name}』的{defender.name}获胜，剩余气血{d_hp}"
        elif a_hp > d_hp:
            winner = "attacker"
            result_text = f"回合结束，『{attacker_name}』的{attacker.name}剩余气血更多，获胜"
        else:
            winner = "defender"
            result_text = f"回合结束，『{defender_name}』的{defender.name}剩余气血更多，获胜"
        
        return {
            "battle_num": battle_num,
            "attacker_beast": attacker.name,
            "defender_beast": defender.name,
            "winner": winner,
            "rounds": rounds,
            "result": result_text,
        }
    
    def _calc_damage(self, attacker, defender) -> int:
        """计算伤害（新公式）
        
        - 当 (攻击 - 防御) ≥ 0 时：伤害 = (攻击 - 防御) × 0.069（四舍五入）
        - 当 (攻击 - 防御) < 0 时：固定扣血 5 点
        """
        # 判断攻击类型
        if attacker.nature and "法系" in attacker.nature:
            attack = attacker.magic_attack
            defense = defender.magic_defense
        else:
            attack = attacker.physical_attack
            defense = defender.physical_defense
        
        diff = attack - defense
        
        if diff >= 0:
            damage = round(diff * 0.069)
        else:
            damage = 5
        
        return max(1, damage)
    
    def get_battle_log(self, battle_id: int) -> Optional[Dict]:
        """获取战斗记录详情"""
        log = self.battle_repo.get_by_id(battle_id)
        if log:
            return log.to_dict()
        return None
    
    def get_dynamics(self, user_id: int = None, dynamic_type: str = "all", limit: int = 20) -> List[Dict]:
        """
        获取动态列表
        
        Args:
            user_id: 用户ID（个人动态需要）
            dynamic_type: "all" = 全服动态, "personal" = 个人动态
            limit: 返回数量
        
        Returns:
            动态列表
        """
        if dynamic_type == "personal" and user_id:
            logs = self.battle_repo.get_user_battles(user_id, limit)
        else:
            logs = self.battle_repo.get_recent_battles(limit)
        
        result = []
        for log in logs:
            result.append({
                "id": log.id,
                "time": log.created_at.strftime("%Y年%m月%d日 %H:%M") if log.created_at else "",
                "remaining": f"剩余{log.remaining_seconds // 60:02d}分{log.remaining_seconds % 60:02d}秒时",
                "attacker": log.attacker_name,
                "attacker_id": log.attacker_id,
                "defender": log.defender_name,
                "defender_id": log.defender_id,
                "floor": log.floor,
                "success": log.is_success,
                "text": self._format_dynamic_text(log),
            })
        
        return result
    
    def _format_dynamic_text(self, log: ZhenyaoBattleLog) -> str:
        """格式化动态文本"""
        if log.is_success:
            return f"{log.attacker_name} 把 {log.defender_name} 打到落花流水，抢夺第{log.floor}层聚魂阵成功！"
        else:
            return f"{log.attacker_name} 挑战 {log.defender_name} 的第{log.floor}层聚魂阵失败！"
