<script setup>
import { computed, ref, onMounted, watch } from 'vue'
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
  { key: 'vip', name: 'VIP' },
]

// 排行数据
const myRank = ref(0)
const rankings = ref([])
const loading = ref(false)

// 擂台筛选（阶段/全部）
const arenaRankName = ref('') // 当前赛区名，例如“天龙”
const arenaZones = ref([]) // 服务器返回可用赛区
const arenaTime = ref('week') // week|total
const arenaScope = ref('zone') // zone|all

const powerRank = ref('total') // total | rankName | arena

// 兼容：老后端不返回 arenaZones，这里给一个前端默认值，保证 UI 可用
const DEFAULT_ARENA_ZONES = [
  { name: '黄阶', min_level: 20, max_level: 29 },
  { name: '玄阶', min_level: 30, max_level: 39 },
  { name: '地阶', min_level: 40, max_level: 49 },
  { name: '天阶', min_level: 50, max_level: 59 },
  { name: '飞马', min_level: 60, max_level: 69 },
  { name: '天龙', min_level: 70, max_level: 79 },
  { name: '战神', min_level: 80, max_level: 100 },
]

// 分页
const currentPage = ref(1)
const totalPages = ref(1)
const pageSize = 10

// 加载排行数据
const loadRankings = async () => {
  loading.value = true
  try {
    let url = `/ranking/list?type=${currentType.value}&page=${currentPage.value}&size=${pageSize}`
    if (currentType.value === 'power') {
      if (powerRank.value && powerRank.value !== 'total') {
        url += `&rank=${encodeURIComponent(powerRank.value)}`
      }
    }
    if (currentType.value === 'arena') {
      // 擂台：只显示赛区排行（按 rank_name）
      if (arenaRankName.value) {
        url += `&rank=${encodeURIComponent(arenaRankName.value)}`
      }
      url += `&time=${encodeURIComponent(arenaTime.value)}`
      url += `&scope=${encodeURIComponent(arenaScope.value)}`
    }
    const res = await http.get(url)
    if (res.data.ok) {
      // 兼容新/老后端：
      // - 新：rankings / totalPages / arenaZones
      // - 老：list / total / page / size
      myRank.value = res.data.myRank || 0

      const rawList = res.data.rankings || res.data.list || []
      const list = Array.isArray(rawList) ? rawList : []
      // 老后端 list 没有 rank 字段，这里补齐，避免模板渲染报错/卡住
      rankings.value = list.map((it, idx) => ({
        ...it,
        rank: Number(it?.rank || (currentPage.value - 1) * pageSize + idx + 1),
      }))

      const total = Number(res.data.total || 0)
      totalPages.value = Number(res.data.totalPages || (total ? Math.ceil(total / pageSize) : 1)) || 1

      // 老后端不返回 arenaZones / arenaRankName：用前端默认值兜底
      arenaZones.value = res.data.arenaZones || arenaZones.value || DEFAULT_ARENA_ZONES
      arenaRankName.value = res.data.arenaRankName || arenaRankName.value || ''
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
  router.push({ path: '/player/detail', query: { id: player.userId } })
}

onMounted(() => {
  // 从路由读取初始类型与rank
  const t = route.query.type
  if (t && ['level','power','arena','vip'].includes(t)) {
    currentType.value = t
  }
  const r = route.query.rank
  if (r) {
    arenaRankName.value = String(r)
  }
  loadRankings()
})

// 返回首页
const goHome = () => {
  router.push('/')
}

const headerText = computed(() => {
  if (currentType.value === 'level') return '排名.用户名.等级.声望'
  if (currentType.value === 'power') return '排名.主角.战力'
  if (currentType.value === 'arena') return '排名.名称.擂台.守擂成功次数'
  return '排名.主角.VIP等级'
})

const selectArenaZone = (name) => {
  arenaRankName.value = String(name || '').trim()
  currentPage.value = 1
  loadRankings()
}

const selectArenaTime = (time) => {
  arenaTime.value = time // week|total
  currentPage.value = 1
  loadRankings()
}

const selectArenaScope = (scope) => {
  arenaScope.value = scope // zone|all
  currentPage.value = 1
  loadRankings()
}

const selectPowerRank = (rankName) => {
  powerRank.value = rankName
  currentPage.value = 1
  loadRankings()
}

const displayZoneName = (z) => {
  if (!z) return ''
  // 参考页：北斗(80-100级)；本项目段位为“战神”，这里仅做展示名称对齐
  if (z.name === '战神') return '北斗'
  return z.name
}

// 擂台分级显示（按你的指定格式）
const formatZoneText = (z) => {
  if (!z) return ''
  if (z.name === '战神') return '战神: Lv.80以上'
  return `${z.name}: Lv.${z.min_level}-${z.max_level}`
}

// 进入擂台时，如果没有默认赛区（未登录时后端不会推断赛区），自动选择黄阶（而非见习）
const autoInitArenaZoneDone = ref(false)
watch(
  () => currentType.value,
  (t) => {
    if (t !== 'arena') return
    autoInitArenaZoneDone.value = false
  },
)
watch(
  () => [currentType.value, arenaRankName.value, arenaZones.value.length, loading.value],
  () => {
    if (currentType.value !== 'arena') return
    if (loading.value) return
    if (autoInitArenaZoneDone.value) return
    if (!arenaRankName.value && arenaZones.value.length) {
      // 优先选择"黄阶"，如果没有则选第一个
      const huangJie = arenaZones.value.find((z) => z.name === '黄阶')
      const target = huangJie || arenaZones.value[0]
      if (target?.name) {
        autoInitArenaZoneDone.value = true
        selectArenaZone(target.name)
      }
    }
  },
)

</script>

<template>
  <div class="ranking-page">
    <!-- 顶部导航（严格模仿参考页：选中项为纯文本，其他为链接，分隔符为“｜”） -->
    <div class="section type-row">
      <span v-for="(t, index) in types" :key="t.key">
        <template v-if="currentType === t.key">
          <span>{{ t.name }}</span>
        </template>
        <template v-else>
          <a class="link" @click="switchType(t.key)">{{ t.name }}</a>
        </template>
        <span v-if="index < types.length - 1">｜</span>
      </span>

      <template v-if="currentType === 'arena' && arenaRankName">
        <span style="margin-left: 6px;">｜ {{ arenaRankName }}擂台</span>
      </template>
    </div>

      <!-- 战力：二级段位导航（仅保留分段 + 总排行；按需求删除“竞技擂台”） -->
    <template v-if="currentType === 'power' && arenaZones.length">
      <div class="section zone-row">
        <span v-for="z in arenaZones" :key="z.name">
          <template v-if="powerRank === z.name">
            <span>{{ displayZoneName(z) }}({{ z.min_level }}-{{ z.max_level }}级)</span>
          </template>
          <template v-else>
            <a class="link" @click="selectPowerRank(z.name)">{{ displayZoneName(z) }}({{ z.min_level }}-{{ z.max_level }}级)</a>
          </template>
          <span>｜</span>
        </span>

        <template v-if="powerRank === 'total'">
          <span>总排行</span>
        </template>
        <template v-else>
          <a class="link" @click="selectPowerRank('total')">总排行</a>
        </template>
      </div>
    </template>

    <!-- 擂台：英豪榜结构（周英豪榜|总英豪榜）（赛区擂台|全部擂台） -->
    <template v-if="currentType === 'arena'">
      <div class="section zone-row">
        <template v-if="arenaTime === 'week'">
          <span>周英豪榜</span>
        </template>
        <template v-else>
          <a class="link" @click="selectArenaTime('week')">周英豪榜</a>
        </template>
        <span>|</span>
        <template v-if="arenaTime === 'total'">
          <span>总英豪榜</span>
        </template>
        <template v-else>
          <a class="link" @click="selectArenaTime('total')">总英豪榜</a>
        </template>
      </div>

      <!-- 分级擂台排行：黄阶/玄阶/.../战神: Lv.80以上 -->
      <template v-if="arenaZones.length">
        <div class="section zone-row">
          <span v-for="(z, idx) in arenaZones" :key="z.name">
            <template v-if="arenaRankName === z.name">
              <span>{{ formatZoneText(z) }}</span>
            </template>
            <template v-else>
              <a class="link" @click="selectArenaZone(z.name)">{{ formatZoneText(z) }}</a>
            </template>
            <span v-if="idx < arenaZones.length - 1">｜</span>
          </span>
        </div>
      </template>

      <!-- 按需求：不再展示“（xx擂台 | 全部擂台）”，只展示“xx擂台” -->
      <div class="section header">{{ (arenaRankName || '本阶段') }}擂台</div>

      <div class="section" v-if="!myRank">您当前暂无排名</div>
    </template>

    <!-- 我的排名提示 -->
    <template v-if="currentType !== 'vip'">
      <div class="section">我的排名: {{ myRank > 0 ? myRank : '未上榜' }}</div>
    </template>

    <!-- 表头（参考页：等级在“我的排名”之后；VIP在“表头”之后显示“我的排名”） -->
    <div class="section header">{{ headerText }}</div>
    <template v-if="currentType === 'vip'">
      <div class="section">我的排名: {{ myRank > 0 ? myRank : '未上榜' }}</div>
    </template>

    <!-- 排名列表 -->
    <div v-if="loading" class="section">加载中...</div>
    <template v-else>
      <div v-if="!rankings.length" class="section">无</div>
      <div v-for="player in rankings" :key="player.rank" class="section rank-item">
        <span class="rank">{{ player.rank }}.</span>
        <a class="link username" @click="viewPlayer(player)">{{ player.nickname }}</a>
        <span v-if="player.vipLevel > 0" class="vip-icon">👑</span>

        <template v-if="currentType === 'level'">
          . ({{ player.level }}级). {{ player.prestige ?? player.exp ?? 0 }}
        </template>
        <template v-else-if="currentType === 'power'">
          . {{ player.power || 0 }}
        </template>
        <template v-else-if="currentType === 'arena'">
          . {{ (player.rankName || arenaRankName || '') }}擂台. {{ player.successCount || 0 }}
        </template>
        <template v-else>
          . VIP{{ player.vipLevel || 0 }}
        </template>
      </div>
    </template>

    <!-- 分页 -->
    <div class="section pager">
      <a class="link" @click="goToPage(currentPage + 1)" v-if="currentPage < totalPages">下页</a>
      <a class="link" @click="goToPage(totalPages)" v-if="currentPage < totalPages">末页</a>
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

    <template v-if="currentType === 'arena'">
      <div class="section">
        <a class="link" @click="router.push('/arena')">返回擂台首页</a>
      </div>
    </template>
  </div>
</template>

<style scoped>
.ranking-page {
  padding: 10px;
  font-size: 19px;
  background: #FFFFFF;
  min-height: 100vh;
  padding: 12px 16px;
  font-size: 18px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 8px 0;
  line-height: 1.6;
}

.type-row {
  margin-bottom: 5px;
}

.zone-row {
  margin-bottom: 6px;
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

.vip-icon {
  margin: 0 2px;
  font-size: 13px;
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
