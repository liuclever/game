<script setup>
import { useMessage } from '@/composables/useMessage'
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

const { message, messageType, showMessage } = useMessage()

const loading = ref(true)
const errorMsg = ref('')
const successMsg = ref('')
const donationItems = ref([])
const allianceStats = ref(null)
const memberStats = ref(null)
const donationForm = reactive({})
const submittingKey = ref('')

const resetFormKeys = items => {
  Object.keys(donationForm).forEach(key => {
    if (!items.some(item => item.key === key)) {
      delete donationForm[key]
    }
  })
  items.forEach(item => {
    if (donationForm[item.key] === undefined) {
      donationForm[item.key] = ''
    }
  })
}

const fetchDonationInfo = async () => {
  loading.value = true
  errorMsg.value = ''
  successMsg.value = ''
  try {
    const res = await http.get('/alliance/warehouse/donation-info')
    if (res.data?.ok) {
      const items = res.data.items || []
      donationItems.value = items
      allianceStats.value = res.data.alliance || null
      memberStats.value = res.data.member || null
      resetFormKeys(items)
    } else {
      errorMsg.value = res.data?.error || '加载捐赠信息失败'
    }
  } catch (err) {
    console.error('加载捐赠信息失败', err)
    errorMsg.value = '网络错误，请稍后再试'
  } finally {
    loading.value = false
  }
}

const handleDonate = async (item) => {
  if (submittingKey.value) return
  const value = donationForm[item.key]
  const amount = Number(value)
  if (!amount || amount <= 0) {
    showMessage('请输入有效的捐赠数量', 'info')
    return
  }
  if (amount > item.available) {
    showMessage(`当前仅拥有 ${item.available} 个${item.name}`, 'info')
    return
  }
  submittingKey.value = item.key
  successMsg.value = ''
  try {
    const res = await http.post('/alliance/warehouse/donate', {
      donations: { [item.key]: amount },
    })
    if (res.data?.ok) {
      successMsg.value = res.data.message || '捐赠成功'
      const updatedItems = donationItems.value.map(existing => {
        if (existing.key !== item.key) return existing
        return {
          ...existing,
          available: Math.max(0, existing.available - amount),
        }
      })
      donationItems.value = updatedItems
      if (res.data.alliance) {
        allianceStats.value = {
          ...(allianceStats.value || {}),
          ...res.data.alliance,
        }
      }
      if (res.data.member) {
        memberStats.value = {
          ...(memberStats.value || {}),
          ...res.data.member,
        }
      }
      donationForm[item.key] = ''
    } else {
      showMessage(res.data?.error || '捐赠失败，请稍后再试', 'error')
    }
  } catch (err) {
    console.error('捐赠失败', err)
    showMessage('网络异常，请稍后再试', 'info')
  } finally {
    submittingKey.value = ''
  }
}

const goBackAlliance = () => {
  router.push('/alliance')
}

const goHome = () => {
  router.push('/')
}

onMounted(() => {
  fetchDonationInfo()
})
</script>

<template>
  <div class="donate-page">
    <!-- 消息提示 -->
    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>

    <div class="title">【捐赠物资】</div>
    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMsg" class="section error">
      {{ errorMsg }}
      <a class="link" @click="fetchDonationInfo">点击重试</a>
    </div>
    <template v-else>
      <div v-if="successMsg" class="section success">{{ successMsg }}</div>
      <div v-if="allianceStats" class="section stats">
        当前联盟资金：{{ allianceStats.funds ?? 0 }}<br />
        当前繁荣度：{{ allianceStats.prosperity ?? 0 }}
      </div>
      <div v-if="memberStats" class="section stats">
        我的贡献：{{ memberStats.contribution ?? 0 }}
      </div>

      <div class="donation-list">
        <div v-for="item in donationItems" :key="item.key" class="donation-row">
          <div class="row-header">
            <span class="name">{{ item.name }}</span>
            <span class="available">拥有：{{ item.available }}</span>
          </div>
          <div class="effects">
            每个可获得：
            <span v-if="item.effects.funds">+{{ item.effects.funds }} 资金；</span>
            <span>+{{ item.effects.prosperity }} 繁荣度；</span>
            <span>+{{ item.effects.contribution }} 个人贡献</span>
          </div>
          <div class="row-action">
            <span class="input-label">捐赠数量：</span>
            <input
              v-model="donationForm[item.key]"
              type="number"
              min="0"
              class="input"
              :disabled="submittingKey === item.key"
            />
            <button
              class="btn"
              :disabled="submittingKey === item.key"
              @click="handleDonate(item)"
            >
              {{ submittingKey === item.key ? '提交中...' : '捐赠' }}
            </button>
          </div>
        </div>
      </div>
    </template>

    <div class="nav">
      <a class="link" @click="goBackAlliance">返回联盟</a><br />
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>

  </div>
</template>

<style scoped>
.donate-page {
  background: #fffef6;
  min-height: 100vh;
  padding: 14px 18px;
  font-size: 13px;
  line-height: 1.8;
  font-family: SimSun, '宋体', serif;
}

.title {
  font-weight: bold;
  color: #4a2b05;
  margin-bottom: 8px;
}

.section {
  margin-bottom: 10px;
}

.stats {
  border: 1px dashed #d6c089;
  padding: 8px 10px;
  background: #fffaf0;
  border-radius: 4px;
}

.success {
  color: #2c7a1f;
}

.error {
  color: #c0392b;
}

.donation-list {
  border: 1px solid #e2d3aa;
  background: #fffaf0;
  padding: 10px 12px;
  border-radius: 4px;
}

.donation-row {
  border-bottom: 1px solid #eedfb8;
  padding: 10px 0;
}

.donation-row:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.row-header {
  display: flex;
  justify-content: space-between;
  font-weight: bold;
}

.effects {
  font-size: 12px;
  color: #7a4e12;
  margin: 4px 0;
}

.row-action {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
}

.input-label {
  margin-right: 4px;
}

.input {
  width: 90px;
  padding: 2px 4px;
  border: 1px solid #c8b27a;
  border-radius: 3px;
}

.btn {
  background: #c57900;
  color: #fff;
  border: none;
  padding: 3px 12px;
  border-radius: 3px;
  cursor: pointer;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.nav {
  margin-top: 16px;
}

.link {
  color: #0066cc;
  cursor: pointer;
}

.link:hover {
  text-decoration: underline;
}

.footer-info {
  margin-top: 18px;
  font-size: 11px;
  color: #777;
  border-top: 1px solid #ddd;
  padding-top: 8px;
}

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
