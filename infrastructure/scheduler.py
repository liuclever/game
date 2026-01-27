# infrastructure/scheduler.py
"""后台定时任务调度器

职责：
- 每日 00:05 自动触发猛虎战场和飞鹤战场开赛
- 防止同一天重复开赛（检查当日是否已有战报）
- 每分钟自动增加所有玩家的活力值（受VIP等级上限限制）
"""

from __future__ import annotations

import logging
import json
from datetime import date
from typing import Optional
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import timezone, timedelta

from infrastructure.db.connection import execute_query, execute_update
from infrastructure.db.player_repo_mysql import MySQLPlayerRepo
from infrastructure.db.player_beast_repo_mysql import MySQLPlayerBeastRepo
from infrastructure.db.immortalize_pool_repo_mysql import MySQLImmortalizePoolRepo

from infrastructure.db.battlefield_repo_mysql import MySQLBattlefieldBattleRepo
from infrastructure.db.alliance_repo_mysql import MySQLAllianceRepo
from application.services.battlefield_service import BattlefieldService
from application.services.immortalize_pool_service import ImmortalizePoolService
from application.services.alliance_service import AllianceService
from application.services.inventory_service import InventoryService
from domain.services.king_final_service import (
    reset_weekly_registration,
    advance_to_finals,
    run_final_stage
)

logger = logging.getLogger(__name__)

_scheduler: Optional[BackgroundScheduler] = None


def _load_vip_energy_max_config() -> dict:
    """加载VIP活力上限配置"""
    base_dir = Path(__file__).resolve().parents[1]
    config_path = base_dir / "configs" / "vip_privileges.json"
    energy_max_map = {}
    try:
        with config_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        for lv_data in data.get("vip_levels", []):
            level = lv_data.get("level", 0)
            vitality_max = lv_data.get("privileges", {}).get("vitality_max", 100)
            energy_max_map[level] = vitality_max
    except Exception as e:
        logger.warning(f"[Scheduler] 加载VIP配置失败: {e}")
    return energy_max_map


def _run_energy_regen():
    """每分钟自动增加所有玩家的活力值"""
    logger.debug("[Scheduler] 执行活力值自动恢复任务")
    
    vip_energy_map = _load_vip_energy_max_config()
    
    for vip_level in range(11):
        energy_max = vip_energy_map.get(vip_level, 100)
        execute_update(
            """
            UPDATE player 
            SET energy = LEAST(energy + 1, %s) 
            WHERE vip_level = %s AND energy < %s
            """,
            (energy_max, vip_level, energy_max),
        )


def _has_today_battle_log(battlefield_type: str) -> bool:
    """检查当天是否已有该战场的战报记录"""
    rows = execute_query(
        """
        SELECT 1 FROM battlefield_battle_log
        WHERE battlefield_type = %s AND DATE(created_at) = CURDATE()
        LIMIT 1
        """,
        (battlefield_type,),
    )
    return bool(rows)


def _run_daily_battlefield():
    """每日自动开赛任务：依次跑猛虎、飞鹤战场"""
    logger.info("[Scheduler] 开始执行每日古战场自动开赛任务")

    player_repo = MySQLPlayerRepo()
    beast_repo = MySQLPlayerBeastRepo()
    battle_repo = MySQLBattlefieldBattleRepo()

    service = BattlefieldService(
        player_repo=player_repo,
        player_beast_repo=beast_repo,
        battle_repo=battle_repo,
    )

    for bf_type in ("tiger", "crane"):
        if _has_today_battle_log(bf_type):
            logger.info(f"[Scheduler] {bf_type} 战场今日已有战报，跳过")
            continue

        try:
            result = service.run_tournament(bf_type)
            if result.get("ok"):
                logger.info(
                    f"[Scheduler] {bf_type} 战场开赛成功，期数={result.get('period')}, "
                    f"参赛人数={result.get('total_players')}, 冠军={result.get('champion_name')}"
                )
            else:
                logger.warning(f"[Scheduler] {bf_type} 战场开赛失败: {result.get('error')}")
        except Exception as e:
            logger.exception(f"[Scheduler] {bf_type} 战场开赛异常: {e}")

    logger.info("[Scheduler] 每日古战场自动开赛任务完成")


