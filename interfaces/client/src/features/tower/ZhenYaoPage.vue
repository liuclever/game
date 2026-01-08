<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

// 加载状态
const loading = ref(true)
const error = ref('')

// 当前显示类型：trial = 试炼层, hell = 炼狱层
const floorType = ref('trial')

// 镇妖数据
const zhenyaoInfo = ref({
  canZhenyao: false,
  playerLevel: 0,
  rankName: '',
  zhenyaoRange: null,
  towerMaxFloor: 0,
  trialCount: 0,
  hellCount: 0,
  trialUsed: 0,         // 试炼层今日已用次数
  hellUsed: 0,          // 炼狱层今日已用次数
  trialLimit: 10,       // 试炼层每日上限
  hellLimit: 10,        // 炼狱层每日上限
  zhenyaoFu: 125,       // 镇妖符数量（预留）
})

// 层数列表
const floors = ref([])

// 分页
const currentPage = ref(1)
const pageSize = 10
const jumpPage = ref(1)

// 动态类型
const dynamicType = ref('all')  // 'all' = 全服动态, 'personal' = 个人动态

// 动态列表（预留）
const dynamics = ref([])

// 加载镇妖信息
const loadZhenyaoInfo = async () => {
  try {
    const res = await http.get('/zhenyao/info')
    zhenyaoInfo.value = {
      canZhenyao: res.data.can_zhenyao,
      playerLevel: res.data.player_level,
      rankName: res.data.rank_name,
      zhenyaoRange: res.data.zhenyao_range,
      towerMaxFloor: res.data.tower_max_floor,
      trialCount: res.data.trial_count,
      hellCount: res.data.hell_count,
      trialUsed: res.data.trial_used || 0,
      hellUsed: res.data.hell_used || 0,
      trialLimit: res.data.trial_limit || 10,
      hellLimit: res.data.hell_limit || 10,
      zhenyaoFu: 125,
    }
    if (!res.data.can_zhenyao) {
      error.value = res.data.error
    }
  } catch (e) {
    console.error('加载镇妖信息失败', e)
    error.value = '加载失败'
  }
}

// 加载层列表
const loadFloors = async () => {
  try {
    const res = await http.get(`/zhenyao/floors?type=${floorType.value}`)
    if (res.data.ok) {
      floors.value = res.data.floors
    } else {
      error.value = res.data.error
    }
  } catch (e) {
    console.error('加载层列表失败', e)
  } finally {
    loading.value = false
  }
}

// 切换试炼层/炼狱层
const switchFloorType = (type) => {
  floorType.value = type
  currentPage.value = 1
  loading.value = true
  loadFloors()
}

// 加载动态列表
const loadDynamics = async () => {
  try {
    const res = await http.get(`/zhenyao/dynamics?type=${dynamicType.value}`)
    if (res.data.ok) {
      dynamics.value = res.data.dynamics
    }
  } catch (e) {
    console.error('加载动态失败', e)
  }
}

// 切换动态类型
const switchDynamic = (type) => {
  dynamicType.value = type
  loadDynamics()
}

onMounted(async () => {
  // 检查URL参数
  if (route.query.type === 'hell') {
    floorType.value = 'hell'
  }
  await loadZhenyaoInfo()
  await loadFloors()
  await loadDynamics()
})

// 分页后的层数
const pagedFloors = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return floors.value.slice(start, start + pageSize)
})

// 总页数
const totalPages = computed(() => {
  return Math.max(1, Math.ceil(floors.value.length / pageSize))
})

// 翻页
const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

const firstPage = () => {
  currentPage.value = 1
}

const lastPage = () => {
  currentPage.value = totalPages.value
}

