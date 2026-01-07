# 数据库初始化脚本

## 文件说明

| 文件 | 说明 |
|------|------|
| `001_create_database.sql` | 创建数据库 |
| `002_create_tables.sql` | 创建数据表 |
| `003_init_data.sql` | 初始化测试数据 |
| `run_all.bat` | Windows一键执行脚本 |

## 使用方法

### Windows

1. 确保MySQL已安装并启动
2. 双击 `run_all.bat`
3. 输入MySQL root密码
4. 等待执行完成

### Linux/Mac

```bash
mysql -u root -p < 001_create_database.sql
mysql -u root -p < 002_create_tables.sql
mysql -u root -p < 003_init_data.sql
```

或一行命令：
```bash
cat 001_create_database.sql 002_create_tables.sql 003_init_data.sql | mysql -u root -p
```

## 数据表结构

### tower_state（闯塔状态表）

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | INT | 用户ID |
| tower_type | VARCHAR(20) | 塔类型(tongtian/longwen/zhanling) |
| current_floor | INT | 当前层数 |
| max_floor_record | INT | 最高纪录 |
| today_count | INT | 今日挑战次数 |
| last_challenge_date | DATE | 最后挑战日期 |

### player_beast（玩家幻兽表）

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | INT | 用户ID |
| name | VARCHAR(50) | 幻兽名称 |
| realm | VARCHAR(20) | 境界 |
| nature | VARCHAR(20) | 特性(法系/物系) |
| hp | INT | 气血 |
| physical_attack | INT | 物攻 |
| magic_attack | INT | 法攻 |
| physical_defense | INT | 物防 |
| magic_defense | INT | 法防 |
| speed | INT | 速度 |
| is_in_team | TINYINT | 是否在战斗队 |
| team_position | INT | 战斗队位置 |
