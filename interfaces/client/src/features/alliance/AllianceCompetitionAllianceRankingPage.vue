<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

const ranking = ref([])
const myRank = ref(null)
const session = ref('')
const page = ref(1)
const pageSize = ref(10)
const totalPages = ref(1)
const totalCount = ref(0)
const loading = ref(false)
const errorMessage = ref('')
const jumpPage = ref(1)

const fetchRanking = async (targetPage = page.value) => {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await http.get('/alliance/competition/alliance-ranking', {
      params: {
        page: targetPage,
        page_size: pageSize.value,
      },
    })
    if (res.data?.ok) {
      page.value = res.data.page || targetPage
      pageSize.value = res.data.page_size || pageSize.value
      totalPages.value = res.data.total_pages || 1
      totalCount.value = res.data.total_count || 0
      session.value = res.data.session || ''
      ranking.value = res.data.rankings || []
      myRank.value = res.data.my_rank || null
      jumpPage.value = page.value
    } else {
      errorMessage.value = res.data?.error || '排行榜加载失败'
    }
  } catch (err) {
    console.error('加载联盟积分排行失败', err)
    errorMessage.value = err.response?.data?.error || '排行榜加载失败'
  } finally {
    loading.value = false
  }
}

const handlePageChange = (targetPage) => {
  if (targetPage === page.value || targetPage < 1 || targetPage > totalPages.value) {
    return
  }
  fetchRanking(targetPage)
}

const handleJump = () => {
  const targetPage = parseInt(jumpPage.value)
  if (targetPage >= 1 && targetPage <= totalPages.value) {
    handlePageChange(targetPage)
  }
}

const goToCompetition = () => {
  router.push('/alliance/competition')
}

const goToAlliance = () => {
  router.push('/alliance')
}

const goHome = () => {
  router.push('/')
}

onMounted(() => {
  fetchRanking(1)
})
</script>

<template>
  <div class="ranking-page">
    <div class="section title-row">
      【联盟排行】第{{ session || '2026-01-11' }}届
    </div>
    
    <div class="section description">
      (威望为战队总成绩的体现)
    </div>
    
    <div class="section" v-if="errorMessage">
      <span class="warn">{{ errorMessage }}</span>
    </div>
    
    <div class="section" v-else-if="!loading">
      <template v-if="myRank">
        您联盟为第{{ myRank }}名,好厉害哦!
      </template>
      <template v-else>
        您暂未入榜，继续加油！
      </template>
    </div>
    
    <div class="section list-header">
      排名.昵称.联盟威望
    </div>
    
    <div
      v-for="item in ranking"
      :key="item.rank"
      class="section"
    >
      {{ item.rank }}.
      <a class="link">{{ item.alliance_name }}</a>
      .{{ item.prestige }}
    </div>
    
    <div class="section" v-if="!loading && !errorMessage && ranking.length === 0">
      暂无联盟积分数据，请稍后再来～
    </div>
    
    <div class="section pager" v-if="totalPages > 1">
      <a
        class="link"
        :class="{ disabled: loading || page === 1 }"
        @click.prevent="!loading && page > 1 && handlePageChange(page - 1)"
      >
        上页
      </a>
      <a
        class="link"
        :class="{ disabled: loading || page >= totalPages }"
        @click.prevent="!loading && page < totalPages && handlePageChange(page + 1)"
      >
        下页
      </a>
      <a
        class="link"
        :class="{ disabled: loading || page >= totalPages }"
        @click.prevent="!loading && page < totalPages && handlePageChange(totalPages)"
      >
        末页
      </a>
      <span class="page-info">{{ page }}/{{ totalPages }}页</span>
      <input
        v-model.number="jumpPage"
        type="number"
        min="1"
        :max="totalPages"
        class="page-input"
        @keyup.enter="handleJump"
      />
      <a class="link" @click.prevent="handleJump">跳转</a>
    </div>
    
    <div class="section spacer">
      <a class="link" @click.prevent="goToCompetition">返回争霸赛</a>
    </div>
    <div class="section">
      <a class="link" @click.prevent="goToAlliance">返回联盟</a>
    </div>
    <div class="section">
      <a class="link" @click.prevent="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.ranking-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 10px 14px 24px;
  font-size: 16px;
  line-height: 1.7;
  font-family: SimSun, '宋体', serif;
}

.section {
  margin: 6px 0;
}

.title-row {
  font-weight: bold;
  font-size: 18px;
}

.description {
  color: #666;
  font-size: 18px;
}

.list-header {
  font-weight: bold;
}

.link {
  color: #0066cc;
  cursor: pointer;
}

.link:hover {
  text-decoration: underline;
}

.link.disabled {
  color: #aaa;
  cursor: not-allowed;
  text-decoration: none;
}

.warn {
  color: #b94a48;
}

.pager {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.page-info {
  margin: 0 8px;
  color: #666;
}

.page-input {
  width: 50px;
  padding: 2px 4px;
  border: 1px solid #ccc;
  border-radius: 2px;
  text-align: center;
}

.spacer {
  margin-top: 16px;
}
</style>
