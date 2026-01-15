<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import http from '@/services/http'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const errorMsg = ref('')
const result = ref(null)

const invItemId = computed(() => {
  const raw = route.query.inv_item_id
  const n = parseInt(String(raw || '0'), 10)
  return Number.isFinite(n) ? n : 0
})

const openOne = async () => {
  loading.value = true
  errorMsg.value = ''
  result.value = null
  try {
    const res = await http.post('/dragonpalace/open-gift', { inv_item_id: invItemId.value })
    if (res.data?.ok) {
      result.value = res.data
    } else {
      errorMsg.value = res.data?.error || '打开失败'
    }
  } catch (e) {
    errorMsg.value = e?.response?.data?.error || '网络错误'
  } finally {
    loading.value = false
  }
}

const openAll = async () => {
  loading.value = true
  errorMsg.value = ''
  result.value = null
  try {
    const res = await http.post('/dragonpalace/open-gift', { inv_item_id: invItemId.value, open_all: true })
    if (res.data?.ok) {
      result.value = res.data
    } else {
      errorMsg.value = res.data?.error || '打开失败'
    }
  } catch (e) {
    errorMsg.value = e?.response?.data?.error || '网络错误'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (!invItemId.value) {
    loading.value = false
    errorMsg.value = '参数缺失'
    return
  }
  openOne()
})

const canOpenMore = computed(() => {
  return (result.value?.remaining_quantity || 0) > 0
})

const goInventory = () => router.push({ path: '/inventory', query: { tab: 'temp' } })
const goHome = () => router.push('/')
</script>

<template>
  <div class="gift-open-page">
    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMsg" class="section red">{{ errorMsg }}</div>

    <template v-else-if="result">
      <div class="section">{{ result.message }}</div>
      <div class="section">剩余数量：{{ result.remaining_quantity }}</div>

      <div class="section spacer">
        <a v-if="canOpenMore" class="link" @click="openOne">继续打开</a>
        <span v-else class="link readonly">继续打开</span>
        <span> </span>
        <a v-if="canOpenMore" class="link" @click="openAll">一键打开</a>
        <span v-else class="link readonly">一键打开</span>
      </div>

      <div class="section spacer">
        <a class="link" @click="goInventory">返回背包</a>
      </div>
      <div class="section">
        <a class="link" @click="goHome">返回游戏首页</a>
      </div>
    </template>
  </div>
</template>

<style scoped>
.gift-open-page {
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

.red {
  color: #CC0000;
}
</style>


