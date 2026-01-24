<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchWarTargets } from '@/api/alliance'

const router = useRouter()

const landTargets = ref([])
const loading = ref(true)
const error = ref('')

const goAlliance = () => {
  router.push('/alliance')
}

const goHome = () => {
  router.push('/')
}

const goDetail = (landId) => {
  router.push(`/alliance/war/land/${landId}`)
}

const loadWarTargets = async () => {
  loading.value = true
  error.value = ''
  try {
    // 传递 all=true 参数，获取所有目标（飞龙军+伏虎军）
    const res = await fetchWarTargets(true)
    if (res?.ok && res.data?.lands) {
      landTargets.value = res.data.lands
    } else {
      error.value = res?.error || '获取土地列表失败'
    }
  } catch (err) {
    error.value = err?.response?.data?.error || '网络异常，稍后重试'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadWarTargets()
})
</script>

<template>
  <div class="targets-page">
    <div class="section title">【土地详情】</div>
    <div class="section header">序号.土地.占领联盟</div>

    <div v-if="loading" class="section status">加载中...</div>
    <div v-else-if="error" class="section error">{{ error }}</div>
    <template v-else>
      <div
        v-for="(land, index) in landTargets"
        :key="land.id"
        class="section row clickable"
        @click="goDetail(land.id)"
      >
        {{ index + 1 }}.<span class="blue">{{ land.label }}.</span> {{ land.owner }}
      </div>
    </template>

    <div class="section footer-links">
      <div @click="goAlliance" class="link">返回联盟</div>
      <div @click="goHome" class="link">返回游戏首页</div>
    </div>
  </div>
</template>

<style scoped>
.targets-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 12px 16px 24px;
  font-family: 'SimSun', '宋体', serif;
  font-size: 16px;
  line-height: 1.6;
  color: #000000;
}

.section {
  margin: 6px 0;
}

.title {
  font-weight: bold;
}

.header {
  font-weight: bold;
  margin-top: 2px;
}

.row {
  display: flex;
  gap: 4px;
  align-items: center;
}

.clickable {
  cursor: pointer;
}

.clickable:hover .blue {
  text-decoration: underline;
}

.blue {
  color: #0066cc;
  margin: 0 6px 0 2px;
}

.footer-links {
  margin-top: 20px;
  display: flex;
  gap: 16px;
}

.link {
  color: #0066cc;
  cursor: pointer;
}

.link:hover {
  text-decoration: underline;
}
</style>
