#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动修复幻兽模板的 all_skill_ids 字段
根据 all_skill_names 自动生成对应的 all_skill_ids
"""

import json
import os
import shutil
from datetime import datetime


def load_skill_name_to_id_map():
    """加载技能名称到ID的映射"""
    skills_path = os.path.join('configs', 'skills.json')
    with open(skills_path, 'r', encoding='utf-8') as f:
        skills_cfg = json.load(f)
    
    skill_ids = skills_cfg.get('skill_ids', {})
    return skill_ids


def fix_beast_templates():
    """修复幻兽模板配置"""
    print("=" * 80)
    print("自动修复幻兽模板 all_skill_ids 字段")
    print("=" * 80)
    
    # 加载技能映射
    skill_name_to_id = load_skill_name_to_id_map()
    print(f"\n✓ 加载了 {len(skill_name_to_id)} 个技能的ID映射")
    
    # 加载幻兽模板
    templates_path = os.path.join('configs', 'beast_templates.json')
    with open(templates_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 备份原文件
    backup_path = templates_path + f'.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    shutil.copy2(templates_path, backup_path)
    print(f"✓ 已备份原文件到: {backup_path}")
    
    # 获取模板列表
    templates = data.get('templates', [])
    print(f"✓ 加载了 {len(templates)} 个幻兽模板\n")
    
    # 统计
    fixed_count = 0
    skipped_count = 0
    error_count = 0
    
    print("开始修复...")
    print("-" * 80)
    
    for template in templates:
        template_id = template.get('id')
        name = template.get('name', f'ID:{template_id}')
        all_skill_ids = template.get('all_skill_ids', [])
        all_skill_names = template.get('all_skill_names', [])
        
        # 如果已经有 all_skill_ids，跳过
        if all_skill_ids:
            skipped_count += 1
            continue
        
        # 如果没有 all_skill_names，也跳过
        if not all_skill_names:
            skipped_count += 1
            continue
        
        # 转换技能名称为ID
        skill_ids = []
        missing_names = []
        for skill_name in all_skill_names:
            skill_id = skill_name_to_id.get(skill_name)
            if skill_id:
                skill_ids.append(skill_id)
            else:
                missing_names.append(skill_name)
        
        if missing_names:
            print(f"⚠ {name} (ID: {template_id}): 以下技能名称找不到ID: {missing_names}")
            error_count += 1
        
        if skill_ids:
            template['all_skill_ids'] = skill_ids
            print(f"✓ {name} (ID: {template_id}): 添加了 {len(skill_ids)} 个技能ID")
            fixed_count += 1
    
    # 保存修复后的文件
    with open(templates_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("-" * 80)
    print(f"\n修复完成！")
    print(f"  ✓ 修复: {fixed_count} 个")
    print(f"  - 跳过: {skipped_count} 个")
    if error_count > 0:
        print(f"  ⚠ 错误: {error_count} 个")
    
    print(f"\n✓ 已保存到: {templates_path}")
    print(f"✓ 备份文件: {backup_path}")


def main():
    try:
        fix_beast_templates()
        print("\n" + "=" * 80)
        print("修复成功！")
        print("=" * 80)
        print("\n说明：")
        print("- 已为所有缺少 all_skill_ids 的幻兽模板添加该字段")
        print("- 原文件已备份")
        print("- 现在幻兽从召唤球打开后会有初始技能")
        print("- 初始技能数量随机（0-N个）")
    except Exception as e:
        print(f"\n✗ 修复失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
