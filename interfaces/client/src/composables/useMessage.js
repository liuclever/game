// 通用消息提示组合式函数
import { ref } from 'vue'

export function useMessage() {
  const message = ref('')
  const messageType = ref('') // success, error, info

  const showMessage = (msg, type = 'info') => {
    message.value = msg
    messageType.value = type
    // 3秒后自动清除
    setTimeout(() => {
      message.value = ''
      messageType.value = ''
    }, 3000)
  }

  return {
    message,
    messageType,
    showMessage
  }
}
