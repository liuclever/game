/**
 * Toast提示 composable
 */
import { ref } from 'vue'

const toasts = ref([])
let toastIdCounter = 0

const ToastType = {
  SUCCESS: 'success',
  ERROR: 'error',
  INFO: 'info',
  WARNING: 'warning',
}

const addToast = (message, type = ToastType.INFO, duration = 3000) => {
  const id = ++toastIdCounter
  const toast = { id, message, type, duration, visible: true }
  
  if (!Array.isArray(toasts.value)) toasts.value = []
  toasts.value.push(toast)
  
  if (duration > 0) {
    setTimeout(() => removeToast(id), duration)
  }
  return id
}

const removeToast = (id) => {
  const index = toasts.value.findIndex(t => t.id === id)
  if (index > -1) toasts.value.splice(index, 1)
}

const clearAll = () => { toasts.value = [] }

export const useToast = () => {
  return {
    toasts: toasts,
    toast: {
      success: (message, duration) => addToast(message, ToastType.SUCCESS, duration),
      error: (message, duration) => addToast(message, ToastType.ERROR, duration || 4000),
      info: (message, duration) => addToast(message, ToastType.INFO, duration),
      warning: (message, duration) => addToast(message, ToastType.WARNING, duration),
    },
    success: (message, duration) => addToast(message, ToastType.SUCCESS, duration),
    error: (message, duration) => addToast(message, ToastType.ERROR, duration || 4000),
    info: (message, duration) => addToast(message, ToastType.INFO, duration),
    warning: (message, duration) => addToast(message, ToastType.WARNING, duration),
    remove: removeToast,
    clear: clearAll,
  }
}

export { ToastType }
