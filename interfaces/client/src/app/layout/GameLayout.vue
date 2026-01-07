<script setup>
import TopAnnouncementBar from './TopAnnouncementBar.vue'
import BottomNavBar from './BottomNavBar.vue'
</script>

<template>
  <div class="game-layout">
    <!-- 顶部黄色公告条 -->
    <TopAnnouncementBar />

    <!-- 中间内容区域：放具体页面 -->
    <div class="main-container">
      <slot />
    </div>

    <!-- 底部导航条 -->
    <BottomNavBar />
  </div>
</template>

<style scoped>
.game-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #ffffff;
}

/* 中间内容：宽度限制 & 上下留点空 */
.main-container {
  flex: 1;
  max-width: 1200px;
  margin: 8px auto 12px;
}
</style>
