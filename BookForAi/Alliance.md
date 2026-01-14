# 联盟模块 (Alliance Module) 全流程说明文档

## 1. 模块概述
联盟模块允许玩家创建、加入和管理联盟。主要包含联盟信息查询、创建联盟、成员管理等核心功能。

## 2. 核心文件结构
- **前端 (Vue 3)**: `interfaces/client/src/features/alliance/AlliancePage.vue`
- **联盟聊天核心**: `interfaces/client/src/features/alliance/AllianceChatPage.vue`
- **后端路由**: `interfaces/routes/alliance_routes.py`
- **应用服务**: `application/services/alliance_service.py`
- **领域实体**: `domain/entities/alliance.py` (包含 `Alliance`, `AllianceMember`, `AllianceChatMessage`)
- **领域规则**: `domain/rules/alliance_rules.py` (等级要求、道具消耗等规则)
- **数据库仓储**: `infrastructure/db/alliance_repo_mysql.py`
- **数据库仓储接口**: `domain/repositories/alliance_repo.py`
- **数据库 SQL 脚本**: `sql/028_alliance_system.sql` (各表建表语句)

### 2.1 公告栏功能结构
- **前端公告入口**: `interfaces/client/src/features/alliance/AlliancePage.vue`、`AllianceCouncilPage.vue`
- **公告详情/修改页**: `interfaces/client/src/features/alliance/AllianceNoticePage.vue`
- **前端路由**: `/alliance/notice`
- **应用服务**: `AllianceService.get_alliance_notice`、`AllianceService.update_alliance_notice`
- **后端接口**:
  - `GET /api/alliance/notice` 获取当前联盟公告及是否可编辑
  - `POST /api/alliance/notice` 盟主修改公告（限制 35 字，非空）
- **仓储方法**: `IAllianceRepo.update_notice` 由 `MySQLAllianceRepo.update_notice` 实现
- **页面交互**：
  1. 在联盟主页或议事厅点击“公告栏”/公告区域，路由跳转到 `/alliance/notice`
  2. 页面展示当前公告。若当前玩家是盟主(`can_edit=True`)，显示输入框与“确认修改”按钮
  3. 点击确认后调用 `POST /api/alliance/notice`，成功后返回“我的联盟”页面并刷新公告文案
  4. 非盟主玩家仅可查看，提示“仅盟主可以修改公告”

### 2.2 成员管理功能结构
- **前端入口**: `AlliancePage.vue` “成员管理”链接、`AllianceCouncilPage.vue` 中的“成员管理”占位
- **成员管理页**: `interfaces/client/src/features/alliance/AllianceMembersPage.vue`
- **前端路由**: `/alliance/members`
- **应用服务**: `AllianceService.get_alliance_members_info`、`update_member_role`、`kick_member`
- **后端接口**:
  - `GET /api/alliance/members?sort=role|contribution|level`
  - `POST /api/alliance/members/role` (body: `target_user_id`, `role`)
  - `POST /api/alliance/members/kick` (body: `target_user_id`)
- **仓储方法**: `update_member_role`、`remove_member`
- **权限规则**（由 `AllianceRules` 定义）：
  - 盟主、 副盟主、长老可编辑公告
  - 仅盟主可任命副盟主/长老（职位候选：盟众、长老、副盟主）
  - 盟主可踢除非盟主；副盟主可踢长老/盟众；长老/盟众不可踢人
- **页面交互**：
  1. 默认按职位优先级排序（盟主→副盟主→长老→盟众）；用户可切换贡献/等级排序
  2. 表格展示：序号、昵称、等级、职位、贡献、操作
  3. 具备权限时显示职位下拉与“调整”按钮；点击“踢出”会调用踢人接口
  4. 底部提供“返回联盟”“返回游戏首页”导航