def _run_immortalize_formation():
    """每小时结算化仙阵收益"""
    logger.debug("[Scheduler] 执行化仙阵经验结算任务")
    rows = execute_query(
        """
        SELECT user_id
        FROM player_immortalize_pool
        WHERE formation_started_at IS NOT NULL
          AND formation_ends_at > NOW()
        """
    )
    if not rows:
        return

    pool_repo = MySQLImmortalizePoolRepo()
    player_repo = MySQLPlayerRepo()
    service = ImmortalizePoolService(
        pool_repo=pool_repo,
        player_repo=player_repo,
    )

    for row in rows:
        user_id = row.get("user_id")
        if not user_id:
            continue
        try:
            result = service.grant_formation_exp_for_user(user_id)
            if result and result.get("total_added"):
                logger.info(
                    "[Scheduler] 化仙阵结算: user=%s, hours=%s, exp=%s, finished=%s",
                    user_id,
                    result.get("hours_processed"),
                    result.get("total_added"),
                    result.get("finished"),
                )
        except Exception as exc:
            logger.exception("[Scheduler] 化仙阵结算失败 user=%s: %s", user_id, exc)


def _run_king_weekly_reset():
    """每周一00:00执行：重置召唤之王报名状态"""
    logger.info("[Scheduler] 开始执行召唤之王周报名重置任务")
    try:
        reset_weekly_registration()
        logger.info("[Scheduler] 召唤之王周报名重置完成")
    except Exception as e:
        logger.exception(f"[Scheduler] 召唤之王周报名重置失败: {e}")


def _run_king_advance_to_finals():
    """每周四23:59执行：选出各赛区前16名进入正赛"""
    logger.info("[Scheduler] 开始执行召唤之王晋级正赛任务")
    try:
        count = advance_to_finals()
        logger.info(f"[Scheduler] 召唤之王晋级正赛完成，共{count}名选手")
    except Exception as e:
        logger.exception(f"[Scheduler] 召唤之王晋级正赛失败: {e}")


def _run_king_final_stage(stage: str):
    """执行召唤之王正赛阶段"""
    logger.info(f"[Scheduler] 开始执行召唤之王{stage}强赛")
    try:
        run_final_stage(stage)
        logger.info(f"[Scheduler] 召唤之王{stage}强赛完成")
    except Exception as e:
        logger.exception(f"[Scheduler] 召唤之王{stage}强赛失败: {e}")


def _run_alliance_season_rewards():
    """每月最后一天23:59发放盟战赛季奖励"""
    logger.info("[Scheduler] 开始执行盟战赛季奖励发放任务")
    try:
        from datetime import datetime
        now = datetime.utcnow()
        # 获取当月的赛季（在最后一天发放当月的奖励）
        season_key = f"{now.year}-{now.month:02d}"
        
        # 初始化服务
        alliance_repo = MySQLAllianceRepo()
        player_repo = MySQLPlayerRepo()
        from infrastructure.db.inventory_repo_mysql import MySQLInventoryRepo
        from infrastructure.config.item_repo_from_config import ConfigItemRepo
        inventory_repo = MySQLInventoryRepo()
        item_repo = ConfigItemRepo()
        inventory_service = InventoryService(item_repo=item_repo, inventory_repo=inventory_repo)
        from infrastructure.db.player_beast_repo_mysql import MySQLPlayerBeastRepo
        beast_repo = MySQLPlayerBeastRepo()
        
        alliance_service = AllianceService(
            alliance_repo=alliance_repo,
            player_repo=player_repo,
            inventory_service=inventory_service,
            beast_repo=beast_repo,
        )
        
        result = alliance_service.distribute_season_rewards(season_key)
        if result.get("ok"):
            logger.info(
                f"[Scheduler] 盟战赛季奖励发放成功，赛季={season_key}, "
                f"发放联盟数={result.get('count', 0)}"
            )
            for dist in result.get("distributed", []):
                logger.info(
                    f"[Scheduler] 联盟{dist.get('alliance_name')}（第{dist.get('rank')}名）"
                    f"奖励已发放给{dist.get('success_count', 0)}/{dist.get('member_count', 0)}名成员"
                )
        else:
            logger.warning(f"[Scheduler] 盟战赛季奖励发放失败: {result.get('error')}")
    except Exception as e:
        logger.exception(f"[Scheduler] 盟战赛季奖励发放异常: {e}")
    
    logger.info("[Scheduler] 盟战赛季奖励发放任务完成")


