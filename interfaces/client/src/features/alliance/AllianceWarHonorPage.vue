<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

const loading = ref(true)
const submitting = ref(false)
const currentHonor = ref(0)
const historicalHonor = ref(0)
const errorMsg = ref('')
const successMsg = ref('')

// 兑换选项配置
const exchangeItems = ref([
  {
    type: 'fire_crystal',
    name: '焚火晶',
    honor: 2,
    quantity: 1,
    description: '2联盟战功兑换1焚火晶'
  },
  {
    type: 'gold_bag',
    name: '金袋',
    honor: 4,
    quantity: 1,
    description: '4联盟战功兑换1金袋'
  },
  {
    type: 'prosperity',
    name: '繁荣度',
    honor: 6,
    quantity: 1000,
    description: '6联盟战功兑换1000繁荣度'
  }
])

const goWar = () => {
  router.push('/alliance/war')
}

const goAlliance = () => {
  router.push('/alliance')
}

const goHome = () => {
  router.push('/')
}

const loadHonorStatus = async () => {
  loading.value = true
  errorMsg.value = ''
  successMsg.value = ''
  try {
    const res = await http.get('/alliance/war/status')
    // 检查响应数据
    if (!res || !res.data) {
      errorMsg.value = '接口返回数据异常'
      return
    }
    
    if (res.data.ok) {
      currentHonor.value = res.data.current_honor || 0
      historicalHonor.value = res.data.war_honor_history || 0
      errorMsg.value = '' // 清除错误信息
    } else {
      // 接口返回了错误信息
      const error = res.data.error || '战功信息获取失败'
      errorMsg.value = error
      // 如果是因为未加入联盟，显示0并清除错误提示（因为这是正常情况）
      if (error.includes('未加入联盟') || error.includes('请先加入联盟')) {
        currentHonor.value = 0
        historicalHonor.value = 0
        errorMsg.value = '' // 未加入联盟时不显示错误，只显示0
      }
    }
  } catch (err) {
    // 网络错误或其他异常
    console.error('加载战功信息失败:', err)
    // 检查是否是网络错误
    if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
      errorMsg.value = '请求超时，请稍后重试'
    } else if (err.response) {
      // 服务器返回了错误响应
      const status = err.response.status
      if (status === 401) {
        errorMsg.value = '请先登录'
      } else if (status === 404) {
        errorMsg.value = '接口不存在，请联系管理员'
      } else if (status >= 500) {
        errorMsg.value = '服务器错误，请稍后重试'
      } else {
        errorMsg.value = err.response.data?.error || `请求失败 (${status})`
      }
    } else if (err.request) {
      // 请求已发出但没有收到响应
      errorMsg.value = '网络连接失败，请检查网络'
    } else {
      // 其他错误
      errorMsg.value = err?.message || '网络异常，请稍后重试'
    }
  } finally {
    loading.value = false
  }
}

const handleExchange = async (item) => {
  if (submitting.value) return
  if (currentHonor.value < item.honor) {
    errorMsg.value = `战功不足，需要${item.honor}战功`
    // 跳转到失败结果页面
    router.push({
      path: '/alliance/war/honor/exchange-result',
      query: {
        success: 'false',
        message: `战功不足，需要${item.honor}战功`
      }
    })
    return
  }
  
  submitting.value = true
  errorMsg.value = ''
  successMsg.value = ''
  try {
    const res = await http.post('/alliance/war/honor/exchange-item', {
      exchange_type: item.type
    })
    if (res.data?.ok) {
      const successMessage = res.data.message || `兑换成功，获得${item.quantity}${item.name}`
      // 跳转到成功结果页面
      router.push({
        path: '/alliance/war/honor/exchange-result',
        query: {
          success: 'true',
          message: successMessage,
          itemName: item.name,
          quantity: item.quantity,
          honorCost: res.data.honor_cost || item.honor,
          remainingHonor: res.data.remaining_honor || (currentHonor.value - item.honor)
        }
      })
    } else {
      const errorMessage = res.data?.error || '兑换失败'
      // 跳转到失败结果页面
      router.push({
        path: '/alliance/war/honor/exchange-result',
        query: {
          success: 'false',
          message: errorMessage
        }
      })
    }
  } catch (err) {
    const errorMessage = err?.response?.data?.error || '网络异常，兑换失败'
    // 跳转到失败结果页面
    router.push({
      path: '/alliance/war/honor/exchange-result',
      query: {
        success: 'false',
        message: errorMessage
      }
    })
  } finally {
    submitting.value = false
  }
}

