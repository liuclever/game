顶层目录说明（总览）

整个项目分为六层，每一层只负责一种“变化方向”：

domain：游戏世界的“规则与概念”

application：一条条“游戏操作”的流程

interfaces：用户/外部系统看到的一切入口

infrastructure：落地到数据库、配置、日志等实现细节

configs：可调的游戏数值和静态配置

tests：保证改代码时不把旧东西搞坏




1. domain/ — 核心规则层（游戏大脑）

负责什么：

描述「游戏世界里有什么」

玩家、地图、怪物、物品、战斗结果、幻兽、镇妖场景等概念

定义「这些东西怎么运作」

伤害怎么算、升级需要多少经验、掉落概率、签到规则、挂机收益等

不负责什么：

不处理 HTTP、路由、页面

不关心数据库长什么样

不管日志、缓存、框架

一句话：domain = 游戏的“物理定律”和“生物设定”。

2. application/ — 用例服务层（游戏操作流程）

负责什么：

把“规则”串成一条条可执行的“操作/用例”，比如：

开始战斗

每日签到

进入地图

领取奖励

决定一次操作的步骤顺序：先查谁、再调用哪条规则、最后存到哪。

不负责什么：

不画界面、不做 HTML

不做数据库细节（只知道有“仓储接口”可以读写）

不决定具体算法（算法由 domain 提供）

一句话：application = “玩家点击某个按钮后，后台实际干的那条业务流程”。

3. interfaces/ — 界面与外部入口层

负责什么：

所有对“外界暴露”的入口：

网页前端 / 后端路由

将来的客户端接口、管理后台接口等

接收请求 → 调用 application 的用例 → 把结果展示出来

不负责什么：

不实现游戏规则

不写业务流程的细节

不碰数据库细节

一句话：interfaces = 所有“看得见、点得着”的入口，只做“翻译”和“展示”。

4. infrastructure/ — 实现细节层

负责什么：

把抽象的“读写玩家、读写怪物、读写地图”等操作真正落地：

数据库访问（ORM、SQL、缓存）

读写配置文件

日志实现、消息队列等技术组件

为 domain / application 提供服务实现（例如仓储实现）。

不负责什么：

不定义业务规则

不决定用例流程

不处理界面展示

一句话：infrastructure = “和具体技术栈强相关的那一层，随时可以换实现”。

5. configs/ — 可配置的游戏数据层

负责什么：

游戏运行时需要但又不是“代码逻辑”的数据：

地图列表、怪物属性、掉落表

经验曲线、战斗公式参数

各类静态或半静态配置文件（JSON/CSV 等）

不负责什么：

不写算法、不写业务流程

只是提供数据源，供其他层读取

一句话：configs = “策划改数值的地方，不用改代码”。

6. tests/ — 测试与质量保障层

负责什么：

对 domain、application 等核心逻辑做自动化测试

保证以后修改时：

升级、战斗、签到等核心规则不被改坏

重构 / 扩展时能快速发现问题

不负责什么：

不参与正式运行

不放业务代码，只放测试用例

一句话：tests = “保证项目不会越改越乱的安全网”。










lingwu_game/
├── domain/                     # ★核心规则（永远最稳定）
│   ├── entities/               # 游戏世界中的概念（纯 Python 类）
│   │   ├── user.py
│   │   ├── monster.py
│   │   ├── map.py
│   │   ├── item.py
│   │   ├── battle_result.py
│   │   └── __init__.py
│   ├── rules/                  # 游戏规则（升级、伤害、掉落…纯逻辑）
│   │   ├── battle_rules.py
│   │   ├── level_rules.py
│   │   ├── signin_rules.py
│   │   └── __init__.py
│   ├── repositories/           # 抽象仓储接口（不依赖 DB）
│   │   ├── user_repo.py
│   │   ├── monster_repo.py
│   │   ├── map_repo.py
│   │   └── __init__.py
│   └── __init__.py

├── application/                # ★用例服务（业务操作流程）
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── signin_service.py
│   │   ├── battle_service.py
│   │   ├── map_service.py
│   │   └── __init__.py
│   ├── dtos/                   # 输入/输出数据结构
│   │   ├── battle_dto.py
│   │   └── __init__.py
│   └── __init__.py

├── interfaces/                 # ★界面层（用户点击 → 调用用例）
│   ├── web/                    # Flask / FastAPI 路由 + HTML
│   │   ├── routes/
│   │   │   ├── home_routes.py
│   │   │   ├── auth_routes.py
│   │   │   ├── map_routes.py
│   │   │   ├── battle_routes.py
│   │   │   └── __init__.py
│   │   ├── templates/
│   │   │   ├── home.html
│   │   │   ├── signin.html
│   │   │   ├── battle_result.html
│   │   │   └── ...
│   │   └── __init__.py
│   └── __init__.py

├── infrastructure/             # ★实现细节（可随时替换）
│   ├── db/
│   │   ├── models.py           # SQLAlchemy 实体
│   │   ├── user_repo_sql.py    # Implement IUserRepo
│   │   ├── monster_repo_sql.py
│   │   ├── map_repo_sql.py
│   │   └── __init__.py
│   ├── config/
│   │   ├── load_maps.py
│   │   ├── load_monsters.py
│   │   └── __init__.py
│   ├── logging/
│   │   └── logger.py
│   └── __init__.py

├── configs/                    # ★游戏配置（可改不需改代码）
│   ├── maps.json
│   ├── monsters.json
│   ├── items.json
│   └── battle_formula.json

├── tests/                      # ★单元测试（保证不怕返工）
│   ├── test_battle_rules.py
│   ├── test_level_rules.py
│   └── ...

├── app.py                      # 入口：注册路由/启动服务
├── requirements.txt
└── README.md
