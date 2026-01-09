<script setup>
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// 从URL参数获取结果信息
const success = route.query.success === 'true' || route.query.success === true
const itemName = route.query.name || ''
const quantity = route.query.quantity || 1
const cost = route.query.cost || 0
const currency = route.query.currency || 'gold'
const category = route.query.category || 'copper'
const errorMessage = route.query.error || '购买失败'

const currencyText = currency === 'gold' ? '铜钱' : '元宝'

const goShop = () => {
  router.push('/shop?category=' + category)
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="result-page">
    <!-- 成功情况 -->
    <template v-if="success">
      <div class="message success">购买{{ quantity }}个【{{ itemName }}】成功！已放入您的背包中。</div>
      <div class="cost">消耗{{ cost }}{{ currencyText }}</div>
    </template>
    
    <!-- 失败情况 -->
    <template v-else>
      <div class="message error">购买失败</div>
      <div class="error-detail">{{ errorMessage }}</div>
    </template>

    <div class="nav-links">
      <div><a class="link" @click="goShop">返回商城</a></div>
      <div><a class="link" @click="goHome">返回游戏首页</a></div>
    </div>

  </div>
</template>

<style scoped>
.result-page {
  background: #FFF8DC;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 14px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.message {
  color: #000;
  font-size: 16px;
  margin-bottom: 12px;
}

.message.success {
  color: #52c41a;
  font-weight: bold;
}

.message.error {
  color: #ff4d4f;
  font-weight: bold;
}

.cost {
  color: #000;
  margin-bottom: 16px;
}

.error-detail {
  color: #666;
  margin-bottom: 16px;
  padding: 8px;
  background: #fff2f0;
  border-left: 4px solid #ff4d4f;
  border-radius: 4px;
}

.nav-links {
  margin-top: 16px;
}

.nav-links div {
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
