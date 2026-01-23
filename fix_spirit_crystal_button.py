#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
在 inventory_service.py 中添加灵力水晶（6101）的使用按钮支持
"""

def main():
    file_path = 'application/services/inventory_service.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the line with 6006 check
    insert_pos = None
    for i, line in enumerate(lines):
        if 'if int(item_template.id) == 6006:' in line:
            print(f'Found战灵钥匙 check at line {i+1}')
            # Insert after the return statement (2 lines after)
            insert_pos = i + 2
            break
    
    if insert_pos is None:
        print('Error: Could not find战灵钥匙 check')
        return
    
    # Check if already added
    if any('6101' in line for line in lines[insert_pos:insert_pos+5]):
        print('灵力水晶 support already exists')
        return
    
    # Insert new lines
    new_lines = [
        '            # 灵力水晶：跳转战灵功能页兑换灵力（前端会提示并跳转）\n',
        '            if int(item_template.id) == 6101:\n',
        '                return (True, "使用")\n'
    ]
    
    lines[insert_pos:insert_pos] = new_lines
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f'✅ Successfully added灵力水晶 support at line {insert_pos+1}')
    print('\n修改内容：')
    print('在战灵钥匙（6006）判断之后添加了：')
    for line in new_lines:
        print(f'  {line.rstrip()}')

if __name__ == '__main__':
    main()
