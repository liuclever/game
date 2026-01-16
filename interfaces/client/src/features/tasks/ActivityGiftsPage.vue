<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

const activePoints = ref(0)
const loading = ref(true)
const error = ref('')
const claimingKey = ref('')
const claimedGifts = ref(new Set())

const giftOptions = [
  { key: 'peach', name: '桃木召唤礼包', threshold: 10 },
  { key: 'bronze', name: '青铜召唤礼包', threshold: 60 },
  { key: 'silver', name: '白银召唤礼包', threshold: 80 },
  { key: 'gold', name: '黄金召唤礼包', threshold: 100 },
]

const giftStates = computed(() =>
  giftOptions.map(gift => {
    const claimed = claimedGifts.value.has(gift.key)
    return {
      ...gift,
      claimed,
      canClaim: !claimed && activePoints.value >= gift.threshold,
    }
  }),
)

const extractClaimedKeys = (completedTasks = []) => {
  const keys = completedTasks
    .filter(task => task.startsWith('claimed_gift:'))
    .map(task => task.replace('claimed_gift:', ''))
  claimedGifts.value = new Set(keys)
}

const fetchActivity = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await fetch('/api/task/daily_activity')
    const result = await response.json()
    if (result.ok) {
      activePoints.value = result.data.activity_value
      extractClaimedKeys(result.data.completed_tasks || [])
    } else {
      throw new Error(result.error || '数据获取失败')
    }
  } catch (err) {
    console.error('Failed to fetch activity gifts data:', err)
    error.value = err?.message || '加载失败'
  } finally {
    loading.value = false
  }
}

const handleClaim = async (gift) => {
  if (gift.claimed) {
    alert('该礼包已领取')
    return
  }
  if (!gift.canClaim) {
    alert(`${gift.name} 需要 ${gift.threshold} 点活跃度方可领取。`)
    return
  }
  if (claimingKey.value) return

  claimingKey.value = gift.key
  try {
    const res = await http.post('/task/activity_gift/claim', { key: gift.key })
    if (res.data?.ok) {
      alert('礼包已发送到背包，请前往背包打开。')
      claimedGifts.value = new Set([...claimedGifts.value, gift.key])
    } else {
      throw new Error(res.data?.error || '领取失败')
    }
  } catch (err) {
    console.error('领取礼包失败', err)
    alert(err?.response?.data?.error || err.message || '领取失败')
  } finally {
    claimingKey.value = ''
  }
}

onMounted(fetchActivity)
</script>

<template>
  <div class="activity-gifts-page">
    <div class="line">【今日累计活跃度:{{ activePoints }}点】</div>
    <div class="line">你当前可以领取以下礼包：</div>

    <div v-if="loading" class="status">加载中...</div>
    <div v-else-if="error" class="status error">{{ error }}</div>

    <div
      v-for="gift in giftStates"
      :key="gift.key"
      class="line gift-row"
      :class="{ available: gift.canClaim }"
    >
      <span>{{ gift.name }}</span>
      <template v-if="gift.claimed">
        <span class="hint">已领取</span>
      </template>
      <template v-else-if="gift.canClaim">
        <span
          class="link"
          :class="{ disabled: claimingKey === gift.key }"
          @click="handleClaim(gift)"
        >
          {{ claimingKey === gift.key ? '领取中...' : '领取' }}
        </span>
      </template>
      <template v-else>
        <span class="hint">（{{ gift.threshold }}点可领）</span>
      </template>
    </div>

    <div class="line link" @click="router.push('/tasks/daily')">返回每日事务</div>
    <div class="line link" @click="router.push('/')">返回游戏首页</div>
  </div>
</template>

<style scoped>
.activity-gifts-page {
  background-color: #fff;
  min-height: 100vh;
  padding: 10px;
  color: #000;
  font-size: 17px;
  line-height: 1.6;
}

.line {
  margin-bottom: 6px;
}

.status {
  margin: 8px 0;
}

.status.error {
  color: #c0392b;
}

.gift-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.gift-row.available span:first-child {
  font-weight: bold;
}

.hint {
  color: #666;
}

.link {
  color: #0000ee;
  text-decoration: underline;
  cursor: pointer;
}

.link.disabled {
  color: #888;
  cursor: not-allowed;
  pointer-events: none;
}
</style>
