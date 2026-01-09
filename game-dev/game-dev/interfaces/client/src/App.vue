<script setup>
// import DebugPanel from '@/components/DebugPanel.vue'
import ToastContainer from '@/components/ToastContainer.vue'
</script>

<template>
  <div id="app-wrapper">
    <router-view />
    <ToastContainer />
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
}
</style>
