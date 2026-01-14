"""
核心数据同步逻辑模块
实现安全的数据同步（不删除远程数据）
"""
import pymysql
from typing import List, Dict, Optional, Tuple
try:
    from .sync_config import get_local_connection, get_remote_connection
    from .sync_table_info import get_table_primary_keys, get_table_columns, get_table_row_count
    from .sync_logger import get_logger
except ImportError:
    from sync_config import get_local_connection, get_remote_connection
    from sync_table_info import get_table_primary_keys, get_table_columns, get_table_row_count
    from sync_logger import get_logger

# 批量处理大小
BATCH_SIZE = 1000


def build_insert_on_duplicate_sql(table_name: str, columns: List[str], primary_keys: List[str]) -> str:
    """构建 INSERT ... ON DUPLICATE KEY UPDATE SQL"""
    if not columns:
        return None
    
    # 构建字段列表
    columns_str = ', '.join([f"`{col}`" for col in columns])
    placeholders = ', '.join(['%s'] * len(columns))
    
    # 构建 UPDATE 部分（排除主键）
    update_columns = [col for col in columns if col not in primary_keys]
    if not update_columns:
        # 如果没有可更新的字段，只插入新记录
        update_clause = ""
    else:
        update_clause = ", ".join([f"`{col}` = VALUES(`{col}`)" for col in update_columns])
    
    if update_clause:
        sql = f"""
            INSERT INTO `{table_name}` ({columns_str})
            VALUES ({placeholders})
            ON DUPLICATE KEY UPDATE {update_clause}
        """
    else:
        # 如果没有可更新的字段，使用 INSERT IGNORE
        sql = f"""
            INSERT IGNORE INTO `{table_name}` ({columns_str})
            VALUES ({placeholders})
        """
    
    return sql.strip()


def sync_table_data(table_name: str, 
                   batch_size: int = BATCH_SIZE,
                   skip_if_empty: bool = False) -> Dict[str, int]:
    """
    同步单个表的数据
    
    Args:
        table_name: 表名
        batch_size: 批量处理大小
        skip_if_empty: 如果本地表为空是否跳过
    
    Returns:
        统计信息字典: {inserted, updated, skipped, errors}
    """
    logger = get_logger()
    stats = {
        'inserted': 0,
        'updated': 0,
        'skipped': 0,
        'errors': 0,
    }
    
    logger.table_start(table_name)
    
    local_conn = None
    remote_conn = None
    
    try:
        # 获取连接
        local_conn = get_local_connection()
        remote_conn = get_remote_connection()
        
        # 检查表是否存在
        with local_conn.cursor() as cursor:
            cursor.execute("SHOW TABLES LIKE %s", (table_name,))
            if not cursor.fetchone():
                logger.table_skip(table_name, "本地表不存在")
                return stats
        
        # 获取表结构信息
        local_columns = get_table_columns(local_conn, table_name)
        if not local_columns:
            logger.table_skip(table_name, "无法获取表字段")
            return stats
        
        primary_keys = get_table_primary_keys(local_conn, table_name)
        if not primary_keys:
            logger.warning(f"表 {table_name} 没有主键，将使用 INSERT IGNORE 模式")
        
        # 检查本地表是否为空
        local_count = get_table_row_count(local_conn, table_name)
        if local_count == 0 and skip_if_empty:
            logger.table_skip(table_name, "本地表为空")
            return stats
        
        # 确保远程表存在（如果不存在则创建）
        with remote_conn.cursor() as cursor:
            cursor.execute("SHOW TABLES LIKE %s", (table_name,))
            if not cursor.fetchone():
                logger.warning(f"远程表 {table_name} 不存在，将创建表结构")
                # 获取创建表的 SQL
                with local_conn.cursor() as local_cursor:
                    local_cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
                    create_sql = local_cursor.fetchone()[1]
                    # 执行创建表
                    cursor.execute(create_sql)
                    remote_conn.commit()
                    logger.info(f"已创建远程表 {table_name}")
        
        # 构建 SQL
        sql = build_insert_on_duplicate_sql(table_name, local_columns, primary_keys)
        if not sql:
            logger.table_skip(table_name, "无法构建 SQL")
            return stats
        
        # 分批读取和同步数据
        offset = 0
        total_processed = 0
        
        with local_conn.cursor() as local_cursor:
            while True:
                # 读取本地数据
                select_sql = f"SELECT {', '.join([f'`{col}`' for col in local_columns])} FROM `{table_name}` LIMIT %s OFFSET %s"
                local_cursor.execute(select_sql, (batch_size, offset))
                rows = local_cursor.fetchall()
                
                if not rows:
                    break
                
                # 准备批量插入数据
                values_list = []
                for row in rows:
                    if isinstance(row, dict):
                        values = [row.get(col) for col in local_columns]
                    else:
                        values = list(row)
                    values_list.append(values)
                
                # 批量插入到远程数据库
                try:
                    with remote_conn.cursor() as remote_cursor:
                        # 执行批量插入
                        remote_cursor.executemany(sql, values_list)
                        affected_rows = remote_cursor.rowcount
                        remote_conn.commit()
                        
                        # 统计（注意：ON DUPLICATE KEY UPDATE 的 affected_rows 可能不准确）
                        # 1 = 插入, 2 = 更新, 0 = 无变化（被忽略）
                        # 这里简化处理，实际可能需要更精确的统计
                        stats['inserted'] += len(values_list)
                        total_processed += len(values_list)
                        
                except Exception as e:
                    logger.error(f"同步表 {table_name} 数据失败 (offset={offset}): {e}")
                    stats['errors'] += len(values_list)
                    remote_conn.rollback()
                
                offset += batch_size
                
                # 进度提示
                if total_processed % (batch_size * 10) == 0:
                    logger.info(f"表 {table_name} 已处理 {total_processed} 行...")
        
        logger.table_success(table_name, stats['inserted'], stats['updated'], stats['skipped'])
        
    except Exception as e:
        logger.error(f"同步表 {table_name} 时发生错误: {e}")
        stats['errors'] += 1
    
    finally:
        if local_conn:
            local_conn.close()
        if remote_conn:
            remote_conn.close()
    
    return stats
