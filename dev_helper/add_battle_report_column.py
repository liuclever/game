"""给召唤之王挑战记录表添加战报字段"""
import pymysql

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # 请填写你的MySQL密码
    'database': 'game_tower',
    'charset': 'utf8mb4'
}

# 添加字段的SQL
ALTER_TABLE_SQL = """
ALTER TABLE king_challenge_logs 
ADD COLUMN battle_report TEXT COMMENT '战报数据(JSON格式)' AFTER area_index
"""

def add_column():
    """添加字段"""
    try:
        # 连接数据库
        print("正在连接数据库...")
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 检查字段是否已存在
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'game_tower' 
            AND TABLE_NAME = 'king_challenge_logs' 
            AND COLUMN_NAME = 'battle_report'
        """)
        result = cursor.fetchone()
        
        if result[0] > 0:
            print("✅ 字段 battle_report 已存在，无需添加")
        else:
            # 添加字段
            print("正在添加字段 battle_report...")
            cursor.execute(ALTER_TABLE_SQL)
            conn.commit()
            print("✅ 字段添加成功！")
        
        print("\n表名: king_challenge_logs")
        print("新字段: battle_report (TEXT)")
        print("\n现在可以重启后端服务了。")
        
        cursor.close()
        conn.close()
        
    except pymysql.err.OperationalError as e:
        if e.args[0] == 1045:
            print("❌ 数据库连接失败：密码错误")
            print("\n请修改脚本中的密码：")
            print("打开 dev_helper/add_battle_report_column.py")
            print("修改第7行的 'password': '' 为你的MySQL密码")
        else:
            print(f"❌ 数据库连接失败：{e}")
    except Exception as e:
        print(f"❌ 添加字段失败：{e}")

if __name__ == "__main__":
    print("=" * 50)
    print("给召唤之王挑战记录表添加战报字段")
    print("=" * 50)
    print()
    
    # 提示用户检查密码
    password = DB_CONFIG['password']
    if not password:
        print("⚠️  注意：密码为空")
        print("如果你的MySQL有密码，请先修改脚本中的密码配置")
        print()
        input("按回车键继续...")
    
    add_column()
    
    print()
    input("按回车键退出...")
