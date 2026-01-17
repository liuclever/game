<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

// 当前塔类型（从URL参数获取）
const towerType = computed(() => route.query.type || 'tongtian')

// 塔名称映射
const towerNames = {
  tongtian: '通天塔',
  longwen: '龙纹塔',
  zhanling: '战灵塔',
}
const towerName = computed(() => towerNames[towerType.value] || '通天塔')

// 加载状态
const loading = ref(true)
const error = ref('')

// 当前层数
const currentFloor = ref(1)
const endFloor = ref(1)
const maxFloor = ref(120)

// 守塔幻兽信息
const guardian = ref({
  name: '远古谜兽',
  level: 1,
})

// 我方幻兽（从后端加载战斗队）
const myBeasts = ref([])
const myPower = ref(0)

// 战斗状态
const battleResult = ref('')
const autoEnabled = ref(true)
const stoppedReason = ref('')
const buffEnabled = ref(true)
const buffBonus = ref(10)

// 累计奖励
const rewards = ref({
  gold: 0,
  exp: 0,
  items: [],
})

// 根据接口结果应用一次闯塔数据（也用于从缓存恢复）
const applyAutoResult = (result, state) => {
  // 更新状态
  currentFloor.value = result.start_floor
  endFloor.value = result.end_floor
  maxFloor.value = state.max_floor
  stoppedReason.value = result.stopped_reason

  // 保存战斗详情
  allBattles.value = result.battles || []

  // 更新奖励
  rewards.value = {
    gold: result.total_rewards.gold || 0,
    exp: result.total_rewards.exp || 0,
    items: result.total_rewards.items || [],
  }

  // 生成活动记录
  const now = new Date()
  activities.value = (result.battles || []).map((battle, index) => {
    const time = new Date(now.getTime() + index * 1000)
    const timeStr = `${(time.getMonth() + 1).toString().padStart(2, '0')}.${time.getDate().toString().padStart(2, '0')} ${time.getHours().toString().padStart(2, '0')}:${time.getMinutes().toString().padStart(2, '0')}`

    return {
      time: timeStr,
      floor: battle.floor,
      result: battle.is_victory ? '完美胜利' : '挑战失败',
      isVictory: battle.is_victory,
      battleIndex: index,
    }
  }).reverse()  // 最新的在前面

  // 设置最后一场战斗的守塔幻兽和结果
  if (result.battles && result.battles.length > 0) {
    const lastBattle = result.battles[result.battles.length - 1]
    if (lastBattle.guardians && lastBattle.guardians.length > 0) {
      guardian.value = lastBattle.guardians[0]
    }
    battleResult.value = lastBattle.is_victory ? '完美胜利' : '挑战失败'
  }

  // 根据停止原因设置状态
  if (stoppedReason.value === 'all_dead') {
    autoEnabled.value = false
    battleResult.value = '挑战失败'
  } else if (stoppedReason.value === 'max_floor') {
    autoEnabled.value = false
    battleResult.value = '已通关'
  } else if (stoppedReason.value === 'daily_limit') {
    autoEnabled.value = false
    battleResult.value = '次数用尽'
  }
}

// 合并相同物品的奖励列表
const mergedItems = computed(() => {
  const itemMap = new Map()
  for (const item of rewards.value.items) {
    const key = item.item_id || item.name
    if (itemMap.has(key)) {
      itemMap.get(key).quantity += item.quantity
    } else {
      itemMap.set(key, { ...item })
    }
  }
  return Array.from(itemMap.values())
})

// 闯塔动态（战斗记录）
const activities = ref([])

// 保存所有战斗详情（用于查看战报）
const allBattles = ref([])

