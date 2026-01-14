"""
联盟相关表同步模块
"""
try:
    from .sync_data_core import sync_table_data
    from .sync_logger import get_logger
except ImportError:
    from sync_data_core import sync_table_data
    from sync_logger import get_logger

# 联盟相关表列表
ALLIANCE_TABLES = [
    'alliances',                          # 联盟基础信息
    'alliance_members',                   # 联盟成员
    'alliance_activities',                # 联盟活动
    'alliance_army_assignments',          # 联盟军队分配
    'alliance_army_signups',              # 联盟军队报名
    'alliance_beast_storage',             # 联盟妖兽仓库
    'alliance_buildings',                 # 联盟建筑
    'alliance_chat_messages',             # 联盟聊天消息
    'alliance_competition_battles',       # 联盟竞赛战斗
    'alliance_competition_personal_battles',  # 联盟竞赛个人战斗
    'alliance_competition_personal_scores',   # 联盟竞赛个人分数
    'alliance_competition_prestige',      # 联盟竞赛声望
    'alliance_competition_registrations', # 联盟竞赛注册
    'alliance_competition_rewards',       # 联盟竞赛奖励
    'alliance_competition_scores',        # 联盟竞赛分数
    'alliance_competition_sessions',      # 联盟竞赛会话
    'alliance_competition_signups',       # 联盟竞赛报名
    'alliance_competition_team_members',  # 联盟竞赛团队成员
    'alliance_competition_teams',         # 联盟竞赛团队
    'alliance_item_storage',             # 联盟物品仓库
    'alliance_land_battle',               # 联盟土地战斗
    'alliance_land_battle_duel',          # 联盟土地战斗决斗
    'alliance_land_battle_round',         # 联盟土地战斗回合
    'alliance_land_registration',         # 联盟土地注册
    'alliance_ore_claims',                # 联盟矿石领取
    'alliance_talents',                   # 联盟天赋
    'alliance_training_participants',     # 联盟训练参与者
    'alliance_training_rooms',            # 联盟训练房间
    'alliance_war_honor_effects',         # 联盟战争荣誉效果
]


def sync_alliance_tables():
    """同步所有联盟相关表"""
    logger = get_logger()
    logger.info("=" * 60)
    logger.info("开始同步联盟相关表")
    logger.info("=" * 60)
    
    total_stats = {
        'inserted': 0,
        'updated': 0,
        'skipped': 0,
        'errors': 0,
    }
    
    for table_name in ALLIANCE_TABLES:
        stats = sync_table_data(table_name, batch_size=1000, skip_if_empty=False)
        total_stats['inserted'] += stats['inserted']
        total_stats['updated'] += stats['updated']
        total_stats['skipped'] += stats['skipped']
        total_stats['errors'] += stats['errors']
    
    logger.info("=" * 60)
    logger.info("联盟相关表同步完成")
    logger.info(f"总计: 插入 {total_stats['inserted']}, 更新 {total_stats['updated']}, "
                f"跳过 {total_stats['skipped']}, 错误 {total_stats['errors']}")
    logger.info("=" * 60)
    
    return total_stats


if __name__ == "__main__":
    sync_alliance_tables()
