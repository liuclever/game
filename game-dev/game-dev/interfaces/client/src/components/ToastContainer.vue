<template>
  <!-- 使用 v-show 而不是 v-if，确保元素始终在 DOM 中 -->
  <div class="game-toast-container" v-show="toasts.length > 0" ref="containerRef">
    <TransitionGroup name="toast" tag="div">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        :class="['game-toast', `game-toast-${toast.type}`]"
        :style="getToastStyle(toast.type)"
        @click="removeToast(toast.id)"
        ref="toastRefs"
      >
        <span class="game-toast-icon" :style="getIconStyle(toast.type)">{{ getIcon(toast.type) }}</span>
        <span class="game-toast-message">{{ toast.message }}</span>
        <span class="game-toast-close" @click.stop="removeToast(toast.id)">×</span>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { watch, onMounted, computed, ref, nextTick } from 'vue'
import { useToast } from '@/composables/useToast'

const { toasts: toastsRef, remove: removeToast } = useToast()
const containerRef = ref(null)
const toastRefs = ref([])

// 使用 computed 确保响应式
const toasts = computed(() => {
  const value = toastsRef.value || []
  return value
})

// 调试信息
watch(toastsRef, async (newToasts) => {
  console.log('[ToastContainer] Toasts changed:', newToasts)
  console.log('[ToastContainer] Toasts length:', newToasts?.length || 0)
  
  // 等待 DOM 更新后检查
  await nextTick()
  if (containerRef.value) {
    const toastElements = containerRef.value.querySelectorAll('.game-toast')
    console.log('[ToastContainer] DOM 中的 Toast 元素数量:', toastElements.length)
    if (toastElements.length > 0) {
      const firstToast = toastElements[0]
      const styles = window.getComputedStyle(firstToast)
      console.log('[ToastContainer] Toast 样式检查:')
      console.log('  - display:', styles.display)
      console.log('  - visibility:', styles.visibility)
      console.log('  - opacity:', styles.opacity)
      console.log('  - position:', styles.position)
      console.log('  - z-index:', styles.zIndex)
    }
  }
}, { deep: true, immediate: true })

onMounted(() => {
  console.log('[ToastContainer] Component mounted')
  console.log('[ToastContainer] Container element:', containerRef.value)
})

const getIcon = (type) => {
  const icons = {
    success: '✓',
    error: '✗',
    info: 'ℹ',
    warning: '⚠',
  }
  return icons[type] || 'ℹ'
}

const getToastStyle = (type) => {
  const styles = {
    success: {
      borderLeftColor: '#52c41a',
      backgroundColor: '#f6ffed',
    },
    error: {
      borderLeftColor: '#ff4d4f',
      backgroundColor: '#fff2f0',
    },
    info: {
      borderLeftColor: '#1890ff',
      backgroundColor: '#e6f7ff',
    },
    warning: {
      borderLeftColor: '#faad14',
      backgroundColor: '#fffbe6',
    },
  }
  return {
    borderLeft: `4px solid ${styles[type]?.borderLeftColor || '#999'}`,
    backgroundColor: styles[type]?.backgroundColor || '#fff',
  }
}

const getIconStyle = (type) => {
  const colors = {
    success: '#52c41a',
    error: '#ff4d4f',
    info: '#1890ff',
    warning: '#faad14',
  }
  return {
    color: colors[type] || '#999',
  }
}
</script>

<style>
/* 全局样式 - 确保优先级最高 */
.game-toast-container {
  position: fixed !important;
  top: 20px !important;
  right: 20px !important;
  z-index: 999999 !important;
  pointer-events: none !important;
  max-width: calc(100vw - 40px) !important;
  display: block !important;
  visibility: visible !important;
}

.game-toast {
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  min-width: 280px !important;
  max-width: 400px !important;
  padding: 12px 16px !important;
  margin-bottom: 12px !important;
  background: #fff !important;
  border-radius: 6px !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
  pointer-events: auto !important;
  cursor: pointer !important;
  font-size: 14px !important;
  line-height: 1.5 !important;
  border-left: 4px solid #999 !important;
  animation: game-toast-slideIn 0.3s ease-out !important;
  opacity: 1 !important;
  visibility: visible !important;
  transform: translateX(0) !important;
}

.game-toast-icon {
  font-size: 18px !important;
  font-weight: bold !important;
  flex-shrink: 0 !important;
  display: inline-block !important;
}

.game-toast-message {
  flex: 1 !important;
  color: #333 !important;
  word-break: break-word !important;
  display: block !important;
}

.game-toast-close {
  font-size: 20px !important;
  color: #999 !important;
  cursor: pointer !important;
  flex-shrink: 0 !important;
  line-height: 1 !important;
  padding: 0 4px !important;
  transition: color 0.2s !important;
  display: inline-block !important;
}

.game-toast-close:hover {
  color: #333 !important;
}

@keyframes game-toast-slideIn {
  from {
    transform: translateX(100%) !important;
    opacity: 0 !important;
  }
  to {
    transform: translateX(0) !important;
    opacity: 1 !important;
  }
}

.toast-enter-active {
  transition: all 0.3s ease-out !important;
}

.toast-leave-active {
  transition: all 0.3s ease-in !important;
}

.toast-enter-from {
  transform: translateX(100%) !important;
  opacity: 0 !important;
}

.toast-leave-to {
  transform: translateX(100%) !important;
  opacity: 0 !important;
}
</style>
