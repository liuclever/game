<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

// 返回前页
const goBack = () => {
  router.back()
}

// 返回游戏首页
const goHome = () => {
  router.push('/')
}

// 去购买
const goToBuy = () => {
  router.push('/shop')
}
</script>

<template>
  <div class="key-insufficient-page">
    <div class="section title-section">
      <span class="title">战灵钥匙不足</span>
      <a class="link" @click="goToBuy">去购买</a>
    </div>
    
    <div class="section spacer">
      <a class="link" @click="goBack">返回前页</a>
    </div>
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
    
  </div>
</template>

<style scoped>
.key-insufficient-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 16px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 2px 0;
}

.title-section {
  margin-bottom: 4px;
}

.title-section .title {
  color: #0066CC;
  margin-right: 8px;
}

.spacer {
  margin-top: 16px;
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
  border-top: 1px solid #ccc;
}

.gray {
  color: #666;
}

.small {
  font-size: 17px;
}
</style>
