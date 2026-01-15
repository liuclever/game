# 配置说明

## 当前配置状态

⚠️ **本地数据库配置已注释**

当前配置中，本地数据库连接已被注释，程序只会连接远程数据库。

## 重要提示

如果本地数据库配置被注释，**同步功能将无法使用**，因为同步需要：
- **源数据库**（本地）：读取数据
- **目标数据库**（远程）：写入数据

## 恢复本地数据库配置

如果需要使用同步功能，请取消注释 `sync_config.py` 中的本地数据库配置：

```python
# 取消注释以下代码
LOCAL_DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '1234',  # 修改为您的本地数据库密码
    'database': 'game_tower',
    'charset': 'utf8mb4',
    'cursorclass': DictCursor,
    'connect_timeout': 10,
}
```

并恢复 `get_local_connection()` 函数：

```python
def get_local_connection():
    """获取本地数据库连接"""
    return pymysql.connect(**LOCAL_DB_CONFIG)
```

## 当前可用功能

✅ **远程数据库连接测试** - 可以测试远程数据库连接  
❌ **数据同步功能** - 需要本地数据库配置才能使用

## 验证远程连接

运行以下命令验证远程数据库连接：

```bash
cd scripts/sync
python sync_config.py
```

如果看到 `[成功] 远程数据库连接正常`，说明远程连接配置正确。