### 2.3 天赋池（学习/研究 + 升级）功能结构
- **前端入口**: `AlliancePage.vue`/`AllianceCouncilPage.vue` 中的“天赋池/天赋研习”链接
- **列表页**: `interfaces/client/src/features/alliance/AllianceTalentPage.vue` 展示当前六类天赋数据
- **详情页**：
  - 学习：`AllianceTalentLearnPage.vue`（路由 `/alliance/talent/:key/learn`）
  - 研究：`AllianceTalentResearchPage.vue`（路由 `/alliance/talent/:key/research`）
- **升级页**: `AllianceTalentUpgradePage.vue`（路由 `/alliance/talent/upgrade`），由联盟建筑列表跳转
- **后端接口**:
  - `GET /api/alliance/talent`：返回建筑等级、是否可研究、六类天赋（玩家等级/研究等级/最大等级/属性加成/是否可学习）
  - `POST /api/alliance/talent/learn`：玩家自身学习天赋（若未满级）
  - `POST /api/alliance/talent/research`：盟主提升对应天赋研究等级（上限=建筑等级）
  - `GET /api/alliance/talent/upgrade-info`：获取天赋池升级详情（当前等级、研究上限、资源需求、阻塞原因）
  - `POST /api/alliance/talent/upgrade`：盟主执行天赋池升级
- **应用服务**: `AllianceService.get_alliance_talent_info`、`learn_alliance_talent`、`research_alliance_talent`
- **升级服务**: `AllianceService.get_talent_pool_upgrade_info`、`upgrade_talent_pool`
- **研发消耗规则**：`AllianceRules.TALENT_RESEARCH_COST_RULES` 记录 2~10 级各阶段研发所需联盟资金/焚火晶（单位为整数，繁荣度在天赋池升级阶段校验），由 `get_talent_research_cost(level, key)` 返回；`get_alliance_talent_info` 同时返回当前联盟 `resources` 供前端展示。
- **领域/仓储更新**:
  - 新增实体 `AllianceTalentResearch`, `PlayerTalentLevel`
  - `IAllianceRepo` + `MySQLAllianceRepo`：实现 `get/update_alliance_talent_research`、`get/update_player_talent_level`
  - SQL 新增 `alliance_talents`、`player_talent_levels` 表
- **升级规则**: `AllianceRules.TALENT_POOL_UPGRADE_RULES`，对 1→10 级的议事厅要求、资金/焚火晶消耗、繁荣度需求进行管理，并通过 `get_talent_pool_upgrade_rule`、`talent_pool_research_cap` 等 helper 提供数据
- **权限规则**:
  - 所有成员可学习本人天赋，但不能超出 `min(联盟建筑等级, 天赋研究等级)`
  - 仅盟主可研究，研究等级 ≤ 联盟建筑等级
  - 仅盟主可升级天赋池，需满足对应议事厅等级、资金、焚火晶与繁荣度条件
- **前端交互**:
  1. 天赋列表展示当前等级/上限/研究等级/属性加成
  2. “学习”按钮跳转到对应详情页，调用 `/talent/learn`
  3. “研究”按钮（仅盟主可见）跳转到研究页，调用 `/talent/research`
  4. “研究”按钮（仅盟主可见）会展示下一等级消耗，检验联盟资金/焚火晶是否充足；耗费成功后刷新研究等级并提示。
  5. “升级”按钮（仅盟主可见）跳转到 `/alliance/talent/upgrade`，页面展示当前/目标等级、研究上限提升、所需资源及阻塞原因，并可调用 `/talent/upgrade`
  6. 操作完成后返回列表可看到最新等级
  7. 列表与详情均提供“返回联盟”“返回游戏首页”

