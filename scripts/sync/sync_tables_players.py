"""
玩家相关表同步模块
"""
try:
    from .sync_data_core import sync_table_data
    from .sync_logger import get_logger
except ImportError:
    from sync_data_core import sync_table_data
    from sync_logger import get_logger

# 玩家相关表列表
PLAYER_TABLES = [
    'player',                    # 玩家基础信息
    'player_bag',                # 玩家背包
    'player_beast',              # 玩家妖兽
    'player_daily_activity',     # 玩家日常活动
    'player_dungeon_progress',   # 玩家副本进度
    'player_effect',             # 玩家效果
    'player_gift_claim',         # 玩家礼包领取
    'player_immortalize_pool',   # 玩家化神池
    'player_inventory',          # 玩家库存
    'player_manor',              # 玩家庄园
    'player_month_card',         # 玩家月卡
    'player_mosoul',             # 玩家魔魂
    'player_spirit',             # 玩家精灵
    'player_talent_levels',      # 玩家天赋等级
]


def sync_player_tables():
    """同步所有玩家相关表"""
    logger = get_logger()
    logger.info("=" * 60)
    logger.info("开始同步玩家相关表")
    logger.info("=" * 60)
    
    total_stats = {
        'inserted': 0,
        'updated': 0,
        'skipped': 0,
        'errors': 0,
    }
    
    for table_name in PLAYER_TABLES:
        stats = sync_table_data(table_name, batch_size=1000, skip_if_empty=False)
        total_stats['inserted'] += stats['inserted']
        total_stats['updated'] += stats['updated']
        total_stats['skipped'] += stats['skipped']
        total_stats['errors'] += stats['errors']
    
    logger.info("=" * 60)
    logger.info("玩家相关表同步完成")
    logger.info(f"总计: 插入 {total_stats['inserted']}, 更新 {total_stats['updated']}, "
                f"跳过 {total_stats['skipped']}, 错误 {total_stats['errors']}")
    logger.info("=" * 60)
    
    return total_stats


if __name__ == "__main__":
    sync_player_tables()
