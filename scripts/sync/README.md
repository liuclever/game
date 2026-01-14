# 数据库同步工具

将本地 `game_tower` 数据库的内容安全同步到远程数据库，**不会删除远程数据库的现有数据**。

## 文件说明

- `sync_config.py` - 数据库连接配置（本地和远程）
- `sync_logger.py` - 日志记录模块
- `sync_table_info.py` - 表信息获取（主键、字段等）
- `sync_data_core.py` - 核心同步逻辑（批量处理、INSERT ON DUPLICATE KEY UPDATE）
- `sync_tables_players.py` - 玩家相关表同步（15个表）
- `sync_tables_alliance.py` - 联盟相关表同步（29个表）
- `sync_tables_battle.py` - 战斗相关表同步（17个表）
- `sync_tables_others.py` - 其他表同步（18个表）
- `sync_main.py` - 主入口脚本

## 使用方法

### 1. 配置数据库连接

编辑 `sync_config.py`，确认本地和远程数据库配置正确：

```python
LOCAL_DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',  # 修改为您的本地数据库密码
    ...
}

REMOTE_DB_CONFIG = {
    'host': '8.146.206.229',
    'user': 'root',
    'password': 'Wxs1230.0',
    ...
}
```

### 2. 运行完整同步

```bash
cd scripts/sync
python sync_main.py
```

### 3. 单独同步某个模块

```bash
# 只同步玩家相关表
python sync_tables_players.py

# 只同步联盟相关表
python sync_tables_alliance.py

# 只同步战斗相关表
python sync_tables_battle.py

# 只同步其他表
python sync_tables_others.py
```

## 同步策略

- **安全同步**: 使用 `INSERT ... ON DUPLICATE KEY UPDATE`，只插入新数据或更新已存在的数据
- **不删除数据**: 不会删除远程数据库中存在的任何数据
- **批量处理**: 每次处理 1000 条记录，提高效率
- **自动创建表**: 如果远程表不存在，会自动创建表结构
- **详细日志**: 记录每个表的同步进度和结果

## 注意事项

1. **首次运行前建议备份远程数据库**
2. 确保本地和远程数据库连接正常
3. 同步过程可能需要较长时间，请耐心等待
4. 日志文件会保存在 `sync_log_YYYYMMDD_HHMMSS.log`

## 同步统计

同步完成后会显示：
- 插入的行数
- 更新的行数
- 跳过的行数
- 错误数

## 故障排除

如果遇到问题：
1. 检查数据库连接配置
2. 查看日志文件了解详细错误信息
3. 确保本地数据库表结构完整
4. 检查网络连接是否正常
