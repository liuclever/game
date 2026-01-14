"""
导出 game_tower 数据库
确保编码和顺序正确
"""
import subprocess
import sys
import os
from datetime import datetime

# 数据库配置（从 connection.py 读取）
# 注意：如果密码不对，请修改为正确的密码
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '1234',  # 请根据实际情况修改（也可能需要尝试 '12345' 或 '123456'）
    'database': 'game_tower',
    'charset': 'utf8mb4',
}

def export_database(output_file=None):
    """
    导出数据库到SQL文件
    
    Args:
        output_file: 输出文件路径，如果为None则使用默认文件名
    """
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'game_tower_{timestamp}.sql'
    
    # 确保输出文件在项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(project_root, output_file)
    
    print(f"正在导出数据库 {DB_CONFIG['database']} 到 {output_path}...")
    print(f"数据库配置: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    
    # 构建 mysqldump 命令
    # 使用以下选项确保编码和顺序正确：
    # --default-character-set=utf8mb4: 指定字符集
    # --single-transaction: 使用单事务模式，确保一致性
    # --routines: 导出存储过程和函数
    # --triggers: 导出触发器
    # --events: 导出事件
    # --skip-extended-insert: 使用多行INSERT语句，便于查看和编辑
    # --complete-insert: 使用完整的INSERT语句，包含列名
    # --add-drop-table: 添加DROP TABLE语句
    # --add-locks: 添加锁表语句
    # --skip-comments: 跳过注释（可选）
    
    cmd = [
        'mysqldump',
        f"--host={DB_CONFIG['host']}",
        f"--port={DB_CONFIG['port']}",
        f"--user={DB_CONFIG['user']}",
        f"--password={DB_CONFIG['password']}",
        f"--default-character-set={DB_CONFIG['charset']}",
        '--single-transaction',
        '--routines',
        '--triggers',
        '--events',
        '--add-drop-table',
        '--add-locks',
        '--complete-insert',
        '--skip-extended-insert',
        DB_CONFIG['database']
    ]
    
    try:
        # 执行导出命令
        with open(output_path, 'w', encoding='utf-8') as f:
            # 添加文件头注释
            f.write(f"""/*
 MySQL数据库导出
 数据库名: {DB_CONFIG['database']}
 导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 字符集: {DB_CONFIG['charset']}
*/\n\n""")
            f.write(f"SET NAMES {DB_CONFIG['charset']};\n")
            f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")
            
            # 执行 mysqldump
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                print(f"导出失败: {stderr}")
                return False
            
            # 写入导出内容
            f.write(stdout)
            
            # 添加文件尾
            f.write("\nSET FOREIGN_KEY_CHECKS = 1;\n")
        
        file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
        print(f"导出成功！")
        print(f"文件路径: {output_path}")
        print(f"文件大小: {file_size:.2f} MB")
        return True
        
    except FileNotFoundError:
        print("错误: 未找到 mysqldump 命令。")
        print("请确保 MySQL 客户端工具已安装并添加到系统 PATH 中。")
        print("\n您也可以手动执行以下命令:")
        print(f"mysqldump -h {DB_CONFIG['host']} -P {DB_CONFIG['port']} -u {DB_CONFIG['user']} -p{DB_CONFIG['password']} --default-character-set={DB_CONFIG['charset']} --single-transaction {DB_CONFIG['database']} > {output_path}")
        return False
    except Exception as e:
        print(f"导出过程中发生错误: {str(e)}")
        return False


if __name__ == "__main__":
    # 支持命令行参数指定输出文件名
    output_file = sys.argv[1] if len(sys.argv) > 1 else None
    
    # 如果提供了参数但只是帮助信息
    if output_file in ['-h', '--help']:
        print("用法: python export_database.py [输出文件名]")
        print("示例: python export_database.py game_tower_backup.sql")
        sys.exit(0)
    
    success = export_database(output_file)
    sys.exit(0 if success else 1)
