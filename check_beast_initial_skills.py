#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查幻兽初始技能配置
找出所有缺少 all_skill_ids 的幻兽模板
"""

import json
import os


def load_skill_name_to_id_map():
    """加载技能名称到ID的映射"""
    skills_path = os.path.join('configs', 'skills.json')
    with open(skills_path, 'r', encoding='utf-8') as f:
        skills_cfg = json.load(f)
    
    skill_ids = skills_cfg.get('skill_ids', {})
    return skill_ids


def check_beast_templates():
    """检查所有幻兽模板的技能配置"""
    print("=" * 80)
    print("检查幻兽初始技能配置")
    print("=" * 80)
    
    # 加载技能映射
    skill_name_to_id = load_skill_name_to_id_map()
    print(f"\n✓ 加载了 {len(skill_name_to_id)} 个技能的ID映射")
    
    # 加载幻兽模板
    templates_path = os.path.join('configs', 'beast_templates.json')
    with open(templates_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    templates = data.get('templates', data)
    if not isinstance(templates, list):
        templates = [data]
    
    print(f"✓ 加载了 {len(templates)} 个幻兽模板\n")
    
    # 统计
    missing_skill_ids = []
    missing_skill_names = []
    has_both = []
    no_skills = []
    
    for template in templates:
        template_id = template.get('id')
        name = template.get('name', f'ID:{template_id}')
        all_skill_ids = template.get('all_skill_ids', [])
        all_skill_names = template.get('all_skill_names', [])
        
        if not all_skill_ids and not all_skill_names:
            no_skills.append((template_id, name))
        elif not all_skill_ids and all_skill_names:
            missing_skill_ids.append((template_id, name, all_skill_names))
        elif all_skill_ids and not all_skill_names:
            missing_skill_names.append((template_id, name, all_skill_ids))
        else:
            has_both.append((template_id, name, all_skill_ids, all_skill_names))
    
    # 输出结果
    print("=" * 80)
    print("统计结果")
    print("=" * 80)
    print(f"✓ 同时有 all_skill_ids 和 all_skill_names: {len(has_both)} 个")
    print(f"⚠ 只有 all_skill_names，缺少 all_skill_ids: {len(missing_skill_ids)} 个")
    print(f"⚠ 只有 all_skill_ids，缺少 all_skill_names: {len(missing_skill_names)} 个")
    print(f"⚠ 两者都没有: {len(no_skills)} 个")
    
    # 详细列出缺少 all_skill_ids 的幻兽
    if missing_skill_ids:
        print("\n" + "=" * 80)
        print("缺少 all_skill_ids 的幻兽（这些幻兽从召唤球打开后没有初始技能）")
        print("=" * 80)
        for template_id, name, skill_names in missing_skill_ids:
            print(f"\nID: {template_id} - {name}")
            print(f"  all_skill_names: {skill_names}")
            
            # 尝试转换为 skill_ids
            skill_ids = []
            missing_names = []
            for skill_name in skill_names:
                skill_id = skill_name_to_id.get(skill_name)
                if skill_id:
                    skill_ids.append(skill_id)
                else:
                    missing_names.append(skill_name)
            
            if skill_ids:
                print(f"  应该设置的 all_skill_ids: {skill_ids}")
            if missing_names:
                print(f"  ⚠ 警告：以下技能名称在 skills.json 中找不到ID: {missing_names}")
    
    # 详细列出没有技能的幻兽
    if no_skills:
        print("\n" + "=" * 80)
        print("没有配置任何技能的幻兽")
        print("=" * 80)
        for template_id, name in no_skills:
            print(f"  ID: {template_id} - {name}")
    
    return {
        'missing_skill_ids': missing_skill_ids,
        'missing_skill_names': missing_skill_names,
        'has_both': has_both,
        'no_skills': no_skills,
        'skill_name_to_id': skill_name_to_id
    }


def generate_fix_script(result):
    """生成修复脚本"""
    missing_skill_ids = result['missing_skill_ids']
    skill_name_to_id = result['skill_name_to_id']
    
    if not missing_skill_ids:
        print("\n✓ 所有幻兽都有正确的技能配置，无需修复")
        return
    
    print("\n" + "=" * 80)
    print("生成修复方案")
    print("=" * 80)
    
    fixes = []
    for template_id, name, skill_names in missing_skill_ids:
        skill_ids = []
        for skill_name in skill_names:
            skill_id = skill_name_to_id.get(skill_name)
            if skill_id:
                skill_ids.append(skill_id)
        
        if skill_ids:
            fixes.append({
                'id': template_id,
                'name': name,
                'all_skill_ids': skill_ids,
                'all_skill_names': skill_names
            })
    
    print(f"\n需要修复 {len(fixes)} 个幻兽模板")
    print("\n修复方案（需要在 configs/beast_templates.json 中添加 all_skill_ids 字段）：")
    print("\n```json")
    for fix in fixes:
        print(f'  // {fix["name"]} (ID: {fix["id"]})')
        print(f'  "all_skill_ids": {json.dumps(fix["all_skill_ids"])},')
        print(f'  "all_skill_names": {json.dumps(fix["all_skill_names"], ensure_ascii=False)},')
        print()
    print("```")


def main():
    result = check_beast_templates()
    generate_fix_script(result)
    
    print("\n" + "=" * 80)
    print("检查完成")
    print("=" * 80)
    print("\n说明：")
    print("- 幻兽初始技能从 all_skill_ids 中随机选择 0-N 个")
    print("- 如果 all_skill_ids 为空，则幻兽没有初始技能")
    print("- 需要在配置文件中添加 all_skill_ids 字段")


if __name__ == "__main__":
    main()
