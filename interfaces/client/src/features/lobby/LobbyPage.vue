<script setup>
import WelcomePanel from './components/WelcomePanel.vue'
import CommonActionsPanel from './components/CommonActionsPanel.vue'
import TrainingPanel from './components/TrainingPanel.vue'
import DungeonPanel from './components/DungeonPanel.vue'
import TownPanel from './components/TownPanel.vue'
import PlayerInfoPanel from './components/PlayerInfoPanel.vue'
import ChatPanel from './components/ChatPanel.vue'
</script>

<template>
  <div class="lobby">
    <!-- 顶部欢迎 + 每日必做 -->
    <WelcomePanel />

    <div class="columns">
      <!-- 左列：常用功能 + 修行 + 活动 + 庄园 + 能力 + 进阶 -->
      <div class="left-col">
        <CommonActionsPanel />
        <TrainingPanel />
        <DungeonPanel />
        <TownPanel />
      </div>

      <!-- 右列：个人信息 + 聊天 -->
      <div class="right-col">
        <PlayerInfoPanel />
        <ChatPanel />
      </div>
    </div>
  </div>
</template>

<style scoped>
.lobby {
  font-size: 12px;
}

/* 中间区域：左固定宽度，右自适应 */
.columns {
  margin-top: 8px;
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 12px;
}

.left-col,
.right-col {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
</style>
