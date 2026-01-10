"""让镇妖测试玩家占领试炼层第101层。

运行方式：
    python tests/Demon_suppression/occupy_floor_101.py

功能：
    - 让 user_id=3000 的测试玩家占领试炼层第101层
    - 占领时长为30分钟
    - 如果该层已被其他玩家占领，会先清空

注意：
    - 需要先运行 create_zhenyao_test_player.py 创建测试玩家
    - 请勿在生产环境运行
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from infrastructure.db.connection import execute_query, execute_update


# 测试玩家ID
TEST_USER_ID = 3000
TARGET_FLOOR = 101
OCCUPY_DURATION_MINUTES = 30


def check_player_exists():
    """检查测试玩家是否存在"""
    rows = execute_query(
        "SELECT user_id, nickname, level FROM player WHERE user_id = %s",
        (TEST_USER_ID,)
    )
    
    if not rows:
        raise ValueError(
            f"测试玩家不存在 (user_id={TEST_USER_ID})，"
            "请先运行 create_zhenyao_test_player.py 创建测试玩家"
        )
    
    player = rows[0]
    print(f"✅ 找到测试玩家: {player['nickname']} (等级{player['level']})")
    
    # 检查等级是否足够（需要80级以上才能镇妖101层）
    if player['level'] < 80:
        raise ValueError(
            f"玩家等级不足（当前{player['level']}级），"
            "需要至少80级才能镇妖101-120层"
        )
    
    return player


def check_tower_progress():
    """检查通天塔进度"""
    rows = execute_query(
        "SELECT max_floor_record FROM tower_state WHERE user_id = %s AND tower_type = 'tongtian'",
        (TEST_USER_ID,)
    )
    
    if not rows:
        raise ValueError(
            "玩家没有通天塔进度记录，"
            "请先运行 create_zhenyao_test_player.py 创建测试玩家"
        )
    
    max_floor = rows[0]['max_floor_record']
    
    if max_floor < TARGET_FLOOR:
        raise ValueError(
            f"通天塔进度不足（当前最高{max_floor}层），"
            f"需要至少{TARGET_FLOOR}层才能镇妖第{TARGET_FLOOR}层"
        )
    
    print(f"✅ 通天塔进度: {max_floor}层")
    return max_floor


def check_beasts():
    """检查是否有出战幻兽"""
    rows = execute_query(
        "SELECT COUNT(*) as cnt FROM player_beast WHERE user_id = %s AND is_in_team = 1",
        (TEST_USER_ID,)
    )
    
    count = rows[0]['cnt'] if rows else 0
    
    if count == 0:
        raise ValueError(
            "玩家没有出战幻兽，"
            "请先运行 create_zhenyao_test_player.py 创建测试玩家和幻兽"
        )
    
    print(f"✅ 出战幻兽数量: {count}")
    return count


def clear_floor_if_occupied():
    """如果目标层已被占领，先清空"""
    rows = execute_query(
        """
        SELECT occupant_id, occupant_name, expire_time 
        FROM zhenyao_floor 
        WHERE floor = %s
        """,
        (TARGET_FLOOR,)
    )
    
    if rows:
        floor_info = rows[0]
        occupant_id = floor_info.get('occupant_id')
        occupant_name = floor_info.get('occupant_name', '')
        expire_time = floor_info.get('expire_time')
        
        if occupant_id:
            # 检查是否已过期
            if expire_time and datetime.now() > expire_time:
                print(f"  ℹ️  第{TARGET_FLOOR}层已被 {occupant_name} 占领，但已过期，将清空")
            else:
                print(f"  ⚠️  第{TARGET_FLOOR}层已被 {occupant_name} 占领，将清空")
            
            # 清空占领信息
            execute_update(
                """
                UPDATE zhenyao_floor 
                SET occupant_id = NULL, 
                    occupant_name = '', 
                    occupy_time = NULL, 
                    expire_time = NULL
                WHERE floor = %s
                """,
                (TARGET_FLOOR,)
            )
            print(f"  ✅ 已清空第{TARGET_FLOOR}层的占领信息")
    else:
        # 如果层不存在，创建它
        execute_update(
            "INSERT INTO zhenyao_floor (floor) VALUES (%s) ON DUPLICATE KEY UPDATE floor = floor",
            (TARGET_FLOOR,)
        )
        print(f"  ✅ 第{TARGET_FLOOR}层为空，可以直接占领")


def occupy_floor(player_name: str):
    """占领目标层"""
    now = datetime.now()
    expire_time = now + timedelta(minutes=OCCUPY_DURATION_MINUTES)
    
    # 更新占领信息
    execute_update(
        """
        UPDATE zhenyao_floor 
        SET occupant_id = %s,
            occupant_name = %s,
            occupy_time = %s,
            expire_time = %s
        WHERE floor = %s
        """,
        (TEST_USER_ID, player_name, now, expire_time, TARGET_FLOOR)
    )
    
    print(f"✅ 成功占领第{TARGET_FLOOR}层")
    print(f"   占领时长: {OCCUPY_DURATION_MINUTES}分钟")
    print(f"   到期时间: {expire_time.strftime('%Y-%m-%d %H:%M:%S')}")


def verify_occupation():
    """验证占领结果"""
    rows = execute_query(
        """
        SELECT occupant_id, occupant_name, expire_time 
        FROM zhenyao_floor 
        WHERE floor = %s
        """,
        (TARGET_FLOOR,)
    )
    
    if not rows:
        raise ValueError("验证失败：无法查询到第101层的信息")
    
    floor_info = rows[0]
    occupant_id = floor_info.get('occupant_id')
    
    if occupant_id != TEST_USER_ID:
        raise ValueError(f"验证失败：第{TARGET_FLOOR}层未被正确占领")
    
    print(f"✅ 验证成功：第{TARGET_FLOOR}层已被 {floor_info['occupant_name']} 占领")


def main():
    """主函数"""
    print("=" * 60)
    print("让测试玩家占领试炼层第101层")
    print("=" * 60)
    print()
    
    try:
        # 1. 检查玩家是否存在
        player = check_player_exists()
        print()
        
        # 2. 检查通天塔进度
        check_tower_progress()
        print()
        
        # 3. 检查出战幻兽
        check_beasts()
        print()
        
        # 4. 清空目标层（如果已被占领）
        clear_floor_if_occupied()
        print()
        
        # 5. 占领目标层
        occupy_floor(player['nickname'])
        print()
        
        # 6. 验证
        verify_occupation()
        print()
        
        print("=" * 60)
        print("完成！")
        print()
        print(f"现在其他玩家可以挑战第{TARGET_FLOOR}层来测试镇妖功能。")
        print(f"测试玩家信息：")
        print(f"  - user_id: {TEST_USER_ID}")
        print(f"  - 账号: zhenyao_test")
        print(f"  - 密码: 123456")
        print(f"  - 昵称: {player['nickname']}")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 操作失败：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
