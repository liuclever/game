<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

const days = ref(7) // 7, 15, 或 30
const loading = ref(false)
const rewardInfo = ref(null)

const rewardConfig = {
  7: {
    title: '7天礼包',
    value: '700元宝',
    items: [
      '化仙丹×1',
      '随机结晶×1',
      '战灵-土灵×1',
      '骰子包×2',
      '捕捉球×3',
      '迷踪符×3'
    ]
  },
  15: {
    title: '15天礼包',
    value: '1500元宝',
    items: [
      '招财神符×1',
      '灵力水晶×1',
      '战灵-土灵×2',
      '炼魂丹×1',
      '强力捕捉球×1',
      '镇妖符×3'
    ]
  },
  30: {
    title: '30天礼包',
    value: '3000元宝',
    items: [
      '铜钱×800000',
      '神·逆鳞碎片×15',
      '追魂法宝×2',
      '重生丹×1',
      '火灵灵石×1',
      '灵力水晶×1',
      '炼魂丹×3',
      '骰子包×2',
      '强力捕捉球×2',
      '捕捉球×6',
      '补签卡×1'
    ]
  }
}

const currentReward = computed(() => rewardConfig[days.value])

const canClaim = computed(() => {
  if (!rewardInfo.value) return false
  return rewardInfo.value.consecutiveDays >= days.value && !rewardInfo.value.claimed
})

const loadRewardInfo = async () => {
  loading.value = true
  try {
    const res = await http.get(`/signin/reward/${days.value}`)
    if (res.data.ok) {
      rewardInfo.value = res.data
    }
  } catch (e) {
    console.error('加载奖励信息失败', e)
  } finally {
    loading.value = false
  }
}

const claimReward = async () => {
  if (!canClaim.value) return
  
  loading.value = true
  try {
    const res = await http.post(`/signin/reward/${days.value}/claim`)
    if (res.data.ok) {
      console.log('领取成功')
      loadRewardInfo()
    } else {
      console.error(res.data.error || '领取失败')
    }
  } catch (e) {
    console.error('领取失败', e)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/signin')
}

const goHome = () => {
  router.push('/')
}

onMounted(() => {
  const d = parseInt(route.query.days)
  if ([7, 15, 30].includes(d)) {
    days.value = d
  }
  loadRewardInfo()
})
</script>

<template>
  <div class="reward-page">
    <div class="section" v-if="loading">加载中...</div>
    
    <template v-else-if="currentReward">
      <!-- 标题 -->
      <div class="section">{{ currentReward.title }}</div>
      
      <!-- 价值 -->
      <div class="section">价值{{ currentReward.value }}，内含：</div>
      
      <!-- 物品列表 -->
      <div class="section" v-for="(item, idx) in currentReward.items" :key="idx">
        {{ item }}
      </div>
      
      <!-- 领取状态 -->
      <div class="section" v-if="rewardInfo">
        <template v-if="rewardInfo.claimed">
          <span style="font-weight: bold;">已领取</span>
        </template>
        <template v-else-if="canClaim">
          <a class="link" @click="claimReward">点击领取</a>
        </template>
        <template v-else>
          <span>需要累计签到{{ days }}天（当前{{ rewardInfo.consecutiveDays }}天）</span>
        </template>
      </div>
    </template>
    
    <!-- 返回链接 -->
    <div class="section">
      <a class="link" @click="goBack">返回前页</a>
    </div>
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.reward-page {
  background: #FFF8DC;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 13px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 4px 0;
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
