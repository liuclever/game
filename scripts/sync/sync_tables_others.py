"""
其他表同步模块
"""
try:
    from .sync_data_core import sync_table_data
    from .sync_logger import get_logger
except ImportError:
    from sync_data_core import sync_table_data
    from sync_logger import get_logger

# 其他表列表
OTHER_TABLES = [
    'beast_bone',                 # 妖兽骨骼
    'cultivation_config',         # 修行配置
    'dragonpalace_daily_state',   # 龙宫每日状态
    'friend_relation',            # 好友关系
    'friend_request',              # 好友请求
    'level_config',               # 等级配置
    'manor_land',                 # 庄园土地
    'mosoul_global_pity',         # 魔魂全局保底
    'mosoul_hunting_state',       # 魔魂狩猎状态
    'private_message',            # 私信
    'recharge_order',             # 充值订单
    'refine_pot_log',             # 炼化炉日志
    'spirit_account',             # 精灵账户
    'task_reward_claims',         # 任务奖励领取
    'tower_state',                # 塔状态
    'tree_player_week',           # 树玩家周
    'tree_week',                  # 树周
    'world_chat_message',         # 世界聊天消息
]


def sync_other_tables():
    """同步所有其他表"""
    logger = get_logger()
    logger.info("=" * 60)
    logger.info("开始同步其他表")
    logger.info("=" * 60)
    
    total_stats = {
        'inserted': 0,
        'updated': 0,
        'skipped': 0,
        'errors': 0,
    }
    
    for table_name in OTHER_TABLES:
        stats = sync_table_data(table_name, batch_size=1000, skip_if_empty=False)
        total_stats['inserted'] += stats['inserted']
        total_stats['updated'] += stats['updated']
        total_stats['skipped'] += stats['skipped']
        total_stats['errors'] += stats['errors']
    
    logger.info("=" * 60)
    logger.info("其他表同步完成")
    logger.info(f"总计: 插入 {total_stats['inserted']}, 更新 {total_stats['updated']}, "
                f"跳过 {total_stats['skipped']}, 错误 {total_stats['errors']}")
    logger.info("=" * 60)
    
    return total_stats


if __name__ == "__main__":
    sync_other_tables()
