/**
 * Toast提示 composable
 * 提供统一的错误、成功、信息提示功能
 */
import { ref } from 'vue'

// Toast消息队列（全局共享）
const toasts = ref([])
let toastIdCounter = 0

// 确保 toasts 是响应式的，并且可以被所有组件访问

/**
 * Toast消息类型
 */
const ToastType = {
  SUCCESS: 'success',
  ERROR: 'error',
  INFO: 'info',
  WARNING: 'warning',
}

/**
 * 添加Toast消息
 * @param {string} message - 消息内容
 * @param {string} type - 消息类型 (success/error/info/warning)
 * @param {number} duration - 显示时长（毫秒），默认3000
 */
const addToast = (message, type = ToastType.INFO, duration = 3000) => {
  console.log('[useToast] addToast called:', { message, type, duration })
  
  const id = ++toastIdCounter
  const toast = {
    id,
    message,
    type,
    duration,
    visible: true,
  }
  
  // 确保 toasts.value 是数组
  if (!Array.isArray(toasts.value)) {
    console.warn('[useToast] toasts.value is not an array, resetting...')
    toasts.value = []
  }
  
  toasts.value.push(toast)
  console.log('[useToast] Toast added, current toasts:', toasts.value)
  console.log('[useToast] Toasts length:', toasts.value.length)
  
  // 自动移除
  if (duration > 0) {
    setTimeout(() => {
      removeToast(id)
    }, duration)
  }
  
  return id
}

/**
 * 移除Toast消息
 * @param {number} id - Toast ID
 */
const removeToast = (id) => {
  console.log('[useToast] removeToast called:', id)
  const index = toasts.value.findIndex(t => t.id === id)
  if (index > -1) {
    toasts.value.splice(index, 1)
    console.log('[useToast] Toast removed, remaining toasts:', toasts.value.length)
  } else {
    console.warn('[useToast] Toast not found:', id)
  }
}

/**
 * 清空所有Toast
 */
const clearAll = () => {
  toasts.value = []
}

/**
 * useToast composable
 */
export const useToast = () => {
  return {
    // Toast消息列表（只读）
    toasts: toasts,
    
    // 成功提示
    success: (message, duration) => addToast(message, ToastType.SUCCESS, duration),
    
    // 错误提示
    error: (message, duration) => addToast(message, ToastType.ERROR, duration || 4000),
    
    // 信息提示
    info: (message, duration) => addToast(message, ToastType.INFO, duration),
    
    // 警告提示
    warning: (message, duration) => addToast(message, ToastType.WARNING, duration),
    
    // 移除指定Toast
    remove: removeToast,
    
    // 清空所有Toast
    clear: clearAll,
  }
}

// 导出Toast类型（供组件使用）
export { ToastType }