const goToPage = () => {
  const page = parseInt(jumpPage.value)
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

// 占领层
const occupyFloor = async (floor) => {
  try {
    const res = await http.post('/zhenyao/occupy', { floor: floor.floor })
    if (res.data.ok) {
      alert(res.data.message)
      loadFloors()  // 刷新列表
    } else {
      alert(res.data.error)
    }
  } catch (e) {
    console.error('占领失败', e)
    alert('占领失败')
  }
}

// 挑战层
const challengeFloor = async (floor) => {
  try {
    const res = await http.post('/zhenyao/challenge', { floor: floor.floor })
    if (res.data.ok) {
      // 跳转到战报页面
      router.push({
        path: '/tower/zhenyao/battle',
        query: { id: res.data.battle_id }
      })
    } else {
      alert(res.data.error)
    }
  } catch (e) {
    console.error('挑战失败', e)
    alert('挑战失败')
  }
}

// 查看战报
const viewBattle = (dynamic) => {
  router.push({
    path: '/tower/zhenyao/battle',
    query: { id: dynamic.id }
  })
}

// 查看玩家信息
const viewPlayer = (playerId) => {
  if (playerId) {
    router.push({
      path: '/player/profile',
      query: { id: playerId }
    })
  }
}

// 格式化剩余时间
const formatRemaining = (seconds) => {
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${minutes}分${secs}秒`
}

// 返回首页
const goHome = () => {
  router.push('/')
}

const refreshSettlement = async () => {
  loading.value = true
  await loadZhenyaoInfo()
  await loadFloors()
  await loadDynamics()
}

// 点击链接
const handleLink = (name) => {
  const routes = {
    '背包': '/inventory',
    '幻兽': '/beast',
    '地图': '/map',
    '擂台': '/arena',
    '闯塔': '/tower',
    '整理背包': '/inventory',
    '商城': '/shop',
  }
  if (routes[name]) {
    router.push(routes[name])
  } else if (name === '简介') {
    alert('镇妖简介')
  } else if (name === '刷新结算') {
    refreshSettlement()
  } else {
    alert(`点击了: ${name}`)
  }
}
</script>

<template>
  <div class="zhenyao-page">
    <!-- 标题 -->
    <div class="section title">
      【镇妖】 <a class="link" @click="handleLink('简介')">简介</a> |<a class="link" @click="handleLink('刷新结算')">刷新结算</a>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="section red">{{ error }}</div>

    <!-- 镇妖信息 -->
    <div class="section">
      镇妖符×{{ zhenyaoInfo.zhenyaoFu }}(试炼免费)
    </div>
    <div class="section">
      <a 
        class="link" 
        :class="{ active: floorType === 'trial' }"
        @click="switchFloorType('trial')"
      >试炼层</a>:<span class="orange">{{ zhenyaoInfo.trialLimit - zhenyaoInfo.trialUsed }}</span>/{{ zhenyaoInfo.trialLimit }}次 
      <a 
        class="link" 
        :class="{ active: floorType === 'hell' }"
        @click="switchFloorType('hell')"
      >炼狱层</a>:<span class="orange">{{ zhenyaoInfo.hellLimit - zhenyaoInfo.hellUsed }}</span>/{{ zhenyaoInfo.hellLimit }}次
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="section gray">加载中...</div>

    <!-- 层数列表 -->
    <template v-else-if="pagedFloors.length > 0">
      <div v-for="floor in pagedFloors" :key="floor.floor" class="section">
        <template v-if="floor.is_occupied">
          <!-- 被占领的层 -->
          第{{ floor.floor }}层 <a class="link username" @click="viewPlayer(floor.occupant_id)">{{ floor.occupant_name }}</a>
          <div class="section">
            剩余:{{ formatRemaining(floor.remaining_seconds) }}
            <template v-if="floor.can_action">
              <a class="link" @click="challengeFloor(floor)">挑战</a>
            </template>
            <template v-else>
              <span class="gray">不可挑战</span>
            </template>
          </div>
        </template>
        <template v-else>
          <!-- 空的层 -->
          第{{ floor.floor }}层 空.
          <template v-if="floor.can_action">
            <a class="link" @click="occupyFloor(floor)">占领</a>
          </template>
          <template v-else>
            <span class="gray">不可占领</span>
          </template>
        </template>
      </div>
    </template>
    <div v-else class="section gray">暂无可用层数</div>

    <!-- 分页 -->
    <div class="section">
      <a class="link" @click="nextPage">下页</a> 
      <a class="link" @click="prevPage">上页</a> 
      <a class="link" @click="firstPage">首页</a> 
      <a class="link" @click="lastPage">末页</a>
    </div>
    <div class="section">
      {{ currentPage }}/{{ totalPages }}页 
      <input 
        type="text" 
        v-model="jumpPage" 
        class="page-input"
      />
      <button class="page-btn" @click="goToPage">跳转</button>
    </div>

    <!-- 整理背包 -->
    <div class="section">
      <a class="link" @click="handleLink('整理背包')">整理背包</a>
    </div>

    <!-- 动态区域 -->
    <div class="section title2">
      【<a 
        class="link" 
        :class="{ active: dynamicType === 'all' }"
        @click="switchDynamic('all')"
      >全服动态</a>.<a 
        class="link"
        :class="{ active: dynamicType === 'personal' }"
        @click="switchDynamic('personal')"
      >个人动态</a>】
    </div>

    <!-- 动态列表 -->
    <template v-if="dynamics.length > 0">
      <div v-for="d in dynamics" :key="d.id" class="section dynamic-item">
        ({{ d.time }}){{ d.remaining }}，
        <span :class="d.success ? 'green' : 'red'">
          <a class="link username" @click="viewPlayer(d.attacker_id)">{{ d.attacker }}</a> 把 
          <a class="link username" @click="viewPlayer(d.defender_id)">{{ d.defender }}</a> 
          {{ d.success ? '打到落花流水，抢夺第' + d.floor + '层聚魂阵成功！' : '挑战第' + d.floor + '层聚魂阵失败！' }}
        </span>
        <a class="link" @click="viewBattle(d)">查看</a>
      </div>
    </template>
    <div v-else class="section gray">
      暂无动态
    </div>

    <!-- 返回首页 -->
    <div class="section spacer">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>

  </div>
</template>

<style scoped>
.zhenyao-page {
  background: #FFF8DC;
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

.link.active {
  color: #CC3300;
  font-weight: bold;
}

.gray {
  color: #666666;
}

.red {
  color: #CC0000;
}

.green {
  color: #009900;
}

.orange {
  color: #FF6600;
  font-weight: bold;
}

.link.username {
  color: #CC6600;
}

.dynamic-item {
  font-size: 12px;
}

.small {
  font-size: 11px;
}

.page-input {
  width: 40px;
  font-size: 12px;
  border: 1px solid #CCCCCC;
  padding: 1px 4px;
}

.page-btn {
  font-size: 12px;
  padding: 1px 8px;
  background: #F0F0F0;
  border: 1px solid #CCCCCC;
  cursor: pointer;
}

.page-btn:hover {
  background: #E0E0E0;
}

.dynamic-placeholder {
  font-style: italic;
}

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}
</style>
