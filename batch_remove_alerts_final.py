"""批量移除alert和confirm - 最终批次"""
import re
import os
import glob

# 搜索所有还有alert或confirm的Vue文件
def find_files_with_alerts():
    files = []
    for filepath in glob.glob("interfaces/client/src/**/*.vue", recursive=True):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if re.search(r'\balert\s*\(|\bconfirm\s*\(', content):
                files.append(filepath)
    return files

def process_file(filepath):
    """处理单个文件"""
    if not os.path.exists(filepath):
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. 检查是否已经导入useMessage
    if 'useMessage' not in content:
        # 在script setup后添加导入
        content = re.sub(
            r'(<script setup>)',
            r'\1\nimport { useMessage } from \'@/composables/useMessage\'',
            content,
            count=1
        )
        
        # 在第一个const之前添加useMessage的使用
        content = re.sub(
            r'(const\s+\w+\s*=\s*ref\()',
            r'const { message, messageType, showMessage } = useMessage()\n\n\1',
            content,
            count=1
        )
    
    # 2. 移除confirm - 直接删除confirm检查
    content = re.sub(
        r"if\s*\(\s*!confirm\([^)]+\)\s*\)\s*\{\s*return\s*\}",
        r"// 已移除确认提示",
        content
    )
    content = re.sub(
        r"if\s*\(\s*!confirm\([^)]+\)\s*\)\s+return",
        r"// 已移除确认提示",
        content
    )
    
    # 3. 替换alert为showMessage
    content = re.sub(
        r"alert\(res\.data\.message\)",
        r"showMessage(res.data.message, 'success')",
        content
    )
    content = re.sub(
        r"alert\(data\.message\)",
        r"showMessage(data.message, 'success')",
        content
    )
    content = re.sub(
        r"alert\(res\.data\.error\)",
        r"showMessage(res.data.error, 'error')",
        content
    )
    content = re.sub(
        r"alert\(data\.error\)",
        r"showMessage(data.error, 'error')",
        content
    )
    
    # 其他alert
    def replace_alert(match):
        msg = match.group(1)
        if '失败' in msg or '不足' in msg or '错误' in msg or 'error' in msg.lower() or '无法' in msg or '缺少' in msg or '已用完' in msg or '不可' in msg or '不满足' in msg:
            return f"showMessage({msg}, 'error')"
        elif '成功' in msg or 'success' in msg.lower() or '获得' in msg or '领取' in msg or '已' in msg:
            return f"showMessage({msg}, 'success')"
        else:
            return f"showMessage({msg}, 'info')"
    
    content = re.sub(r'alert\(([^)]+)\)', replace_alert, content)
    
    # 4. 在template中添加消息显示区域
    if '<div v-if="message"' not in content and 'class="message"' not in content:
        content = re.sub(
            r'(<template>\s*<div[^>]*>)',
            r'\1\n    <!-- 消息提示 -->\n    <div v-if="message" class="message" :class="messageType">\n      {{ message }}\n    </div>\n',
            content,
            count=1
        )
    
    # 5. 在style中添加消息样式
    if '.message {' not in content:
        message_styles = '''
/* 消息提示样式 */
.message {
  padding: 12px;
  margin: 12px 0;
  border-radius: 4px;
  font-weight: bold;
  text-align: center;
}

.message.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.message.info {
  background: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}
'''
        content = re.sub(r'</style>', message_styles + '\n</style>', content, count=1)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

print("=" * 60)
print("批量移除alert和confirm - 最终批次")
print("=" * 60)
print()

files = find_files_with_alerts()
print(f"找到 {len(files)} 个文件还有alert或confirm")
print()

processed = 0
for filepath in files:
    print(f"处理: {filepath}")
    if process_file(filepath):
        processed += 1
        print(f"  ✓ 已处理")
    else:
        print(f"  - 跳过")

print()
print("=" * 60)
print(f"完成！共处理 {processed}/{len(files)} 个文件")
print("=" * 60)
