"""
修复修行字段问题：
1. 检查数据库中是否存在旧的 cultivation_start 字段
2. 如果存在，将数据迁移到新的 cultivation_start_time 字段
3. 确保所有字段都存在并且数据正确
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from infrastructure.db.connection import execute_query, execute_update

def check_and_fix_cultivation_fields():
    print("检查修行相关字段...")
    
    # 1. 检查现有字段
    columns = execute_query("""
        SELECT COLUMN_NAME 
        FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = DATABASE() 
        AND TABLE_NAME = 'player' 
        AND COLUMN_NAME LIKE 'cultivation%'
    """)
    
    existing_columns = {row['COLUMN_NAME'] for row in columns}
    print(f"现有的cultivation字段: {existing_columns}")
    
    # 2. 如果存在旧字段 cultivation_start，需要迁移数据
    if 'cultivation_start' in existing_columns and 'cultivation_start_time' not in existing_columns:
        print("发现旧字段 cultivation_start，重命名为 cultivation_start_time...")
        execute_update("""
            ALTER TABLE player 
            CHANGE COLUMN cultivation_start cultivation_start_time DATETIME DEFAULT NULL
        """)
        print("✓ 字段重命名完成")
    elif 'cultivation_start' in existing_columns and 'cultivation_start_time' in existing_columns:
        print("同时存在 cultivation_start 和 cultivation_start_time，迁移数据...")
        # 将旧字段的数据复制到新字段
        execute_update("""
            UPDATE player 
            SET cultivation_start_time = cultivation_start 
            WHERE cultivation_start IS NOT NULL 
            AND cultivation_start_time IS NULL
        """)
        print("✓ 数据迁移完成")
        
        # 删除旧字段
        execute_update("ALTER TABLE player DROP COLUMN cultivation_start")
        print("✓ 删除旧字段 cultivation_start")
    
    # 3. 确保所有必需字段都存在
    required_fields = {
        'cultivation_start_time': 'DATETIME DEFAULT NULL',
        'cultivation_area': 'VARCHAR(50) DEFAULT NULL',
        'cultivation_dungeon': 'VARCHAR(50) DEFAULT NULL'
    }
    
    for field_name, field_def in required_fields.items():
        if field_name not in existing_columns:
            print(f"添加缺失的字段 {field_name}...")
            execute_update(f"ALTER TABLE player ADD COLUMN {field_name} {field_def}")
            print(f"✓ 添加字段 {field_name} 完成")
        else:
            print(f"✓ 字段 {field_name} 已存在")
    
    # 4. 检查是否有正在修行的用户数据
    cultivation_data = execute_query("""
        SELECT user_id, nickname, cultivation_start_time, cultivation_area, cultivation_dungeon
        FROM player 
        WHERE cultivation_start_time IS NOT NULL
    """)
    
    if cultivation_data:
        print(f"\n当前正在修行的用户数量: {len(cultivation_data)}")
        for row in cultivation_data:
            print(f"  - 用户 {row['nickname']} (ID:{row['user_id']}): "
                  f"开始时间={row['cultivation_start_time']}, "
                  f"区域={row['cultivation_area']}, "
                  f"副本={row['cultivation_dungeon']}")
    else:
        print("\n当前没有用户正在修行")
    
    print("\n✅ 修复完成！")

if __name__ == "__main__":
    try:
        check_and_fix_cultivation_fields()
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

