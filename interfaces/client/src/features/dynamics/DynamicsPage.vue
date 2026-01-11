<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const dynamics = ref([])
const loading = ref(false)
const currentPage = ref(1)
const totalPages = ref(1)
const pageInput = ref('1')

const loadDynamics = async (page = 1) => {
  loading.value = true
  try {
    const res = await http.get('/dynamics/my-dynamics', { params: { page, page_size: 10 } })
    if (res.data.ok) {
      dynamics.value = res.data.dynamics || []
      currentPage.value = res.data.page || 1
      totalPages.value = res.data.total_pages || 1
      pageInput.value = String(currentPage.value)
    }
  } finally { loading.value = false }
}

const jumpToPage = () => {
  const page = parseInt(pageInput.value)
  if (page >= 1 && page <= totalPages.value) loadDynamics(page)
  else pageInput.value = String(currentPage.value)
}
const nextPage = () => { if (currentPage.value < totalPages.value) loadDynamics(currentPage.value + 1) }
const prevPage = () => { if (currentPage.value > 1) loadDynamics(currentPage.value - 1) }
const firstPage = () => { loadDynamics(1) }
const lastPage = () => { loadDynamics(totalPages.value) }
const goBack = () => { router.back() }
const goHome = () => { router.push('/') }

const viewBattleDetail = (dynamic) => {
  if (!dynamic.has_detail || !dynamic.battle_id) return
  router.push({
    path: '/dynamics/battle-report',
    query: {
      type: dynamic.battle_type,
      id: dynamic.battle_id
    }
  })
}

const viewPlayer = (playerId) => {
  if (!playerId) return
  router.push({
    path: '/player/detail',
    query: { id: playerId }
  })
}

onMounted(() => { loadDynamics(1) })
</script>

<template>
  <div class="dynamics-page">
    <div class="section title">【我的动态】</div>
    <div class="section dynamics-list">
      <div v-if="loading" class="item">加载中...</div>
      <div v-for="(d, index) in dynamics" :key="d.id" class="item">
        {{ index + 1 }}.({{ d.time }})
        <template v-if="d.opponent_name && d.opponent_id">
          <template v-for="(part, partIndex) in d.text.split(d.opponent_name)" :key="partIndex">
            <a 
              v-if="partIndex > 0" 
              class="link player-name" 
              @click="viewPlayer(d.opponent_id)"
            >{{ d.opponent_name }}</a>
            <span>{{ part }}</span>
          </template>
        </template>
        <span v-else>{{ d.text }}</span>
        <a v-if="d.has_detail" class="link" @click="viewBattleDetail(d)">查看</a>
      </div>
      <div v-if="!loading && dynamics.length === 0" class="item gray">暂无动态</div>
    </div>
    <div class="section pager">
      <a class="link" @click="prevPage" v-if="currentPage > 1">上页</a>
      <a class="link" @click="firstPage" v-if="currentPage > 1">首页</a>
      <a class="link" @click="nextPage" v-if="currentPage < totalPages">下页</a>
      <a class="link" @click="lastPage" v-if="currentPage < totalPages">末页</a>
      <span>{{ currentPage }}/{{ totalPages }}页</span>
      <input v-model="pageInput" type="number" class="page-input" />
      <button class="btn" @click="jumpToPage">跳转</button>
    </div>
    <div class="section"><a class="link" @click="goBack">返回前页</a></div>
    <div class="section"><a class="link" @click="goHome">返回游戏首页</a></div>
  </div>
</template>

<style scoped>
.dynamics-page { background: #FFF8DC; min-height: 100vh; padding: 8px 12px; font-size: 13px; line-height: 1.6; font-family: SimSun, "宋体", serif; }
.section { margin: 4px 0; }
.title { font-weight: bold; margin-bottom: 8px; }
.dynamics-list { border: 1px solid #ddd; padding: 8px; min-height: 200px; }
.item { margin: 4px 0; padding: 2px 0; }
.gray { color: #666; }
.pager { display: flex; gap: 8px; align-items: center; }
.page-input { width: 50px; padding: 2px 4px; border: 1px solid #ccc; text-align: center; }
.btn { padding: 4px 12px; background: #0066CC; color: white; border: 1px solid #0066CC; cursor: pointer; font-size: 13px; }
.link { color: #0066CC; cursor: pointer; text-decoration: underline; }
.link:hover { text-decoration: underline; }
.player-name { color: #0066CC; }
</style>
