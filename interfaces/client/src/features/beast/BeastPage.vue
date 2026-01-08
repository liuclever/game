<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

// ========== 加载状态 ==========
const loading = ref(true)
const errorMsg = ref('')

// ========== 玩家信息 ==========
const playerLevel = ref(1)
const maxTeamSize = ref(1)

// ========== 战斗队伍 ==========
const battleTeam = ref([])

// ========== 幻兽栏 ==========
const beastList = ref([])

const maxBeastSlots = ref(14)
const storageCount = ref(0)
const maxStorage = ref(0)
const hasAlliance = ref(false)
const storageVisible = ref(false)
const storageLoading = ref(false)
const storageError = ref('')
const storageList = ref([])

// ========== 加载数据 ==========
const loadBeastData = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await http.get('/beast/list')
    if (res.data.ok) {
      playerLevel.value = res.data.playerLevel
      maxTeamSize.value = res.data.maxTeamSize
      maxBeastSlots.value = res.data.maxBeastSlots
      storageCount.value = res.data.storageCount
      maxStorage.value = res.data.maxStorage
      hasAlliance.value = !!res.data.hasAlliance
      beastList.value = res.data.beastList
      battleTeam.value = res.data.teamBeasts
    } else {
      errorMsg.value = res.data.error || '加载失败'
    }
  } catch (err) {
    errorMsg.value = '网络错误，请稍后重试'
    console.error('加载幻兽数据失败:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadBeastData()
})

// ========== 分页 ==========
const currentPage = ref(1)
const pageSize = 5
const jumpPage = ref(1)

const totalPages = computed(() => {
  return Math.max(1, Math.ceil(beastList.value.length / pageSize))
})

const pagedBeasts = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return beastList.value.slice(start, start + pageSize)
})

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
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

// ========== 队伍操作 ==========
// 换下（从队伍移除）
const removeFromTeam = async (beast) => {
  try {
    const res = await http.post('/beast/leave-team', { beastId: beast.id })
    if (res.data.ok) {
      await loadBeastData()  // 重新加载数据
    } else {
      alert(res.data.error || '操作失败')
    }
  } catch (err) {
    alert('网络错误')
    console.error(err)
  }
}

// 上移
const moveUp = async (beast) => {
  try {
    const res = await http.post('/beast/move-up', { beastId: beast.id })
    if (res.data.ok) {
      await loadBeastData()  // 重新加载数据
    } else {
      alert(res.data.error || '操作失败')
    }
  } catch (err) {
    alert('网络错误')
    console.error(err)
  }
}

// 加入队伍
const addToTeam = async (beast) => {
  try {
    const res = await http.post('/beast/join-team', { beastId: beast.id })
    if (res.data.ok) {
      await loadBeastData()  // 重新加载数据
    } else {
      alert(res.data.error || '操作失败')
    }
  } catch (err) {
    alert('网络错误')
    console.error(err)
  }
}

const loadStorageList = async () => {
  storageLoading.value = true
  storageError.value = ''
  try {
    const res = await http.get('/alliance/beast-storage')
    if (res.data.ok) {
      storageList.value = res.data.storageList || []
      storageCount.value = res.data.count ?? storageCount.value
      maxStorage.value = res.data.capacity ?? maxStorage.value
    } else {
      storageError.value = res.data.error || '加载失败'
    }
  } catch (err) {
    console.error('加载幻兽室失败:', err)
    storageError.value = '网络错误，请稍后重试'
  } finally {
    storageLoading.value = false
  }
}

const openStorage = async () => {
  if (!hasAlliance.value) {
    alert('加入联盟后才能使用幻兽室')
    return
  }
  storageVisible.value = true
  await loadStorageList()
}

const closeStorage = () => {
  storageVisible.value = false
}

const storeToStorage = async (beast) => {
  if (!hasAlliance.value) {
    alert('加入联盟后才能寄存幻兽')
    return
  }
  if (storageCount.value >= maxStorage.value) {
    alert('幻兽室已满，请先取回一只幻兽')
    return
  }
  try {
    const res = await http.post('/alliance/beast-storage/store', { beastId: beast.id })
    if (res.data.ok) {
      alert('寄存成功')
      await loadBeastData()
      if (storageVisible.value) {
        await loadStorageList()
      }
    } else {
      alert(res.data.error || '寄存失败')
    }
  } catch (err) {
    console.error('寄存失败:', err)
    alert('网络错误，请稍后重试')
  }
}

const retrieveFromStorage = async (record) => {
  try {
    const res = await http.post('/alliance/beast-storage/retrieve', { storageId: record.storageId })
    if (res.data.ok) {
      alert('幻兽已取回')
      await loadBeastData()
      await loadStorageList()
    } else {
      alert(res.data.error || '取回失败')
    }
  } catch (err) {
    console.error('取回失败:', err)
    alert('网络错误，请稍后重试')
  }
}

const formatStoredAt = (value) => {
  if (!value) return ''
  try {
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) {
      return value
    }
    return date.toLocaleString()
  } catch (err) {
    return value
  }
}

// ========== 导航 ==========
const goHome = () => {
  router.push('/')
}

const goTower = () => {
  router.push('/tower')
}

// 查看幻兽详情
const viewBeastDetail = (beast) => {
  router.push(`/beast/${beast.id}`)
}

