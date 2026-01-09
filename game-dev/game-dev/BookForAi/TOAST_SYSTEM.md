# Toast提示系统改造文档

## 概述
将项目中所有使用浏览器原生 `alert()` 弹窗的地方替换为统一的 Toast 提示系统，提升用户体验。

## 实现内容

### 1. Toast组件系统

#### 1.1 useToast Composable
**文件**: `interfaces/client/src/composables/useToast.js`

提供统一的提示接口：
- `toast.success(message, duration)` - 成功提示（绿色）
- `toast.error(message, duration)` - 错误提示（红色）
- `toast.info(message, duration)` - 信息提示（蓝色）
- `toast.warning(message, duration)` - 警告提示（黄色）

#### 1.2 ToastContainer组件
**文件**: `interfaces/client/src/components/ToastContainer.vue`

- 显示在页面右上角
- 支持多个Toast同时显示
- 自动消失（默认3秒，错误提示4秒）
- 可点击关闭
- 平滑的动画效果

#### 1.3 全局注册
**文件**: `interfaces/client/src/App.vue`

在App.vue中引入并注册ToastContainer组件，使其全局可用。

### 2. 替换规则

#### 2.1 错误提示
- `alert('错误信息')` → `toast.error('错误信息')`
- `alert(res.data.error)` → `toast.error(res.data.error)`

#### 2.2 成功提示
- `alert('成功信息')` → `toast.success('成功信息')`
- `alert(res.data.message)` (在res.data.ok为true时) → `toast.success(res.data.message)`

#### 2.3 信息提示
- `alert('功能待实现')` → `toast.info('功能待实现')`
- `alert('提示信息')` → `toast.info('提示信息')`

### 3. 已替换的文件

已批量替换了以下文件中的所有alert调用：
- 商城相关页面
- 玩家详情页面
- 私信聊天页面
- 世界聊天页面
- 动态页面
- 好友页面
- 任务奖励页面
- 活动礼包页面
- 主页面
- 赞助页面
- 庄园页面
- 地图页面
- 炼妖页面
- 塔防页面
- 镇妖页面
- 其他功能页面

**总计**: 31个文件已替换

### 4. Toast样式

#### 4.1 成功提示（绿色）
- 左侧边框：绿色 (#52c41a)
- 背景：浅绿色 (#f6ffed)
- 图标：✓

#### 4.2 错误提示（红色）
- 左侧边框：红色 (#ff4d4f)
- 背景：浅红色 (#fff2f0)
- 图标：✗
- 显示时长：4秒（比成功提示长）

#### 4.3 信息提示（蓝色）
- 左侧边框：蓝色 (#1890ff)
- 背景：浅蓝色 (#e6f7ff)
- 图标：ℹ

#### 4.4 警告提示（黄色）
- 左侧边框：黄色 (#faad14)
- 背景：浅黄色 (#fffbe6)
- 图标：⚠

### 5. 使用示例

```javascript
import { useToast } from '@/composables/useToast'
const { toast } = useToast()

// 成功提示
toast.success('购买成功！')

// 错误提示
toast.error('元宝不足')

// 信息提示
toast.info('功能待实现')

// 警告提示
toast.warning('请注意')
```

### 6. 优势

1. **非阻塞式**: Toast提示不会阻塞用户操作
2. **统一风格**: 所有提示使用统一的样式和动画
3. **更好的UX**: 用户可以继续操作，无需点击确认
4. **类型区分**: 通过颜色和图标快速识别提示类型
5. **自动消失**: 无需手动关闭，减少操作步骤

### 7. 注意事项

1. **成功消息**: 在 `res.data.ok === true` 时使用 `toast.success()`
2. **错误消息**: 在操作失败时使用 `toast.error()`
3. **信息提示**: 用于功能待实现、提示信息等场景使用 `toast.info()`
4. **显示时长**: 
   - 成功/信息/警告：默认3秒
   - 错误：默认4秒
   - 可通过第二个参数自定义

### 8. 测试建议

1. 测试各种操作的成功/失败提示
2. 测试多个Toast同时显示
3. 测试Toast自动消失
4. 测试点击关闭功能
5. 测试不同屏幕尺寸下的显示效果

## 修复的文件清单

- `interfaces/client/src/composables/useToast.js` - 新建
- `interfaces/client/src/components/ToastContainer.vue` - 新建
- `interfaces/client/src/App.vue` - 添加ToastContainer
- 31个功能页面文件 - 替换alert为toast

## 总结

所有弹窗提示已统一改为Toast提示系统，提升了用户体验，使界面更加现代化和友好。
