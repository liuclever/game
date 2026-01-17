<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

// 当前战场类型
const currentType = ref('tiger')  // tiger=猛虎战场, crane=飞鹤战场

// 战场信息
const battlefieldInfo = ref({
  period: 0,
  levelRange: '20-39',
  signUpTime: '6点-20点',
  redCount: 0,
  blueCount: 0,
})

// 报名状态
const isSignedUp = ref(false)
const signupLoading = ref(false)

// 上期战绩
const lastResult = ref({
  period: 0,
  tigerKing: { name: '', team: '', kills: 0 },
  craneKing: { name: '', team: '', kills: 0 },
  kingReward: '战王宝藏',
})

// 我的战绩
const myResult = ref({
  period: 0,
  team: '',
  won: false,
  kills: 0,
  campReward: '',
  killReward: '',
})

// 当前登录玩家昵称 & 杀敌数（按胜场统计）
const meNickname = ref('')
const myKillCount = ref(0)

// 加载战场信息
const loadBattlefieldInfo = async () => {
  try {
    const res = await http.get(`/battlefield/info?type=${currentType.value}`)
    if (res.data.ok) {
      battlefieldInfo.value = res.data.battlefield
      lastResult.value = res.data.lastResult
      myResult.value = res.data.myResult
      isSignedUp.value = !!res.data.isSignedUp
      await loadMyKillCount()
    }
  } catch (e) {
    console.error('加载战场信息失败', e)
  }
}

// 获取当前用户昵称
const loadMe = async () => {
  try {
    const res = await http.get('/auth/status')
    if (res.data && res.data.ok && res.data.nickname) {
      meNickname.value = res.data.nickname
    }
  } catch (e) {
    console.error('获取用户信息失败', e)
  }
}

// 计算当前玩家的胜场 = 杀敌数
const loadMyKillCount = async () => {
  myKillCount.value = 0
  if (!meNickname.value) return
  try {
    const res = await http.get(`/battlefield/yesterday?type=${currentType.value}`)
    if (res.data && res.data.ok) {
      const matches = res.data.matches || []
      let wins = 0
      for (const m of matches) {
        const isFirst = m.firstPlayer === meNickname.value
        const isSecond = m.secondPlayer === meNickname.value
        if (!isFirst && !isSecond) continue
        const isFirstWin = !!m.isFirstWin
        const win = isFirst ? isFirstWin : !isFirstWin
        if (win) wins += 1
      }
      myKillCount.value = wins
    }
  } catch (e) {
    console.error('计算杀敌数失败', e)
  }
}

// 切换战场类型
const switchType = (type) => {
  currentType.value = type
  loadBattlefieldInfo()
}

// 查看简介
const viewIntro = () => {
  router.push('/battlefield/intro')
}

// 查看昨日战况
const viewYesterday = () => {
  router.push(`/battlefield/yesterday?type=${currentType.value}`)
}

// 报名参战
const signupBattlefield = async () => {
  if (signupLoading.value || isSignedUp.value) return
  signupLoading.value = true
  try {
    const res = await http.post('/battlefield/signup', { type: currentType.value })
    if (res.data.ok) {
      console.error(res.data.message || '报名成功')
      isSignedUp.value = true
      loadBattlefieldInfo()
    } else {
      console.error(res.data.error || '报名失败')
    }
  } catch (e) {
    const status = e?.response?.status
    const data = e?.response?.data
    const serverMsg =
      (data && typeof data === 'object' && (data.error || data.message)) ||
      (typeof data === 'string' ? data.slice(0, 200) : '')

    // 后端会返回：当前不在报名时间（06:00-20:00）
    if (typeof serverMsg === 'string' && serverMsg.includes('不在报名时间')) {
      console.error('不在报名时间段')
      return
    }

    let msg = serverMsg || e?.message || '报名失败'
    if (status === 500 && !serverMsg) {
      msg = '服务器错误（500）。请确认后端已启动，并查看后端控制台日志。'
    }
    console.error('报名失败：' + msg)
  } finally {
    signupLoading.value = false
  }
}

// 查看杀敌详细
const viewKillDetail = () => {
  router.push(`/battlefield/kill-detail?type=${currentType.value}`)
}

// 返回首页
const goHome = () => {
  router.push('/')
}

onMounted(() => {
  loadMe().then(() => {
    loadBattlefieldInfo()
  })
})
</script>

<template>
  <div class="battlefield-page">
    <!-- 标题 -->
    <div class="section title">
      【古战场】 {{ battlefieldInfo.period }}期 
      <a class="link" @click="viewIntro">简介</a>
    </div>

    <!-- 战场切换 -->
    <div class="section">
      <a 
        class="link" 
        :class="{ active: currentType === 'tiger' }"
        @click="switchType('tiger')"
      >猛虎战场</a>|<a 
        class="link"
        :class="{ active: currentType === 'crane' }"
        @click="switchType('crane')"
      >飞鹤战场</a>
    </div>

    <!-- 基本信息 -->
    <div class="section">要求等级:{{ battlefieldInfo.levelRange }}</div>
    <div class="section">报名时间:{{ battlefieldInfo.signUpTime }}</div>
    <div class="section">军力对比:{{ battlefieldInfo.redCount }} VS {{ battlefieldInfo.blueCount }}</div>

    <!-- 报名按钮 -->
    <div class="section">
      <a
        class="link action"
        :class="{ disabled: signupLoading || isSignedUp }"
        @click="signupBattlefield"
      >
        {{ isSignedUp ? '已报名，等待开战' : (signupLoading ? '报名中...' : '报名参战') }}
      </a>
    </div>

    <!-- 上期战绩 -->
    <div class="section title2">
      [上期战绩]{{ lastResult.period }}期 
      <a class="link orange" @click="viewYesterday">昨日战况</a>
    </div>
    <div class="section">
      猛虎战王:{{ lastResult.tigerKing.name }} ({{ lastResult.tigerKing.kills }}杀)
    </div>
    <div class="section">
      飞鹤战王:{{ lastResult.craneKing.name }} ({{ lastResult.craneKing.kills }}杀)
    </div>
    <div class="section">战王额外奖励：{{ lastResult.kingReward }}</div>

    <!-- 我的战绩 -->
    <div class="section title2">[我的战绩]{{ myResult.period }}期</div>
    <div class="section">{{ myResult.won ? '胜利' : '' }}</div>
    <div class="section">
      杀敌: {{ myKillCount }}人 
      <a class="link" @click="viewKillDetail">详细</a>
    </div>
    <div class="section">战场奖励:{{ myResult.campReward }}</div>
    <div class="section">杀敌奖励:{{ myResult.killReward }}</div>

    <!-- 返回 -->
    <div class="nav-links">
      <div><a class="link" @click="goHome">返回游戏首页</a></div>
    </div>

  </div>
</template>

<style scoped>
.battlefield-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 10px 12px;
  font-size: 17px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.title {
  font-weight: bold;
  color: #333;
}

.title2 {
  font-weight: bold;
  margin-top: 10px;
}

.section {
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

.link.active {
  font-weight: bold;
  color: #333;
}

.red {
  color: #CC0000;
}

.blue {
  color: #0066CC;
}

.orange {
  color: #FF6600;
}

.gray {
  color: #666;
}

.nav-links {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #ccc;
}

.footer {
  margin-top: 20px;
}

.small {
  font-size: 17px;
}
</style>
