<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

// 当前排行类型
const currentType = ref('level')
const types = [
  { key: 'level', name: '等级' },
  { key: 'power', name: '战力' },
  { key: 'arena', name: '擂台' },
  { key: 'tower', name: '通天塔' },
  { key: 'dragon', name: '龙纹塔' },
  { key: 'achieve', name: '成就' },
  { key: 'charm', name: '魅力' },
  { key: 'vip', name: 'VIP' },
]

// 排行数据
const myRank = ref(0)
const rankings = ref([])
const loading = ref(false)

// 擂台筛选（阶段/全部）
const arenaRankName = ref('') // 服务器返回的当前阶段名，例如“天龙”
const arenaFilter = ref('stage') // 'stage' 当前阶段 | 'all' 全部

// 分页
const currentPage = ref(1)
const totalPages = ref(1)
const pageSize = 10

// 加载排行数据
const loadRankings = async () => {
  loading.value = true
  try {
    let url = `/ranking/list?type=${currentType.value}&page=${currentPage.value}&size=${pageSize}`
    if (currentType.value === 'arena') {
      // arena筛选：stage=按当前阶段；all=全部
      if (arenaFilter.value === 'all') {
        // 不带rank参数 = 全部擂台
      } else if (arenaRankName.value) {
        url += `&rank=${encodeURIComponent(arenaRankName.value)}`
      }
    }
    const res = await http.get(url)
    if (res.data.ok) {
      myRank.value = res.data.myRank || 0
      rankings.value = res.data.rankings || []
      totalPages.value = res.data.totalPages || 1
      if (currentType.value === 'arena') {
        arenaRankName.value = res.data.arenaRankName || arenaRankName.value
      }
    }
  } catch (e) {
    console.error('加载排行失败', e)
  } finally {
    loading.value = false
  }
}

// 切换排行类型
const switchType = (type) => {
  currentType.value = type
  currentPage.value = 1
  // 重置擂台筛选
  if (type === 'arena') {
    arenaFilter.value = 'stage'
  }
  loadRankings()
}

// 跳转页码
const goToPage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  loadRankings()
}

// 输入页码跳转
const pageInput = ref(1)
const jumpToPage = () => {
  const page = parseInt(pageInput.value)
  if (page >= 1 && page <= totalPages.value) {
    goToPage(page)
  }
}

// 查看玩家信息
const viewPlayer = (player) => {
  router.push(`/player?id=${player.userId}`)
}

onMounted(() => {
  // 从路由读取初始类型与rank
  const t = route.query.type
  if (t && ['level','power','arena','tower','dragon','achieve','charm','vip'].includes(t)) {
    currentType.value = t
  }
  const r = route.query.rank
  if (r) {
    arenaFilter.value = r === 'all' ? 'all' : 'stage'
    if (r !== 'all') arenaRankName.value = String(r)
  }
  loadRankings()
})

// 点击链接
const handleLink = (name) => {
  const routes = {
    '背包': '/inventory',
    '幻兽': '/beast',
    '地图': '/map',
    '擂台': '/arena',
    '闯塔': '/tower',
    '排行': '/ranking',
    '商城': '/shop',
    'VIP': '/vip',
    '提升': '/vip',
    '活力': '/vip',
    '兑换': '/exchange',
  }
  if (routes[name]) {
    router.push(routes[name])
  } else {
    alert(`点击了: ${name}`)
  }
}

// 返回首页
const goHome = () => {
  router.push('/')
}

// 获取排名显示值
const getRankValue = (player) => {
  switch (currentType.value) {
    case 'level':
      return player.prestige || 0
    case 'power':
      return player.power || 0
    case 'arena':
      return player.successCount || 0
    case 'tower':
      return player.towerFloor || 0
    default:
      return player.value || 0
  }
}

// 获取排名显示标签
const getRankLabel = () => {
  switch (currentType.value) {
    case 'level':
      return '声望'
    case 'power':
      return '战力'
    case 'arena':
      return '守擂成功数'
    case 'tower':
      return '层数'
    default:
      return '数值'
  }
}

// 切换擂台范围（阶段/全部）
const switchArenaScope = (scope) => {
  arenaFilter.value = scope // 'stage' | 'all'
  currentPage.value = 1
  loadRankings()
}
</script>

