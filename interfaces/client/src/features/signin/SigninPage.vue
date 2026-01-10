<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

const loading = ref(false)
const signinInfo = ref({
  hasSigned: false,
  consecutiveDays: 0,
  currentMonth: '',
  currentYear: 0,
  signinDays: [] // 本月已签到的日期
})

const loadSigninInfo = async () => {
  loading.value = true
  try {
    const res = await http.get('/signin/info')
    if (res.data.ok) {
      // 只提取需要的字段
      signinInfo.value = {
        hasSigned: res.data.hasSigned || false,
        consecutiveDays: res.data.consecutiveDays || 0,
        currentMonth: res.data.currentMonth || '',
        currentYear: res.data.currentYear || 0,
        signinDays: res.data.signinDays || []
      }
    }
  } catch (e) {
    console.error('加载签到信息失败', e)
  } finally {
    loading.value = false
  }
}

const doSignin = async () => {
  if (signinInfo.value.hasSigned) {
    console.log('今天已经签到过了')
    return
  }
  
  loading.value = true
  try {
    const res = await http.post('/signin')
    if (res.data.ok) {
      console.log(res.data.message)
      loadSigninInfo()
    } else {
      console.error(res.data.error || '签到失败')
    }
  } catch (e) {
    console.error('签到失败', e)
    const errorMsg = e?.response?.data?.error || e?.message || '签到失败'
    console.error('签到失败：' + errorMsg)
  } finally {
    loading.value = false
  }
}

const goMakeup = () => {
  router.push('/signin/makeup')
}

const goReward = (days) => {
  router.push(`/signin/reward?days=${days}`)
}

const goBack = () => {
  router.push('/')
}

onMounted(() => {
  loadSigninInfo()
})
</script>

<template>
  <div class="signin-page">
    <div class="section" v-if="loading">加载中...</div>
    
    <template v-else>
      <!-- 签到状态 -->
      <div class="section">
        {{ signinInfo.currentYear }}年{{ signinInfo.currentMonth }}月{{ new Date().getDate() }}日 
        <span v-if="signinInfo.hasSigned">已签到</span>
        <span v-else>未签到</span>
      </div>
      
      <!-- 累积签到信息 -->
      <div class="section">
        本月累积签到{{ signinInfo.signinDays?.length || 0 }}天 
        <a class="link" @click="goMakeup">补签</a>
      </div>
      
      <!-- 礼包信息 -->
      <div class="section">
        <a class="link" @click="goReward(7)">7天礼包</a>. 
        <span v-if="signinInfo.consecutiveDays >= 7">已领取</span>
        <span v-else>未满足</span>
      </div>
      
      <div class="section">
        <a class="link" @click="goReward(15)">15天礼包</a>. 
        <span v-if="signinInfo.consecutiveDays >= 15">已领取</span>
        <span v-else>未满足</span>
      </div>
      
      <div class="section">
        <a class="link" @click="goReward(30)">30天礼包</a>. 
        <span v-if="signinInfo.consecutiveDays >= 30">已领取</span>
        <span v-else>未满足</span>
      </div>
      
      <!-- 签到按钮 -->
      <div class="section" v-if="!signinInfo.hasSigned">
        <a class="link" @click="doSignin">点击签到</a>
      </div>
    </template>
    
    <!-- 返回链接 -->
    <div class="section">
      <a class="link" @click="goBack">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.signin-page {
  background: #FFF8DC;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 13px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 8px 0;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}
</style>
