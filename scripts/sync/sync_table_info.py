"""
表信息获取模块
获取表的主键、字段等信息
"""
from typing import List, Dict, Optional, Tuple
import pymysql
try:
    from .sync_config import get_local_connection, get_remote_connection
except ImportError:
    from sync_config import get_local_connection, get_remote_connection


def get_table_primary_keys(conn: pymysql.Connection, table_name: str) -> List[str]:
    """获取表的主键字段列表"""
    primary_keys = []
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = %s 
                AND CONSTRAINT_NAME = 'PRIMARY'
                ORDER BY ORDINAL_POSITION
            """, (table_name,))
            results = cursor.fetchall()
            # 处理 DictCursor 和普通游标的返回结果
            if results and isinstance(results[0], dict):
                primary_keys = [row['COLUMN_NAME'] for row in results]
            else:
                primary_keys = [row[0] for row in results]
    except Exception as e:
        print(f"获取表 {table_name} 主键失败: {e}")
    return primary_keys


def get_table_columns(conn: pymysql.Connection, table_name: str) -> List[str]:
    """获取表的所有字段列表"""
    columns = []
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = %s 
                ORDER BY ORDINAL_POSITION
            """, (table_name,))
            results = cursor.fetchall()
            # 处理 DictCursor 和普通游标的返回结果
            if results and isinstance(results[0], dict):
                columns = [row['COLUMN_NAME'] for row in results]
            else:
                columns = [row[0] for row in results]
    except Exception as e:
        print(f"获取表 {table_name} 字段失败: {e}")
    return columns


def get_table_row_count(conn: pymysql.Connection, table_name: str) -> int:
    """获取表的行数"""
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) as cnt FROM `{table_name}`")
            result = cursor.fetchone()
            if isinstance(result, dict):
                return result.get('cnt', 0)
            else:
                return result[0] if result else 0
    except Exception as e:
        print(f"获取表 {table_name} 行数失败: {e}")
        return 0


def get_all_tables(conn: pymysql.Connection) -> List[str]:
    """获取数据库所有表名"""
    tables = []
    try:
        with conn.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            results = cursor.fetchall()
            # 处理 DictCursor 和普通游标的返回结果
            if results and isinstance(results[0], dict):
                # DictCursor 返回的键名可能是 'Tables_in_game_tower' 或类似的
                key = list(results[0].keys())[0]
                tables = [row[key] for row in results]
            else:
                tables = [row[0] for row in results]
    except Exception as e:
        print(f"获取表列表失败: {e}")
    return tables


def compare_table_structure(local_conn: pymysql.Connection, 
                           remote_conn: pymysql.Connection, 
                           table_name: str) -> Dict:
    """比较本地和远程表结构"""
    result = {
        'exists_local': False,
        'exists_remote': False,
        'columns_match': False,
        'primary_keys_match': False,
        'local_columns': [],
        'remote_columns': [],
        'local_pk': [],
        'remote_pk': [],
    }
    
    # 检查表是否存在
    local_tables = get_all_tables(local_conn)
    remote_tables = get_all_tables(remote_conn)
    
    result['exists_local'] = table_name in local_tables
    result['exists_remote'] = table_name in remote_tables
    
    if not result['exists_local']:
        return result
    
    # 获取字段和主键
    result['local_columns'] = get_table_columns(local_conn, table_name)
    result['local_pk'] = get_table_primary_keys(local_conn, table_name)
    
    if result['exists_remote']:
        result['remote_columns'] = get_table_columns(remote_conn, table_name)
        result['remote_pk'] = get_table_primary_keys(remote_conn, table_name)
        
        # 比较字段和主键
        result['columns_match'] = set(result['local_columns']) == set(result['remote_columns'])
        result['primary_keys_match'] = result['local_pk'] == result['remote_pk']
    
    return result