### 2.4 幻兽室（联盟寄存 + 升级）
- **使用场景**：玩家幻兽栏已满时，可将幻兽寄存到当前联盟的幻兽室中，稍后再取回。
- **容量规则**：`AllianceRules.beast_storage_capacity(alliance_level)`，即联盟等级 1 级可存 1 只，2 级可存 2 只，以此类推，最少 1 格。
- **升级规则**：`AllianceRules.BEAST_ROOM_UPGRADE_RULES` 定义 1→10 级幻兽室升级要求（议事厅等级、资金、焚火晶、繁荣度）。通过 `get_beast_room_upgrade_rule`、`beast_room_capacity_from_level` 计算每级容量，“每升一级容量 +1”。
- **领域/仓储**
  - 实体：`AllianceBeastStorage`
  - 接口：`IAllianceRepo` 新增 `get_beast_storage` / `add_beast_storage` / `remove_beast_storage` / `count_beast_storage` 等方法
  - MySQL 实现：`infrastructure/db/alliance_repo_mysql.py`，使用 `alliance_beast_storage` 表
  - SQL：`sql/028_alliance_system.sql` 中创建 `alliance_beast_storage`
- **应用服务**：`AllianceService`
  - `get_beast_storage_summary(user_id)`：用于 `/api/beast/list` 返回容量/占用
  - `get_beast_storage_info(user_id)`：用于查看清单
  - `store_beast_in_alliance_storage(user_id, beast_id)`：寄存幻兽（校验所属、在队/出战状态、容量、重复寄存等）
  - `retrieve_beast_from_alliance_storage(user_id, storage_id)`：取回幻兽（仅限本人寄存的记录）
- **升级服务**：`AllianceService.get_beast_room_upgrade_info`、`AllianceService.upgrade_beast_room`
- **接口层**
  - `GET /api/alliance/beast-storage`：返回当前联盟所有寄存记录列表
  - `POST /api/alliance/beast-storage/store`：寄存幻兽（body: `beastId`）
  - `POST /api/alliance/beast-storage/retrieve`：取回幻兽（body: `storageId`）
  - `GET /api/alliance/beast/upgrade-info`：获取幻兽室升级需求（盟主可见阻塞原因）
  - `POST /api/alliance/beast/upgrade`：执行幻兽室升级（仅盟主，扣除资金/焚火晶、校验繁荣度）
- **前端**
  - `interfaces/client/src/features/beast/BeastPage.vue`：在幻兽栏中显示“寄存室(占用/容量)”；“寄存”按钮调用 `/beast-storage/store`；新增弹层展示寄存列表并可取回；未加入联盟或仓库满时给出提示。
  - `interfaces/client/src/features/alliance/AllianceBeastUpgradePage.vue`：盟主点击联盟建筑页的“幻兽室→升级”后跳转至 `/alliance/beast/upgrade`，页面展示当前/下一等级容量、资源需求、阻塞原因，并允许调用 `/beast/upgrade` 进行升级；成功后刷新显示。

#### 寄存仓库升级
- **规则**：`AllianceRules.ITEM_STORAGE_UPGRADE_RULES`（每级容量 +5，基础 5 格），配合 `get_item_storage_upgrade_rule`、`item_storage_capacity_from_level` 计算容量。
- **服务**：`AllianceService.get_item_storage_upgrade_info`、`upgrade_item_storage`（仅盟主管理，校验议事厅等级/资金/焚火晶/繁荣度）。
- **接口**：
  - `GET /api/alliance/item-storage/upgrade-info`：返回当前仓库等级、容量、下一等级需求与阻塞原因。
  - `POST /api/alliance/item-storage/upgrade`：盟主执行升级，扣除资源并返回最新容量与联盟资金/焚火晶。
- **前端**：`AllianceItemUpgradePage.vue`（路由 `/alliance/item/upgrade`）展示升级详情，按钮调用上述接口；联盟建筑页“寄存仓库→升级”跳转此页面。
- **注意事项**
  - 存入前需保证幻兽不在战斗队/未出战。
  - 取回时需验证寄存记录属于本人且所在联盟一致。
  - 容量变更（联盟升级）无需迁移数据，实时依据当前联盟等级计算。

