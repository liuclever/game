<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()
const loading = ref(true)
const rankingData = ref(null)
const errorMsg = ref('')
const currentPage = ref(1)
const pageSize = 10
const jumpPage = ref(1)

const fetchRanking = async (page = 1) => {
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await http.get(`/alliance/competition/elite-ranking?page=${page}&page_size=${pageSize}`)
    if (res.data?.ok) {
      rankingData.value = res.data
      currentPage.value = res.data.page || 1
      jumpPage.value = res.data.page || 1
    } else {
      errorMsg.value = res.data?.error || '获取排行榜失败'
    }
  } catch (err) {
    console.error('获取排行榜失败', err)
    errorMsg.value = err.response?.data?.error || '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}

const goToPage = (page) => {
  if (page >= 1 && page <= (rankingData.value?.total_pages || 1)) {
    fetchRanking(page)
  }
}

const jumpToPage = () => {
  const page = parseInt(jumpPage.value)
  if (page >= 1 && page <= (rankingData.value?.total_pages || 1)) {
    goToPage(page)
  } else {
    jumpPage.value = currentPage.value
  }
}

const nextPage = () => {
  if (currentPage.value < (rankingData.value?.total_pages || 1)) {
    goToPage(currentPage.value + 1)
  }
}

const lastPage = () => {
  if (rankingData.value?.total_pages) {
    goToPage(rankingData.value.total_pages)
  }
}

const goBackCompetition = () => {
  router.push('/alliance/competition')
}

const goBackAlliance = () => {
  router.push('/alliance')
}

const goHome = () => {
  router.push('/')
}

const viewPlayerProfile = (userId) => {
  if (!userId) return
  router.push(`/player/profile?id=${userId}`)
}

onMounted(() => {
  const page = parseInt(route.query.page) || 1
  fetchRanking(page)
})
</script>

<template>
  <div class="elite-ranking-page">
    <div v-if="loading">加载中...</div>
    <div v-else-if="errorMsg">{{ errorMsg }}</div>
    <template v-else-if="rankingData">
      <div>【精英排行】第{{ rankingData.session || '2026-01-11' }}届</div>
      <div>排名.昵称.联盟.积分</div>
      <div v-if="rankingData.rankings && rankingData.rankings.length > 0">
        <div v-for="item in rankingData.rankings" :key="item.id || item.rank">
          {{ item.rank }}. <a v-if="item.user_id" class="link" @click="viewPlayerProfile(item.user_id)">{{ item.nickname }}</a><span v-else>{{ item.nickname }}</span>.{{ item.alliance_name ? '『' + item.alliance_name + '』' : '' }}.{{ item.score }}
        </div>
      </div>
      <div v-else>暂无排行数据</div>
      <div v-if="rankingData.total_pages > 1" class="pagination">
        <a class="link" @click="nextPage" :class="{ disabled: currentPage >= rankingData.total_pages }">下页</a>
        <a class="link" @click="lastPage" :class="{ disabled: currentPage >= rankingData.total_pages }">末页</a>
        <span>{{ currentPage }}/{{ rankingData.total_pages }}页</span>
        <input v-model.number="jumpPage" type="number" min="1" :max="rankingData.total_pages" style="width: 40px; margin: 0 5px;" />
        <a class="link" @click="jumpToPage">跳转</a>
      </div>
      <div>
        <a class="link" @click="goBackCompetition">返回争霸赛</a>
      </div>
      <div>
        <a class="link" @click="goBackAlliance">返回联盟</a>
      </div>
      <div>
        <a class="link" @click="goHome">返回游戏首页</a>
      </div>
    </template>
  </div>
</template>

<style scoped>
.elite-ranking-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 17px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover:not(.disabled) {
  text-decoration: underline;
}

.link.disabled {
  color: #999;
  cursor: not-allowed;
}

.pagination {
  margin: 10px 0;
}
</style>
