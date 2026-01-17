<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

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
    console.error('该礼包已领取')
    return
  }
  if (claimingKey.value) {
    console.error('正在领取中，请稍候...')
    return
  }

  claimingKey.value = gift.key
  try {
    const res = await http.post('/gifts/claim', { key: gift.key })
    if (res.data?.ok) {
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
    console.error(errorMsg)
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
</style>
