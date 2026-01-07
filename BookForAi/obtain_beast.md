# 在背包打开召唤球功能涉及的文件与路径

## 1. 功能描述
玩家在背包中点击“召唤球”类道具（ID范围：20001-30000），通过“使用”功能开启，获得对应的幻兽。

## 2. 前端相关文件
- **文件路径**: `interfaces/client/src/features/inventory/InventoryPage.vue`
- **关键函数**: `useItem(item)`
- **说明**: 
    - 识别物品名称是否包含“召唤球”，弹出确认框。
    - 调用后端接口 `/api/inventory/use`，传递物品在背包中的唯一 ID (`id`) 和数量 (`quantity: 1`)。

## 3. 后端路由相关文件
- **文件路径**: `interfaces/routes/inventory_routes.py`
- **关键接口**: `@inventory_bp.post("/use")`
- **说明**: 
    - 接收前端请求。
    - 调用 `services.inventory_service.use_item` 执行逻辑。

- **文件路径**: `interfaces/routes/beast_routes.py`
- **关键函数**: `obtain_beast_for_user(user_id, template_id, realm, level)`
- **说明**: 
    - 被 `inventory_service` 调用（通过局部导入解决循环依赖）。
    - 调用 `services.beast_service.obtain_beast_randomly` 生成幻兽。
    - 返回生成的幻兽信息。

## 4. 后端服务逻辑文件
- **文件路径**: `application/services/inventory_service.py`
- **关键函数**: `use_item(user_id, inv_item_id, quantity)`
- **代码段说明**:
    - **识别逻辑** (约 433 行): `elif 20001 <= item_template.id < 30000: # 幻兽召唤球`
    - **名称解析**: 将“青龙召唤球”等名称中的“召唤球”后缀去掉，得到“青龙”。
    - **模板查找**: 根据名称查找对应的幻兽模板。
    - **发放逻辑**: 调用 `obtain_beast_for_user` 为玩家添加幻兽。
    - **扣除逻辑**: `_remove_item_from_slot` 扣除消耗的道具。

- **文件路径**: `application/services/beast_service.py`
- **关键函数**: `obtain_beast_randomly`
- **说明**: 处理幻兽随机属性生成、初始技能分配并保存到数据库。

## 5. 配置与实体文件
- **配置文件**: `configs/items.json`
- **说明**: 定义了召唤球道具及其 ID（如 20001、20002 等）。

- **实体类**: `domain/entities/item.py`
- **说明**: `Item` (模板) 和 `InventoryItem` (实例) 的定义。
