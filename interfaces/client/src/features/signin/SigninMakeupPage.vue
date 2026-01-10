<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

const loading = ref(false)
const makeupInfo = ref({
  availableMakeups: 0,
  maxMakeups: 3,
  currentCards: 0,
  missedDays: [], // 本月未签到的日期
  currentMonth: '',
  currentYear: 0
})

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
  console.log('购买补签卡功能')
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
          {{ day }}日 <a class="link">补签</a>
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
</style>
