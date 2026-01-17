<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
<<<<<<< HEAD
=======
import MainMenuLinks from '@/features/main/components/MainMenuLinks.vue'
>>>>>>> new/daily-book

const router = useRouter()
const route = useRoute()

const rewards = ref([])
const drawType = ref('')

onMounted(() => {
  // 从sessionStorage获取抽奖结果
  const data = sessionStorage.getItem('lottery_result')
  if (data) {
    try {
      const parsed = JSON.parse(data)
      rewards.value = parsed.rewards || []
      drawType.value = parsed.drawType || ''
    } catch (e) {
      console.error('解析抽奖结果失败', e)
    }
  }
})

const drawTypeText = computed(() => {
  return drawType.value === 'ten' ? '十连抽' : '单抽'
})

const goBack = () => {
  router.push('/announcement/wheel_lottery')
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="lottery-result-page">
    <div class="section title">【{{ drawTypeText }}结果】</div>
    
    <div class="section" v-if="rewards.length === 0">
      <span class="gray">暂无抽奖结果</span>
    </div>
    
    <template v-else>
      <div class="section">恭喜获得以下物品：</div>
      <div class="reward-list">
        <div v-for="(reward, idx) in rewards" :key="idx" class="reward-item">
          <span class="reward-name">{{ reward.name }}</span>
          <span class="reward-qty" v-if="reward.quantity > 1">×{{ reward.quantity }}</span>
        </div>
      </div>
    </template>
    
    <div class="divider"></div>
<<<<<<< HEAD
=======

    <!-- 主页菜单（严格复刻主页内容与UI） -->
    <MainMenuLinks />
>>>>>>> new/daily-book
    
    <div class="section nav-links">
      <a class="link" @click="goBack">返回轮盘抽奖</a>
    </div>
    <div class="section nav-links">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.lottery-result-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 12px 16px;
<<<<<<< HEAD
  font-size: 16px;
=======
  font-size: 18px;
>>>>>>> new/daily-book
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 8px 0;
}

.title {
<<<<<<< HEAD
  font-size: 18px;
=======
  font-size: 20px;
>>>>>>> new/daily-book
  font-weight: bold;
  color: #CC3300;
  margin-bottom: 12px;
}

.divider {
  border-top: 1px dashed #CCCCCC;
  margin: 16px 0;
}

.reward-list {
  margin: 12px 0;
  padding: 12px;
  background: #ffffff;
  border: 1px solid #DDD;
  border-radius: 4px;
}

.reward-item {
  margin: 6px 0;
  padding: 4px 0;
  border-bottom: 1px dashed #EEE;
}

.reward-item:last-child {
  border-bottom: none;
}

.reward-name {
  color: #000000;
  font-weight: bold;
}

.reward-qty {
  color: #666;
  margin-left: 4px;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.gray {
  color: #999999;
}

.nav-links {
  margin-top: 8px;
}
</style>

