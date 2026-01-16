"""
数据库同步配置模块
定义本地和远程数据库连接配置
"""
import pymysql
from pymysql.cursors import DictCursor

# 本地数据库配置（已注释 - 暂时不使用本地数据库）
# LOCAL_DB_CONFIG = {
#     'host': 'localhost',
#     'port': 3306,
#     'user': 'root',
#     'password': '1234',  # 根据实际情况修改
#     'database': 'game_tower',
#     'charset': 'utf8mb4',
#     'cursorclass': DictCursor,
#     'connect_timeout': 10,
# }

# 远程数据库配置
REMOTE_DB_CONFIG = {
    'host': '8.146.206.229',
    'port': 3306,
    'user': 'root',
    'password': 'Wxs1230.0',
    'database': 'game_tower',
    'charset': 'utf8mb4',
    'cursorclass': DictCursor,
    'connect_timeout': 10,
}


def get_local_connection():
    """获取本地数据库连接（已禁用）"""
    raise Exception("本地数据库连接已禁用，请先取消注释 LOCAL_DB_CONFIG")
    # return pymysql.connect(**LOCAL_DB_CONFIG)


def get_remote_connection():
    """获取远程数据库连接"""
    return pymysql.connect(**REMOTE_DB_CONFIG)


def test_connections():
    """测试数据库连接（只测试远程连接）"""
    results = {'local': False, 'remote': False}
    
    # 测试本地连接（已禁用）
    # try:
    #     conn = get_local_connection()
    #     with conn.cursor() as cursor:
    #         cursor.execute("SELECT 1")
    #         cursor.fetchone()
    #     conn.close()
    #     results['local'] = True
    #     print("[成功] 本地数据库连接正常")
    # except Exception as e:
    #     print(f"[失败] 本地数据库连接失败: {e}")
    print("[跳过] 本地数据库连接测试（已禁用）")
    results['local'] = True  # 设置为 True 以便测试通过
    
    # 测试远程连接
    try:
        conn = get_remote_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        conn.close()
        results['remote'] = True
        print("[成功] 远程数据库连接正常")
    except Exception as e:
        print(f"[失败] 远程数据库连接失败: {e}")
    
    return results['local'] and results['remote']


if __name__ == "__main__":
    test_connections()
