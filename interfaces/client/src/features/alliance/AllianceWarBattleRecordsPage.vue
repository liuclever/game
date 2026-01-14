<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

const records = ref([])
const loading = ref(false)
const errorMessage = ref('')

const fetchRecords = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await http.get('/alliance/war/battle-records', {
      params: {
        limit: 50
      }
    })
    if (res.data?.ok) {
      records.value = res.data.records || []
    } else {
      errorMessage.value = res.data?.error || '获取战绩失败'
    }
  } catch (err) {
    console.error('加载联盟战绩失败', err)
    errorMessage.value = err.response?.data?.error || '获取战绩失败'
  } finally {
    loading.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getResultLabel = (result) => {
  const labels = {
    1: '胜利',
    0: '失败',
    '-1': '平局'
  }
  return labels[result] || '未知'
}

const getResultClass = (result) => {
  if (result === 1) return 'win'
  if (result === 0) return 'lose'
  return 'draw'
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
  fetchRecords()
})
</script>

<template>
  <div class="records-page">
    <div class="section title-row">
      【联盟战绩】 <a class="link" @click.prevent="goWar">返回</a>
    </div>

    <div v-if="loading" class="section">
      正在加载战绩...
    </div>
    <div v-else-if="errorMessage" class="section warn">
      {{ errorMessage }}
    </div>
    <div v-else class="section">
      <template v-if="records.length > 0">
        <div class="section list-header">
          对战日期 / 对手联盟 / 土地 / 结果 / 获得战功
        </div>
        <div
          v-for="record in records"
          :key="record.id"
          class="section record-item"
        >
          <div class="record-date">{{ formatDate(record.war_date || record.created_at) }}</div>
          <div class="record-detail">
            <span>对手：<span class="blue">{{ record.opponent_alliance_name || '未知联盟' }}</span></span>
            <span>土地：{{ record.land_name || `土地${record.land_id}` }}</span>
            <span>结果：<span :class="getResultClass(record.battle_result)">{{ getResultLabel(record.battle_result) }}</span></span>
            <span>战功：+{{ record.honor_gained || 0 }}</span>
          </div>
        </div>
      </template>
      <div v-else class="section">
        暂无对战记录
      </div>
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
.records-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 12px 16px 20px;
  font-size: 16px;
  line-height: 1.6;
  font-family: 'SimSun', '宋体', serif;
  color: #000;
}

.section {
  margin: 8px 0;
}

.title-row {
  font-weight: bold;
  font-size: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.link {
  color: #0066cc;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.list-header {
  font-weight: bold;
  padding: 4px 0;
  border-bottom: 1px solid #ddd;
}

.record-item {
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.record-date {
  font-weight: bold;
  margin-bottom: 4px;
}

.record-detail {
  display: flex;
  flex-direction: column;
  gap: 4px;
  color: #555;
}

.blue {
  color: #0066cc;
}

.win {
  color: #0a840a;
  font-weight: bold;
}

.lose {
  color: #c03;
  font-weight: bold;
}

.draw {
  color: #888;
}

.warn {
  color: #c03;
}

.spacer {
  margin-top: 16px;
}
</style>
