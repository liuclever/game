<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

// ========== 加载状态 ==========
const loading = ref(true)
const errorMsg = ref('')

// ========== 幻兽列表 ==========
const beastList = ref([])

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

// ========== 加载数据 ==========
const loadData = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await http.get('/beast/list')
    if (res.data.ok) {
      beastList.value = res.data.beastList || []
    } else {
      errorMsg.value = res.data.error || '加载失败'
    }
  } catch (err) {
    errorMsg.value = '网络错误，请稍后重试'
    console.error('加载数据失败:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})

// ========== 操作 ==========
// 分配经验给幻兽
const allocateExp = (beast) => {
  router.push(`/huaxian/allocate/${beast.id}`)
}

// ========== 导航 ==========
const goBack = () => {
  router.push('/huaxian')
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="allocate-page">
    <!-- 加载状态 -->
    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMsg" class="section" style="color: red;">{{ errorMsg }}</div>
    
    <template v-if="!loading">
      <!-- 标题 -->
      <div class="section title">
        【化仙池经验分配】
      </div>
      
      <!-- 幻兽列表 -->
      <template v-if="pagedBeasts.length > 0">
        <template v-for="beast in pagedBeasts" :key="beast.id">
          <div class="section">
            <a class="link">{{ beast.name }}<template v-if="beast.realm">-{{ beast.realm }}</template></a>({{ beast.level }}级) <a class="link" @click="allocateExp(beast)">分配</a>
          </div>
          <div class="section">
            战力:{{ beast.power || 0 }}
          </div>
        </template>
      </template>
      <div v-else class="section gray">
        暂无幻兽
      </div>
      
      <!-- 分页 -->
      <div class="section spacer" v-if="beastList.length > pageSize">
        <a class="link" @click="nextPage">下页</a> <a class="link" @click="lastPage">末页</a>
      </div>
      <div class="section" v-if="beastList.length > pageSize">
        {{ currentPage }}/{{ totalPages }}页 
        <input type="text" v-model="jumpPage" class="page-input" />
        <button class="page-btn" @click="goToPage">跳转</button>
      </div>
    </template>

    <!-- 返回 -->
    <div class="section spacer">
      <a class="link" @click="goBack">返回前页</a>
    </div>
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>

  </div>
</template>

<style scoped>
.allocate-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 16px;
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
  font-size: 17px;
}

.page-input {
  width: 40px;
  font-size: 18px;
  border: 1px solid #CCCCCC;
  padding: 1px 4px;
}

.page-btn {
  font-size: 18px;
  padding: 1px 8px;
  background: #ffffff;
  border: 1px solid #CCCCCC;
  cursor: pointer;
}

.page-btn:hover {
  background: #ffffff;
}

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}
</style>
