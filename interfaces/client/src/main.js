import { createApp } from 'vue'
import '@/style.css'
import App from './App.vue'
import router from './router'
import { uiAlert } from '@/stores/uiOverlayStore'

// 禁用浏览器系统 alert 弹框：统一走页面内提示
window.alert = (msg) => uiAlert(String(msg ?? ''), 'info')

createApp(App).use(router).mount('#app')
