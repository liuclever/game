# 玩家系统文件路径与功能说明

本文档用于帮助AI快速定位玩家系统相关文件及其功能。

---

## 一、领域层 (Domain Layer)

### 1. 实体 (Entities)
| 文件路径 | 功能说明 |
|---------|---------|
| `domain/entities/player.py` | **玩家实体核心定义**<br>- `Player` 类：玩家数据模型（user_id、昵称、等级、经验、金币、元宝、强化石、体力、声望、VIP等属性）<br>- 等级系统：`add_exp()` 增加经验并自动升级、`exp_to_next_level()` 获取升级所需经验<br>- 阶位系统：`get_rank_name()` 获取阶位名称（黄阶/玄阶/地阶/天阶/飞马/玄武/战神）<br>- 召唤师称号：`get_summoner_title()` 获取x星x品召唤师称号<br>- 镇妖系统：`get_zhenyao_range()` 获取可镇妖层数范围、`can_zhenyao()` 是否可镇妖<br>- `ZhenyaoFloor` 类：镇妖层信息实体 |

### 2. 仓库接口 (Repository Interfaces)
| 文件路径 | 功能说明 |
|---------|---------|
| `domain/repositories/player_repo.py` | **玩家仓库接口协议**<br>- `IPlayerRepo`：玩家数据访问接口（get_by_id、save）<br>- `IZhenyaoRepo`：镇妖数据访问接口（获取层、占领层、释放层等） |

---

## 二、基础设施层 (Infrastructure Layer)

### 1. MySQL数据库实现
| 文件路径 | 功能说明 |
|---------|---------|
| `infrastructure/db/player_repo_mysql.py` | **MySQL玩家仓库实现**<br>- `MySQLPlayerRepo`：玩家CRUD操作（get_by_id、get_by_username、verify_login、save、create、create_with_auth）<br>- `MySQLZhenyaoRepo`：镇妖层CRUD操作<br>- 便捷函数：`get_player_by_id()`、`update_gold()` |
| `infrastructure/db/player_beast_repo_mysql.py` | **玩家幻兽仓库**<br>- `PlayerBeastData`：玩家幻兽数据类（属性、资质、技能等）<br>- `MySQLPlayerBeastRepo`：幻兽CRUD操作（获取战斗队、获取所有幻兽、更新、创建、删除/放生）<br>- 便捷函数：`get_beast_by_id()`、`get_beasts_by_user()` |

### 2. 内存实现（测试用）
| 文件路径 | 功能说明 |
|---------|---------|
| `infrastructure/memory/player_repo_inmemory.py` | **内存玩家仓库**<br>- `InMemoryPlayerRepo`：用字典存储玩家数据，用于本地测试 |

---

## 三、应用层 (Application Layer)

### 服务 (Services)
| 文件路径 | 功能说明 |
|---------|---------|
| `application/services/auth_service.py` | **登录注册服务**<br>- `AuthService`：注册(`register`)、登录(`login`)、获取玩家(`get_player`)<br>- 测试模式：新用户自动获得满资质幻兽、大量道具、通天塔进度<br>- `_create_default_beasts()`：创建默认幻兽<br>- `_create_test_mode_items()`：创建测试道具 |
| `application/services/cultivation_service.py` | **修行系统服务**<br>- `CultivationService`：修行状态查询、开始修行、领取奖励、终止修行<br>- `levelup()`：晋级（消耗声望提升等级）<br>- 修行配置：不同时长对应不同声望奖励 |

---

## 四、接口层 (Interfaces Layer)

### 1. API路由 (Routes)
| 文件路径 | 功能说明 |
|---------|---------|
| `interfaces/routes/player_routes.py` | **玩家相关API路由**<br>- `GET /api/player/info`：获取当前玩家基础信息<br>- `GET /api/player/profile?id=xxx`：获取其他玩家个人信息页<br>- `POST /api/player/levelup`：晋级<br>- `GET /api/cultivation/status`：获取修行状态<br>- `GET /api/cultivation/options`：获取修行选项<br>- `POST /api/cultivation/start`：开始修行<br>- `POST /api/cultivation/harvest`：领取修行奖励<br>- `POST /api/cultivation/stop`：终止修行 |

### 2. 前端页面 (Vue Components)
| 文件路径 | 功能说明 |
|---------|---------|
| `interfaces/client/src/features/player/PlayerDetailPage.vue` | **玩家详情页**<br>- 显示玩家ID、等级、魅力、声望、活力、铜钱等<br>- 显示战宠列表、综合战力、战绩<br>- 操作：写信、加好友、拉黑、切磋 |
| `interfaces/client/src/features/player/PlayerProfilePage.vue` | **玩家个人信息页**<br>- 功能与PlayerDetailPage类似<br>- 显示玩家动态 |

---

## 五、配置文件 (Configs)

| 文件路径 | 功能说明 |
|---------|---------|
| `configs/player_level_up_exp.json` | **玩家升级经验配置**<br>- `max_level`：最大等级（100）<br>- `exp_to_next_level`：每级升级所需经验映射（1-99级） |

---

## 六、相关常量与规则

### 等级阶位配置（在 player.py 中定义）
```
RANK_CONFIG = [
    (1, 29, "黄阶", None),        # 不能镇妖
    (30, 39, "玄阶", (1, 20)),    # 镇妖1-20层
    (40, 49, "地阶", (21, 40)),   # 镇妖21-40层
    (50, 59, "天阶", (41, 60)),   # 镇妖41-60层
    (60, 69, "飞马", (61, 80)),   # 镇妖61-80层
    (70, 79, "玄武", (81, 100)),  # 镇妖81-100层
    (80, 100, "战神", (101, 120)) # 镇妖101-120层
]
```

### 修行配置（在 cultivation_service.py 中定义）
```
CULTIVATION_CONFIG = {
    1小时: 50声望,
    2小时: 120声望,
    4小时: 280声望,
    8小时: 650声望,
    12小时: 1100声望
}
```

---

## 七、数据流向

```
前端(Vue) 
    ↓ HTTP请求
API路由(player_routes.py)
    ↓ 调用
应用服务(auth_service.py / cultivation_service.py)
    ↓ 使用
仓库实现(player_repo_mysql.py / player_beast_repo_mysql.py)
    ↓ 操作
MySQL数据库
```

---

## 八、关键类关系

```
Player (实体)
    ├── IPlayerRepo (仓库接口)
    │       ├── MySQLPlayerRepo (MySQL实现)
    │       └── InMemoryPlayerRepo (内存实现)
    ├── AuthService (认证服务)
    └── CultivationService (修行服务)

PlayerBeastData (玩家幻兽数据)
    └── MySQLPlayerBeastRepo (幻兽仓库)
```
