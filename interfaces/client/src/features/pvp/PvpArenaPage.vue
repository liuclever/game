<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 基本信息
const openTime = ref('8:00-23:59')
const currentKing = ref({ name: '天师钟馗', title: '👹', wins: 888 })
const todayReward = ref('铜钱60万、追魂法宝5个、灵力水晶1个、木灵灵石2个、金灵灵石1个(低概率)')

// 连胜信息
const myWins = ref(3)
const todayBestWins = ref(3)

// 推荐对手
const opponents = ref([
  { name: '扛把子8号', level: 75 },
  { name: '杨永信', level: 79, guild: '暗河风流鬼' },
])

// 刷新倒计时
const refreshCountdown = ref(300) // 5分钟=300秒
let countdownTimer = null

// 最近战斗记录
const lastBattle = ref({
  opponent: '月挽星回べう',
  guild: '切磋匠天門ゞ',
  result: '胜利',
  winsChange: '+1',
  energyCost: 15,
})

// 连胜奖励配置
const winRewards = ref([
  { wins: 1, reward: '铜钱1000、结晶随机×1', canClaim: false },
  { wins: 2, reward: '铜钱5000、强力捕捉球×2', canClaim: false },
  { wins: 3, reward: '铜钱1万、化仙丹1个、随机结晶×1', canClaim: false },
  { wins: 4, reward: '铜钱5万、活力草1个、重生丹1个', canClaim: false },
  { wins: 5, reward: '铜钱10万、活力草2个、重生丹1个', canClaim: false },
  { wins: 6, reward: '铜钱15万、追魂法宝1个、神·逆鳞碎片1个', canClaim: false },
])

// 是否已达成6连胜
const hasSixWinReward = ref(false)

// 格式化倒计时
const formatCountdown = () => {
  const min = Math.floor(refreshCountdown.value / 60)
  const sec = refreshCountdown.value % 60
  return `${min}分${sec}秒`
}

// 开始倒计时
const startCountdown = () => {
  countdownTimer = setInterval(() => {
    if (refreshCountdown.value > 0) {
      refreshCountdown.value--
    } else {
      refreshCountdown.value = 300
      // 自动刷新对手
    }
  }, 1000)
}

// 查看简介
const viewIntro = () => {
  router.push('/pvp/intro')
}

// 查看今日连胜榜
const viewTodayRank = () => {
  alert('今日连胜榜')
}

// 查看历届连胜王
const viewHistoryKings = () => {
  alert('历届连胜王')
}

// 查看玩家详情
const viewPlayer = (name, guild) => {
  router.push(`/player/detail?name=${encodeURIComponent(name)}&guild=${encodeURIComponent(guild || '')}`)
}

// 切磋对手
const challenge = (opponent) => {
  alert(`切磋 ${opponent.name}`)
}

// 手动刷新
const manualRefresh = () => {
  alert('刷新对手列表')
}

// 立即刷新(消耗元宝)
const instantRefresh = () => {
  alert('消耗50元宝立即刷新')
}

// 查看战斗详情
const viewBattleDetail = () => {
  router.push('/pvp/report')
}

// 领取奖励
const claimReward = (wins) => {
  alert(`领取${wins}连胜奖励`)
}

// 返回首页
const goHome = () => {
  router.push('/')
}

onMounted(() => {
  startCountdown()
})

onUnmounted(() => {
  if (countdownTimer) clearInterval(countdownTimer)
})
</script>

<template>
  <div class="pvp-page">
    <!-- 标题 -->
    <div class="section title">
      【连胜竞技场】 <a class="link" @click="viewIntro">简介</a>
    </div>

    <!-- 开放时间 -->
    <div class="section">开放时间:{{ openTime }}</div>

    <!-- 当前连胜王 -->
    <div class="section">
      当前连胜王: <a class="link orange" @click="viewPlayer(currentKing.name)">{{ currentKing.name }}</a> {{ currentKing.title }} .{{ currentKing.wins }}连胜
    </div>
    <div class="section gray">
      (今日连胜大奖:{{ todayReward }})
    </div>

    <!-- 榜单链接 -->
    <div class="section">
      <a class="link orange" @click="viewTodayRank">今日连胜榜</a>. 
      <a class="link" @click="viewHistoryKings">历届连胜王</a>
    </div>

    <!-- 我的连胜 -->
    <div class="section">当前连胜:{{ myWins }}/今日最高:{{ todayBestWins }}</div>
    <div class="section">请与推荐对手切磋</div>

    <!-- 推荐对手 -->
    <div class="section" v-for="(opp, index) in opponents" :key="index">
      <template v-if="opp.guild">
        <span class="orange">{{ opp.guild }}</span>丨<a class="link orange" @click="viewPlayer(opp.name, opp.guild)">{{ opp.name }}</a>
      </template>
      <template v-else>
        <a class="link orange" @click="viewPlayer(opp.name)">{{ opp.name }}</a>
      </template>
      ({{ opp.level }}级). <span class="link readonly">切磋</span>
    </div>

    <!-- 刷新 -->
    <div class="section">
      {{ formatCountdown() }}后将自动刷新 <a class="link orange" @click="manualRefresh">刷新</a>
    </div>
    <div class="section">
      <a class="link orange" @click="instantRefresh">立即刷新(消耗50元宝)</a>
    </div>

    <!-- 最近战斗 -->
    <div class="section">
      {{ lastBattle.guild }} {{ lastBattle.opponent }} {{ lastBattle.result }}，连胜次数{{ lastBattle.winsChange }}，活力-{{ lastBattle.energyCost }} 
      <a class="link" @click="viewBattleDetail">查看</a>
    </div>

    <!-- 连胜奖励 -->
    <div class="section title2">连胜奖励:</div>
    <div class="section gray small">（备注：6连胜奖励未达到前，每次切磋需要耗费100活力，6连胜奖励达成后，每次切磋消耗15活力）</div>
    <div class="section" v-for="reward in winRewards" :key="reward.wins">
      {{ reward.wins }}连胜:{{ reward.reward }}
      <template v-if="reward.canClaim">
        <a class="link" @click="claimReward(reward.wins)">领取</a>
      </template>
      <template v-else>
        <span class="gray">(未达到)</span>
      </template>
    </div>

    <!-- 返回 -->
    <div class="nav-links">
      <div><a class="link" @click="goHome">返回竞技首页</a></div>
      <div><a class="link" @click="goHome">返回游戏首页</a></div>
    </div>

  </div>
</template>

<style scoped>
.pvp-page {
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
  margin-top: 15px;
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

.link.readonly {
  color: #000000;
  cursor: default;
  pointer-events: none;
  text-decoration: none;
}

.link.readonly:hover {
  text-decoration: none;
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