<template>
  <div class="ranking-page">
    <!-- 类型切换 -->
    <div class="section type-row">
      <template v-for="(t, index) in types.slice(0, 4)" :key="t.key">
        <a 
          class="link" 
          :class="{ active: currentType === t.key }"
          @click="switchType(t.key)"
        >{{ t.name }}</a>
        <span v-if="index < 3"> | </span>
      </template>
    </div>
    <div class="section type-row">
      <template v-for="(t, index) in types.slice(4)" :key="t.key">
        <a 
          class="link" 
          :class="{ active: currentType === t.key }"
          @click="switchType(t.key)"
        >{{ t.name }}</a>
        <span v-if="index < types.slice(4).length - 1"> | </span>
      </template>
    </div>

    <!-- 擂台专用头部（阶段/全部切换） -->
    <template v-if="currentType === 'arena'">
      <div class="section header">
        （<a class="link" :class="{active: arenaFilter==='stage'}" @click="switchArenaScope('stage')">{{ arenaRankName || '本阶段' }}擂台</a>
        | <a class="link" :class="{active: arenaFilter==='all'}" @click="switchArenaScope('all')">全部擂台</a>）
      </div>
    </template>

    <!-- 我的排名提示 -->
    <div class="section" v-if="currentType !== 'arena'">
      我的排名: <span class="orange">{{ myRank > 0 ? myRank : '未上榜' }}</span>
    </div>
    <div class="section" v-else>
      您的排名为第<span class="orange">{{ myRank > 0 ? myRank : '未上榜' }}</span>名
    </div>

    <!-- 表头 -->
    <div class="section header">
      <template v-if="currentType === 'arena'">
        排名.名称.擂台.守擂成功次数
      </template>
      <template v-else>
        排名.用户名.等级.{{ getRankLabel() }}
      </template>
    </div>

    <!-- 排名列表 -->
    <div v-if="loading" class="section">加载中...</div>
    <template v-else>
      <template v-if="currentType === 'arena'">
        <div v-for="player in rankings" :key="player.rank" class="section rank-item">
          <span class="rank">{{ player.rank }}.</span>
          <a class="link username" @click="viewPlayer(player)">{{ player.nickname }}</a>
          <span class="icon">🦋</span>.
          {{ (arenaFilter==='stage' ? (arenaRankName + '擂台') : '全部擂台') }}.
          {{ player.successCount }}
        </div>
      </template>
      <template v-else>
        <div v-for="player in rankings" :key="player.rank" class="section rank-item">
          <span class="rank">{{ player.rank }}.</span>
          <a class="link username" @click="viewPlayer(player)">{{ player.nickname }}</a>
          <span class="icon">🐦</span>.
          ({{ player.level }}级).
          {{ getRankValue(player) }}
        </div>
      </template>
    </template>

    <!-- 分页 -->
    <div class="section pager">
      <a class="link" @click="goToPage(currentPage + 1)" v-if="currentPage < totalPages">下页</a>
      <a class="link" @click="goToPage(totalPages)" v-if="currentPage < totalPages"> 末页</a>
    </div>
    <div class="section pager">
      {{ currentPage }}/{{ totalPages }}页
      <input type="number" v-model="pageInput" class="page-input" min="1" :max="totalPages" />
      <button @click="jumpToPage" class="jump-btn">跳转</button>
    </div>

    <!-- 返回首页 -->
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.ranking-page {
  padding: 10px;
  font-size: 14px;
  background: #f5f5dc;
  min-height: 100vh;
}

.section {
  margin: 8px 0;
  line-height: 1.6;
}

.type-row {
  margin-bottom: 5px;
}

.link {
  color: #1e90ff;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.link.active {
  color: #333;
  font-weight: bold;
}

.link.username {
  color: #cc0000;
}

.orange {
  color: #ff6600;
}

.header {
  color: #666;
}

.rank-item {
  line-height: 1.8;
}

.rank {
  display: inline-block;
  min-width: 25px;
}

.icon {
  color: #ffcc00;
}

.pager {
  margin-top: 15px;
}

.page-input {
  width: 50px;
  padding: 2px 5px;
  margin: 0 5px;
}

.jump-btn {
  padding: 2px 10px;
  cursor: pointer;
}
</style>
