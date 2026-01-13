<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
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
const isRegistered = ref(false)
const cooldownRemaining = ref(0)

// 可挑战的玩家列表
const challengers = ref([])

// 正赛信息
const finalStageInfo = ref({
  stages: {},
  myAchievement: '未参加正赛',
  myBestStage: null,
  stageStatus: {}
})

// 正赛奖励信息
const rewardInfo = ref({
  myRank: 0,
  rewardTier: null,
  canClaim: false,
  alreadyClaimed: false
})

// 当前查看的正赛阶段
const viewingStage = ref(null)

// 动态列表
const dynamics = ref([])

// 冷却倒计时定时器
let cooldownTimer = null

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
      isRegistered.value = res.data.isRegistered || false
      cooldownRemaining.value = res.data.cooldownRemaining || 0
      
      if (cooldownRemaining.value > 0) {
        startCooldownTimer()
      }
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

// 启动冷却倒计时
const startCooldownTimer = () => {
  if (cooldownTimer) clearInterval(cooldownTimer)
  
  cooldownTimer = setInterval(() => {
    if (cooldownRemaining.value > 0) {
      cooldownRemaining.value--
    } else {
      clearInterval(cooldownTimer)
      cooldownTimer = null
    }
  }, 1000)
}

// 加载动态
const loadDynamics = async () => {
  try {
    const res = await http.get('/king/dynamics')
    if (res.data.ok) {
      dynamics.value = res.data.dynamics || []
    }
  } catch (e) {
    console.error('加载动态失败', e)
  }
}

// 加载正赛信息
const loadFinalStageInfo = async () => {
  try {
    const res = await http.get('/king/final_stage_info')
    if (res.data.ok) {
      finalStageInfo.value = {
        stages: res.data.stages || {},
        myAchievement: res.data.myAchievement || '未参加正赛',
        myBestStage: res.data.myBestStage,
        stageStatus: res.data.stageStatus || {}
      }
    }
  } catch (e) {
    console.error('加载正赛信息失败', e)
  }
}

// 查看某个阶段的对阵
const viewStage = (stage) => {
  viewingStage.value = stage
}

// 关闭阶段查看
const closeStageView = () => {
  viewingStage.value = null
}

// 获取阶段状态文本
const getStageStatus = (stage) => {
  const matches = finalStageInfo.value.stages[stage] || []
  if (matches.length === 0) return '未开始'
  const allFinished = matches.every(m => m.isWinner !== null || m.isBye === 1)
  return allFinished ? '已结束' : '进行中'
}

// 报名
const doRegister = async () => {
  try {
    const res = await http.post('/king/register')
    if (res.data.ok) {
      alert(res.data.message)
      loadKingInfo()
    } else {
      alert(res.data.error || '报名失败')
    }
  } catch (e) {
    console.error('报名失败', e)
    alert(e?.response?.data?.error || '报名失败')
  }
}

// 发起挑战
const doChallenge = async (target) => {
  if (challenging.value) return
  if (todayCount.value >= todayMax.value) {
    alert('今日挑战次数已用完')
    return
  }
  if (cooldownRemaining.value > 0) {
    alert(`冷却中，还需等待${cooldownRemaining.value}秒`)
    return
  }
  
  challenging.value = true
  try {
    const res = await http.post('/king/challenge', { targetUserId: target.userId })
    if (res.data.ok) {
      // 保存战报到 sessionStorage
      if (res.data.battleReport) {
        sessionStorage.setItem('king_battle_report', JSON.stringify(res.data.battleReport))
        router.push('/king/battle-report')
      } else {
        alert(res.data.message)
        loadKingInfo()
        loadDynamics()
      }
    } else {
      alert(res.data.error || '挑战失败')
      loadKingInfo()
      loadDynamics()
    }
  } catch (e) {
    console.error('挑战失败', e)
    alert(e?.response?.data?.error || '挑战失败')
  } finally {
    challenging.value = false
  }
}

// 查看战报
const viewBattleReport = (logId) => {
  router.push({ path: '/king/battle-report', query: { logId } })
}

