# 魔魂系统开发文档 (MoSoul System)

本文档记录了魔魂系统的代码分布与实现逻辑，方便后续修改和维护。

## 1. 配置文件 (Configurations)
存放魔魂的基础数据、类型定义及猎魂/强化等规则。
- `configs/mosoul_types.json`: 魔魂类型及其基础属性模板。
- `configs/mosoul_hunting.json`: 猎魂池配置、概率及消耗。
- `configs/mosoul_upgrade.json`: 魔魂升级/进阶的消耗与成长系数。

## 2. 后端接口 (Backend API)
- `interfaces/routes/mosoul_routes.py`: 魔魂相关的 API 路由定义（如猎魂、佩戴、升级等接口）。

## 3. 核心业务逻辑 (Core Logic)
- `domain/entities/mosoul.py`: 魔魂实体类定义、模板数据加载。
- `domain/services/mosoul_system.py`: 魔魂系统核心逻辑实现（计算属性、处理逻辑）。
- `infrastructure/db/mosoul_repo_mysql.py`: 魔魂相关的数据库操作（增删改查）。

## 4. 前端页面 (Frontend Pages)
存放于 `interfaces/client/src/features/beast/` 目录下，文件通常以 `MoSoul` 开头：
- `MoSoulPage.vue`: 魔魂主入口页面（展示已装备魔魂，可取下/摄魂）。
- `MoSoulOverviewPage.vue`: 魔魂总览/列表。
- `MoSoulHuntingPage.vue`: 猎魂系统页面。
- `MoSoulWarehousePage.vue`: 魔魂仓库/背包。
- `MoSoulDetailPage.vue`: 魔魂详情展示。
- `MoSoulSelectPage.vue`: 佩戴/更换魔魂的选择页面。
- `MoSoulAbsorbPage.vue`: 摄魂页面（消耗储魂器中的魔魂为目标魔魂提供经验）。

## 6. 摄魂规则 (Absorb/Upgrade Rules)
摄魂是让魔魂升级的过程，通过消耗其他魔魂来获得经验值：

### 经验值提供规则
不同品质魔魂提供的经验：
- 黄魂: 50经验
- 玄魂: 100经验
- 地魂: 200经验
- 天魂: 400经验
- 龙魂: 800经验
- 神魂: 1000经验
- 废魂: 0经验（无法作为材料）

### 升级经验需求
不同品质魔魂升级所需经验配置在 `configs/mosoul_upgrade.json` 的 `upgrade_exp` 字段中：
- 最大等级: 10级
- 每级所需经验按品质递增（详见配置文件）

### 摄魂流程
1. 选择已装备的目标魔魂点击"摄魂"
2. 从储魂器中选择材料魔魂点击"摄取"
3. 材料魔魂消失，目标魔魂获得经验
4. 经验足够时自动升级（可连续升级）

## 5. 依赖获取路径
在 `mosoul_routes.py` 中通过以下导入获取具体实现：
- `domain.entities.mosoul`: 实体与模板。
- `infrastructure.db.mosoul_repo_mysql`: 数据库持久化。
- `domain.services.mosoul_system`: 业务逻辑计算。
