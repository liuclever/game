"""测试增幅技能属性加成功能

测试场景：
1. 查看测试账号幻兽的当前属性
2. 给幻兽打上增幅技能书（强力）
3. 验证物攻是否增加了对应的百分比
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from domain.services.beast_stats import calc_beast_attributes, get_beast_max_realm, get_buff_skill_bonuses
import json


def test_amplification_skills():
    """测试增幅技能功能"""
    
    print("=" * 60)
    print("测试增幅技能属性加成功能")
    print("=" * 60)
    
    # 模拟一只15级血螳螂的属性
    print("\n【测试幻兽】: 15级血螳螂")
    print("物攻裸数值: 200 (假设)")
    
    # 测试增幅技能加成计算
    print("\n【测试增幅技能加成】")
    
    # 测试1: 强力技能（+9%物攻）
    test_skills_1 = ["强力"]
    bonuses_1 = get_buff_skill_bonuses(test_skills_1)
    print(f"\n技能: {test_skills_1}")
    print(f"加成配置: {bonuses_1}")
    
    naked_attack = 200
    buffed_attack_1 = int(naked_attack * (1 + bonuses_1.get('physical_attack', 0.0)))
    increase_1 = buffed_attack_1 - naked_attack
    
    print(f"物攻变化: {naked_attack} -> {buffed_attack_1} (增加 {increase_1})")
    print(f"预期增加: {int(naked_attack * 0.09)} (9%)")
    
    if increase_1 == int(naked_attack * 0.09):
        print("✅ 强力技能加成正确")
    else:
        print("❌ 强力技能加成不正确")
    
    # 测试2: 高级强力技能（+18%物攻）
    test_skills_2 = ["高级强力"]
    bonuses_2 = get_buff_skill_bonuses(test_skills_2)
    print(f"\n技能: {test_skills_2}")
    print(f"加成配置: {bonuses_2}")
    
    buffed_attack_2 = int(naked_attack * (1 + bonuses_2.get('physical_attack', 0.0)))
    increase_2 = buffed_attack_2 - naked_attack
    
    print(f"物攻变化: {naked_attack} -> {buffed_attack_2} (增加 {increase_2})")
    print(f"预期增加: {int(naked_attack * 0.18)} (18%)")
    
    if increase_2 == int(naked_attack * 0.18):
        print("✅ 高级强力技能加成正确")
    else:
        print("❌ 高级强力技能加成不正确")
    
    # 测试3: 多个增幅技能叠加
    test_skills_3 = ["强力", "防御", "敏捷", "体魄"]
    bonuses_3 = get_buff_skill_bonuses(test_skills_3)
    print(f"\n技能: {test_skills_3}")
    print(f"加成配置: {bonuses_3}")
    
    naked_hp = 1000
    naked_defense = 150
    naked_speed = 50
    
    buffed_attack_3 = int(naked_attack * (1 + bonuses_3.get('physical_attack', 0.0)))
    buffed_hp_3 = int(naked_hp * (1 + bonuses_3.get('hp', 0.0)))
    buffed_defense_3 = int(naked_defense * (1 + bonuses_3.get('physical_defense', 0.0)))
    buffed_speed_3 = int(naked_speed * (1 + bonuses_3.get('speed', 0.0)))
    
    print(f"物攻变化: {naked_attack} -> {buffed_attack_3} (增加 {buffed_attack_3 - naked_attack}, +9%)")
    print(f"气血变化: {naked_hp} -> {buffed_hp_3} (增加 {buffed_hp_3 - naked_hp}, +10%)")
    print(f"物防变化: {naked_defense} -> {buffed_defense_3} (增加 {buffed_defense_3 - naked_defense}, +5%)")
    print(f"速度变化: {naked_speed} -> {buffed_speed_3} (增加 {buffed_speed_3 - naked_speed}, +10%)")
    
    # 测试4: 验证技能配置文件加载
    print("\n【验证技能配置文件】")
    all_buff_skills = [
        "强力", "高级强力",
        "智慧", "高级智慧",
        "防御", "高级防御",
        "魔抗", "高级魔抗",
        "敏捷", "高级敏捷",
        "体魄", "高级体魄"
    ]
    
    for skill in all_buff_skills:
        bonuses = get_buff_skill_bonuses([skill])
        non_zero_bonuses = {k: v for k, v in bonuses.items() if v != 0.0}
        if non_zero_bonuses:
            print(f"  {skill}: {non_zero_bonuses}")
        else:
            print(f"  ❌ {skill}: 未找到配置")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    
    print("\n【使用说明】")
    print("1. 增幅技能会基于幻兽的裸属性（不含魔魂、战骨、战灵）计算加成")
    print("2. 打书成功后，幻兽属性会自动重新计算并更新")
    print("3. 前端需要刷新幻兽详情页面才能看到更新后的属性")
    print("4. 战力也会随着属性增加而增加")


if __name__ == "__main__":
    test_amplification_skills()