### 2.5 火能修行（焚火晶产出）
- **玩法概述**：联盟成员可在修行广场创建/加入修行房间，持续 120 分钟后可领取焚火晶奖励。每日每人仅能修行一次，最多 4 人同修，人数 ≥2 时额外奖励 +2 个焚火晶。联盟等级越高，基础奖励越高（1 级 9 个，每升一级 +2）。
- **领域层**
  - 实体：`AllianceTrainingRoom`、`AllianceTrainingParticipant`
  - 规则：`AllianceRules` 增加 `TRAINING_DURATION_MINUTES`、`TRAINING_DAILY_LIMIT`、`training_crystal_reward`
- **仓储接口**：`IAllianceRepo` 新增以下方法：
  - `create_training_room` / `get_training_rooms` / `get_training_room_by_id`
  - `add_training_participant` / `get_training_participant` / `get_training_participant_by_room`
  - `get_training_participants` / `get_training_participation_today`
  - `mark_training_claimed` / `update_training_room_status` / `update_alliance_crystals`
- **数据库实现**：`infrastructure/db/alliance_repo_mysql.py`
  - 新建表 `alliance_training_rooms`、`alliance_training_participants`（见 `sql/028_alliance_system.sql`）
  - 实现上述仓储方法；更新联盟焚火晶字段
- **应用服务**：`AllianceService`
  - `get_training_ground_info`：聚合房间、参与者、今日限制、奖励状态
  - `create_training_room`：创建房间并自动加入创建者
  - `join_training_room`：校验每日限制/房间人数/状态后加入
  - `claim_training_reward`：校验结束状态、计算奖励、写入 `mark_training_claimed`、更新联盟焚火晶
- **接口层**：`interfaces/routes/alliance_routes.py`
  - `GET /api/alliance/training-ground`
  - `POST /api/alliance/training-ground/rooms`
  - `POST /api/alliance/training-ground/rooms/join`
  - `POST /api/alliance/training-ground/claim`
- **前端**：`interfaces/client/src/features/alliance/AllianceTrainingGroundPage.vue`
  - 首次加载调用 `GET /alliance/training-ground`
  - 支持创建房间、加入房间、领取奖励、刷新状态
  - 展示房间成员、结束倒计时、奖励说明
- **注意事项**
  - 每日限制通过 `get_training_participation_today` 控制
  - 修行结束状态以房间创建时间 +120 分钟判断，结束后统一标记 `completed`
  - 奖励发放后更新联盟焚火晶，并返回最新总量，供前端提示

### 2.6 联盟捐赠（资金 & 繁荣度&贡献）
- **功能概述**：联盟成员通过捐献指定物资为联盟增加资金、繁荣度，同时累计个人贡献。当前支持「金袋」与「焚火晶」。
- **兑换规则**（`AllianceRules.DONATION_RULES`）：
  - 金袋（item_id=6005）：+100 联盟资金、+100 繁荣度、+0 焚火晶、+10 贡献/个
  - 焚火晶（item_id=1004）：+0 联盟资金、+10 繁荣度、+1 联盟焚火晶、+1 贡献/个
- **领域层**：
  - `AllianceRules.get_donation_rule/donation_keys` 统一管理可捐献物资与收益。
- **仓储接口**（`IAllianceRepo`）：
  - `update_alliance_resources(alliance_id, funds_delta, prosperity_delta)`
  - `update_member_contribution(user_id, delta)`
- **数据库实现**：`MySQLAllianceRepo` 在 `alliances`、`alliance_members` 表上执行增量更新，并对资金/繁荣度/贡献做 `GREATEST(0, …)` 保护。
- **应用服务**（`AllianceService`）：
  - `get_donation_info(user_id)`：校验联盟身份，读取玩家背包数量，返回可捐献列表、当前联盟资金/繁荣度/焚火晶、个人贡献。
  - `donate_resources(user_id, donations)`：逐项校验数量、扣除背包物品、累计并写回联盟资金/繁荣度/焚火晶及成员贡献，输出最新统计。
  - 依赖 `InventoryService` 进行库存查询与 `remove_item`，捕获 `InventoryError` 并回传友好提示。
