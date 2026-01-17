<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import UiToast from '@/components/UiToast.vue'
import UiDialog from '@/components/UiDialog.vue'
// import DebugPanel from '@/components/DebugPanel.vue'

const router = useRouter()
const isNavigating = ref(false)

// 监听路由变化，显示加载状态
router.beforeEach(() => {
  isNavigating.value = true
})

router.afterEach(() => {
  // 延迟隐藏加载状态，确保页面已渲染
  setTimeout(() => {
    isNavigating.value = false
  }, 50)
})
</script>

<template>
  <div class="app-container">
    <!-- 路由过渡动画 -->
    <transition name="fade" mode="out-in">
      <router-view v-if="!isNavigating" />
      <div v-else class="loading-overlay">
        <div class="loading-text">加载中...</div>
      </div>
    </transition>
    <UiToast />
    <UiDialog />
    <!-- <DebugPanel /> -->
  </div>
</template>

<style>
/* 全局重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: SimSun, "宋体", serif;
  background-color: #ffffff !important; /* 确保背景为白色 */
}

/* 路由过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 加载覆盖层 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  z-index: 9999;
}

.loading-text {
  font-size: 17px;
  color: #666;
}
</style>
