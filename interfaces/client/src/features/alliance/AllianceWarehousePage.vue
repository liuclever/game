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
    <div v-if="loading">加载中...</div>
    <div v-else-if="errorMsg">{{ errorMsg }}</div>
    <template v-else-if="allianceData">
      <div>【联盟仓库】</div>
      <div><a class="link" @click="donateResources">捐赠物资>></a></div>
      <div v-for="item in statList" :key="item.label">
        {{ item.label }}：{{ item.value }}
      </div>
      <div><a class="link" @click="goBackAlliance">返回联盟</a></div>
      <div><a class="link" @click="goHome">返回游戏首页</a></div>
    </template>
    <div v-else>尚未加入联盟，无法查看仓库</div>
  </div>
</template>

<style scoped>
.warehouse-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 16px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}
</style>
