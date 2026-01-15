<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'
import { useMessage } from '@/composables/useMessage'

const router = useRouter()
const { message, messageType, showMessage } = useMessage()

const loading = ref(true)
const error = ref('')
const gifts = ref([])
const claimingKey = ref('')

const fetchGifts = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await http.get('/gifts/list')
    if (res.data?.ok) {
      gifts.value = res.data.gifts || []
    } else {
      throw new Error(res.data?.error || '加载失败')
    }
  } catch (e) {
    console.error('加载礼包失败', e)
    error.value = e?.response?.data?.error || e?.message || '加载礼包失败'
  } finally {
    loading.value = false
  }
}

const claimGift = async (gift) => {
  if (!gift || !gift.key) return
  if (gift.claimed) {
    showMessage('该礼包已领取', 'info')
    return
  }
  if (claimingKey.value) {
    showMessage('正在领取中，请稍候...', 'info')
    return
  }

  claimingKey.value = gift.key
  try {
    const res = await http.post('/gifts/claim', { key: gift.key })
    if (res.data?.ok) {
      const rewards = res.data.rewards || {}
      let msg = `领取成功：${gift.name}`
      const rewardParts = []
      if (rewards.gold) rewardParts.push(`铜钱：+${rewards.gold}`)
      if (rewards.yuanbao) rewardParts.push(`元宝：+${rewards.yuanbao}`)
      if (rewards.items && rewards.items.length) {
        rewardParts.push(`物品：${rewards.items.map(i => `${i.name}×${i.quantity}`).join('、')}`)
      }
      if (rewardParts.length > 0) {
        msg += `（${rewardParts.join('，')}）`
      }
      showMessage(msg, 'success')
      // 立即更新本地状态，防止重复点击
      const giftIndex = gifts.value.findIndex(g => g.key === gift.key)
      if (giftIndex >= 0) {
        gifts.value[giftIndex].claimed = true
      }
      await fetchGifts()
    } else {
      throw new Error(res.data?.error || '领取失败')
    }
  } catch (e) {
    console.error('领取礼包失败', e)
    const errorMsg = e?.response?.data?.error || e?.message || '领取礼包失败'
    showMessage(errorMsg, 'error')
    // 如果是因为已领取导致的错误，更新本地状态
    if (errorMsg.includes('已领取')) {
      const giftIndex = gifts.value.findIndex(g => g.key === gift.key)
      if (giftIndex >= 0) {
        gifts.value[giftIndex].claimed = true
      }
    }
  } finally {
    claimingKey.value = ''
  }
}

onMounted(fetchGifts)
</script>

<template>
  <div class="gifts-page">
    <!-- 消息提示 -->
    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>

    <div class="line">【礼包】</div>

    <div v-if="loading" class="line gray">加载中...</div>
    <div v-else-if="error" class="line error">{{ error }}</div>

    <template v-else>
      <div class="line" v-for="gift in gifts" :key="gift.key">
        {{ gift.name }}：{{ gift.detail }}
        <template v-if="gift.claimed">
          <span class="gray"> 已领取</span>
        </template>
        <template v-else>
          <a class="link" @click="claimGift(gift)">{{ claimingKey === gift.key ? '领取中...' : '领取' }}</a>
        </template>
      </div>
    </template>

    <div class="line">
      <a class="link" @click="router.push('/')">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.gifts-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 16px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.line {
  margin: 2px 0;
}

.gray {
  color: #666;
}

.error {
  color: #c0392b;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.link.disabled {
  color: #999;
  cursor: not-allowed;
  text-decoration: none;
}

.message {
  padding: 8px 12px;
  margin: 8px 0;
  border-radius: 4px;
  font-size: 16px;
  line-height: 1.5;
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
