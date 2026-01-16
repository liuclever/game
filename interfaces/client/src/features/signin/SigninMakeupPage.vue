<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

const loading = ref(false)
const message = ref('') // 提示信息
const messageType = ref('') // 消息类型: success, error, info
const makeupInfo = ref({
  availableMakeups: 0,
  maxMakeups: 3,
  currentCards: 0,
  missedDays: [], // 本月未签到的日期
  currentMonth: '',
  currentYear: 0
})

// 显示消息
const showMessage = (msg, type = 'info') => {
  message.value = msg
  messageType.value = type
  // 3秒后自动清除
  setTimeout(() => {
    message.value = ''
    messageType.value = ''
  }, 3000)
}

const loadMakeupInfo = async () => {
  loading.value = true
  try {
    const res = await http.get('/signin/makeup/info')
    if (res.data.ok) {
      makeupInfo.value = res.data
    }
  } catch (e) {
    console.error('加载补签信息失败', e)
  } finally {
    loading.value = false
  }
}

const buyCard = () => {
  // 跳转到商城购买补签卡（商品ID: 127）
  router.push('/shop/item/127')
}

const doMakeup = async (day) => {
  if (makeupInfo.value.currentCards < 1) {
    // 补签卡不足，显示提示
    showMessage('补签卡不足，请前往商城购买', 'error')
    return
  }
  
  loading.value = true
  try {
    const res = await http.post('/signin/makeup', { day })
    if (res.data.ok) {
      showMessage(res.data.message || '补签成功！', 'success')
      // 刷新补签信息
      await loadMakeupInfo()
    } else {
      const errorMsg = res.data.error || '补签失败'
      showMessage(errorMsg, 'error')
    }
  } catch (e) {
    console.error('补签失败', e)
    const errorMsg = e?.response?.data?.error || e?.message || '补签失败'
    showMessage('补签失败：' + errorMsg, 'error')
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/signin')
}

const goHome = () => {
  router.push('/')
}

onMounted(() => {
  loadMakeupInfo()
})
</script>

<template>
  <div class="makeup-page">
    <div class="section" v-if="loading">加载中...</div>
    
    <!-- 消息提示 -->
    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>
    
    <template v-else>
      <!-- 补签信息 -->
      <div class="section">
        您可以补签{{ makeupInfo.availableMakeups }}/{{ makeupInfo.maxMakeups }}次 
        当前补签卡{{ makeupInfo.currentCards }}个 
        <a class="link" @click="buyCard">购买</a>
      </div>
      
      <!-- 提示信息 -->
      <div class="section">
        英雄，您下面几天没来哦
      </div>
      
      <!-- 当前月份 -->
      <div class="section">
        {{ makeupInfo.currentYear }}年{{ makeupInfo.currentMonth }}月
      </div>
      
      <!-- 未签到日期列表 -->
      <div class="section" v-if="makeupInfo.missedDays && makeupInfo.missedDays.length > 0">
        <div v-for="day in makeupInfo.missedDays" :key="day" class="missed-day">
          {{ day }}日 <a class="link" @click="doMakeup(day)">补签</a>
        </div>
      </div>
      <div class="section" v-else>
        本月没有需要补签的日期
      </div>
    </template>
    
    <!-- 返回链接 -->
    <div class="section">
      <a class="link" @click="goBack">返回签到首页</a>
    </div>
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.makeup-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 13px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 8px 0;
}

.missed-day {
  margin: 4px 0;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

/* 消息提示样式 */
.message {
  padding: 12px;
  margin: 12px 0;
  border-radius: 4px;
  font-weight: bold;
  text-align: center;
}

.message.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.message.info {
  background: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}
</style>