const canExchange = (item) => {
  return currentHonor.value >= item.honor && !submitting.value
}

onMounted(() => {
  loadHonorStatus()
})
</script>

<template>
  <div class="honor-page">
    <div class="section title-row">
      【战功兑换】 <a class="link" @click.prevent="goWar">返回</a>
    </div>

    <div class="section tabs">
      <span class="tab active">联盟战功</span>
    </div>

    <div v-if="loading" class="section">
      正在加载战功信息...
    </div>
    <div v-else class="section values">
      <div>
        当前战功: <span class="blue">{{ currentHonor }}</span>
      </div>
      <div>
        历史战功: <span class="blue">{{ historicalHonor }}</span>
      </div>
    </div>

    <div v-if="errorMsg" class="section warn">
      {{ errorMsg }}
    </div>

    <div v-if="successMsg" class="section success">
      {{ successMsg }}
    </div>

    <div class="section">
      【兑换列表】（共 {{ exchangeItems.length }} 项）
    </div>
    <div class="section list-header">
      名称 / 战功消耗
    </div>
    <div v-for="item in exchangeItems" :key="item.type" class="section exchange-row">
      <div class="exchange-main">
        <div class="exchange-name">
          {{ item.name }}
        </div>
        <div class="exchange-desc">
          {{ item.description }}
        </div>
        <div v-if="currentHonor < item.honor" class="exchange-reason warn">
          战功不足，需要{{ item.honor }}战功
        </div>
      </div>
      <div class="exchange-actions">
        <div class="cost">消耗战功：{{ item.honor }}</div>
        <button
          class="exchange-btn"
          :disabled="!canExchange(item)"
          @click="handleExchange(item)"
        >
          {{ canExchange(item) ? (submitting ? '兑换中…' : '兑换') : '不可兑换' }}
        </button>
      </div>
    </div>

    <div class="section info-block">
      <div>⚠️ 仅盟主与副盟主可以执行战功兑换。</div>
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
.honor-page {
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

.values {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.title-row {
  font-weight: bold;
  font-size: 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tabs {
  margin-top: 4px;
}

.tab {
  padding: 2px 6px;
  border: 1px solid #d2a94a;
  background: #f9e2a0;
}

.tab.active {
  font-weight: bold;
}

.link {
  color: #0066cc;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.blue {
  color: #0066cc;
}

.warn {
  color: #c03;
}

.success {
  color: #0a840a;
}

.spacer {
  margin-top: 16px;
}

.list-header {
  font-weight: bold;
  border-bottom: 1px solid #d2a94a;
  padding-bottom: 4px;
}

.exchange-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  border-bottom: 1px dashed #d8c48a;
  padding-bottom: 8px;
}

.exchange-row:last-of-type {
  border-bottom: none;
}

.exchange-main {
  flex: 1;
}

.exchange-name {
  font-size: 17px;
  font-weight: bold;
}

.exchange-desc {
  font-size: 18px;
  color: #555;
  margin-top: 4px;
}

.exchange-reason {
  font-size: 18px;
  margin-top: 4px;
}

.exchange-actions {
  min-width: 120px;
  text-align: right;
}

.cost {
  font-size: 18px;
  margin-bottom: 6px;
}

.exchange-btn {
  padding: 4px 10px;
  border: 1px solid #0a6abf;
  background: #1084e3;
  color: #fff;
  cursor: pointer;
  font-size: 18px;
}

.exchange-btn:disabled {
  background: #ffffff;
  border-color: #aaa;
  color: #999;
  cursor: not-allowed;
}

.info-block {
  background: #fff3d6;
  border: 1px solid #e0c88f;
  padding: 8px;
  font-size: 18px;
  line-height: 1.5;
}
</style>
