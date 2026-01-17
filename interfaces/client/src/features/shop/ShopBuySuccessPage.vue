<script setup>
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// 从URL参数获取购买信息
const itemName = route.query.name || ''
const quantity = route.query.quantity || 1
const cost = route.query.cost || 0
const currency = route.query.currency || 'gold'
const category = route.query.category || 'copper'

const currencyText = currency === 'gold' ? '铜钱' : '元宝'

const goShop = () => {
  router.push('/shop?category=' + category)
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="success-page">
    <div class="message">购买{{ quantity }}个【{{ itemName }}】成功！已放入您的背包中。</div>
    <div class="cost">消耗{{ cost }}{{ currencyText }}</div>

    <div class="nav-links">
      <div><a class="link" @click="goShop">返回商城</a></div>
      <div><a class="link" @click="goHome">返回游戏首页</a></div>
    </div>

  </div>
</template>

<style scoped>
.success-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 17px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.message {
  color: #000;
}

.cost {
  color: #000;
  margin-bottom: 16px;
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

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}

.gray {
  color: #666666;
}

.small {
  font-size: 17px;
}
</style>
