# 副本挑战返回首页白屏Bug修复说明

## 修改时间
2026年1月17日

## 问题描述
点击副本挑战，再点击界面最下方的"返回游戏首页"，页面显示白屏，必须刷新一次页面才有数据。

## 问题分析

### 根本原因
MainPage组件只在 `onMounted` 钩子中加载数据，但是当使用Vue Router从其他页面返回时：
1. 如果组件被缓存（keep-alive），`onMounted` 不会再次触发
2. 组件虽然显示了，但数据没有重新加载
3. 导致页面显示为空白（白屏）

### 原有代码问题
```javascript
// MainPage.vue
onMounted(() => {
  checkAuth()
  loadAllianceTop3()
  loadAnnouncements()
})
```

**问题**：
- 只在组件首次挂载时加载数据
- 从其他页面返回时不会重新加载
- 导致页面显示空白

## 修复方案

### 文件1：`interfaces/client/src/features/main/MainPage.vue`

#### 修改1：导入onActivated钩子

**修改位置**：第2行

**修改前**：
```javascript
import { ref, onMounted, onUnmounted, computed } from 'vue'
```

**修改后**：
```javascript
import { ref, onMounted, onUnmounted, onActivated, computed } from 'vue'
```

#### 修改2：添加onActivated钩子

**修改位置**：第467-477行

**修改前**：
```javascript
onMounted(() => {
  checkAuth()
  loadAllianceTop3()
  loadAnnouncements()
})

onUnmounted(() => {
  if (countdownTimer) clearInterval(countdownTimer)
  if (moveTimer) clearInterval(moveTimer)
})
```

**修改后**：
```javascript
onMounted(() => {
  checkAuth()
  loadAllianceTop3()
  loadAnnouncements()
})

onActivated(() => {
  // 当页面被激活时（从其他页面返回），重新加载数据
  checkAuth()
  loadAllianceTop3()
  loadAnnouncements()
})

onUnmounted(() => {
  if (countdownTimer) clearInterval(countdownTimer)
  if (moveTimer) clearInterval(moveTimer)
})
```

### 文件2：`interfaces/client/src/features/dungeon/DungeonChallengePage.vue`

**修改位置**：`goBack()` 函数

**修改说明**：恢复为简单的路由跳转，因为问题不在这里

```javascript
const goBack = () => {
  router.push('/')
}
```

## 技术细节

### Vue生命周期钩子

#### onMounted
- **触发时机**：组件首次挂载到DOM后
- **特点**：只触发一次
- **问题**：如果组件被缓存，返回时不会再次触发

#### onActivated
- **触发时机**：组件被激活时（包括首次激活和从缓存中恢复）
- **特点**：每次组件显示时都会触发
- **用途**：适合在keep-alive缓存的组件中重新加载数据

### Keep-Alive缓存

Vue Router可能会缓存组件以提高性能：
- 缓存的组件不会被销毁和重新创建
- `onMounted` 和 `onUnmounted` 不会重复触发
- 需要使用 `onActivated` 和 `onDeactivated` 来处理激活/停用逻辑

## 修复效果

**修复前**：
1. 用户进入副本挑战页面
2. 点击"返回游戏首页"
3. 页面显示白屏（组件已渲染但数据未加载）
4. 必须手动刷新页面才能看到数据

**修复后**：
1. 用户进入副本挑战页面
2. 点击"返回游戏首页"
3. `onActivated` 钩子触发
4. 自动重新加载数据（checkAuth、loadAllianceTop3、loadAnnouncements）
5. 页面正常显示，无需刷新

## 影响范围

- 修复了从任何页面返回主页时的白屏问题
- 确保主页数据始终是最新的
- 不影响其他页面的功能
- 提升了用户体验

## 其他可能受益的场景

这个修复也会改善以下场景：
1. 从幻兽详情返回主页
2. 从背包返回主页
3. 从任务页面返回主页
4. 从任何子页面返回主页

所有这些场景现在都会自动重新加载主页数据。

## 总结

通过添加 `onActivated` 钩子，确保MainPage组件在每次被激活时都会重新加载数据，彻底解决了返回主页时的白屏问题。这是Vue组件缓存场景下的标准解决方案。
