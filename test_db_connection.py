"""
测试数据库连接
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

print("=" * 60)
print("测试数据库连接")
print("=" * 60)

print("\n[1] 导入数据库模块...")
try:
    from infrastructure.db.connection import execute_query, DB_CONFIG
    print("✅ 导入成功")
except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()
    input("\n按任意键退出...")
    sys.exit(1)

print("\n[2] 数据库配置:")
print(f"   Host: {DB_CONFIG['host']}")
print(f"   Port: {DB_CONFIG['port']}")
print(f"   User: {DB_CONFIG['user']}")
print(f"   Database: {DB_CONFIG['database']}")

print("\n[3] 测试连接...")
try:
    result = execute_query("SELECT VERSION() as version, DATABASE() as db")
    print("✅ 连接成功!")
    print(f"   MySQL版本: {result[0]['version']}")
    print(f"   当前数据库: {result[0]['db']}")
except Exception as e:
    print(f"❌ 连接失败: {e}")
    import traceback
    traceback.print_exc()
    input("\n按任意键退出...")
    sys.exit(1)

print("\n[4] 查询玩家表...")
try:
    result = execute_query("SELECT COUNT(*) as count, MAX(user_id) as max_id FROM player")
    print("✅ 查询成功!")
    print(f"   当前玩家数: {result[0]['count']}")
    print(f"   最大ID: {result[0]['max_id']}")
except Exception as e:
    print(f"❌ 查询失败: {e}")
    import traceback
    traceback.print_exc()
    input("\n按任意键退出...")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ 所有测试通过！数据库连接正常")
print("=" * 60)

input("\n按任意键退出...")
