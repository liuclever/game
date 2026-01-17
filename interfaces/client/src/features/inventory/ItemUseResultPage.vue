<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MainMenuLinks from '@/features/main/components/MainMenuLinks.vue'

const route = useRoute()
const router = useRouter()

const itemName = ref('')
const quantity = ref(1)
const message = ref('')
const rewards = ref({})

// 解析奖励数据
const parseRewards = () => {
  try {
    const rewardsStr = route.query.rewards
    if (rewardsStr) {
      rewards.value = JSON.parse(rewardsStr)
    }
  } catch (e) {
    console.error('解析奖励数据失败', e)
  }
}

// 返回背包
const goBack = () => {
  router.push('/inventory')
}

// 返回首页
const goHome = () => {
  router.push('/')
}

onMounted(() => {
  itemName.value = route.query.itemName || ''
  quantity.value = parseInt(route.query.quantity) || 1
  message.value = route.query.message || '使用成功'
  parseRewards()
})
</script>

<template>
  <div class="result-page">
    <div class="section title">【使用结果】</div>
    
    <div class="section">
      <div class="success-message">{{ message }}</div>
    </div>

    <div class="section" v-if="Object.keys(rewards).length > 0">
      <div class="rewards-title">获得奖励：</div>
      <div class="rewards-list">
        <div v-for="(count, name) in rewards" :key="name" class="reward-item">
          {{ name }}×{{ count }}
        </div>
      </div>
    </div>

    <div class="section">
      <a class="link" @click="goBack">返回背包</a>
    </div>
    <!-- 主页菜单（严格复刻主页内容与UI） -->
    <MainMenuLinks />
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.result-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 19px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 8px 0;
}

.title {
  font-weight: bold;
  font-size: 20px;
  margin-bottom: 12px;
}

.success-message {
  color: #155724;
  font-weight: bold;
  font-size: 20px;
  padding: 12px;
  background: #d4edda;
  border: 1px solid #c3e6cb;
  border-radius: 4px;
  margin-bottom: 16px;
}

.rewards-title {
  font-weight: bold;
  margin-bottom: 8px;
}

.rewards-list {
  padding: 12px;
  background: #f5f5f5;
  border-radius: 4px;
}

.reward-item {
  padding: 4px 0;
  color: #CC3300;
  font-weight: bold;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
  margin-right: 12px;
}

.link:hover {
  text-decoration: underline;
}
</style>
