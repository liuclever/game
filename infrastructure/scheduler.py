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


def start_scheduler():
    """启动后台调度器（应在应用启动时调用一次）"""
    global _scheduler
    if _scheduler is not None:
        return  # 已启动

    _scheduler = BackgroundScheduler(daemon=True)
    # 每天 00:05 触发
    _scheduler.add_job(
        _run_daily_battlefield,
        trigger="cron",
        hour=0,
        minute=5,
        id="daily_battlefield",
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
    
    _scheduler.start()
    logger.info("[Scheduler] 后台调度器已启动，包含召唤之王定时任务和盟战赛季奖励任务")


def shutdown_scheduler():
    """关闭调度器（可选，应用退出时调用）"""
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("[Scheduler] 后台调度器已关闭")

