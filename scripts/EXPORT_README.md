# 数据库导出说明

## 功能
导出 `game_tower` 数据库，确保编码（UTF-8）和顺序正确。

## 使用方法

### 方法一：使用批处理脚本（推荐，Windows系统）

直接双击运行或在命令行执行：
```bash
scripts\export_database.bat
```

或者：
```bash
cd scripts
export_database.bat
```

### 方法二：使用Python脚本

```bash
python scripts/export_database.py
```

或者指定输出文件名：
```bash
python scripts/export_database.py game_tower_backup.sql
```

## 配置说明

脚本使用的数据库配置：
- 主机: localhost
- 端口: 3306
- 用户名: root
- 密码: 1234（如果密码不对，请修改脚本中的密码）
- 数据库名: game_tower
- 字符集: utf8mb4

## 导出选项说明

脚本使用以下 mysqldump 选项确保导出质量：

- `--default-character-set=utf8mb4`: 指定字符集为 UTF-8（确保中文等字符正确导出）
- `--single-transaction`: 使用单事务模式，确保数据一致性
- `--routines`: 导出存储过程和函数
- `--triggers`: 导出触发器
- `--events`: 导出事件
- `--add-drop-table`: 添加 DROP TABLE 语句（导入时会先删除表）
- `--add-locks`: 添加锁表语句
- `--complete-insert`: 使用完整的 INSERT 语句（包含列名）
- `--skip-extended-insert`: 使用多行 INSERT 语句（便于查看和编辑）

## 输出文件

导出的SQL文件会保存在项目根目录，文件名格式为：
- `game_tower_YYYYMMDD_HHMMSS.sql`（自动生成时间戳）
- 或指定的文件名（如果使用 Python 脚本并提供了文件名参数）

## 注意事项

1. **密码配置**: 如果数据库密码不是 `1234`，请修改脚本中的密码配置
   - Python脚本: 修改 `scripts/export_database.py` 中的 `DB_CONFIG['password']`
   - 批处理脚本: 修改 `scripts/export_database.bat` 中的 `DB_PASSWORD`

2. **MySQL客户端工具**: 确保系统已安装 MySQL 客户端工具，并且 `mysqldump` 命令在系统 PATH 中

3. **字符编码**: 导出的SQL文件使用 UTF-8 编码，可以正确处理中文等字符

4. **导入数据库**: 导出的SQL文件可以使用以下命令导入：
   ```bash
   mysql -u root -p game_tower < game_tower_YYYYMMDD_HHMMSS.sql
   ```
