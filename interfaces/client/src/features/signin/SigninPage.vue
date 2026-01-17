<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'
import MainMenuLinks from '@/features/main/components/MainMenuLinks.vue'

const router = useRouter()

const loading = ref(false)
const signinInfo = ref({
  hasSigned: false,
  consecutiveDays: 0,
  currentMonth: '',
  currentYear: 0,
  signinDays: [] // 本月已签到的日期
})

const rewardStatus = ref({
  7: { claimed: false, canClaim: false },
  15: { claimed: false, canClaim: false },
  30: { claimed: false, canClaim: false }
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
      
      // 加载各个奖励的状态
      await loadRewardStatus()
    }
  } catch (e) {
    console.error('加载签到信息失败', e)
  } finally {
    loading.value = false
  }
}

const loadRewardStatus = async () => {
  for (const days of [7, 15, 30]) {
    try {
      const res = await http.get(`/signin/reward/${days}`)
      console.log(`${days}天奖励状态:`, res.data)
      if (res.data.ok) {
        rewardStatus.value[days] = {
          claimed: res.data.claimed || false,
          canClaim: res.data.canClaim || false
        }
      }
    } catch (e) {
      console.error(`加载${days}天奖励状态失败`, e)
    }
  }
  console.log('最终奖励状态:', rewardStatus.value)
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
        <span v-if="rewardStatus[7].claimed">已领取</span>
        <span v-else-if="rewardStatus[7].canClaim">可领取</span>
        <span v-else>未满足</span>
      </div>
      
      <div class="section">
        <a class="link" @click="goReward(15)">15天礼包</a>. 
        <span v-if="rewardStatus[15].claimed">已领取</span>
        <span v-else-if="rewardStatus[15].canClaim">可领取</span>
        <span v-else>未满足</span>
      </div>
      
      <div class="section">
        <a class="link" @click="goReward(30)">30天礼包</a>. 
        <span v-if="rewardStatus[30].claimed">已领取</span>
        <span v-else-if="rewardStatus[30].canClaim">可领取</span>
        <span v-else>未满足</span>
      </div>
      
      <!-- 签到按钮 -->
      <div class="section" v-if="!signinInfo.hasSigned">
        <a class="link" @click="doSignin">点击签到</a>
      </div>
    </template>
    
<<<<<<< HEAD
=======
    <!-- 主页菜单（严格复刻主页内容与UI） -->
    <MainMenuLinks />

>>>>>>> new/daily-book
    <!-- 返回链接 -->
    <div class="section">
      <a class="link" @click="goBack">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.signin-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 18px;
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
