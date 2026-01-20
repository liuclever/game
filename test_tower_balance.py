#!/usr/bin/env python3
"""
测试通天塔和龙纹塔战斗平衡性

验证相同战力的玩家在两个塔中能达到相近的层数
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from infrastructure.config.tower_config_repo import ConfigTowerRepo


def test_tower_balance():
    """测试通天塔和龙纹塔的平衡性"""
    
    repo = ConfigTowerRepo()
    
    print("=" * 80)
    print("通天塔 vs 龙纹塔 战斗平衡性测试")
    print("=" * 80)
    print()
    
    # 测试关键层数的守护兽配置
    test_floors = [1, 10, 20, 30, 40, 50, 60, 61, 70, 80, 90, 100]
    
    all_identical = True
    
    for floor in test_floors:
        tongtian_guardians = repo.get_guardians_for_floor("tongtian", floor)
        longwen_guardians = repo.get_guardians_for_floor("longwen", floor)
        
        if not tongtian_guardians or not longwen_guardians:
            continue
        
        t = tongtian_guardians[0]
        l = longwen_guardians[0]
        
        # 检查属性是否完全一致
        is_identical = (
            t.hp == l.hp and
            t.physical_attack == l.physical_attack and
            t.magic_attack == l.magic_attack and
            t.physical_defense == l.physical_defense and
            t.magic_defense == l.magic_defense and
            t.speed == l.speed
        )
        
        status = "✓ 一致" if is_identical else "✗ 不一致"
        
        if not is_identical:
            all_identical = False
            print(f"第 {floor:3d} 层: {status}")
            print(f"  通天塔: HP={t.hp:5d} 物攻={t.physical_attack:4d} 法攻={t.magic_attack:4d} 物防={t.physical_defense:4d} 法防={t.magic_defense:4d} 速度={t.speed:3d}")
            print(f"  龙纹塔: HP={l.hp:5d} 物攻={l.physical_attack:4d} 法攻={l.magic_attack:4d} 物防={l.physical_defense:4d} 法防={l.magic_defense:4d} 速度={l.speed:3d}")
            print()
        else:
            print(f"第 {floor:3d} 层: {status} - HP={t.hp:5d} 攻={t.physical_attack:4d} 防={t.physical_defense:4d} 速={t.speed:3d}")
    
    print()
    print("=" * 80)
    
    if all_identical:
        print("✓ 测试通过：通天塔和龙纹塔守护兽属性完全一致")
        print()
        print("预期效果：")
        print("- 相同战力的玩家在两个塔中应该能达到相近的层数")
        print("- 差异应该小于5层（由随机因素和守护兽数量差异导致）")
        print()
        print("建议：")
        print("1. 使用测试账号分别挑战两个塔，验证实际效果")
        print("2. 如果需要调整难度，建议修改鼓舞加成或守护兽数量")
        print("3. 不建议修改守护兽基础属性，以保持两塔平衡")
    else:
        print("✗ 测试失败：通天塔和龙纹塔守护兽属性存在差异")
        print()
        print("请检查配置文件：")
        print("- configs/tower_guardians.json")
        print("- infrastructure/config/tower_config_repo.py")
    
    print("=" * 80)
    
    return all_identical


if __name__ == "__main__":
    success = test_tower_balance()
    sys.exit(0 if success else 1)
