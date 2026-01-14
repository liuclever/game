<script setup>
import { useMessage } from '@/composables/useMessage'
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

// 当前选中的塔
const { message, messageType, showMessage } = useMessage()

const currentTower = ref('tongtian')
const towers = {
  tongtian: '通天塔',
  longwen: '龙纹塔',
  zhanling: '战灵塔',
}

// 闯塔数据
const towerInfo = ref({
  currentFloor: 1,
  maxFloorRecord: 1,
  todayCount: 0,
  dailyLimit: 4,
  maxFloor: 120,
  energyCost: 20,
  rewards: '幻兽经验、付费道具',
  buffEnabled: true,
  buffBonus: 10,
})

// 鼓舞状态
const inspireStatus = ref({
  active: false,
  remaining_seconds: 0,
  inspire_pill_count: 0,
})

// 倒计时定时器
let inspireTimer = null

// 闯塔动态
const activities = ref([])

// 加载闯塔信息
const loadTowerInfo = async () => {
  try {
    const res = await http.get(`/tower/info?type=${currentTower.value}`)
    towerInfo.value = {
      currentFloor: res.data.current_floor,
      maxFloorRecord: res.data.max_floor_record,
      todayCount: res.data.today_count,
      dailyLimit: res.data.daily_limit,
      maxFloor: res.data.max_floor,
      energyCost: res.data.energy_cost,
      buffEnabled: res.data.buff?.enabled ?? true,
      buffBonus: (res.data.buff?.attack_bonus ?? 0.1) * 100,
      rewards: '幻兽经验、付费道具',
    }
  } catch (e) {
    console.error('加载闯塔信息失败', e)
  }
}

// 检查是否测试模式
const checkTestMode = async () => {
  try {
    const res = await http.get('/auth/game-config')
    return res.data.is_test_mode
  } catch (e) {
    return false
  }
}

// 切换塔类型
const switchTower = async (type) => {
  // 测试模式下禁止访问战灵塔
  if (type === 'zhanling') {
    const isTest = await checkTestMode()
    if (isTest) {
      showMessage('测试模式下战灵塔未开放', 'info')
      return
    }
  }
  currentTower.value = type
  loadTowerInfo()
}

// 加载鼓舞状态
const loadInspireStatus = async () => {
  try {
    const res = await http.get('/tower/inspire/status')
    if (res.data.ok) {
      inspireStatus.value = res.data
      if (res.data.active && res.data.remaining_seconds > 0) {
        startInspireCountdown()
      }
    }
  } catch (e) {
    console.error('加载鼓舞状态失败', e)
  }
}

// 启动鼓舞倒计时
const startInspireCountdown = () => {
  if (inspireTimer) clearInterval(inspireTimer)
  inspireTimer = setInterval(() => {
    if (inspireStatus.value.remaining_seconds > 0) {
      inspireStatus.value.remaining_seconds--
    } else {
      clearInterval(inspireTimer)
      inspireStatus.value.active = false
    }
  }, 1000)
}

