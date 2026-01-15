"""
战斗相关表同步模块
"""
try:
    from .sync_data_core import sync_table_data
    from .sync_logger import get_logger
except ImportError:
    from sync_data_core import sync_table_data
    from sync_logger import get_logger

# 战斗相关表列表
BATTLE_TABLES = [
    'arena',                      # 竞技场
    'arena_battle_log',           # 竞技场战斗日志
    'arena_daily_challenge',       # 竞技场每日挑战
    'arena_stats',                # 竞技场统计
    'arena_streak',               # 竞技场连胜
    'arena_streak_history',       # 竞技场连胜历史
    'battlefield_battle_log',    # 战场战斗日志
    'battlefield_signup',         # 战场报名
    'king_challenge_logs',        # 王者挑战日志
    'king_challenge_rank',        # 王者挑战排名
    'king_final_stage',           # 王者最终阶段
    'king_reward_claimed',        # 王者奖励领取
    'king_season_config',         # 王者赛季配置
    'spar_battle_log',            # 切磋战斗日志
    'spar_records',               # 切磋记录
    'zhenyao_battle_log',        # 镇妖战斗日志
    'zhenyao_daily_count',        # 镇妖每日次数
    'zhenyao_floor',              # 镇妖层数
]


def sync_battle_tables():
    """同步所有战斗相关表"""
    logger = get_logger()
    logger.info("=" * 60)
    logger.info("开始同步战斗相关表")
    logger.info("=" * 60)
    
    total_stats = {
        'inserted': 0,
        'updated': 0,
        'skipped': 0,
        'errors': 0,
    }
    
    for table_name in BATTLE_TABLES:
        stats = sync_table_data(table_name, batch_size=1000, skip_if_empty=False)
        total_stats['inserted'] += stats['inserted']
        total_stats['updated'] += stats['updated']
        total_stats['skipped'] += stats['skipped']
        total_stats['errors'] += stats['errors']
    
    logger.info("=" * 60)
    logger.info("战斗相关表同步完成")
    logger.info(f"总计: 插入 {total_stats['inserted']}, 更新 {total_stats['updated']}, "
                f"跳过 {total_stats['skipped']}, 错误 {total_stats['errors']}")
    logger.info("=" * 60)
    
    return total_stats


if __name__ == "__main__":
    sync_battle_tables()
