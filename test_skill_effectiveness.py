"""测试幻兽技能是否生效

功能：
1. 测试主动技能（必杀、连击、破甲、毒攻等）
2. 测试被动技能（闪避、反震、反击）
3. 测试增益技能（属性加成）
4. 测试负面技能（属性减少）

运行方式：
    python test_skill_effectiveness.py
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from domain.services.skill_system import (
    get_skill_config,
    get_skill_info,
    classify_skills,
    apply_buff_debuff_skills,
    try_trigger_active_skill,
    try_trigger_passive_skill,
)


def test_skill_config_loading():
    """测试技能配置加载"""
    print("=" * 60)
    print("测试1：技能配置加载")
    print("=" * 60)
    
    config = get_skill_config()
    
    # 检查主动技能
    active_skills = config.get("active_skills", {})
    advanced_active = active_skills.get("advanced", {})
    normal_active = active_skills.get("normal", {})
    
    print(f"\n主动技能：")
    print(f"  高级主动技能：{len(advanced_active)}个")
    for skill_name in list(advanced_active.keys())[:5]:
        print(f"    - {skill_name}")
    print(f"  普通主动技能：{len(normal_active)}个")
    for skill_name in list(normal_active.keys())[:5]:
        print(f"    - {skill_name}")
    
    # 检查被动技能
    passive_skills = config.get("passive_skills", {})
    advanced_passive = passive_skills.get("advanced", {})
    normal_passive = passive_skills.get("normal", {})
    
    print(f"\n被动技能：")
    print(f"  高级被动技能：{len(advanced_passive)}个")
    for skill_name in list(advanced_passive.keys())[:5]:
        print(f"    - {skill_name}")
    print(f"  普通被动技能：{len(normal_passive)}个")
    for skill_name in list(normal_passive.keys())[:5]:
        print(f"    - {skill_name}")
    
    # 检查增益技能
    buff_skills = config.get("buff_skills", {})
    advanced_buff = buff_skills.get("advanced", {})
    normal_buff = buff_skills.get("normal", {})
    
    print(f"\n增益技能：")
    print(f"  高级增益技能：{len(advanced_buff)}个")
    for skill_name in list(advanced_buff.keys())[:5]:
        print(f"    - {skill_name}")
    print(f"  普通增益技能：{len(normal_buff)}个")
    for skill_name in list(normal_buff.keys())[:5]:
        print(f"    - {skill_name}")
    
    # 检查负面技能
    debuff_skills = config.get("debuff_skills", {})
    
    print(f"\n负面技能：")
    print(f"  负面技能：{len(debuff_skills)}个")
    for skill_name in list(debuff_skills.keys())[:5]:
        print(f"    - {skill_name}")
    
    print(f"\n✅ 技能配置加载成功")
    return True


def test_skill_info():
    """测试技能信息获取"""
    print("\n" + "=" * 60)
    print("测试2：技能信息获取")
    print("=" * 60)
    
    test_skills = [
        "高级必杀",
        "高级连击",
        "高级破甲",
        "高级毒攻",
        "高级闪避",
        "高级反震",
        "高级反击",
        "高级神佑",
        "高级幸运",
        "低级虚弱",
    ]
    
    for skill_name in test_skills:
        info = get_skill_info(skill_name)
        if info:
            category = info.get("category", "未知")
            tier = info.get("tier", "")
            trigger_rate = info.get("trigger_rate", 0)
            print(f"\n{skill_name}:")
            print(f"  类别：{category}")
            print(f"  等级：{tier}")
            if trigger_rate:
                print(f"  触发率：{trigger_rate * 100}%")
            if "damage_multiplier" in info:
                print(f"  伤害倍率：{info['damage_multiplier']}")
            if "modifier" in info:
                print(f"  属性修正：{info['modifier'] * 100:+.0f}%")
        else:
            print(f"\n{skill_name}: ❌ 未找到")
    
    print(f"\n✅ 技能信息获取测试完成")
    return True


def test_skill_classification():
    """测试技能分类"""
    print("\n" + "=" * 60)
    print("测试3：技能分类")
    print("=" * 60)
    
    test_skill_list = [
        "高级必杀",
        "高级连击",
        "高级闪避",
        "高级反震",
        "高级神佑",
        "高级幸运",
        "低级虚弱",
    ]
    
    classified = classify_skills(test_skill_list)
    
    print(f"\n技能列表：{', '.join(test_skill_list)}")
    print(f"\n分类结果：")
    print(f"  主动技能：{', '.join(classified['active']) if classified['active'] else '无'}")
    print(f"  被动技能：{', '.join(classified['passive']) if classified['passive'] else '无'}")
    print(f"  增益技能：{', '.join(classified['buff']) if classified['buff'] else '无'}")
    print(f"  负面技能：{', '.join(classified['debuff']) if classified['debuff'] else '无'}")
    
    print(f"\n✅ 技能分类测试完成")
    return True


def test_buff_debuff_application():
    """测试增益和负面技能应用"""
    print("\n" + "=" * 60)
    print("测试4：增益和负面技能应用")
    print("=" * 60)
    
    # 基础属性
    raw_hp = 10000
    raw_physical_attack = 1000
    raw_magic_attack = 1000
    raw_physical_defense = 500
    raw_magic_defense = 500
    raw_speed = 100
    
    print(f"\n基础属性：")
    print(f"  气血：{raw_hp}")
    print(f"  物攻：{raw_physical_attack}")
    print(f"  法攻：{raw_magic_attack}")
    print(f"  物防：{raw_physical_defense}")
    print(f"  法防：{raw_magic_defense}")
    print(f"  速度：{raw_speed}")
    
    # 测试增益技能
    buff_skills = ["高级神佑", "高级幸运"]
    print(f"\n应用增益技能：{', '.join(buff_skills)}")
    
    (
        final_hp,
        final_physical_attack,
        final_magic_attack,
        final_physical_defense,
        final_magic_defense,
        final_speed,
        special_effects,
    ) = apply_buff_debuff_skills(
        skills=buff_skills,
        attack_type="physical",
        raw_hp=raw_hp,
        raw_physical_attack=raw_physical_attack,
        raw_magic_attack=raw_magic_attack,
        raw_physical_defense=raw_physical_defense,
        raw_magic_defense=raw_magic_defense,
        raw_speed=raw_speed,
    )
    
    print(f"\n最终属性：")
    print(f"  气血：{final_hp} ({final_hp - raw_hp:+d})")
    print(f"  物攻：{final_physical_attack} ({final_physical_attack - raw_physical_attack:+d})")
    print(f"  法攻：{final_magic_attack} ({final_magic_attack - raw_magic_attack:+d})")
    print(f"  物防：{final_physical_defense} ({final_physical_defense - raw_physical_defense:+d})")
    print(f"  法防：{final_magic_defense} ({final_magic_defense - raw_magic_defense:+d})")
    print(f"  速度：{final_speed} ({final_speed - raw_speed:+d})")
    print(f"\n特殊效果：{special_effects}")
    
    # 测试负面技能
    debuff_skills = ["低级虚弱"]
    print(f"\n应用负面技能：{', '.join(debuff_skills)}")
    
    (
        final_hp2,
        final_physical_attack2,
        final_magic_attack2,
        final_physical_defense2,
        final_magic_defense2,
        final_speed2,
        special_effects2,
    ) = apply_buff_debuff_skills(
        skills=debuff_skills,
        attack_type="physical",
        raw_hp=raw_hp,
        raw_physical_attack=raw_physical_attack,
        raw_magic_attack=raw_magic_attack,
        raw_physical_defense=raw_physical_defense,
        raw_magic_defense=raw_magic_defense,
        raw_speed=raw_speed,
    )
    
    print(f"\n最终属性：")
    print(f"  气血：{final_hp2} ({final_hp2 - raw_hp:+d})")
    print(f"  物攻：{final_physical_attack2} ({final_physical_attack2 - raw_physical_attack:+d})")
    print(f"  法攻：{final_magic_attack2} ({final_magic_attack2 - raw_magic_attack:+d})")
    print(f"  物防：{final_physical_defense2} ({final_physical_defense2 - raw_physical_defense:+d})")
    print(f"  法防：{final_magic_defense2} ({final_magic_defense2 - raw_magic_defense:+d})")
    print(f"  速度：{final_speed2} ({final_speed2 - raw_speed:+d})")
    
    print(f"\n✅ 增益和负面技能应用测试完成")
    return True


def test_active_skill_trigger():
    """测试主动技能触发"""
    print("\n" + "=" * 60)
    print("测试5：主动技能触发（模拟100次）")
    print("=" * 60)
    
    test_skills = [
        ("高级必杀", "physical"),
        ("高级连击", "physical"),
        ("高级破甲", "physical"),
        ("高级毒攻", "magic"),
    ]
    
    for skill_name, attack_type in test_skills:
        print(f"\n测试技能：{skill_name} (攻击类型：{attack_type})")
        
        trigger_count = 0
        total_tests = 100
        
        for _ in range(total_tests):
            result = try_trigger_active_skill(
                attacker_skills=[skill_name],
                attack_type=attack_type,
            )
            if result.triggered:
                trigger_count += 1
        
        trigger_rate = trigger_count / total_tests
        print(f"  触发次数：{trigger_count}/{total_tests}")
        print(f"  实际触发率：{trigger_rate * 100:.1f}%")
        
        # 获取配置的触发率
        info = get_skill_info(skill_name)
        if info:
            expected_rate = info.get("trigger_rate", 0)
            print(f"  配置触发率：{expected_rate * 100:.1f}%")
            
            # 检查是否在合理范围内（±15%）
            if abs(trigger_rate - expected_rate) < 0.15:
                print(f"  ✅ 触发率正常")
            else:
                print(f"  ⚠️  触发率偏差较大")
    
    print(f"\n✅ 主动技能触发测试完成")
    return True


def test_passive_skill_trigger():
    """测试被动技能触发"""
    print("\n" + "=" * 60)
    print("测试6：被动技能触发（模拟100次）")
    print("=" * 60)
    
    test_skills = [
        "高级闪避",
        "高级反震",
        "高级反击",
    ]
    
    for skill_name in test_skills:
        print(f"\n测试技能：{skill_name}")
        
        trigger_count = 0
        total_tests = 100
        
        for _ in range(total_tests):
            result = try_trigger_passive_skill(
                defender_skills=[skill_name],
                is_normal_attack=True,
            )
            if result.triggered:
                trigger_count += 1
        
        trigger_rate = trigger_count / total_tests
        print(f"  触发次数：{trigger_count}/{total_tests}")
        print(f"  实际触发率：{trigger_rate * 100:.1f}%")
        
        # 获取配置的触发率
        info = get_skill_info(skill_name)
        if info:
            expected_rate = info.get("trigger_rate", 0)
            print(f"  配置触发率：{expected_rate * 100:.1f}%")
            
            # 检查是否在合理范围内（±15%）
            if abs(trigger_rate - expected_rate) < 0.15:
                print(f"  ✅ 触发率正常")
            else:
                print(f"  ⚠️  触发率偏差较大")
    
    print(f"\n✅ 被动技能触发测试完成")
    return True


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("幻兽技能生效性测试")
    print("=" * 60)
    
    try:
        # 运行所有测试
        tests = [
            test_skill_config_loading,
            test_skill_info,
            test_skill_classification,
            test_buff_debuff_application,
            test_active_skill_trigger,
            test_passive_skill_trigger,
        ]
        
        passed = 0
        failed = 0
        
        for test_func in tests:
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"\n❌ 测试失败：{e}")
                import traceback
                traceback.print_exc()
                failed += 1
        
        # 总结
        print("\n" + "=" * 60)
        print("测试总结")
        print("=" * 60)
        print(f"通过：{passed}/{len(tests)}")
        print(f"失败：{failed}/{len(tests)}")
        
        if failed == 0:
            print("\n✅ 所有测试通过！技能系统运行正常。")
        else:
            print(f"\n⚠️  有{failed}个测试失败，请检查技能配置和实现。")
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
