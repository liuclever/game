<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import UiToast from '@/components/UiToast.vue'
import UiDialog from '@/components/UiDialog.vue'
// import DebugPanel from '@/components/DebugPanel.vue'

const router = useRouter()

// 添加路由日志
router.beforeEach((to, from, next) => {
  console.log('[App] 路由导航:', from.path, '→', to.path)
  next()
})

router.afterEach((to, from) => {
  console.log('[App] 路由完成:', from.path, '→', to.path)
})
</script>

<template>
  <div class="app-container">
    <!-- 路由视图：使用 key 强制组件重新渲染 -->
    <router-view :key="$route.fullPath" />
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
</style>
