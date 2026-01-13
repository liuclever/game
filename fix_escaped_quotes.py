"""修复错误转义的单引号"""
import os
import glob

def fix_file(filepath):
    """修复单个文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 修复错误的转义
        content = content.replace("\\'", "'")
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return False

print("=" * 60)
print("修复错误转义的单引号")
print("=" * 60)
print()

# 搜索所有Vue文件
files = glob.glob("interfaces/client/src/**/*.vue", recursive=True)
print(f"找到 {len(files)} 个Vue文件")
print()

fixed = 0
for filepath in files:
    if fix_file(filepath):
        fixed += 1
        print(f"✓ 修复: {filepath}")

print()
print("=" * 60)
print(f"完成！共修复 {fixed} 个文件")
print("=" * 60)
