#!/usr/bin/env python3
"""
诊断通天塔和龙纹塔守护兽属性差异

对比前100层的守护兽属性，找出为什么相同战力在通天塔只能打到20层，
而在龙纹塔能打到61层。
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from infrastructure.config.tower_config_repo import ConfigTowerRepo


def diagnose_tower_guardians():
    """对比通天塔和龙纹塔的守护兽属性"""
    
    repo = ConfigTowerRepo()
    
    print("=" * 80)
    print("通天塔 vs 龙纹塔 守护兽属性对比")
    print("=" * 80)
    print()
    
    # 对比关键层数
    test_floors = [1, 5, 10, 15, 20, 25, 30, 40, 50, 60, 61]
    
    for floor in test_floors:
        print(f"\n{'=' * 80}")
        print(f"第 {floor} 层对比")
        print(f"{'=' * 80}")
        
        # 通天塔守护兽
        tongtian_guardians = repo.get_guardians_for_floor("tongtian", floor)
        print(f"\n【通天塔】第{floor}层 - {len(tongtian_guardians)}只守护兽:")
        for i, g in enumerate(tongtian_guardians, 1):
            print(f"  守护兽{i}: {g.name}")
            print(f"    等级: {g.level}")
            print(f"    特性: {g.nature}")
            print(f"    气血: {g.hp}")
            print(f"    物攻: {g.physical_attack}")
            print(f"    法攻: {g.magic_attack}")
            print(f"    物防: {g.physical_defense}")
            print(f"    法防: {g.magic_defense}")
            print(f"    速度: {g.speed}")
            print()
        
        # 龙纹塔守护兽
        longwen_guardians = repo.get_guardians_for_floor("longwen", floor)
        print(f"【龙纹塔】第{floor}层 - {len(longwen_guardians)}只守护兽:")
        for i, g in enumerate(longwen_guardians, 1):
            print(f"  守护兽{i}: {g.name}")
            print(f"    等级: {g.level}")
            print(f"    特性: {g.nature}")
            print(f"    气血: {g.hp}")
            print(f"    物攻: {g.physical_attack}")
            print(f"    法攻: {g.magic_attack}")
            print(f"    物防: {g.physical_defense}")
            print(f"    法防: {g.magic_defense}")
            print(f"    速度: {g.speed}")
            print()
        
        # 计算差异
        if tongtian_guardians and longwen_guardians:
            t = tongtian_guardians[0]
            l = longwen_guardians[0]
            
            print(f"【属性差异】")
            print(f"  气血差: {t.hp - l.hp} ({t.hp / l.hp:.2f}x)")
            print(f"  物攻差: {t.physical_attack - l.physical_attack} ({t.physical_attack / l.physical_attack:.2f}x)")
            print(f"  法攻差: {t.magic_attack - l.magic_attack} ({t.magic_attack / l.magic_attack:.2f}x)")
            print(f"  物防差: {t.physical_defense - l.physical_defense} ({t.physical_defense / l.physical_defense:.2f}x)")
            print(f"  法防差: {t.magic_defense - l.magic_defense} ({t.magic_defense / l.magic_defense:.2f}x)")
            print(f"  速度差: {t.speed - l.speed}")


if __name__ == "__main__":
    diagnose_tower_guardians()
