"""直接创建召唤之王挑战记录表"""
import pymysql

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # 请填写你的MySQL密码
    'database': 'game_tower',
    'charset': 'utf8mb4'
}

# 创建表的SQL
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS king_challenge_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    challenger_id INT NOT NULL COMMENT '挑战者ID',
    challenger_name VARCHAR(50) NOT NULL COMMENT '挑战者昵称',
    defender_id INT NOT NULL COMMENT '防守者ID',
    defender_name VARCHAR(50) NOT NULL COMMENT '防守者昵称',
    challenger_wins BOOLEAN NOT NULL COMMENT '挑战者是否胜利',
    challenger_rank_before INT NOT NULL COMMENT '挑战者挑战前排名',
    challenger_rank_after INT NOT NULL COMMENT '挑战者挑战后排名',
    defender_rank_before INT NOT NULL COMMENT '防守者挑战前排名',
    defender_rank_after INT NOT NULL COMMENT '防守者挑战后排名',
    area_index INT NOT NULL COMMENT '赛区编号',
    challenge_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '挑战时间',
    INDEX idx_area_time (area_index, challenge_time),
    INDEX idx_challenger (challenger_id, challenge_time),
    INDEX idx_defender (defender_id, challenge_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='召唤之王挑战记录'
"""

def create_table():
    """创建表"""
    try:
        # 连接数据库
        print("正在连接数据库...")
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 创建表
        print("正在创建表 king_challenge_logs...")
        cursor.execute(CREATE_TABLE_SQL)
        conn.commit()
        
        print("✅ 表创建成功！")
        print("\n表名: king_challenge_logs")
        print("数据库: game_tower")
        print("\n现在可以重启后端服务了。")
        
        cursor.close()
        conn.close()
        
    except pymysql.err.OperationalError as e:
        if e.args[0] == 1045:
            print("❌ 数据库连接失败：密码错误")
            print("\n请修改脚本中的密码：")
            print("打开 dev_helper/create_king_logs_table.py")
            print("修改第7行的 'password': '' 为你的MySQL密码")
        else:
            print(f"❌ 数据库连接失败：{e}")
    except Exception as e:
        print(f"❌ 创建表失败：{e}")

if __name__ == "__main__":
    print("=" * 50)
    print("创建召唤之王挑战记录表")
    print("=" * 50)
    print()
    
    # 提示用户检查密码
    password = DB_CONFIG['password']
    if not password:
        print("⚠️  注意：密码为空")
        print("如果你的MySQL有密码，请先修改脚本中的密码配置")
        print()
        input("按回车键继续...")
    
    create_table()
    
    print()
    input("按回车键退出...")
