import { createApp } from 'vue'
import '@/style.css'
import App from './App.vue'
import router from './router'
import { useToast } from './composables/useToast'

const app = createApp(App).use(router)

// 在开发环境下，将 toast 挂载到 window 对象，方便在控制台测试
if (import.meta.env.DEV) {
  app.config.globalProperties.$toast = useToast().toast
  // 也挂载到 window
  window.testToast = () => {
    const { toast } = useToast()
    console.log('测试 Toast...')
    toast.success('成功提示测试')
    setTimeout(() => toast.error('错误提示测试'), 500)
    setTimeout(() => toast.info('信息提示测试'), 1000)
    setTimeout(() => toast.warning('警告提示测试'), 1500)
  }
  console.log('💡 提示：在控制台输入 testToast() 可以测试 Toast 功能')
}

app.mount('#app')
