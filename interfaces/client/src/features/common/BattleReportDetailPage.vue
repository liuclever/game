<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// 战斗数据（从 sessionStorage 或路由参数获取）
const battleData = ref(null)
const loading = ref(true)
const error = ref('')

// 分页相关
const currentPage = ref(1)
const roundsPerPage = 10

// 从 sessionStorage 加载战斗数据
const loadBattleData = () => {
  const storageKey = route.query.storageKey || 'battle_report_detail'
  const data = sessionStorage.getItem(storageKey)
  
  if (data) {
    try {
      battleData.value = JSON.parse(data)
      loading.value = false
    } catch (e) {
      console.error('解析战斗数据失败', e)
      error.value = '战斗数据格式错误'
      loading.value = false
    }
  } else {
    error.value = '未找到战斗数据'
    loading.value = false
  }
}

// 所有回合
const allRounds = computed(() => {
  if (!battleData.value || !battleData.value.rounds) return []
  return battleData.value.rounds
})

// 总页数
const totalPages = computed(() => {
  return Math.ceil(allRounds.value.length / roundsPerPage)
})

// 当前页的回合
const currentRounds = computed(() => {
  const start = (currentPage.value - 1) * roundsPerPage
  const end = start + roundsPerPage
  return allRounds.value.slice(start, end)
})

// 战斗标题
const battleTitle = computed(() => {
  if (!battleData.value) return '详细战报'
  return battleData.value.title || '详细战报'
})

// 战斗结果
const battleResult = computed(() => {
  if (!battleData.value) return ''
  return battleData.value.result || ''
})

// 是否有上一页
const hasPrevPage = computed(() => currentPage.value > 1)

// 是否有下一页
const hasNextPage = computed(() => currentPage.value < totalPages.value)

// 上一页
const prevPage = () => {
  if (hasPrevPage.value) {
    currentPage.value--
  }
}

// 下一页
const nextPage = () => {
  if (hasNextPage.value) {
    currentPage.value++
  }
}

// 跳转到指定页
const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

// 返回
const goBack = () => {
  router.back()
}

// 返回首页
const goHome = () => {
  router.push('/')
}

onMounted(() => {
  loadBattleData()
})
</script>

<template>
  <div class="report-page">
    <!-- 标题 -->
    <div class="section title">
      【{{ battleTitle }}】 <a class="link" @click="goBack">返回</a>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="section">加载中...</div>
    
    <!-- 错误 -->
    <div v-else-if="error" class="section red">{{ error }}</div>
    
    <!-- 战斗数据 -->
    <template v-else-if="battleData">
      <!-- 战斗信息 -->
      <div v-if="battleData.info" class="section">
        {{ battleData.info }}
      </div>

      <!-- 分页导航（顶部） -->
      <div v-if="totalPages > 1" class="section pagination">
        <a v-if="hasPrevPage" class="link" @click="prevPage">上一页</a>
        <span v-else class="gray">上一页</span>
        <span class="page-info">第{{ currentPage }}/{{ totalPages }}页</span>
        <a v-if="hasNextPage" class="link" @click="nextPage">下一页</a>
        <span v-else class="gray">下一页</span>
      </div>

      <!-- 当前页的回合 -->
      <div v-for="(round, index) in currentRounds" :key="round.round_num || index" class="section">
        <template v-if="round.description">
          [回合{{ round.round_num }}]: {{ round.description }}
        </template>
        <template v-else-if="round.action">
          [回合{{ round.round_num }}]: {{ round.action }}
        </template>
        <template v-else>
          {{ round }}
        </template>
      </div>

      <!-- 战斗结果（最后一页显示） -->
      <div v-if="currentPage === totalPages && battleResult" class="section result">
        [战斗结束]: {{ battleResult }}
      </div>

      <!-- 分页导航（底部） -->
      <div v-if="totalPages > 1" class="section pagination">
        <a v-if="hasPrevPage" class="link" @click="prevPage">上一页</a>
        <span v-else class="gray">上一页</span>
        <span class="page-info">第{{ currentPage }}/{{ totalPages }}页</span>
        <a v-if="hasNextPage" class="link" @click="nextPage">下一页</a>
        <span v-else class="gray">下一页</span>
      </div>

      <!-- 页码快速跳转 -->
      <div v-if="totalPages > 1" class="section page-numbers">
        跳转到：
        <template v-for="page in totalPages" :key="page">
          <a 
            v-if="page !== currentPage" 
            class="link page-num" 
            @click="goToPage(page)"
          >{{ page }}</a>
          <span v-else class="current-page">{{ page }}</span>
        </template>
      </div>
    </template>

    <!-- 导航 -->
    <div class="section spacer">
      <a class="link" @click="goBack">返回前页</a>
    </div>
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.report-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 16px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 4px 0;
}

.title {
  font-weight: bold;
  margin-bottom: 8px;
}

.pagination {
  margin: 12px 0;
  padding: 8px 0;
  border-top: 1px solid #EEEEEE;
  border-bottom: 1px solid #EEEEEE;
}

.page-info {
  margin: 0 12px;
  color: #333333;
}

.page-numbers {
  margin: 8px 0;
}

.page-num {
  margin: 0 4px;
}

.current-page {
  margin: 0 4px;
  color: #CC3300;
  font-weight: bold;
}

.result {
  margin-top: 12px;
  padding-top: 8px;
  border-top: 1px solid #EEEEEE;
  font-weight: bold;
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
  color: #999999;
}

.red {
  color: #CC0000;
}
</style>
