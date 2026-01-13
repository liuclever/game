<script setup>
import { useMessage } from '@/composables/useMessage'
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

const { message, messageType, showMessage } = useMessage()

const loading = ref(true)
const errorMessage = ref('')
const cardStatus = ref(null)
const purchaseLoading = ref(false)
const claimLoading = ref(false)

const fetchStatus = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await http.get('/sponsor/month-card/status')
    if (res.data?.ok) {
      cardStatus.value = res.data.data || null
    } else {
      throw new Error(res.data?.error || '加载失败')
    }
  } catch (err) {
    console.error('加载月卡状态失败', err)
    errorMessage.value = err?.response?.data?.error || err.message || '加载失败，请稍后再试'
  } finally {
    loading.value = false
  }
}

const handlePurchase = async () => {
  if (purchaseLoading.value) return
  purchaseLoading.value = true
  try {
    const res = await http.post('/sponsor/month-card/purchase')
    if (res.data?.ok) {
      showMessage(`购买成功！已发放 ${res.data.data?.immediate_reward ?? 1000} 元宝。`, 'success')
      await fetchStatus()
    } else {
      throw new Error(res.data?.error || '购买失败')
    }
  } catch (err) {
    showMessage(err?.response?.data?.error || err.message || '购买失败，请稍后再试', 'error')
  } finally {
    purchaseLoading.value = false
  }
}

const handleClaim = async () => {
  if (claimLoading.value) return
  claimLoading.value = true
  try {
    const res = await http.post('/sponsor/month-card/claim')
    if (res.data?.ok) {
      showMessage(`领取成功！获得 ${res.data.data?.reward ?? 200} 元宝。`, 'success')
      await fetchStatus()
    } else {
      throw new Error(res.data?.error || '领取失败')
    }
  } catch (err) {
    showMessage(err?.response?.data?.error || err.message || '领取失败，请稍后再试', 'error')
  } finally {
    claimLoading.value = false
  }
}

const goBack = () => {
  router.push('/sponsor')
}

onMounted(() => {
  fetchStatus()
})
</script>

<template>
  <div class="month-card-page">
    <!-- 消息提示 -->
    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>

    <div class="section">【月卡中心】</div>
    
    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMessage" class="section error">{{ errorMessage }}</div>
    <template v-else-if="cardStatus">
      <div class="section">
        月卡状态: 
        <span v-if="cardStatus.is_active" class="active">生效中</span>
        <span v-else class="inactive">未激活</span>
      </div>
      
      <template v-if="cardStatus.is_active">
        <div class="section">剩余天数: {{ cardStatus.days_left }} 天</div>
        <div class="section">到期日期: {{ cardStatus.end_date }}</div>
        <div class="section">
          今日奖励: 
          <template v-if="cardStatus.today_claimed">
            <span class="claimed">已领取</span>
          </template>
          <template v-else>
            <a class="link" @click="handleClaim">{{ claimLoading ? '领取中...' : '领取200元宝' }}</a>
          </template>
        </div>
      </template>
      
      <div class="section">【月卡说明】</div>
      <div class="section">价格: 30宝石</div>
      <div class="section">购买立即获得: 1000元宝</div>
      <div class="section">每日可领取: 200元宝 × 30天</div>
      <div class="section">总价值: 1000 + 200×30 = 7000元宝</div>
      
      <div class="section">
        <template v-if="cardStatus.is_active">
          <a class="link" @click="handlePurchase">{{ purchaseLoading ? '购买中...' : '续费月卡（30宝石，+30天）' }}</a>
        </template>
        <template v-else>
          <a class="link" @click="handlePurchase">{{ purchaseLoading ? '购买中...' : '购买月卡（30宝石）' }}</a>
        </template>
      </div>
    </template>
    
    <div class="section">
      <a class="link" @click="goBack">返回赞助中心</a>
    </div>
  </div>
</template>

<style scoped>
.month-card-page {
  min-height: 100vh;
  background: #f5f5dc;
  padding: 10px 15px;
  font-size: 14px;
  color: #333;
  font-family: 'SimSun', '宋体', serif;
  line-height: 1.8;
}
.section { margin: 4px 0; }
.link { color: #0066cc; cursor: pointer; }
.link:hover { text-decoration: underline; }
.active { color: #006600; font-weight: bold; }
.inactive { color: #999; }
.claimed { color: #999; }
.hint { color: #666; font-size: 12px; }
.error { color: #c62828; }

/* 消息提示样式 */
.message {
  padding: 12px;
  margin: 12px 0;
  border-radius: 4px;
  font-weight: bold;
  text-align: center;
}

.message.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.message.info {
  background: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}

</style>