// 调用自动闯塔API
const startAutoChallenge = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const res = await http.post('/tower/auto', {
      tower_type: towerType.value,
      use_buff: buffEnabled.value,
    })
    
    if (res.data.ok) {
      const result = res.data.result
      const state = res.data.state

      applyAutoResult(result, state)

      // 缓存本次闯塔结果，返回详细战报页后可以直接恢复
      const cacheKey = `autoTowerResult:${towerType.value}`
      sessionStorage.setItem(cacheKey, JSON.stringify({ result, state }))
    } else {
      error.value = res.data.error || '闯塔失败'
    }
  } catch (e) {
    console.error('自动闯塔失败', e)
    error.value = e?.response?.data?.error || e?.message || '网络错误'
  } finally {
    loading.value = false
  }
}

// 刷新（重新请求并覆盖缓存）
const refresh = () => {
  startAutoChallenge()
}

// 继续挑战（再打一次当前层）
const continueChallenge = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const res = await http.post('/tower/auto', {
      tower_type: towerType.value,
      use_buff: buffEnabled.value,
      is_continue: true,  // 标记为继续挑战，不消耗今日次数
    })
    
    if (res.data.ok) {
      const result = res.data.result
      const state = res.data.state
      
      applyAutoResult(result, state)
      
      // 更新缓存
      const cacheKey = `autoTowerResult:${towerType.value}`
      sessionStorage.setItem(cacheKey, JSON.stringify({ result, state }))
    } else {
      error.value = res.data.error || '挑战失败'
    }
  } catch (e) {
    console.error('继续挑战失败', e)
    error.value = e?.response?.data?.error || e?.message || '网络错误'
  } finally {
    loading.value = false
  }
}

// 退出闯塔（发放累积奖励到背包）
const exitChallenge = async () => {
  if (!confirm('确定要退出闯塔吗？累积的奖励将发放到背包。')) {
    return
  }
  
  try {
    await http.post('/tower/reset', {
      tower_type: towerType.value,
      pending_rewards: rewards.value,
    })
  } catch (e) {
    console.error('重置闯塔失败', e)
  }
  // 清理本次闯塔缓存和当前战报缓存
  const cacheKey = `autoTowerResult:${towerType.value}`
  sessionStorage.removeItem(cacheKey)
  sessionStorage.removeItem('currentBattle')
  router.push('/tower')
}

// 返回首页
const goHome = () => {
  router.push('/')
}

const goHuaXian = () => {
  router.push('/huaxian')
}

// 查看战报
const viewReport = (activity) => {
  // 将战斗数据存到 sessionStorage，供战报页面使用
  const battle = allBattles.value[activity.battleIndex]
  if (battle) {
    sessionStorage.setItem('currentBattle', JSON.stringify(battle))
  }
  router.push({
    path: '/tower/report',
    query: { floor: activity.floor, type: towerType.value }
  })
}

// 查看守塔幻兽详情
const viewGuardianDetail = () => {
  router.push({
    path: '/tower/beast',
    query: {
      beastType: 'guardian',
      towerType: towerType.value,
      floor: endFloor.value,
    }
  })
}

// 查看玩家幻兽详情
const viewPlayerBeastDetail = (beastId) => {
  router.push({
    path: '/tower/beast',
    query: {
      beastType: 'player',
      beastId: beastId,
    }
  })
}

// 点击链接
const handleLink = (name) => {
  const routes = {
    '背包': '/inventory',
    '幻兽': '/beast',
    '地图': '/map',
    '擂台': '/arena',
    '闯塔': '/tower',
    '商城': '/shop',
  }
  if (routes[name]) {
    router.push(routes[name])
  } else {
    console.error(`点击了: ${name}`)
  }
}

// 加载战斗队幻兽
const loadTeamBeasts = async () => {
  try {
    const res = await http.get('/beast/team')
    if (res.data.ok) {
      myBeasts.value = res.data.beasts.map(b => ({
        id: b.id,
        name: b.name,
        realm: b.realm,
      }))
      // 计算总战力
      myPower.value = res.data.beasts.reduce((sum, b) => sum + (b.power || 0), 0)
    }
  } catch (e) {
    console.error('加载战斗队失败', e)
  }
}

