"""
MySQL数据库连接配置
"""
import pymysql
from pymysql.cursors import DictCursor


# 数据库配置
DB_CONFIG = {
    'host': '8.146.206.229',
    'port': 3306,
    'user': 'root',
    'password': 'Wxs1230.0',
    'database': 'game_tower',
    'charset': 'utf8mb4',
    'cursorclass': DictCursor,
}


def get_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)


def execute_query(sql: str, params: tuple = None) -> list:
    """执行查询，返回结果列表"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        conn.close()


def execute_update(sql: str, params: tuple = None) -> int:
    """执行更新，返回影响行数"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            result = cursor.execute(sql, params)
            conn.commit()
            return result
    finally:
        conn.close()


def execute_insert(sql: str, params: tuple = None) -> int:
    """执行插入，返回自增ID"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            conn.commit()
            return cursor.lastrowid
    finally:
        conn.close()
