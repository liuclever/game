<script setup>
import { reactive, ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

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
    // 跳转到失败页面
    router.push({
      path: '/alliance/donate/result',
      query: {
        success: 'false',
        message: '请输入有效的捐赠数量'
      }
    })
    return
  }
  if (amount > item.available) {
    // 跳转到失败页面
    router.push({
      path: '/alliance/donate/result',
      query: {
        success: 'false',
        message: `当前仅拥有 ${item.available} 个${item.name}`
      }
    })
    return
  }
  submittingKey.value = item.key
  successMsg.value = ''
  try {
    const res = await http.post('/alliance/warehouse/donate', {
      donations: { [item.key]: amount },
    })
    if (res.data?.ok) {
      // 跳转到成功页面
      router.push({
        path: '/alliance/donate/result',
        query: {
          success: 'true',
          message: res.data.message || '捐赠成功',
          itemName: `${item.name} × ${amount}`
        }
      })
    } else {
      // 跳转到失败页面
      router.push({
        path: '/alliance/donate/result',
        query: {
          success: 'false',
          message: res.data?.error || '捐赠失败，请稍后再试'
        }
      })
    }
  } catch (err) {
    console.error('捐赠失败', err)
    // 跳转到失败页面
    router.push({
      path: '/alliance/donate/result',
      query: {
        success: 'false',
        message: err.response?.data?.error || '网络异常，请稍后再试'
      }
    })
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

// 监听路由变化，如果从结果页面返回则刷新数据
watch(() => route.query.refresh, (newVal) => {
  if (newVal === '1') {
    fetchDonationInfo()
  }
})
</script>

<template>
  <div class="donate-page">
    <div>【捐赠物资】</div>
    <div v-if="loading">加载中...</div>
    <div v-else-if="errorMsg">
      {{ errorMsg }}
      <a class="link" @click="fetchDonationInfo">点击重试</a>
    </div>
    <template v-else>
      <div v-if="successMsg">{{ successMsg }}</div>
      <div v-if="allianceStats">
        当前联盟资金：{{ allianceStats.funds ?? 0 }}<br />
        当前繁荣度：{{ allianceStats.prosperity ?? 0 }}
      </div>
      <div v-if="memberStats">
        我的贡献：{{ memberStats.contribution ?? 0 }}
      </div>

      <div v-for="item in donationItems" :key="item.key">
        <div>{{ item.name }} 拥有：{{ item.available }}</div>
        <div>每个可获得：
          <span v-if="item.effects.funds">+{{ item.effects.funds }} 资金；</span>
          <span>+{{ item.effects.prosperity }} 繁荣度；</span>
          <span>+{{ item.effects.contribution }} 个人贡献</span>
        </div>
        <div>
          捐赠数量：
          <input
            v-model="donationForm[item.key]"
            type="number"
            min="0"
            :disabled="submittingKey === item.key"
          />
          <button
            :disabled="submittingKey === item.key"
            @click="handleDonate(item)"
          >
            {{ submittingKey === item.key ? '提交中...' : '捐赠' }}
          </button>
        </div>
      </div>
    </template>

    <div><a class="link" @click="goBackAlliance">返回联盟</a></div>
    <div><a class="link" @click="goHome">返回游戏首页</a></div>
  </div>
</template>

<style scoped>
.donate-page {
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