// 格式化鼓舞剩余时间
const formatInspireTime = computed(() => {
  const seconds = inspireStatus.value.remaining_seconds
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}分${s.toString().padStart(2, '0')}秒`
})

// 使用鼓舞丹
const useInspirePill = async () => {
  if (inspireStatus.value.active) {
    showMessage('鼓舞效果正在生效中，无法叠加使用！', 'info')
    return
  }
  if (inspireStatus.value.inspire_pill_count <= 0) {
    showMessage('鼓舞丹不足！可通过开启钛金宝箱、秘银宝箱获得，或在商城购买。', 'error')
    return
  }
  
  try {
    const res = await http.post('/tower/inspire/use')
    if (res.data.ok) {
      showMessage(res.data.message, 'success')
      loadInspireStatus()
    } else {
      showMessage(res.data.error, 'error')
    }
  } catch (e) {
    console.error('使用鼓舞丹失败', e)
  }
}

onMounted(() => {
  loadTowerInfo()
  loadInspireStatus()
})

onUnmounted(() => {
  if (inspireTimer) clearInterval(inspireTimer)
})

// 自动闯塔
const autoChallenge = () => {
  router.push(`/tower/challenge?type=${currentTower.value}`)
}

// 镇妖
const suppress = () => {
  router.push('/tower/zhenyao')
}

// 查看战报
const viewReport = (activity) => {
  router.push({
    path: '/tower/report',
    query: { floor: activity.floor }
  })
}

// 返回首页
const goHome = () => {
  router.push('/')
}

// 点击链接
const handleLink = (name) => {
  const routes = {
    '背包': '/inventory',
    '幻兽': '/beast',
    '地图': '/map',
    '擂台': '/arena',
    '闯塔': '/tower',
    '排行': '/ranking',
    '召唤之王挑战赛': '/king',
    '商城': '/shop',
    '兑换': '/exchange',
    '化仙': '/huaxian',
    'VIP': '/vip',
    '提升': '/vip',
    '活力': '/vip',
    '图鉴': '/handbook',
  }
  if (name === '简介') {
    router.push(`/tower/intro?type=${currentTower.value}`)
  } else if (routes[name]) {
    router.push(routes[name])
  } else {
    showMessage(`点击了: ${name}`, 'info')
  }
}
</script>

<template>
  <div class="tower-page">
    <!-- 消息提示 -->
    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>

    <!-- 标题 -->
    <div class="section title">
      【勇闯重塔】 <a class="link" @click="handleLink('简介')">简介</a>
    </div>

    <!-- 塔类型切换 -->
    <div class="section">
      <a 
        class="link" 
        :class="{ active: currentTower === 'tongtian' }"
        @click="switchTower('tongtian')"
      >通天塔</a> | 
      <a 
        class="link"
        :class="{ active: currentTower === 'longwen' }"
        @click="switchTower('longwen')"
      >龙纹塔</a> | 
      <a 
        class="link"
        :class="{ active: currentTower === 'zhanling' }"
        @click="switchTower('zhanling')"
      >战灵塔</a>
    </div>

    <!-- 闯塔信息 -->
    <div class="section">
      当前层数:{{ Math.min(towerInfo.currentFloor, towerInfo.maxFloor) }}/{{ towerInfo.maxFloor }}层
      <span v-if="towerInfo.currentFloor > towerInfo.maxFloor" class="green">(已通关)</span>
    </div>
    <div class="section">
      今日闯塔:{{ towerInfo.todayCount }}/{{ towerInfo.dailyLimit }}
    </div>
    <div class="section">
      最高纪录:{{ Math.min(towerInfo.maxFloorRecord, towerInfo.maxFloor) }}层
    </div>
    <div class="section">
      每次消耗: {{ towerInfo.energyCost }}活力
    </div>
    <div class="section">
      闯塔奖励: {{ towerInfo.rewards }}
    </div>

    <!-- 操作按钮 -->
    <div class="section">
      <a class="link" @click="autoChallenge">自动闯塔</a>
      <a class="link suppress-btn" @click="suppress">镇妖</a>
    </div>
    
    <!-- 鼓舞状态 -->
    <!-- <div class="section" v-if="inspireStatus.active">
      鼓舞: <span class="green">生效中</span> 
      <span class="gray">(剩余{{ formatInspireTime }}，战力+10%)</span>
    </div>
    <div class="section" v-else>
      鼓舞: <a class="link" @click="useInspirePill">使用鼓舞丹</a>
      <span class="gray"> (战力+10%，持续30分钟)</span>
    </div>
    <div class="section">
      鼓舞丹: {{ inspireStatus.inspire_pill_count }}个
    </div> -->

    <!-- 闯塔动态 -->
    <div class="section title2">【闯塔动态】</div>
    <div v-for="(activity, index) in activities" :key="index" class="section">
      <span class="gray">({{ activity.time }})</span>{{ towers[currentTower] }}第{{ activity.floor }}层,<span class="green">{{ activity.result }}</span> 
      <a class="link" @click="viewReport(activity)">详细战报</a>
    </div>

    <!-- 皇城 -->
    <div class="section spacer">
      皇城:<span class="link readonly">召唤之王挑战赛</span>
    </div>

    <!-- 导航菜单 -->
    <div class="section">
      <a class="link" @click="handleLink('幻兽')">幻兽</a>. 
      <a class="link" @click="handleLink('背包')">背包</a>. 
      <a class="link" @click="handleLink('商城')">商城</a>. 
      <a class="link" @click="handleLink('赞助')">赞助</a>. 
      <a class="link" @click="handleLink('礼包')">礼包</a>
    </div>
    <div class="section">
      <a class="link" @click="handleLink('联盟')">联盟</a>. 
      <a class="link" @click="handleLink('盟战')">盟战</a>. 
      <a class="link" @click="handleLink('地图')">地图</a>. 
      <span class="link readonly">天赋</span>. 
      <a class="link" @click="handleLink('化仙')">化仙</a>
    </div>
    <div class="section">
      <span class="link readonly">切磋</span>. 
      <a class="link active">闯塔</a>. 
      <a class="link" @click="handleLink('战场')">战场</a>. 
      <a class="link" @click="handleLink('擂台')">擂台</a>. 
      <span class="link readonly">坐骑</span>
    </div>
    <div class="section">
      <a class="link" @click="router.push('/tree')">古树</a>. 
      <a class="link" @click="handleLink('排行')">排行</a>. 
      <span class="link readonly">成就</span>. 
      <a class="link" @click="handleLink('图鉴')">图鉴</a>. 
      <span class="link readonly">攻略</span>
    </div>
    <div class="section">
      <a class="link" @click="handleLink('兑换')">兑换</a>. 
      <span class="link readonly">签到</span>. 
      <span class="link readonly">论坛</span>. 
      <a class="link" @click="handleLink('VIP')">VIP</a>. 
      <span class="link readonly">安全锁</span>
    </div>

    <!-- 返回首页 -->
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.tower-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 13px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 2px 0;
}

.title {
  margin-bottom: 8px;
}

.title2 {
  margin-top: 12px;
  margin-bottom: 4px;
}

.spacer {
  margin-top: 16px;
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

.link.active {
  color: #CC3300;
  font-weight: bold;
}

.link.username {
  color: #CC6600;
}

.link.suppress-btn {
  margin-left: 16px;
}

.gray {
  color: #666666;
}

.green {
  color: #009900;
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