const handleLink = (name) => {
  if (name === '寄存室') {
    openStorage()
    return
  }
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
</script>

<template>
  <div class="beast-page">
    <!-- 加载状态 -->
    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMsg" class="section" style="color: red;">{{ errorMsg }}</div>
    
    <!-- 战斗队 -->
    <div v-if="!loading" class="section title">
      【战斗队({{ battleTeam.length }}/{{ maxTeamSize }})】
    </div>
    <div v-for="(beast, index) in battleTeam" :key="beast.id" class="section">
      {{ index + 1 }}. <a class="link" @click="viewBeastDetail(beast)">{{ beast.name }}-{{ beast.realm }}</a> ({{ beast.level }}级) 
      <a class="link" @click="removeFromTeam(beast)">换下</a>
      <template v-if="index > 0">
        <a class="link" @click="moveUp(beast)"> 上</a>
      </template>
    </div>
    <div class="section">
      <a class="link" @click="handleLink('战场')">战场</a>. 
      <a class="link" @click="goTower">闯塔</a>. 
      <span class="link readonly">切磋</span>. 
      <a class="link" @click="handleLink('地图')">地图</a>. 
      <a class="link" @click="handleLink('擂台')">擂台</a>
    </div>

    <!-- 幻兽栏 -->
    <div v-if="!loading" class="section title">
      【幻兽栏({{ beastList.length }}/{{ maxBeastSlots }})】<a class="link" @click="handleLink('寄存室')">寄存室({{ storageCount }}/{{ maxStorage }})</a>
    </div>
    <template v-for="(beast, index) in pagedBeasts" :key="beast.id">
      <div class="section">
        {{ (currentPage - 1) * pageSize + index + 1 }}. <a class="link" @click="viewBeastDetail(beast)">{{ beast.name }}-{{ beast.realm }}</a>({{ beast.level }}级) 
        <template v-if="beast.inTeam">
          <span class="gray">(出战中)</span>
        </template>
        <template v-else>
          <a class="link" @click="addToTeam(beast)">出战</a>
          <a class="link" @click="storeToStorage(beast)"> 寄存</a>
        </template>
      </div>
      <div class="section indent">
        综合战力: {{ beast.power }}
      </div>
    </template>

    <!-- 分页 -->
    <div class="section" v-if="beastList.length > pageSize">
      <a class="link" @click="nextPage">下页</a> 
      <a class="link" @click="lastPage">末页</a>
      {{ currentPage }}/{{ totalPages }}页 
      <input type="text" v-model="jumpPage" class="page-input" />
      <button class="page-btn" @click="goToPage">跳转</button>
    </div>

    <!-- 返回 -->
    <div class="section spacer">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>

    <!-- 版权 -->

    <!-- 联盟幻兽室 -->
    <div v-if="storageVisible" class="storage-overlay">
      <div class="storage-panel">
        <div class="storage-header">
          <span>联盟幻兽室 ({{ storageCount }}/{{ maxStorage }})</span>
          <button class="close-btn" @click="closeStorage">关闭</button>
        </div>
        <div class="storage-body">
          <div v-if="storageLoading" class="storage-status">加载中...</div>
          <div v-else-if="storageError" class="storage-status error">{{ storageError }}</div>
          <template v-else>
            <div class="storage-summary">
              联盟等级决定容量。当前还可寄存 <strong>{{ Math.max(0, maxStorage - storageCount) }}</strong> 只幻兽。
            </div>
            <div v-if="!storageList.length" class="storage-empty">当前没有寄存的幻兽。</div>
            <div v-else class="storage-list">
              <div v-for="record in storageList" :key="record.storageId" class="storage-item">
                <div class="storage-item-main">
                  <div class="storage-name">{{ record.name || ('幻兽 #' + record.beastId) }}</div>
                  <div class="storage-meta">
                    Lv.{{ record.level || 1 }}
                    <span class="divider">|</span>
                    存入时间：{{ formatStoredAt(record.storedAt) || '未知' }}
                  </div>
                </div>
                <div class="storage-actions">
                  <button 
                    v-if="record.ownerIsSelf" 
                    class="link-btn" 
                    @click="retrieveFromStorage(record)"
                  >
                    取回
                  </button>
                  <span v-else class="gray small">盟友寄存</span>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.beast-page {
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
  margin-top: 12px;
  margin-bottom: 4px;
}

.title:first-child {
  margin-top: 0;
}

.indent {
  padding-left: 16px;
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

.gray {
  color: #666666;
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

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}

.storage-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding-top: 40px;
  z-index: 99;
}

.storage-panel {
  width: min(520px, 92%);
  background: #FFFDF7;
  border: 1px solid #B8860B;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
  border-radius: 6px;
  overflow: hidden;
}

.storage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: linear-gradient(90deg, #F6E2B3, #FADFA0);
  font-weight: bold;
  color: #805A08;
}

.close-btn {
  border: none;
  background: transparent;
  color: #805A08;
  cursor: pointer;
  font-size: 13px;
}

.storage-body {
  max-height: 360px;
  overflow-y: auto;
  padding: 12px;
}

.storage-summary {
  font-size: 12px;
  margin-bottom: 8px;
  color: #8B4513;
}

.storage-empty {
  text-align: center;
  color: #777;
  padding: 40px 0;
}

.storage-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.storage-item {
  border: 1px solid #E0C48C;
  border-radius: 6px;
  padding: 8px 10px;
  background: #FFF9EC;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.storage-item-main {
  max-width: calc(100% - 90px);
}

.storage-name {
  font-weight: bold;
  color: #704214;
}

.storage-meta {
  font-size: 12px;
  color: #7A6A53;
}

.divider {
  margin: 0 6px;
  color: #C0A070;
}

.storage-actions {
  text-align: right;
}

.link-btn {
  border: none;
  background: none;
  color: #0066CC;
  cursor: pointer;
  font-size: 13px;
}

.storage-status {
  padding: 20px 0;
  text-align: center;
}

.storage-status.error {
  color: #C0392B;
}
</style>