def _run_daily_dungeon_reset():
    """每日00:00重置所有副本进度到第1层"""
    logger.info("[Scheduler] 开始执行副本每日重置任务")
    try:
        # 重置所有玩家的所有副本进度到第1层
        result = execute_update("""
            UPDATE player_dungeon_progress
            SET current_floor = 1,
                floor_cleared = TRUE,
                floor_event_type = 'beast',
                resets_today = 0,
                last_reset_date = CURDATE(),
                loot_claimed = TRUE
            WHERE current_floor > 1
        """)
        logger.info(f"[Scheduler] 副本每日重置完成，共重置 {result} 条记录")
    except Exception as e:
        logger.exception(f"[Scheduler] 副本每日重置失败: {e}")


def _run_alliance_war_battle():
    """每周三和周六20:00自动执行盟战对战"""
    logger.info("[Scheduler] 开始执行盟战自动对战任务")
    try:
        from infrastructure.db.alliance_repo_mysql import MySQLAllianceRepo
        from infrastructure.db.player_repo_mysql import MySQLPlayerRepo
        from infrastructure.db.player_beast_repo_mysql import MySQLPlayerBeastRepo
        from application.services.alliance_battle_service import AllianceBattleService
        from application.services.beast_pvp_service import BeastPvpService
        from datetime import datetime
        
        alliance_repo = MySQLAllianceRepo()
        player_repo = MySQLPlayerRepo()
        player_beast_repo = MySQLPlayerBeastRepo()
        beast_pvp_service = BeastPvpService()
        
        battle_service = AllianceBattleService(
            alliance_repo=alliance_repo,
            player_repo=player_repo,
            player_beast_repo=player_beast_repo,
            beast_pvp_service=beast_pvp_service,
        )
        
        # 验证当前时间是否在对战时间内（定时任务应该在对战时间触发，但做双重检查）
        from application.services.alliance_service import AllianceService
        from datetime import timezone, timedelta
        alliance_service = AllianceService(
            alliance_repo=alliance_repo,
            player_repo=player_repo,
            inventory_service=None,  # 定时任务不需要
            beast_repo=player_beast_repo,
        )
        # 使用中国时区（UTC+8）的当前时间
        china_tz = timezone(timedelta(hours=8))
        now = datetime.now(china_tz)
        is_war, phase, status = alliance_service._is_war_time(now)
        if not is_war or status != "battle":
            logger.warning(
                f"[Scheduler] 当前不在对战时间内（状态：{status}），但定时任务已触发。"
                f"将继续执行对战流程以确保土地争夺战正常进行。"
            )
        
        # 所有土地ID（1-4）
        land_ids = [1, 2, 3, 4]
        total_battles = 0
        success_count = 0
        
        for land_id in land_ids:
            try:
                # 执行完整对战流程（类似测试功能的"测试开战-全部土地"）
                from domain.entities.alliance_registration import (
                    STATUS_VICTOR, STATUS_REGISTERED, STATUS_CONFIRMED,
                    STATUS_ELIMINATED, STATUS_CANCELLED, STATUS_IN_BATTLE
                )
                
                # 1. 修复报名状态：将异常状态重置为已报名
                all_registrations = alliance_repo.list_land_registrations_by_land(land_id)
                fixed_count = 0
                for reg in all_registrations:
                    if reg.status not in [STATUS_REGISTERED, STATUS_CONFIRMED, STATUS_VICTOR, STATUS_CANCELLED]:
                        reg.status = STATUS_REGISTERED
                        alliance_repo.save_land_registration(reg)
                        fixed_count += 1
                
                if fixed_count > 0:
                    logger.info(f"[Scheduler] 土地 {land_id} 修复了 {fixed_count} 个报名状态")
                
                # 2. 循环配对和执行对战，直到只剩下一个胜利者
                round_number = 0
                max_rounds = 10  # 防止无限循环
                
                while round_number < max_rounds:
                    round_number += 1
                    logger.info(f"[Scheduler] 土地 {land_id} 第 {round_number} 轮配对")
                    
                    # 检查当前有多少个活跃的报名
                    all_registrations = alliance_repo.list_land_registrations_by_land(land_id)
                    active_registrations = [r for r in all_registrations if r.is_active() or r.status == STATUS_VICTOR]
                    victor_registrations = [r for r in all_registrations if r.status == STATUS_VICTOR]
                    
                    # 如果有多个胜利者，重置状态以便下一轮配对
                    if len(victor_registrations) > 1:
                        for victor in victor_registrations:
                            victor.status = STATUS_REGISTERED
                            alliance_repo.save_land_registration(victor)
                        logger.info(f"[Scheduler] 土地 {land_id} 有 {len(victor_registrations)} 个胜利者，重置状态以便下一轮配对")
                    
                    # 检查是否只剩下一个胜利者
                    if len(victor_registrations) == 1 and len(active_registrations) == 1:
                        victor = victor_registrations[0]
                        war_date = now.date()
                        weekday = now.weekday()
                        war_phase = "first" if weekday <= 2 else "second"
                        season_key = now.strftime("%Y-%m")
                        alliance_repo.increment_alliance_war_score(victor.alliance_id, season_key, 1)
                        alliance_repo.set_land_occupation(land_id, victor.alliance_id, war_phase, war_date)
                        logger.info(f"[Scheduler] 土地 {land_id} 已被联盟 {victor.alliance_id} 占领（最终胜利者）")
                        success_count += 1
                        break
                    
                    # 如果只有一个活跃的报名，自动成为胜利者并占领土地
                    if len(active_registrations) == 1 and len(victor_registrations) == 0:
                        victor = active_registrations[0]
                        victor.status = STATUS_VICTOR
                        alliance_repo.save_land_registration(victor)
                        war_date = now.date()
                        weekday = now.weekday()
                        war_phase = "first" if weekday <= 2 else "second"
                        season_key = now.strftime("%Y-%m")
                        alliance_repo.increment_alliance_war_score(victor.alliance_id, season_key, 1)
                        alliance_repo.set_land_occupation(land_id, victor.alliance_id, war_phase, war_date)
                        logger.info(f"[Scheduler] 土地 {land_id} 已被联盟 {victor.alliance_id} 占领（唯一报名者）")
                        success_count += 1
                        break
                    
                    # 配对联盟
                    try:
                        pair_result = battle_service.lock_and_pair_land(land_id)
                    except Exception as e:
                        logger.exception(f"[Scheduler] 土地 {land_id} 配对时发生异常")
                        break
                    
                    if not pair_result.get("ok"):
                        error = pair_result.get("error", "未知错误")
                        if "至少需要两个联盟报名" not in error:
                            logger.warning(f"[Scheduler] 土地 {land_id} 配对失败: {error}")
                        break
                    
                    # 如果已经直接占领了
                    if pair_result.get("occupation"):
                        logger.info(f"[Scheduler] 土地 {land_id} 已被直接占领")
                        success_count += 1
                        break
                    
                    # 如果所有报名都弃权了
                    battles = pair_result.get("battles", [])
                    if not battles or len(battles) == 0:
                        logger.info(f"[Scheduler] 土地 {land_id} 没有需要配对的对战（所有报名都已弃权）")
                        break
                    
                    total_battles += len(battles)
                    logger.info(f"[Scheduler] 土地 {land_id} 配对成功，共 {len(battles)} 场对战")
                    
                    # 执行每场对战的所有回合
                    for battle_info in battles:
                        battle_id = battle_info["battle_id"]
                        left_alliance_id = battle_info["left_alliance_id"]
                        right_alliance_id = battle_info["right_alliance_id"]
                        
                        logger.info(
                            f"[Scheduler] 开始执行土地 {land_id} 对战 {battle_id}: "
                            f"联盟 {left_alliance_id} vs 联盟 {right_alliance_id}"
                        )
                        
                        # 循环推进回合直到战斗结束
                        rounds_executed = 0
                        battle_finished = False
                        max_rounds_per_battle = 20
                        
                        while not battle_finished and rounds_executed < max_rounds_per_battle:
                            try:
                                advance_result = battle_service.advance_round(battle_id)
                                if not advance_result.get("ok"):
                                    logger.warning(
                                        f"[Scheduler] 土地 {land_id} 对战 {battle_id} 第 {rounds_executed + 1} 回合推进失败: {advance_result.get('error')}"
                                    )
                                    break
                                
                                rounds_executed += 1
                                
                                if advance_result.get("battle_finished"):
                                    battle_finished = True
                                    success_count += 1
                                    logger.info(
                                        f"[Scheduler] 土地 {land_id} 对战 {battle_id} 完成（共 {rounds_executed} 回合）"
                                    )
                                    break
                            except Exception as e:
                                logger.exception(f"[Scheduler] 土地 {land_id} 对战 {battle_id} 执行异常")
                                break
                        
                        if rounds_executed >= max_rounds_per_battle:
                            logger.warning(
                                f"[Scheduler] 土地 {land_id} 对战 {battle_id} 达到最大回合数限制"
                            )
                    
                    # 执行完所有对战后，检查最终胜利者
                    all_registrations = alliance_repo.list_land_registrations_by_land(land_id)
                    victor_registrations = [r for r in all_registrations if r.status == STATUS_VICTOR]
                    
                    # 如果只有一个胜利者，是最终胜利者
                    if len(victor_registrations) == 1:
                        victor = victor_registrations[0]
                        war_date = now.date()
                        weekday = now.weekday()
                        war_phase = "first" if weekday <= 2 else "second"
                        season_key = now.strftime("%Y-%m")
                        alliance_repo.increment_alliance_war_score(victor.alliance_id, season_key, 1)
                        alliance_repo.set_land_occupation(land_id, victor.alliance_id, war_phase, war_date)
                        logger.info(f"[Scheduler] 土地 {land_id} 已被联盟 {victor.alliance_id} 占领（最终胜利者）")
                        success_count += 1
                        break
                    
                    # 如果有多个胜利者，继续下一轮配对
                    if len(victor_registrations) > 1:
                        continue
                    
                    # 如果没有胜利者，可能所有报名都已弃权或被淘汰
                    active_registrations = [r for r in all_registrations if r.is_active() or r.status == STATUS_VICTOR]
                    if len(active_registrations) == 0:
                        logger.info(f"[Scheduler] 土地 {land_id} 没有活跃的报名，对战结束")
                        break
                
                if round_number >= max_rounds:
                    logger.warning(f"[Scheduler] 土地 {land_id} 达到最大轮数限制，停止执行")
                
            except Exception as e:
                logger.exception(f"[Scheduler] 土地 {land_id} 对战执行异常: {e}")
        
        logger.info(
            f"[Scheduler] 盟战自动对战任务完成，共执行 {total_battles} 场对战，"
            f"成功完成 {success_count} 场"
        )
        
        # 所有土地对战完成后，递增届次
        try:
            new_session = alliance_service._increment_war_session_number()
            logger.info(f"[Scheduler] 盟战届次已递增至第 {new_session} 届")
        except Exception as e:
            logger.exception(f"[Scheduler] 递增盟战届次时发生异常: {e}")
    except Exception as e:
        logger.exception(f"[Scheduler] 盟战自动对战任务异常: {e}")


