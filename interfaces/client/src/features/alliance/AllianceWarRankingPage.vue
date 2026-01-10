<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

const ranking = ref([])
const myRank = ref(null)
const page = ref(1)
const size = ref(10)
const total = ref(0)
const loading = ref(false)
const errorMessage = ref('')

const fetchRanking = async (targetPage = page.value) => {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await http.get('/alliance/war/ranking', {
      params: {
        page: targetPage,
        size: size.value,
      },
    })
    if (res.data?.ok && res.data.data) {
      page.value = res.data.data.page || targetPage
      size.value = res.data.data.size || size.value
      total.value = res.data.data.total || 0
      ranking.value = res.data.data.ranking || []
      myRank.value = res.data.data.myRank || null
    } else {
      errorMessage.value = res.data?.error || '排行榜加载失败'
    }
  } catch (err) {
    console.error('加载盟战战功排行失败', err)
    errorMessage.value = err.response?.data?.error || '排行榜加载失败'
  } finally {
    loading.value = false
  }
}

const handlePageChange = (targetPage) => {
  if (targetPage === page.value || targetPage < 1) {
    return
  }
  const maxPage = Math.max(1, Math.ceil(total.value / size.value))
  if (targetPage > maxPage) {
    targetPage = maxPage
  }
  fetchRanking(targetPage)
}

const goWar = () => {
  router.push('/alliance/war')
}

const goAlliance = () => {
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
      【本月盟战排行】 <a class="link" @click.prevent="goWar">返回</a>
    </div>
    <div class="section" v-if="errorMessage">
      <span class="warn">{{ errorMessage }}</span>
    </div>
    <div class="section" v-else>
      <template v-if="myRank">
        您的联盟排名为第{{ myRank.rank }}名 ({{ myRank.allianceName }}，战功: {{ myRank.score }})，好厉害哦！
      </template>
      <template v-else-if="!loading">
        您暂未入榜，继续加油！
      </template>
      <template v-else>
        正在加载您的联盟排名...
      </template>
    </div>
    <div class="section top-spot" v-if="ranking.length">
      天下第一联盟(恭喜)
      <a class="link">{{ ranking[0].allianceName }}</a>
      (战功: {{ ranking[0].score }})
    </div>
    <div class="section" v-else-if="!loading && !errorMessage">
      暂无联盟战功数据，请稍后再来～
    </div>

    <div class="section list-header">
      排名. 队呼. 联盟战功
    </div>
    <div
      v-for="item in ranking"
      :key="item.rank"
      class="section"
    >
      {{ item.rank }}.
      <a class="link">{{ item.allianceName }}</a>
      .{{ item.score }}
    </div>

    <div class="section pager">
      <a
        class="link"
        :class="{ disabled: loading || page === 1 }"
        @click.prevent="!loading && page > 1 && handlePageChange(page - 1)"
      >
        上页
      </a>
      <a
        class="link"
        :class="{ disabled: loading || page * size >= total }"
        @click.prevent="!loading && page * size < total && handlePageChange(page + 1)"
      >
        下页
      </a>
      <a
        class="link"
        :class="{ disabled: loading || page * size >= total }"
        @click.prevent="!loading && page * size < total && handlePageChange(Math.ceil(total / size))"
      >
        末页
      </a>
    </div>

    <div class="section spacer">
      <a class="link" @click.prevent="goWar">返回盟战</a>
    </div>
    <div class="section">
      <a class="link" @click.prevent="goAlliance">返回联盟</a>
    </div>
    <div class="section">
      <a class="link" @click.prevent="goHome">返回游戏首页</a>
    </div>

  </div>
</template>

<style scoped>
.ranking-page {
  background: #fff8dc;
  min-height: 100vh;
  padding: 10px 14px 24px;
  font-size: 13px;
  line-height: 1.7;
  font-family: SimSun, '宋体', serif;
}

.section {
  margin: 6px 0;
}

.title-row {
  font-weight: bold;
  font-size: 15px;
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

.gray {
  color: #777;
}

.warn {
  color: #b94a48;
}

.small {
  font-size: 11px;
}

.pager a + a {
  margin-left: 12px;
}

.top-spot {
  font-weight: bold;
}

.footer {
  margin-top: 20px;
}

.spacer {
  margin-top: 16px;
}
</style>
