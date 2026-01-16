<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

// 当前选中的赛区
const currentArea = ref(1) // 1 或 2

// 排名数据
const rankings = ref([])
const loading = ref(false)

// 分页
const currentPage = ref(1)
const pageSize = 10
const jumpPage = ref(1)

// 分页计算
const pagedRankings = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return rankings.value.slice(start, start + pageSize)
})

const totalPages = computed(() => {
  return Math.max(1, Math.ceil(rankings.value.length / pageSize))
})

// 加载排名数据
const loadRankings = async () => {
  loading.value = true
  try {
    const res = await http.get('/king/ranking', {
      params: { area: currentArea.value }
    })
    if (res.data.ok) {
      rankings.value = res.data.rankings || []
    }
  } catch (e) {
    console.error('加载排名失败', e)
    // 使用模拟数据
    rankings.value = generateMockData()
  } finally {
    loading.value = false
  }
}

// 生成模拟数据
const generateMockData = () => {
  const names = [
    '终焉', '1000出号', 'WorkingWrong', '功夫熊猫', '春夏秋冬',
    '梦西游丶悟空', '暗河总指挥丨净心', '暗河摆渡人丨星河', '洋柿子', '荒天帝',
    '剑舞红尘', '青云子', '逍遥侯', '墨染青衣', '星辰大海',
    '云中君', '月下独酌', '风华绝代', '烟雨江南', '醉卧沙场'
  ]
  const data = []
  const offset = (currentArea.value - 1) * 100
  for (let i = 0; i < 120; i++) {
    data.push({
      rank: i + 1,
      nickname: names[i % names.length] + (i >= names.length ? (i + offset) : ''),
      score: 10000 - i * 50
    })
  }
  return data
}

// 切换赛区
const switchArea = (area) => {
  if (currentArea.value === area) return
  currentArea.value = area
  currentPage.value = 1
  loadRankings()
}

// 分页操作
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

const goBack = () => router.push('/king')
const goHome = () => router.push('/')

onMounted(() => {
  loadRankings()
})
</script>

<template>
  <div class="ranking-page">
    <div class="section title">【英豪榜】</div>
    
    <!-- 赛区切换 -->
    <div class="section">
      <a 
        class="link area-link" 
        :class="{ active: currentArea === 1 }"
        @click="switchArea(1)"
      >[1赛区]</a>
      <a 
        class="link area-link" 
        :class="{ active: currentArea === 2 }"
        @click="switchArea(2)"
      >[2赛区]</a>
    </div>

    <!-- 排名列表 -->
    <div class="section">排名.用户名</div>
    <div v-if="loading" class="section gray">加载中...</div>
    <template v-else>
      <div v-for="item in pagedRankings" :key="item.rank" class="section rank-row">
        <span class="rank-num">{{ item.rank }}.</span>
        <span class="nickname">{{ item.nickname }}</span>
      </div>
    </template>

    <!-- 分页 -->
    <div class="section pagination" v-if="rankings.length > 0">
      <a class="link" @click="nextPage">下页</a> 
      <a class="link" @click="lastPage">末页</a>
      <div class="page-info">
        {{ currentPage }}/{{ totalPages }}页
        <input type="text" v-model="jumpPage" class="page-input" />
        <button class="page-btn" @click="goToPage">跳转</button>
      </div>
    </div>

    <div class="section spacer">
      <a class="link" @click="goBack">返回挑战赛首页</a>
    </div>
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>

  </div>
</template>

<style scoped>
.ranking-page {
  padding: 10px;
  font-size: 14px;
  background: #FFFFFF;
  min-height: 100vh;
}

.section {
  margin: 8px 0;
  line-height: 1.6;
}

.title {
  font-weight: bold;
  color: #333;
}

.link {
  color: #1e90ff;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.area-link {
  margin-right: 8px;
}

.area-link.active {
  color: #333;
  font-weight: bold;
}

.rank-row {
  padding-left: 5px;
}

.rank-num {
  display: inline-block;
  min-width: 30px;
}

.nickname {
  color: #1e90ff;
}

.pagination {
  margin-top: 12px;
}

.page-info {
  margin-top: 4px;
}

.page-input {
  width: 40px;
  font-size: 12px;
  border: 1px solid #ccc;
  padding: 1px 4px;
}

.page-btn {
  font-size: 12px;
  padding: 1px 8px;
  background: #f0f0f0;
  border: 1px solid #ccc;
  cursor: pointer;
}

.page-btn:hover {
  background: #e0e0e0;
}

.spacer {
  margin-top: 20px;
}

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #ccc;
}

.gray {
  color: #666;
}

.small {
  font-size: 11px;
}
</style>
