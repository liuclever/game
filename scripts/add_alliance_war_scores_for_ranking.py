#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""为测试联盟添加联盟战功数据，用于排行榜显示"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.db.connection import execute_query, execute_update

def ensure_table_exists():
    """确保 alliance_war_scores 表存在"""
    sql = """
    CREATE TABLE IF NOT EXISTS alliance_war_scores (
        id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
        alliance_id INT NOT NULL,
        season_key CHAR(7) NOT NULL COMMENT '自然月，格式 YYYY-MM',
        score INT NOT NULL DEFAULT 0,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (id),
        UNIQUE KEY uk_alliance_season (alliance_id, season_key),
        CONSTRAINT fk_war_scores_alliance FOREIGN KEY (alliance_id) REFERENCES alliances(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='联盟战功月度积分';
    """
    try:
        execute_update(sql)
        print("[OK] alliance_war_scores 表已确认存在")
    except Exception as e:
        print(f"[ERROR] 创建表失败: {e}")
        raise

def get_test_alliances():
    """获取测试联盟列表"""
    sql = "SELECT id, name FROM alliances WHERE name LIKE '测试联盟%' ORDER BY id LIMIT 5"
    rows = execute_query(sql)
    return rows

def add_war_scores_for_alliances():
    """为测试联盟添加战功数据"""
    # 确保表存在
    ensure_table_exists()
    
    # 获取当前月份作为赛季
    season_key = datetime.now().strftime("%Y-%m")
    print(f"\n当前赛季: {season_key}")
    
    # 获取测试联盟
    alliances = get_test_alliances()
    if not alliances:
        print("未找到测试联盟，请先运行 create_alliance_war_test_data.py")
        return
    
    print(f"\n找到 {len(alliances)} 个测试联盟:")
    for alliance in alliances:
        print(f"  - {alliance['name']} (ID: {alliance['id']})")
    
    # 为前3个联盟添加不同的战功数量（确保有排名）
    # 第1名：100战功
    # 第2名：70战功
    # 第3名：40战功
    scores = [100, 70, 40, 20, 10]  # 为5个联盟设置不同的战功
    
    print(f"\n为联盟添加战功数据...")
    for idx, alliance in enumerate(alliances[:5]):
        alliance_id = alliance['id']
        alliance_name = alliance['name']
        score = scores[idx] if idx < len(scores) else 10
        
        # 使用 INSERT ... ON DUPLICATE KEY UPDATE 来插入或更新
        sql = """
        INSERT INTO alliance_war_scores (alliance_id, season_key, score)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            score = VALUES(score),
            updated_at = CURRENT_TIMESTAMP
        """
        try:
            execute_update(sql, (alliance_id, season_key, score))
            print(f"  [OK] {alliance_name} (ID: {alliance_id}): {score} 战功")
        except Exception as e:
            print(f"  [ERROR] {alliance_name} (ID: {alliance_id}): 添加失败 - {e}")
    
    # 验证数据
    print(f"\n验证排行榜数据...")
    sql = """
    SELECT 
        aws.alliance_id,
        a.name AS alliance_name,
        a.level AS alliance_level,
        aws.score
    FROM alliance_war_scores aws
    INNER JOIN alliances a ON a.id = aws.alliance_id
    WHERE aws.season_key = %s
    ORDER BY aws.score DESC
    LIMIT 5
    """
    rows = execute_query(sql, (season_key,))
    
    if rows:
        print("\n当前排行榜（前5名）:")
        for idx, row in enumerate(rows, 1):
            print(f"  第{idx}名: {row['alliance_name']} (等级{row['alliance_level']}) - {row['score']} 战功")
    else:
        print("  未找到排行榜数据")

if __name__ == "__main__":
    try:
        add_war_scores_for_alliances()
        print("\n[OK] 完成！")
    except Exception as e:
        print(f"\n[ERROR] 错误: {e}")
        import traceback
        traceback.print_exc()
