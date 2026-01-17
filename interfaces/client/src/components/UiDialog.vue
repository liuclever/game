<script setup>
import { computed } from 'vue'
import { uiOverlay, closeDialog } from '@/stores/uiOverlayStore'

const isPrompt = computed(() => uiOverlay.dialog.mode === 'prompt')

const onOk = () => {
  if (isPrompt.value) {
    closeDialog(uiOverlay.dialog.input)
  } else {
    closeDialog(true)
  }
}

const onCancel = () => {
  if (isPrompt.value) {
    closeDialog(null)
  } else {
    closeDialog(false)
  }
}
</script>

<template>
  <div v-if="uiOverlay.dialog.visible" class="ui-dialog-mask">
    <div class="ui-dialog">
      <div class="msg">{{ uiOverlay.dialog.message }}</div>

      <input
        v-if="isPrompt"
        class="input"
        v-model="uiOverlay.dialog.input"
        :placeholder="uiOverlay.dialog.placeholder"
      />

      <div class="actions">
        <button class="btn btn-ok" @click="onOk">{{ uiOverlay.dialog.okText }}</button>
        <button class="btn" @click="onCancel">{{ uiOverlay.dialog.cancelText }}</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ui-dialog-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.35);
  z-index: 10001;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}
.ui-dialog {
  width: min(520px, 92vw);
  background: #fff;
  border: 1px solid #ccc;
  padding: 12px;
  font-family: SimSun, "宋体", serif;
  font-size: 16px;
  line-height: 1.6;
}
.msg {
  margin-bottom: 10px;
  white-space: pre-wrap;
  word-break: break-word;
}
.input {
  width: 100%;
  padding: 6px 8px;
  font-size: 16px;
  border: 1px solid #ccc;
}
.actions {
  margin-top: 12px;
  display: flex;
  gap: 8px;
}
.btn {
  padding: 4px 16px;
  font-size: 16px;
  cursor: pointer;
  border: 1px solid #ccc;
  background: #fff;
}
.btn-ok {
  border-color: #0066cc;
  background: #0066cc;
  color: #fff;
}
</style>


