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
    alert('该礼包已领取')
    return
  }
  if (claimingKey.value) return

  claimingKey.value = gift.key
  try {
    const res = await http.post('/gifts/claim', { key: gift.key })
    if (res.data?.ok) {
      const rewards = res.data.rewards || {}
      let msg = `领取成功：${gift.name}`
      if (rewards.gold) msg += `\n铜钱：+${rewards.gold}`
      if (rewards.yuanbao) msg += `\n元宝：+${rewards.yuanbao}`
      if (rewards.items && rewards.items.length) {
        msg += `\n物品：` + rewards.items.map(i => `${i.name}×${i.quantity}`).join('、')
      }
      alert(msg)
      await fetchGifts()
    } else {
      throw new Error(res.data?.error || '领取失败')
    }
  } catch (e) {
    console.error('领取礼包失败', e)
    alert(e?.response?.data?.error || e?.message || '领取礼包失败')
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
  background: #FFF8DC;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 13px;
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
</style>
