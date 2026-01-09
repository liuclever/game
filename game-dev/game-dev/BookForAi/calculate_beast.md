# 幻兽资质与属性计算过程文档

本文档详细记录了玩家使用“召唤球”获得幻兽后的资质生成及各属性（四维、战力、星级）的详细计算逻辑与涉及的文件路径。

---

## 1. 核心流程概述

1.  **道具使用**：玩家在背包点击使用召唤球。
2.  **触发获取**：系统识别召唤球对应的幻兽模板。
3.  **随机生成 (Factory)**：根据模板配置的资质范围，随机生成幻兽的初始资质、性格、境界和成长率。
4.  **属性计算 (Stats)**：基于生成的资质、等级、境界倍率和成长率倍率，计算幻兽的最终战斗属性（HP、物攻、法攻、防御、速度）。
5.  **星级展示**：根据资质数值计算在详情页显示的实心星与空心星数量。

---

## 2. 涉及文件及其路径

### 2.1 业务入口层
- **物品使用处理**：`application/services/inventory_service.py`
    - 方法：`use_item(self, user_id, inv_item_id, quantity)`
    - 逻辑：识别 20001-30000 范围内的召唤球 ID，调用幻兽获取逻辑。
- **路由分发**：`interfaces/routes/beast_routes.py`
    - 方法：`obtain_beast_for_user(user_id, template_id, realm, level)`
    - 逻辑：封装了幻兽生成的 API 入口。

### 2.2 应用服务层
- **幻兽服务**：`application/services/beast_service.py`
    - 方法：`obtain_beast_randomly(self, user_id, template_id, realm, level)`
    - 逻辑：衔接 Factory 进行实例化并调用 Repo 进行数据库持久化。

### 2.3 领域逻辑层 (核心计算)
- **幻兽生成工厂**：`domain/services/beast_factory.py`
    - 方法：`create_initial_beast(user_id, template)`
    - **关键逻辑**：
        - 随机资质：`random.randint(template.hp_aptitude_min, template.hp_aptitude_max)`
        - 随机性格：从性格列表中随机抽取。
        - 初始属性设置。
- **属性计算逻辑**：`domain/services/beast_stats.py`
    - 方法：`calc_beast_attributes(...)`
    - **核心公式**：
        - `HP = (基础生命 + 境界提升) * 境界倍率 + (生命资质 * 等级 * 成长倍率 / 200)`
        - `攻击 = (基础攻击 + 境界提升) * 境界倍率 + (攻击资质 * 等级 * 成长倍率 / 100)`
        - `战力 = HP/4 + 攻击 + 防御 + 速度`
    - 方法：`calc_beast_aptitude_stars(...)`
    - **星级逻辑**：
        - 每 200 点资质为一个“大档位”（1 颗星）。
        - 具体的实心星与空心星转换逻辑在此定义。

### 2.4 数据与配置层
- **幻兽模板配置**：`infrastructure/config/beast_template_repo_from_config.py`
    - 作用：定义每种幻兽的初始资质范围（min/max）。
- **境界倍率配置**：`configs/growth_rate_multipliers.json` 或代码硬编码。
- **数据库持久化**：`infrastructure/db/player_beast_repo_mysql.py`
    - 字段：`physical_attack_aptitude`, `magic_attack_aptitude` 等。

---

## 3. 常见验证与修改点

1.  **资质范围修改**：修改幻兽模板中的 `_min` 和 `_max` 字段。
2.  **属性加成调整**：在 `domain/services/beast_stats.py` 的 `calc_beast_attributes` 中调整公式系数。
3.  **物/法攻区分**：检查 `calc_beast_attributes` 是否正确读取了对应的 `phys_atk_aptitude` 或 `magic_atk_aptitude`。
4.  **星级阈值修改**：在 `calc_beast_aptitude_stars` 中修改 `200` 这个步进值。

---

## 4. 后续 AI 验证建议

若要验证计算逻辑是否正确，建议 AI 重点审查：
1. `domain/services/beast_stats.py` 中的 `calc_beast_attributes` 是否正确应用了所有参数。
2. `interfaces/routes/beast_routes.py` 中的 `_calc_beast_stats` 是否在返回前端前正确同步了数据库与计算结果。
