# 数据库同步配置完成 ✅

## 配置状态

✅ **本地数据库连接**: 正常  
✅ **远程数据库连接**: 正常  
✅ **同步功能测试**: 通过

## 当前配置

### 本地数据库
- 主机: localhost
- 端口: 3306
- 用户: root
- 密码: 1234
- 数据库: game_tower

### 远程数据库
- 主机: 8.146.206.229
- 端口: 3306
- 用户: root
- 密码: Wxs1230.0
- 数据库: game_tower

## 使用方法

### 1. 运行完整同步（推荐）

同步所有表到远程数据库：

```bash
cd scripts/sync
python sync_main.py
```

这将同步所有 79 个表：
- 玩家相关表（15个）
- 联盟相关表（29个）
- 战斗相关表（17个）
- 其他表（18个）

### 2. 分模块同步

如果只想同步特定类型的表：

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

### 3. 测试单个表

```bash
python test_sync.py
```

## 安全说明

✅ **不会删除远程数据**: 使用 `INSERT ... ON DUPLICATE KEY UPDATE`，只插入新数据或更新已存在的数据

✅ **自动创建表**: 如果远程表不存在，会自动创建表结构

✅ **批量处理**: 每次处理 1000 条记录，提高效率

✅ **详细日志**: 所有操作都会记录到日志文件中

## 日志文件

同步完成后会生成日志文件：
- 文件名格式: `sync_log_YYYYMMDD_HHMMSS.log`
- 位置: `scripts/sync/` 目录下

## 注意事项

1. **首次运行前建议备份远程数据库**
2. 同步过程可能需要较长时间（取决于数据量）
3. 可以随时按 `Ctrl+C` 中断同步
4. 中断后可以重新运行，会继续同步未完成的表

## 故障排除

如果遇到问题：

1. **检查数据库连接**
   ```bash
   python sync_config.py
   ```

2. **查看日志文件**了解详细错误信息

3. **测试单个表**
   ```bash
   python test_sync.py
   ```

## 下一步

配置已完成，您现在可以：

1. 运行完整同步: `python sync_main.py`
2. 或者先测试单个表: `python test_sync.py`

祝您使用愉快！ 🚀
