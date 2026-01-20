"""验证代码修复"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 读取文件内容
file_path = 'interfaces/routes/alliance_routes.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("=" * 80)
print("验证代码修复")
print("=" * 80)

# 检查关键代码
checks = [
    ('total_contribution字段存在', '"total_contribution":' in content or "'total_contribution':" in content),
    ('getattr调用存在', 'getattr(member_info, \'total_contribution\'' in content),
    ('member_info字典包含total_contribution', 'member_info": {' in content and 'total_contribution' in content.split('member_info": {')[1].split('}')[0] if 'member_info": {' in content else False),
]

print("\n[代码检查]")
all_ok = True
for check_name, check_result in checks:
    status = "OK" if check_result else "FAIL"
    print(f"  {status}: {check_name}")
    if not check_result:
        all_ok = False

# 查找total_contribution相关代码行
print("\n[相关代码行]")
lines = content.split('\n')
for i, line in enumerate(lines, 1):
    if 'total_contribution' in line:
        print(f"  第{i}行: {line.strip()}")

if all_ok:
    print("\n[结论] 代码已正确更新！")
    print("如果API响应中仍然没有total_contribution字段，")
    print("请完全停止并重新启动Flask服务。")
else:
    print("\n[结论] 代码可能未正确更新，请检查。")

print("=" * 80)
