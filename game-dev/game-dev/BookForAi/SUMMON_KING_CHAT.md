# 召唤之王聊天功能实现说明

## 功能概述

召唤之王聊天功能允许召唤之王挑战赛的冠军发布置顶消息，这些消息会显示在聊天列表的最顶部，且只保留最新的一条。

## 实现逻辑

### 1. 权限验证

**数据库字段：**
- `player.is_summon_king` (TINYINT): 标识玩家是否是召唤之王（1=是，0=否）

**验证逻辑：**
```python
def _is_summon_king(self, user_id: int) -> bool:
    """检查玩家是否是召唤之王"""
    rows = execute_query(
        "SELECT is_summon_king FROM player WHERE user_id = %s",
        (user_id,)
    )
    if rows:
        return bool(rows[0].get('is_summon_king', 0))
    return False
```

**权限检查：**
- 发送置顶消息时，必须验证 `is_summon_king = 1`
- 非召唤之王尝试发送置顶消息会返回错误："只有召唤之王才能发布置顶消息"

### 2. 置顶消息逻辑

**核心规则：只保留最新一条置顶消息**

**实现方式：**
```python
# 发送新的置顶消息前，先取消所有之前的置顶
if message_type == 'summon_king':
    execute_update(
        "UPDATE world_chat_message SET is_pinned = 0 WHERE is_pinned = 1",
        ()
    )

# 插入新消息，标记为置顶
message_id = execute_insert(
    """INSERT INTO world_chat_message 
       (user_id, nickname, message_type, content, is_pinned) 
       VALUES (%s, %s, %s, %s, %s)""",
    (user_id, player.nickname, message_type, content.strip(), 1)
)
```

**数据库字段：**
- `world_chat_message.is_pinned` (TINYINT): 是否置顶（1=置顶，0=普通）

### 3. 消息类型

**两种消息类型：**

1. **普通消息 (`normal`)**
   - 消耗1个小喇叭（物品ID: 6012）
   - 最多35个字符
   - 不置顶
   - 所有玩家都可以发送

2. **召唤之王置顶消息 (`summon_king`)**
   - 不消耗小喇叭
   - 最多35个字符
   - 自动置顶
   - 只有召唤之王可以发送

### 4. 前端显示逻辑

**首页显示（ChatPanel.vue）：**
- 显示1条置顶消息（如果有）
- 显示最多3条普通喊话消息
- 不显示联盟和系统消息

**世界聊天页面（WorldChatPage.vue）：**
- 置顶消息单独显示在最顶部（带特殊样式）
- 普通消息列表（分页，每页10条）
- 召唤之王按钮（仅召唤之王可见）

### 5. API接口

**后端接口：**

1. `POST /api/world-chat/send`
   - 发送消息（普通/召唤之王）
   - 参数：`content`, `message_type` ('normal' 或 'summon_king')

2. `GET /api/world-chat/messages`
   - 获取消息列表（分页）
   - 排除置顶消息（置顶消息单独获取）

3. `GET /api/world-chat/pinned`
   - 获取当前置顶消息（只有一条）

4. `GET /api/world-chat/homepage`
   - 获取首页消息（3条普通喊话）

5. `GET /api/world-chat/is-summon-king`
   - 检查当前玩家是否是召唤之王

## 测试结果

### 测试场景

1. ✅ **设置召唤之王**：成功设置用户为召唤之王
2. ✅ **发送普通消息**：成功发送，正确消耗小喇叭
3. ✅ **发送第一条置顶消息**：成功发送并置顶
4. ✅ **发送第二条置顶消息**：成功替换第一条，只保留最新一条
5. ✅ **非召唤之王无法发送**：正确阻止非召唤之王发送置顶消息
6. ✅ **验证只有一条置顶**：数据库中只有1条置顶消息
7. ✅ **显示所有消息**：置顶消息正确显示在最顶部

### 测试数据

- **test1 (user_id=1)**：已设置为召唤之王，可以发送置顶消息
- **test2 (user_id=2)**：普通用户，只能发送普通消息

## 使用说明

### 设置召唤之王

```sql
UPDATE player SET is_summon_king = 1 WHERE user_id = 1;
```

### 发送置顶消息

1. 确保玩家 `is_summon_king = 1`
2. 在世界聊天页面点击【召唤之王】按钮
3. 输入消息内容（最多35字）
4. 点击发送

### 查看置顶消息

- 首页：在聊天面板顶部显示
- 世界聊天页面：单独显示在最顶部，带特殊样式

## 注意事项

1. **置顶消息替换**：每次发送新的置顶消息，会自动取消之前的置顶
2. **权限验证**：前端和后端都会验证召唤之王身份
3. **消息长度**：所有消息限制在35个字符以内
4. **小喇叭消耗**：只有普通消息消耗小喇叭，置顶消息不消耗