def _check_and_compensate_dungeon_reset():
    """检查并补偿执行副本重置（启动时调用）"""
    try:
        from datetime import date
        today = date.today()
        
        # 检查是否有需要重置的副本（当前层数>1 且 上次重置日期不是今天）
        records = execute_query("""
            SELECT COUNT(*) as count 
            FROM player_dungeon_progress 
            WHERE current_floor > 1 
            AND (last_reset_date IS NULL OR last_reset_date < CURDATE())
        """)
        
        count = records[0]['count'] if records else 0
        if count > 0:
            logger.info(f"[Scheduler] 启动时发现 {count} 条副本需要重置，立即执行补偿重置")
            _run_daily_dungeon_reset()
        else:
            logger.info("[Scheduler] 启动时检查：所有副本状态正常，无需补偿重置")
    except Exception as e:
        logger.exception(f"[Scheduler] 启动时补偿检查失败: {e}")


def start_scheduler():
    """启动后台调度器（应在应用启动时调用一次）"""
    global _scheduler
    if _scheduler is not None:
        return  # 已启动

    # 启动时检查并补偿执行副本重置
    _check_and_compensate_dungeon_reset()

    # 使用中国时区（UTC+8）
    china_tz = timezone(timedelta(hours=8))
    _scheduler = BackgroundScheduler(daemon=True, timezone=china_tz)
    # 每天 00:05 触发
    _scheduler.add_job(
        _run_daily_battlefield,
        trigger="cron",
        hour=0,
        minute=5,
        id="daily_battlefield",
        replace_existing=True,
    )
    # 每天 00:00 重置副本进度
    _scheduler.add_job(
        _run_daily_dungeon_reset,
        trigger="cron",
        hour=0,
        minute=0,
        id="daily_dungeon_reset",
        replace_existing=True,
    )
    # 每分钟增加活力值
    _scheduler.add_job(
        _run_energy_regen,
        trigger="interval",
        minutes=1,
        id="energy_regen",
        replace_existing=True,
    )
    # 每小时化仙阵结算
    _scheduler.add_job(
        _run_immortalize_formation,
        trigger="interval",
        hours=1,
        id="immortalize_formation",
        replace_existing=True,
    )
    
    # ===== 召唤之王定时任务 =====
    # 每周一 00:00 - 重置报名状态
    _scheduler.add_job(
        _run_king_weekly_reset,
        trigger="cron",
        day_of_week="mon",
        hour=0,
        minute=0,
        id="king_weekly_reset",
        replace_existing=True,
    )
    # 每周四 23:59 - 晋级正赛
    _scheduler.add_job(
        _run_king_advance_to_finals,
        trigger="cron",
        day_of_week="thu",
        hour=23,
        minute=59,
        id="king_advance_finals",
        replace_existing=True,
    )
    # 每周五 12:00-16:00 - 正赛各阶段
    for hour, stage in [(12, '32'), (13, '16'), (14, '8'), (15, '4'), (16, '2')]:
        _scheduler.add_job(
            lambda s=stage: _run_king_final_stage(s),
            trigger="cron",
            day_of_week="fri",
            hour=hour,
            minute=0,
            id=f"king_{stage}_stage",
            replace_existing=True,
        )
    
    # ===== 盟战赛季奖励定时任务 =====
    # 每月最后一天 23:59 - 发放赛季奖励
    _scheduler.add_job(
        _run_alliance_season_rewards,
        trigger="cron",
        day="last",
        hour=23,
        minute=59,
        id="alliance_season_rewards",
        replace_existing=True,
    )
    
    # ===== 盟战自动对战定时任务 =====
    # 周三 20:00 - 第一次盟战自动对战
    _scheduler.add_job(
        _run_alliance_war_battle,
        trigger="cron",
        day_of_week="wed",
        hour=20,
        minute=0,
        id="alliance_war_battle_wed",
        replace_existing=True,
    )
    # 周六 20:00 - 第二次盟战自动对战
    _scheduler.add_job(
        _run_alliance_war_battle,
        trigger="cron",
        day_of_week="sat",
        hour=20,
        minute=0,
        id="alliance_war_battle_sat",
        replace_existing=True,
    )
    
    _scheduler.start()
    logger.info("[Scheduler] 后台调度器已启动，包含副本每日重置、召唤之王定时任务、盟战赛季奖励任务和盟战自动对战任务")


def shutdown_scheduler():
    """关闭调度器（可选，应用退出时调用）"""
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("[Scheduler] 后台调度器已关闭")