- **接口层**（`interfaces/routes/alliance_routes.py`）：
  - `GET /api/alliance/warehouse/donation-info` → `alliance_service.get_donation_info`
  - `POST /api/alliance/warehouse/donate` (body: `{ donations: { gold_bag: 1, fire_crystal: 10 } }`)
- **前端**：
  - 页面：`interfaces/client/src/features/alliance/AllianceDonatePage.vue`
  - 加载时调用 donation-info 接口并展示各物资可用数量与收益；提交调用 donate 接口，成功后更新联盟与个人统计。
  - 仓库页 `AllianceWarehousePage.vue` “捐赠物资>>” 链接路由 `/alliance/donate`。
- **注意事项**：
  1. 仅联盟成员可访问捐赠接口。
  2. 单次请求可同时提交多种物资，服务端按规则合并增量。
  3. 所有数量必须为正整数，物资不足时直接提示并终止整次扣除。

## 3. 核心业务流程：创建联盟
1. **前端触发**: 玩家在 `AlliancePage.vue` 输入联盟名并点击创建。
2. **后端请求**: POST `/api/alliance/create`.
3. **逻辑处理 (alliance_service.py)**:
    - 检查玩家是否存在。
    - 检查玩家是否已加入其他联盟 (alliance_members 表)。
    - 检查联盟名是否已被占用 (alliances 表)。
    - 检查玩家是否拥有“盟主证明” (道具 ID: 11001)。
    - 校验玩家等级 (需满 30 级)。
    - 扣除“盟主证明”。
    - 在 alliances 表中插入新联盟数据。
    - 在 alliance_members 表中插入盟主成员关系。

## 4. 数据库结构 (MySQL)

### alliances 表
| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| `id` | INT | 自增 ID，主键 |
| `name` | VARCHAR(100) | 联盟名称 (唯一) |
| `leader_id` | INT | 盟主玩家 ID |
| `level` | INT | 联盟等级 (默认 1) |
| `exp` | INT | 联盟经验 (默认 0) |
| `notice` | TEXT | 联盟公告 |
| `created_at` | DATETIME | 创建时间 |

### alliance_members 表
| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| `alliance_id` | INT | 所属联盟 ID |
| `user_id` | INT | 玩家 ID (主键) |
| `role` | TINYINT | 角色 (1: 盟主, 0: 成员) |
| `contribution` | INT | 联盟贡献度 |
| `joined_at` | DATETIME | 加入时间 |

### alliance_chat_messages 表
| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| `id` | INT | 自增 ID，主键 |
| `alliance_id` | INT | 联盟 ID |
| `user_id` | INT | 发送者玩家 ID |
| `content` | TEXT | 消息内容 |
| `created_at` | DATETIME | 发送时间 |

> 公告字段保存在 `alliances.notice`，更新公告时仅修改该字段，无需追加其他表。

## 5. 常见问题排查建议
- **(重要) 表不存在错误**: 若出现 Table 'game_tower.alliance_members' 或 'game_tower.alliance_chat_messages' doesn't exist，请检查数据库初始化脚本是否包含相关表。
- **发送消息失败**: 检查玩家是否在联盟内，检查 `alliance_chat_messages` 表是否已创建。

## 6. 联盟聊天室功能
联盟成员可以在聊天室中实时交流。消息对全联盟成员可见。
- **前端路由**: `/alliance/chat`
- **前端模块**: `interfaces/client/src/features/alliance/AllianceChatPage.vue`
- **后端接口**:
    - `GET /api/alliance/chat/messages`: 获取最近 50 条聊天记录。
    - `POST /api/alliance/chat/send`: 发送聊天消息。
- **业务逻辑**:
    - 前端采用 3 秒轮询机制获取最新消息。
    - 后端在 `AllianceService` 中校验玩家联盟身份。
    - 数据库 `alliance_chat_messages` 表存储消息内容及发送时间。
    - 查询时关联 `player` 表获取发送者昵称。
