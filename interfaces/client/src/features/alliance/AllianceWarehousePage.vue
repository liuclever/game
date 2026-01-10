<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const loading = ref(true)
const allianceData = ref(null)
const errorMsg = ref('')

const fetchAllianceInfo = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await http.get('/alliance/my')
    if (res.data?.ok) {
      allianceData.value = res.data
    } else {
      allianceData.value = null
      errorMsg.value = res.data?.error || '未能获取联盟信息'
    }
  } catch (err) {
    console.error('获取联盟信息失败:', err)
    allianceData.value = null
    errorMsg.value = '网络错误，请稍后再试'
  } finally {
    loading.value = false
  }
}

const statList = computed(() => {
  if (!allianceData.value?.alliance) {
    return []
  }
  const alliance = allianceData.value.alliance
  return [
    { label: '联盟资金', value: alliance.funds ?? 0 },
    { label: '繁荣度', value: alliance.prosperity ?? 0 },
    { label: '焚火晶', value: alliance.crystals ?? 0 },
    { label: '内丹', value: alliance.inner_pills ?? 0 },
  ]
})

const donateResources = () => {
  router.push('/alliance/donate')
}

const goToItemStorage = () => {
  router.push('/alliance/item-storage')
}

const goBackAlliance = () => {
  router.push('/alliance')
}

const goHome = () => {
  router.push('/')
}

onMounted(() => {
  fetchAllianceInfo()
})
</script>

<template>
  <div class="warehouse-page">
    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMsg" class="section error">{{ errorMsg }}</div>
    <template v-else-if="allianceData">
      <div class="section title">【联盟仓库】</div>
      <div class="section donate">
        <a class="link" @click="donateResources">捐赠物资>></a>
      </div>
      <div class="section stats">
        <div v-for="item in statList" :key="item.label" class="stat-item">
          {{ item.label }}：{{ item.value }}
        </div>
      </div>

      <div class="section nav">
        <a class="link" @click="goToItemStorage">进入寄存仓库</a><br />
        <a class="link" @click="goBackAlliance">返回联盟</a><br />
        <a class="link" @click="goHome">返回游戏首页</a>
      </div>

    </template>
    <div v-else class="section">尚未加入联盟，无法查看仓库</div>
  </div>
</template>

<style scoped>
.warehouse-page {
  background: #fffef6;
  min-height: 100vh;
  padding: 10px 18px;
  font-size: 13px;
  line-height: 1.7;
  font-family: SimSun, '宋体', serif;
}

.section {
  margin: 8px 0;
}

.title {
  font-size: 16px;
  font-weight: bold;
  color: #4a2b05;
}

.donate {
  color: #7a4e12;
}

.stats {
  border: 1px solid #e2d3aa;
  padding: 8px 12px;
  background: #fffaf0;
  border-radius: 4px;
}

.stat-item + .stat-item {
  margin-top: 4px;
}

.nav {
  margin-top: 12px;
}

.footer-info {
  margin-top: 18px;
  font-size: 11px;
  color: #777;
  border-top: 1px solid #ddd;
  padding-top: 8px;
}

.link {
  color: #0066cc;
  cursor: pointer;
}

.link:hover {
  text-decoration: underline;
}

.error {
  color: #c0392b;
}
</style>