onMounted(async () => {
  // 先加载战斗队幻兽
  await loadTeamBeasts()
  
  // 如果有缓存的自动闯塔结果，则直接恢复；否则调用接口重新计算
  const cacheKey = `autoTowerResult:${towerType.value}`
  const cached = sessionStorage.getItem(cacheKey)
  if (cached) {
    try {
      const { result, state } = JSON.parse(cached)
      applyAutoResult(result, state)
      loading.value = false
      return
    } catch (e) {
      console.error('解析自动闯塔缓存失败', e)
      sessionStorage.removeItem(cacheKey)
    }
  }
  startAutoChallenge()
})
</script>

<template>
  <div class="challenge-page">
    <!-- 加载中 -->
    <div v-if="loading" class="section">正在闯塔中...</div>
    
    <!-- 错误 -->
    <div v-else-if="error" class="section red">{{ error }}</div>
    
    <!-- 闯塔结果 -->
    <template v-else>
      <!-- 标题 -->
      <div class="section title">
        【{{ towerName }}-第{{ endFloor }}/{{ maxFloor }}层】 
        <a class="link" @click="refresh">刷新</a>
      </div>

      <div class="section">
        <a class="link" @click="goHuaXian">化仙</a>
      </div>

      <!-- 守塔幻兽 -->
      <div class="section">
        守塔幻兽: <a class="link" @click="viewGuardianDetail">{{ guardian.name }}</a> (Lv.{{ guardian.level }})
      </div>

    <!-- 我方幻兽 -->
    <div class="section">
      闯塔幻兽: 
      <template v-for="(beast, index) in myBeasts" :key="index">
        <a class="link" @click="viewPlayerBeastDetail(beast.id)">{{ beast.name }}-{{ beast.realm }}</a>
        <template v-if="index < myBeasts.length - 1"> | </template>
      </template>
    </div>
    <div class="section">
      综合战力: {{ myPower }}
    </div>

    <!-- 战斗信息 -->
    <div class="section">
      战斗结果: <span :class="battleResult === '挑战失败' ? 'red' : 'green'">{{ battleResult }}</span>
    </div>
    <div v-if="battleResult === '挑战失败'" class="section">
      <a class="link" @click="continueChallenge">重新挑战第{{ endFloor }}层</a>
      <span class="gray">（不消耗今日次数）</span>
    </div>
    <div v-else class="section">
      继续闯塔: <a class="link" @click="continueChallenge">继续挑战</a>
    </div>
    <div class="section">
      自动闯塔: <span class="green">{{ autoEnabled ? '已经开启' : '已关闭' }}</span>
    </div>

    <!-- 累计奖励 -->
    <div class="section">
      累计奖励: 铜钱×{{ rewards.gold }}
    </div>
    <div v-for="(item, idx) in mergedItems" :key="idx" class="section">
      {{ item.name }} ×{{ item.quantity }}
    </div>

    <!-- 退出 -->
    <div class="section">
      <a class="link" @click="exitChallenge">退出此次闯塔</a>
      <span class="gray">（发放累积奖励到背包）</span>
    </div>

    <!-- 闯塔动态 -->
    <div class="section title2">【闯塔动态】</div>
    <div v-for="(activity, index) in activities" :key="index" class="section">
      <span class="gray">({{ activity.time }})</span>{{ towerName }}第{{ activity.floor }}层,<span :class="activity.isVictory ? 'green' : 'red'">{{ activity.result }}</span> 
      <a class="link" @click="viewReport(activity)">详细战报</a>
    </div>

    <!-- 返回首页 -->
    <div class="section spacer">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
    </template>

  </div>
</template>

<style scoped>
.challenge-page {
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

.gray {
  color: #666666;
}

.small {
  font-size: 11px;
}

.green {
  color: #009900;
}

.red {
  color: #CC0000;
}

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}
</style>
