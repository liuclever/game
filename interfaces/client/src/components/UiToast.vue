<script setup>
import { uiOverlay } from '@/stores/uiOverlayStore'
</script>

<template>
  <div v-if="uiOverlay.toast.visible" class="ui-toast" :class="uiOverlay.toast.type">
    {{ uiOverlay.toast.message }}
  </div>
</template>

<style scoped>
.ui-toast {
  position: fixed;
  left: 50%;
  bottom: 24px;
  transform: translateX(-50%);
  max-width: 86vw;
  padding: 8px 12px;
  border: 1px solid #ccc;
  background: #fff;
  font-size: 16px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
  z-index: 10000;
}
.ui-toast.info {
  color: #333;
}
.ui-toast.success {
  color: #009900;
  border-color: #009900;
}
.ui-toast.error {
  color: #cc0000;
  border-color: #cc0000;
}
</style>


