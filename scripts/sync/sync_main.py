"""
数据库同步主入口脚本
将本地数据库同步到远程数据库（不删除远程数据）
"""
import sys
import os
from datetime import datetime

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from .sync_config import test_connections
    from .sync_logger import get_logger
    from .sync_tables_players import sync_player_tables
    from .sync_tables_alliance import sync_alliance_tables
    from .sync_tables_battle import sync_battle_tables
    from .sync_tables_others import sync_other_tables
except ImportError:
    from sync_config import test_connections
    from sync_logger import get_logger
    from sync_tables_players import sync_player_tables
    from sync_tables_alliance import sync_alliance_tables
    from sync_tables_battle import sync_battle_tables
    from sync_tables_others import sync_other_tables


def main():
    """主函数"""
    # 创建日志文件
    log_file = f"sync_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logger = get_logger(log_file)
    
    logger.info("=" * 60)
    logger.info("数据库同步开始")
    logger.info(f"日志文件: {log_file}")
    logger.info("=" * 60)
    
    # 测试数据库连接
    logger.info("测试数据库连接...")
    if not test_connections():
        logger.error("数据库连接测试失败，请检查配置")
        return 1
    
    logger.info("数据库连接测试通过")
    logger.info("")
    
    # 总统计
    total_stats = {
        'inserted': 0,
        'updated': 0,
        'skipped': 0,
        'errors': 0,
    }
    
    try:
        # 同步玩家相关表
        stats = sync_player_tables()
        total_stats['inserted'] += stats['inserted']
        total_stats['updated'] += stats['updated']
        total_stats['skipped'] += stats['skipped']
        total_stats['errors'] += stats['errors']
        logger.info("")
        
        # 同步联盟相关表
        stats = sync_alliance_tables()
        total_stats['inserted'] += stats['inserted']
        total_stats['updated'] += stats['updated']
        total_stats['skipped'] += stats['skipped']
        total_stats['errors'] += stats['errors']
        logger.info("")
        
        # 同步战斗相关表
        stats = sync_battle_tables()
        total_stats['inserted'] += stats['inserted']
        total_stats['updated'] += stats['updated']
        total_stats['skipped'] += stats['skipped']
        total_stats['errors'] += stats['errors']
        logger.info("")
        
        # 同步其他表
        stats = sync_other_tables()
        total_stats['inserted'] += stats['inserted']
        total_stats['updated'] += stats['updated']
        total_stats['skipped'] += stats['skipped']
        total_stats['errors'] += stats['errors']
        
    except KeyboardInterrupt:
        logger.warning("用户中断同步")
        return 1
    except Exception as e:
        logger.error(f"同步过程中发生错误: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1
    
    # 打印最终统计
    logger.info("")
    logger.info("=" * 60)
    logger.info("数据库同步完成")
    logger.info("=" * 60)
    logger.info(f"总插入行数: {total_stats['inserted']}")
    logger.info(f"总更新行数: {total_stats['updated']}")
    logger.info(f"总跳过行数: {total_stats['skipped']}")
    logger.info(f"总错误数: {total_stats['errors']}")
    logger.info(f"日志文件: {log_file}")
    logger.info("=" * 60)
    
    return 0 if total_stats['errors'] == 0 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
