<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

// 顶部切换：预选赛 / 正赛
const phase = ref('pre') // 'pre' | 'final'

// 基本信息
const area = ref('')
const myRank = ref(0)
const winStreak = ref(0)
const todayCount = ref(0)
const todayMax = ref(15)
const totalPlayers = ref(0)
const loading = ref(false)
const challenging = ref(false)
const error = ref('')

// 可挑战的玩家列表
const challengers = ref([])

// 正赛奖励信息
const rewardInfo = ref({
  myRank: 0,
  rewardTier: null,
  canClaim: false,
  alreadyClaimed: false
})

// 动态（占位）
const dynamics = ref([
  { time: '12-04 22:59', text: '洋柿子 挑战你，你大胜而归，排名保持不变', view: true },
  { time: '12-04 14:12', text: '你挑战 功夫熊猫，你惜败，排名保持不变', view: true },
  { time: '12-03 05:43', text: '荒天帝 挑战你，你大胜而归，排名保持不变', view: true },
])

const goHome = () => router.push('/')
const goRanking = () => router.push('/king/ranking')
const goIntro = () => router.push('/king/intro')

// 加载挑战赛基本信息
const loadKingInfo = async () => {
  loading.value = true
  try {
    const res = await http.get('/king/info')
    if (res.data.ok) {
      area.value = res.data.areaName || ''
      totalPlayers.value = res.data.totalPlayers || 0
      myRank.value = res.data.myRank || 0
      winStreak.value = res.data.winStreak || 0
      todayCount.value = res.data.todayChallenges || 0
      todayMax.value = res.data.todayMax || 15
      challengers.value = res.data.challengers || []
    } else {
      error.value = res.data.error || '加载失败'
    }
  } catch (e) {
    console.error('加载挑战赛信息失败', e)
    error.value = '加载失败'
  } finally {
    loading.value = false
  }
}

// 发起挑战
const doChallenge = async (target) => {
  if (challenging.value) return
  if (todayCount.value >= todayMax.value) {
    alert('今日挑战次数已用完')
    return
  }
  
  challenging.value = true
  try {
    const res = await http.post('/king/challenge', { targetUserId: target.userId })
    if (res.data.ok) {
      alert(res.data.message)
      // 刷新数据
      loadKingInfo()
    } else {
      alert(res.data.error || '挑战失败')
    }
  } catch (e) {
    console.error('挑战失败', e)
    alert('挑战失败')
  } finally {
    challenging.value = false
  }
}

// 查看玩家信息
const viewPlayer = (userId) => {
  router.push(`/player?id=${userId}`)
}

// 加载正赛奖励信息
const loadRewardInfo = async () => {
  try {
    const res = await http.get('/king/reward_info')
    if (res.data.ok) {
      rewardInfo.value = {
        myRank: res.data.myRank || 0,
        rewardTier: res.data.rewardTier,
        canClaim: res.data.canClaim,
        alreadyClaimed: res.data.alreadyClaimed
      }
    }
  } catch (e) {
    console.error('加载奖励信息失败', e)
  }
}

// 领取正赛奖励
const claimReward = async () => {
  try {
    const res = await http.post('/king/claim_reward')
    if (res.data.ok) {
      alert(res.data.message)
      loadRewardInfo()
    } else {
      alert(res.data.error || '领取失败')
    }
  } catch (e) {
    console.error('领取奖励失败', e)
    alert('领取失败')
  }
}

onMounted(() => {
  loadKingInfo()
  loadRewardInfo()
})
</script>

<template>
  <div class="king-page">
    <div class="section title">【召唤之王挑战赛】 <a class="link" @click="goIntro">简介</a></div>

    <div class="section">召唤之王：<span class="blue">低调</span></div>

    <!-- 赛程切换 -->
    <div class="section">
      <a class="link" :class="{active: phase==='pre'}" @click="phase='pre'">预选赛</a>
      <a class="link" :class="{active: phase==='final'}" @click="phase='final'"> 正赛</a>
    </div>

    <!-- 概览信息 -->
    <div class="section" v-if="loading">加载中...</div>
    <div class="section warning" v-if="error">{{ error }}</div>
    <div class="section">我的赛区：<span class="orange">{{ area || '—' }}</span>（<a class="link" @click="goRanking">排名</a>）</div>
    
    <!-- 挑战列表：显示在"我的赛区"和"排名"之间 -->
    <template v-if="phase === 'pre' && challengers.length > 0">
      <div class="section title2">排名挑战：</div>
      <div v-for="c in challengers" :key="c.userId" class="section challenger-row">
        <span class="rank-num">{{ c.rank }}.</span>
        <a class="link username" @click="viewPlayer(c.userId)">{{ c.nickname }}</a>
        <a class="link challenge-btn" @click="doChallenge(c)" :class="{ disabled: challenging }">
          {{ challenging ? '挑战中...' : '挑战' }}
        </a>
      </div>
    </template>
    <template v-else-if="phase === 'pre' && myRank === 1">
      <div class="section">排名挑战：你已是第一名，无人可挑战！</div>
    </template>
    <template v-else-if="phase === 'final'">
      <div class="section gray">正赛阶段由系统自动匹配对手</div>
      <!-- 正赛奖励 -->
      <div class="section title2">【正赛奖励】</div>
      <div v-if="rewardInfo.rewardTier" class="section">
        你的排名：第{{ rewardInfo.myRank }}名（{{ rewardInfo.rewardTier.name }}）
      </div>
      <div v-if="rewardInfo.canClaim" class="section">
        可领取奖励：<span class="orange">{{ rewardInfo.rewardTier.gold }}</span>铜钱
        <a class="link" @click="claimReward">领取</a>
      </div>
      <div v-else-if="rewardInfo.alreadyClaimed" class="section gray">
        奖励已领取
      </div>
      <div v-else-if="!rewardInfo.rewardTier" class="section gray">
        排名不在奖励范围内（需进入32强）
      </div>
    </template>
    
    <div class="section">排名：<span class="orange">{{ myRank }}</span> 名</div>
    <div class="section">连胜：{{ winStreak }} 场</div>
    <div class="section">今日战令：{{ todayCount }}/{{ todayMax }}</div>
    <div class="section gray">预选赛奖励：挑战成功+20000铜钱，失败+2000铜钱</div>

    <!-- 动态 -->
    <div class="section title2">【预选赛动态】<a class="link gray"> 更多</a></div>
    <div v-for="(d, idx) in dynamics" :key="idx" class="section">
      <span class="gray">{{ d.time }}</span> {{ d.text }}
      <a v-if="d.view" class="link"> 查看</a>
    </div>

    <div class="section spacer">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.king-page { padding: 10px; font-size: 14px; background: #f5f5dc; min-height: 100vh; }
.section { margin: 8px 0; line-height: 1.6; }
.title { font-weight: bold; color: #333; }
.title2 { font-weight: bold; color: #333; margin-top: 12px; }
.link { color: #1e90ff; cursor: pointer; text-decoration: none; }
.link:hover { text-decoration: underline; }
.link.active { color: #ff6600; font-weight: bold; }
.link.username { color: #cc0000; }
.link.challenge-btn { margin-left: 10px; }
.link.disabled { color: #999; pointer-events: none; }
.orange { color: #ff6600; }
.blue { color: #3366cc; }
.gray { color: #888; }
.spacer { margin-top: 12px; }
.challenger-row { padding-left: 10px; }
.rank-num { display: inline-block; min-width: 30px; }
</style>
