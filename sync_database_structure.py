"""同步数据库结构 - 添加缺失的表和字段"""
from infrastructure.db.connection import execute_update, execute_query

print("=" * 60)
print("开始同步数据库结构")
print("=" * 60)

# 1. 添加 signin_rewards_claimed 字段到 player 表
print("\n【1】添加 player.signin_rewards_claimed 字段...")
try:
    # 先检查字段是否已存在
    cols = execute_query("DESCRIBE player")
    has_field = any(c['Field'] == 'signin_rewards_claimed' for c in cols)
    
    if has_field:
        print("✅ signin_rewards_claimed 字段已存在，跳过")
    else:
        execute_update("""
            ALTER TABLE player 
            ADD COLUMN signin_rewards_claimed VARCHAR(50) DEFAULT '' 
            COMMENT '已领取的签到奖励，逗号分隔，例如: 7,15,30'
        """)
        print("✅ 成功添加 signin_rewards_claimed 字段")
except Exception as e:
    print(f"❌ 添加字段失败: {e}")

# 2. 创建 player_signin_records 表
print("\n【2】创建 player_signin_records 表...")
try:
    # 先检查表是否已存在
    tables = execute_query("SHOW TABLES LIKE 'player_signin_records'")
    
    if tables:
        print("✅ player_signin_records 表已存在，跳过")
    else:
        execute_update("""
            CREATE TABLE player_signin_records (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                signin_date DATE NOT NULL,
                is_makeup TINYINT DEFAULT 0 COMMENT '是否为补签: 0-正常签到, 1-补签',
                reward_copper INT DEFAULT 0 COMMENT '获得的铜钱奖励',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY uk_user_date (user_id, signin_date),
                KEY idx_user_id (user_id),
                KEY idx_signin_date (signin_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='玩家签到记录表'
        """)
        print("✅ 成功创建 player_signin_records 表")
except Exception as e:
    print(f"❌ 创建表失败: {e}")

# 3. 验证结果
print("\n" + "=" * 60)
print("验证同步结果")
print("=" * 60)

# 验证字段
print("\n【验证字段】")
cols = execute_query("DESCRIBE player")
has_field = any(c['Field'] == 'signin_rewards_claimed' for c in cols)
if has_field:
    print("✅ signin_rewards_claimed 字段存在")
else:
    print("❌ signin_rewards_claimed 字段不存在")

# 验证表
print("\n【验证表】")
tables = execute_query("SHOW TABLES LIKE 'player_signin_records'")
if tables:
    print("✅ player_signin_records 表存在")
    # 显示表结构
    structure = execute_query("DESCRIBE player_signin_records")
    print("\n表结构:")
    for col in structure:
        print(f"  {col['Field']:20} {col['Type']:20} NULL:{col['Null']:3} KEY:{col['Key']:3}")
else:
    print("❌ player_signin_records 表不存在")

print("\n" + "=" * 60)
print("同步完成！")
print("=" * 60)
