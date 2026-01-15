# 项目架构说明文档 (Architecture Documentation)

本项目的目标是构建一个高内聚、低耦合的游戏后端系统，遵循 **DDD (领域驱动设计)** 和 **整洁架构 (Clean Architecture)** 的核心思想。

## 核心设计原则

1.  **分层原则**：代码分为四个主要层次：接口层 (Interfaces)、应用层 (Application)、领域层 (Domain) 和 基础设施层 (Infrastructure)。
2.  **依赖倒置**：核心业务逻辑（领域层）不应依赖于外部框架或数据库（基础设施层）。依赖关系应由外向内：`Interfaces -> Application -> Domain <- Infrastructure`。
3.  **杜绝单体大文件**：禁止将所有功能堆到一个文件中。每个业务模块应根据功能垂直拆分，并按层次水平划分。

## 目录结构与职责

### 1. 领域层 (Domain Layer) - `domain/`
项目最核心、最纯净的部分。

*   **Entities (`domain/entities/`)**: 包含业务对象及其内在逻辑。
    *   *准则*：应该是纯 Python 类（如 `dataclass`），不包含数据库操作。
    *   *示例*：`Player` 类中包含 `add_exp` (加经验升级) 和 `recover_energy` (活力恢复) 逻辑。
*   **Repositories (`domain/repositories/`)**: 定义数据访问的接口（抽象基类）。
    *   *准则*：仅定义方法签名，不实现具体存储逻辑。
*   **Services (`domain/services/`)**: 涉及多个实体交互的复杂业务逻辑。
    *   *示例*：`BeastStatCalculator` 负责计算幻兽属性。

### 2. 应用层 (Application Layer) - `application//services/`
负责协调领域对象和外部服务。

*   **Services**: 具体的用例实现。
    *   *准则*：从仓库加载实体，调用实体方法执行业务逻辑，最后持久化实体。
    *   *示例*：`AuthService` 协调 `IPlayerRepo` 和 `BeastFactory` 完成用户注册流程。

### 3. 基础设施层 (Infrastructure Layer) - `infrastructure/`
负责具体的技术细节实现。

*   **Database (`infrastructure/db/`)**: 实现领域层定义的 Repository 接口。
    *   *准则*：此处包含具体的 SQL 语句和数据库连接逻辑。
    *   *示例*：`MySQLPlayerRepo` 实现了磁盘存储。
*   **Config (`infrastructure/config/`)**: 全局配置加载。

### 4. 接口层 (Interface Layer) - `interfaces/`
负责接收外部请求并返回响应。

*   **Routes (`interfaces/routes/`)**: 定义 API 端点。
    *   *准则*：仅负责解析请求参数，调用 **Application Service**，并进行格式化输出。不应包含任何业务逻辑或数据库直接调用。

---

## AI 开发指引：新增功能流程

当你需要新增一个功能（例如：好友系统）时，请按以下步骤操作：

1.  **定义实体**：在 `domain/entities/friend.py` 中创建 `Friend` 实体。
2.  **定义仓库接口**：在 `domain/repositories/friend_repo.py` 中定义 `IFriendRepo`。
3.  **实现基础设施**：在 `infrastructure/db/friend_repo_mysql.py` 中实现具体 SQL 逻辑。
4.  **编写应用服务**：在 `application/services/friend_service.py` 中编写业务逻辑。
5.  **暴露接口**：在 `interfaces/routes/friend_routes.py` 中增加路由。

## 注意事项 (Anti-patterns)

*   ❌ **禁止** 在 `domain/` 中导入 `infrastructure/` 或 `application/`。
*   ❌ **禁止** 在 `interfaces/` 中直接书写 SQL 语句（应在 `infrastructure/` 处理）。
*   ❌ **禁止** 所有函数都塞进一个 `utils.py` 或 `main.py`。
*   ✅ **推荐** 使用仓库模式 (Repository Pattern) 隔离数据源，方便后续更换数据库。
