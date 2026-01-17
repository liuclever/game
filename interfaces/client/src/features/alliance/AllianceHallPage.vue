<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

const loading = ref(true)
const errorMsg = ref('')

const keyword = ref('')
const page = ref(1)
const size = 10

const data = ref({
  alliances: [],
  total: 0,
  total_pages: 1,
  already_in_alliance: false,
})

const totalPages = computed(() => Number(data.value?.total_pages || 1) || 1)

const fetchList = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await http.get('/alliance/list', {
      params: {
        keyword: keyword.value || undefined,
        page: page.value,
        size,
      },
    })
    if (res.data?.ok) {
      data.value = res.data
    } else {
      errorMsg.value = res.data?.error || '加载失败'
    }
  } catch (e) {
    errorMsg.value = e?.response?.data?.error || '加载失败'
  } finally {
    loading.value = false
  }
}

const search = async () => {
  page.value = 1
  await fetchList()
}

const join = async (a) => {
  if (!a?.id) return
  if (!confirm(`确定加入【${a.name}】吗？`)) return
  try {
    const res = await http.post('/alliance/join', { alliance_id: a.id })
    if (res.data?.ok) {
      console.error(res.data.message || '加入成功')
      router.push('/alliance')
      return
    }
    console.error(res.data?.error || '加入失败')
  } catch (e) {
    console.error(e?.response?.data?.error || '加入失败')
  } finally {
    await fetchList()
  }
}

const goAlliance = () => router.push('/alliance')
const goHome = () => router.push('/')

const goToPage = async (p) => {
  if (p < 1 || p > totalPages.value) return
  page.value = p
  await fetchList()
}

onMounted(() => {
  // 如果URL中有keyword参数（比如从玩家详情页点击联盟名称跳转过来），设置搜索关键词并搜索
  const keywordParam = route.query.keyword
  if (keywordParam && typeof keywordParam === 'string') {
    keyword.value = keywordParam
    // 设置关键词后自动执行搜索
    search()
  } else {
    fetchList()
  }
})
</script>

<template>
  <div class="alliance-hall-page">
    <div class="section title">【联盟大厅】</div>

    <div class="section">
      <input v-model="keyword" class="input" placeholder="输入联盟名" />
      <button class="btn" @click="search" :disabled="loading">搜索</button>
    </div>

    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMsg" class="section error">{{ errorMsg }}</div>

    <template v-else>
      <div v-if="data.already_in_alliance" class="section gray">
        你已加入联盟，无法加入其他联盟
      </div>

      <div v-if="!data.alliances || data.alliances.length === 0" class="section gray">
        暂无联盟
      </div>

      <div
        v-for="a in data.alliances"
        :key="a.id"
        class="section item"
      >
        <span class="name">{{ a.name }}</span>
        <span class="meta">(Lv.{{ a.level }}，成员 {{ a.member_count }}/{{ a.member_capacity }})</span>
        <a
          v-if="a.can_join"
          class="link"
          @click="join(a)"
        >加入</a>
        <span v-else class="gray">不可加入</span>
      </div>

      <div class="section pager">
        <a class="link" v-if="page > 1" @click="goToPage(1)">首页</a>
        <a class="link" v-if="page > 1" @click="goToPage(page - 1)">上页</a>
        <a class="link" v-if="page < totalPages" @click="goToPage(page + 1)">下页</a>
        <a class="link" v-if="page < totalPages" @click="goToPage(totalPages)">末页</a>
        <span class="gray" style="margin-left: 8px;">{{ page }}/{{ totalPages }}页</span>
      </div>
    </template>

    <div class="section spacer">
      <a class="link" @click="goAlliance">返回联盟</a>
    </div>
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.alliance-hall-page {
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

.input {
  width: 180px;
  padding: 2px 6px;
  margin-right: 6px;
}

.btn {
  padding: 2px 8px;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
  margin-left: 8px;
}

.link:hover {
  text-decoration: underline;
}

.item {
  display: flex;
  align-items: center;
}

.name {
  font-weight: bold;
}

.meta {
  margin-left: 6px;
}

.error {
  color: red;
}

.gray {
  color: #666;
}

.spacer {
  margin-top: 16px;
}
</style>