// 查看玩家信息
const viewPlayer = (userId) => {
  router.push({ path: '/player/profile', query: { id: userId } })
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

// 检查是否是星期一
const isMonday = () => {
  return new Date().getDay() === 1
}

onMounted(() => {
  loadKingInfo()
  loadRewardInfo()
  loadDynamics()
  loadFinalStageInfo()
})

onUnmounted(() => {
  if (cooldownTimer) {
    clearInterval(cooldownTimer)
    cooldownTimer = null
  }
})
</script>

<template>
  <div class="king-page">
    <div class="section title">【召唤之王挑战赛】 <a class="link" @click="goIntro">简介</a></div>

    <div class="section">召唤之王：<span class="blue">低调</span></div>

    <!-- 报名按钮（仅星期一显示） -->
    <div class="section" v-if="isMonday() && !isRegistered">
      <a class="link orange" @click="doRegister">点击报名</a>
    </div>
    <div class="section gray" v-else-if="isRegistered">
      已报名本周挑战赛
    </div>

    <!-- 赛程切换 -->
    <div class="section">
      <a class="link" :class="{active: phase==='pre'}" @click="phase='pre'">预选赛</a>
      <a class="link" :class="{active: phase==='final'}" @click="phase='final'"> 正赛</a>
    </div>

    <!-- 概览信息 -->
    <div class="section" v-if="loading">加载中...</div>
    <div class="section warning" v-if="error">{{ error }}</div>
    <div class="section">我的赛区：<span class="orange">{{ area || '—' }}</span>（<a class="link" @click="goRanking">排名</a>）</div>
    
    <!-- 挑战列表 -->
    <template v-if="phase === 'pre' && challengers.length > 0">
      <div class="section title2">排名挑战：</div>
      <div v-for="c in challengers" :key="c.userId" class="section challenger-row">
        <span class="rank-num">{{ c.rank }}.</span>
        <a class="link username" @click="viewPlayer(c.userId)">{{ c.nickname }}</a>
        <a 
          class="link challenge-btn" 
          @click="doChallenge(c)" 
          :class="{ disabled: challenging || cooldownRemaining > 0 }"
        >
          {{ challenging ? '挑战中...' : (cooldownRemaining > 0 ? `冷却中(${cooldownRemaining}秒)` : '挑战') }}
        </a>
      </div>
    </template>
    <template v-else-if="phase === 'pre' && myRank === 1">
      <div class="section">排名挑战：你已是第一名，无人可挑战！</div>
    </template>
    <template v-else-if="phase === 'final'">
      <!-- 正赛阶段列表 -->
      <div class="section">
        <a class="link" @click="viewStage('32')">64进32</a>({{ getStageStatus('32') }})
      </div>
      <div class="section">
        <a class="link" @click="viewStage('16')">32进16</a>({{ getStageStatus('16') }})
      </div>
      <div class="section">
        <a class="link" @click="viewStage('8')">16进8</a>({{ getStageStatus('8') }})
      </div>
      <div class="section">
        <a class="link" @click="viewStage('4')">8进4</a>({{ getStageStatus('4') }})
      </div>
      <div class="section">
        <a class="link" @click="viewStage('2')">半决赛</a>({{ getStageStatus('2') }})
      </div>
      <div class="section">
        <a class="link" @click="viewStage('champion')">决赛</a>({{ getStageStatus('champion') }})
      </div>
      
      <div class="section">我的战绩:{{ finalStageInfo.myAchievement }}</div>
      
      <!-- 奖励信息 -->
      <div class="section">
        奖励:
        <template v-if="rewardInfo.rewardTier">
          正赛{{ rewardInfo.rewardTier.name }}礼包
        </template>
        <template v-else>
          未获得奖励
        </template>
        <a v-if="rewardInfo.canClaim" class="link" @click="claimReward">领取奖励</a>
        <span v-else-if="rewardInfo.alreadyClaimed" class="gray">（已领取）</span>
      </div>
      
      <!-- 阶段对阵详情弹窗 -->
      <div v-if="viewingStage" class="stage-modal">
        <div class="modal-content">
          <div class="section title2">
            {{ viewingStage === 'champion' ? '决赛' : viewingStage === '2' ? '半决赛' : `${viewingStage}强赛` }}
            <a class="link" @click="closeStageView" style="float: right;">关闭</a>
          </div>
          
          <template v-if="finalStageInfo.stages[viewingStage] && finalStageInfo.stages[viewingStage].length > 0">
            <div v-for="(match, idx) in finalStageInfo.stages[viewingStage]" :key="idx" class="section">
              <template v-if="match.isBye">
                {{ match.nickname }} 轮空晋级
              </template>
              <template v-else-if="match.matchId">
                第{{ match.matchId }}场: 
                <span :class="{ 'winner': match.isWinner === 1 }">{{ match.nickname }}</span>
                vs
                <span :class="{ 'winner': match.isWinner === 0 }">{{ match.opponentNickname }}</span>
                <template v-if="match.isWinner !== null">
                  - {{ match.isWinner === 1 ? match.nickname : match.opponentNickname }}获胜
                </template>
              </template>
            </div>
          </template>
          <div v-else class="section gray">该阶段暂无对阵信息</div>
        </div>
      </div>
    </template>
    
    <!-- 预选赛信息 -->
    <template v-if="phase === 'pre'">
      <div class="section">排名：<span class="orange">{{ myRank }}</span> 名</div>
      <div class="section">连胜：{{ winStreak }} 场</div>
      <div class="section">今日战令：{{ todayCount }}/{{ todayMax }}</div>
      <div class="section gray" v-if="cooldownRemaining > 0">挑战冷却：{{ cooldownRemaining }}秒</div>
      <div class="section gray">预选赛奖励：挑战成功+20000铜钱，失败+2000铜钱</div>

      <!-- 动态 -->
      <div class="section title2">【预选赛动态】<a class="link gray"> 更多</a></div>
      <div v-if="dynamics.length === 0" class="section gray">暂无动态</div>
      <div v-for="(d, idx) in dynamics" :key="idx" class="section">
        <span class="gray">{{ d.time }}</span> {{ d.text }}
        <a v-if="d.canView" class="link" @click="viewBattleReport(d.logId)"> 查看</a>
      </div>
    </template>

    <div class="section spacer">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.king-page { 
  padding: 10px; 
  font-size: 13px; 
  background: #FFF8DC; 
  min-height: 100vh;
  font-family: SimSun, "宋体", serif;
}
.section { margin: 8px 0; line-height: 1.6; }
.title { font-weight: bold; color: #333; }
.title2 { font-weight: bold; color: #333; margin-top: 12px; }
.link { color: #0066CC; cursor: pointer; text-decoration: none; }
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

.stage-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #FFF8DC;
  padding: 20px;
  border-radius: 4px;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.winner {
  color: #ff6600;
  font-weight: bold;
}
</style>
