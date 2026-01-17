<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import http from '@/services/http'
import { uiAlert } from '@/stores/uiOverlayStore'

const router = useRouter()
const route = useRoute()

const loading = ref(true)
const errorMsg = ref('')

const element = computed(() => String(route.query.element || 'earth'))

const spirits = ref([])

const list = computed(() => {
  // 仅展示当前元素、未锁定、未装备（/spirit/warehouse 已筛掉已装备）
  const el = element.value
  return (spirits.value || []).filter((s) => String(s.element) === el).filter((s) => {
    const lines = s.lines || []
    const locked = lines.some((ln) => ln && ln.unlocked && ln.locked)
    return !locked
  })
})

const load = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await http.get('/spirit/warehouse')
    if (res.data?.ok) {
      spirits.value = res.data.spirits || []
    } else {
      errorMsg.value = res.data?.error || '加载失败'
    }
  } catch (e) {
    errorMsg.value = e?.response?.data?.error || '加载失败'
  } finally {
    loading.value = false
  }
}

const confirmSell = async () => {
  if (!list.value.length) {
    uiAlert('没有可出售的战灵（未锁定）', 'info')
    return
  }
  try {
    const res = await http.post('/spirit/warehouse/sell-batch', { element: element.value })
    if (res.data?.ok) {
      router.push({
        path: '/spirit/warehouse/sell-result',
        query: {
          gained: String(res.data.gained_spirit_power || 0),
        },
      })
    } else {
      uiAlert(res.data?.error || '出售失败', 'error')
    }
  } catch (e) {
    uiAlert(e?.response?.data?.error || '出售失败', 'error')
  }
}

const goBack = () => router.back()
const goHome = () => router.push('/')

onMounted(() => load())
</script>

<template>
  <div class="page">
    <div class="section title">【灵件室】</div>

    <div class="section" v-if="loading">加载中...</div>
    <div class="section red" v-else-if="errorMsg">{{ errorMsg }}</div>

    <template v-else>
      <div class="section">您将出售以下战灵</div>
      <div class="section" v-if="list.length === 0">暂无可出售战灵</div>
      <div class="section" v-for="s in list" :key="s.id">
        {{ s.name }} ({{ (s.lines || []).length }}条属性)
      </div>

      <div class="section spacer">
        <a class="link" @click="confirmSell">确认售出</a>
      </div>

      <div class="section spacer">
        <a class="link" @click="goBack">返回前页</a>
      </div>
      <div class="section">
        <a class="link" @click="goHome">返回游戏首页</a>
      </div>
    </template>
  </div>
</template>

<style scoped>
.page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 18px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}
.section {
  margin: 4px 0;
}
.title {
  font-weight: bold;
}
.spacer {
  margin-top: 16px;
}
.link {
  color: #0066cc;
  cursor: pointer;
  text-decoration: none;
}
.link:hover {
  text-decoration: underline;
}
.red {
  color: #cc0000;
}
</style>


