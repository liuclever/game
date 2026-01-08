<template>
  <div class="task-rewards-page">
    <div class="header">
      <router-link class="link" to="/">← 返回首页</router-link>
      <h1>任务奖励</h1>
    </div>

    <div v-if="loading" class="status">加载中...</div>
    <div v-else-if="error" class="status error">{{ error }}</div>

    <div v-else class="rewards">
      <div
        v-for="reward in rewards"
        :key="reward.key"
        class="reward-card"
        :class="{ claimed: reward.claimed }"
      >
        <div class="reward-info">
          <div class="reward-name">{{ reward.name }}</div>
          <div class="reward-desc">
            {{ reward.description || formatDescription(reward) }}
          </div>
        </div>
        <button
          class="claim-btn"
          :disabled="reward.claimed || claimingKey === reward.key"
          @click="claimReward(reward)"
        >
          <template v-if="reward.claimed">已领取</template>
          <template v-else-if="claimingKey === reward.key">领取中...</template>
          <template v-else>领取</template>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import http from '@/services/http'

const rewards = ref([])
const loading = ref(false)
const error = ref('')
const claimingKey = ref('')

const loadRewards = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await http.get('/task/reward/status')
    if (res.data?.ok) {
      rewards.value = res.data.rewards || []
    } else {
      throw new Error(res.data?.error || '加载失败')
    }
  } catch (err) {
    console.error('加载任务奖励失败', err)
    error.value = err?.response?.data?.error || err.message || '加载失败'
  } finally {
    loading.value = false
  }
}

const claimReward = async (reward) => {
  if (reward.claimed || claimingKey.value) return
  claimingKey.value = reward.key
  try {
    const res = await http.post('/task/reward/claim', { key: reward.key })
    if (res.data?.ok) {
      reward.claimed = true
      alert(`领取成功：${reward.name} x${reward.amount}`)
    } else {
      throw new Error(res.data?.error || '领取失败')
    }
  } catch (err) {
    console.error('领取奖励失败', err)
    alert(err?.response?.data?.error || err.message || '领取失败')
  } finally {
    claimingKey.value = ''
  }
}

const formatDescription = (reward) => {
  if (reward.reward_type === 'item') {
    return `${reward.name} x${reward.amount}`
  }
  if (reward.reward_type === 'gold') {
    return `铜钱 x${reward.amount}`
  }
  return reward.name
}

onMounted(loadRewards)
</script>

<style scoped>
.task-rewards-page {
  max-width: 520px;
  margin: 0 auto;
  padding: 20px;
  color: #2d2d2d;
}

.header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.header h1 {
  margin: 0;
  font-size: 22px;
  color: #1b4b91;
}

.link {
  color: #1b4b91;
  text-decoration: none;
  font-size: 14px;
}

.status {
  text-align: center;
  padding: 20px 0;
  font-size: 16px;
}

.status.error {
  color: #c0392b;
}

.rewards {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.reward-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border: 1px solid #dcdcdc;
  border-radius: 10px;
  background: #fff;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.06);
}

.reward-card.claimed {
  opacity: 0.65;
}

.reward-info {
  flex: 1;
  margin-right: 16px;
}

.reward-name {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 6px;
}

.reward-desc {
  font-size: 14px;
  color: #666;
}

.claim-btn {
  min-width: 80px;
  padding: 8px 16px;
  border: none;
  border-radius: 999px;
  background: linear-gradient(135deg, #ffb347, #ffcc33);
  color: #40210f;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.15s ease, opacity 0.15s ease;
}

.claim-btn:disabled {
  background: #e0e0e0;
  color: #777;
  cursor: not-allowed;
}

.claim-btn:not(:disabled):hover {
  transform: translateY(-1px);
}
</style>
